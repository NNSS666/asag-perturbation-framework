"""
Submit a large JSONL batch in chunks that fit within OpenAI's enqueued token limit.

Splits the input file into chunks, submits each one, waits for completion,
and downloads results — all automatically. No babysitting needed.

Usage:
    PYTHONPATH=src python3 -m scripts.submit_batch_chunked runs/batch_input/llm_openai_gpt-5.4-mini_level1.jsonl

    # Custom chunk size (default 5000 requests per chunk)
    PYTHONPATH=src python3 -m scripts.submit_batch_chunked --chunk-size 3000 runs/batch_input/FILE.jsonl

    # Resume from a previous interrupted run
    PYTHONPATH=src python3 -m scripts.submit_batch_chunked --resume runs/batch_input/FILE.jsonl
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List


def _read_lines(path: Path) -> List[str]:
    """Read non-empty lines from a JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        return [line for line in f if line.strip()]


def _chunk_list(lst: List[str], size: int) -> List[List[str]]:
    """Split a list into chunks of given size."""
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def _load_progress(progress_path: Path) -> int:
    """Load the index of the last completed chunk."""
    if not progress_path.exists():
        return -1
    with open(progress_path, "r") as f:
        data = json.load(f)
    return data.get("last_completed_chunk", -1)


def _save_progress(progress_path: Path, chunk_idx: int, batch_id: str) -> None:
    """Save progress after a chunk completes."""
    history = []
    if progress_path.exists():
        with open(progress_path, "r") as f:
            data = json.load(f)
            history = data.get("history", [])

    history.append({"chunk": chunk_idx, "batch_id": batch_id})

    with open(progress_path, "w") as f:
        json.dump({
            "last_completed_chunk": chunk_idx,
            "history": history,
        }, f, indent=2)


def submit_and_wait(lines: List[str], chunk_idx: int, total_chunks: int,
                    grader_name: str, output_dir: Path) -> Path:
    """Submit one chunk, poll until done, download results. Returns output path."""
    from openai import OpenAI

    client = OpenAI()

    # Write chunk to temp file
    chunk_path = output_dir / f"_chunk_{chunk_idx:03d}.jsonl"
    with open(chunk_path, "w") as f:
        f.writelines(lines)

    n_requests = len(lines)
    print(f"\n{'='*60}")
    print(f"Chunk {chunk_idx + 1}/{total_chunks} — {n_requests:,} requests")
    print(f"{'='*60}")

    # Upload
    print("  Uploading...")
    batch_file = client.files.create(
        file=open(chunk_path, "rb"),
        purpose="batch",
    )
    print(f"  File: {batch_file.id}")

    # Create batch
    batch = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": f"{grader_name}_chunk{chunk_idx:03d}"},
    )
    print(f"  Batch: {batch.id}")
    print(f"  Status: {batch.status}")

    # Poll until done
    poll_interval = 30  # seconds
    while True:
        time.sleep(poll_interval)
        batch = client.batches.retrieve(batch.id)
        rc = batch.request_counts

        if rc and rc.total > 0:
            pct = rc.completed / rc.total * 100
            print(
                f"\r  [{batch.status}] {rc.completed}/{rc.total} ({pct:.0f}%) "
                f"| {rc.failed} failed",
                end="", flush=True,
            )
        else:
            print(f"\r  [{batch.status}] waiting...", end="", flush=True)

        if batch.status == "completed":
            print()  # newline
            break
        elif batch.status in ("failed", "expired", "cancelled"):
            print(f"\n  ERROR: Batch {batch.status}")
            if batch.errors and batch.errors.data:
                for err in batch.errors.data:
                    print(f"    {err.message}")
            sys.exit(1)

        # Increase poll interval gradually (max 2 min)
        poll_interval = min(poll_interval + 10, 120)

    # Download results
    result_path = output_dir / f"chunk_{chunk_idx:03d}_results.jsonl"
    if batch.output_file_id:
        content = client.files.content(batch.output_file_id)
        with open(result_path, "w") as f:
            f.write(content.text)
        n_results = sum(1 for l in content.text.strip().split("\n") if l.strip())
        print(f"  Downloaded: {n_results:,} results -> {result_path.name}")
    else:
        print("  WARNING: No output file available")

    # Cleanup temp chunk file
    chunk_path.unlink(missing_ok=True)

    return result_path


def merge_results(output_dir: Path, grader_name: str) -> Path:
    """Merge all chunk results into a single output file."""
    merged_path = output_dir.parent / "batch_output" / f"{grader_name}.jsonl"
    merged_path.parent.mkdir(parents=True, exist_ok=True)

    chunk_files = sorted(output_dir.glob("chunk_*_results.jsonl"))
    total = 0

    with open(merged_path, "w") as out:
        for cf in chunk_files:
            with open(cf, "r") as f:
                for line in f:
                    if line.strip():
                        out.write(line)
                        total += 1

    print(f"\nMerged {total:,} results -> {merged_path}")
    return merged_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Submit batch in chunks with automatic polling."
    )
    parser.add_argument("input_file", help="Path to the full JSONL batch input file")
    parser.add_argument(
        "--chunk-size", type=int, default=5000,
        help="Requests per chunk (default: 5000)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from last completed chunk"
    )
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    # Infer grader name
    grader_name = input_path.stem  # e.g. llm_openai_gpt-5.4-mini_level1

    # Setup output directory for chunks
    output_dir = Path("runs") / "batch_chunks" / grader_name
    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = output_dir / "_progress.json"

    # Read and chunk
    all_lines = _read_lines(input_path)
    chunks = _chunk_list(all_lines, args.chunk_size)

    print(f"Input: {input_path.name}")
    print(f"Total requests: {len(all_lines):,}")
    print(f"Chunk size: {args.chunk_size:,}")
    print(f"Chunks: {len(chunks)}")

    # Resume support
    start_from = 0
    if args.resume:
        start_from = _load_progress(progress_path) + 1
        if start_from > 0:
            print(f"Resuming from chunk {start_from + 1}/{len(chunks)}")

    if start_from >= len(chunks):
        print("All chunks already completed!")
    else:
        # Process chunks sequentially
        t_start = time.time()
        for i in range(start_from, len(chunks)):
            result_path = submit_and_wait(
                chunks[i], i, len(chunks), grader_name, output_dir
            )
            _save_progress(progress_path, i, "completed")

            elapsed = time.time() - t_start
            chunks_done = i - start_from + 1
            chunks_left = len(chunks) - i - 1
            if chunks_done > 0 and chunks_left > 0:
                avg_per_chunk = elapsed / chunks_done
                eta_min = (chunks_left * avg_per_chunk) / 60
                print(f"  ETA remaining: ~{eta_min:.0f} min")

    # Merge all chunk results
    merged = merge_results(output_dir, grader_name)

    total_time = time.time() - t_start if start_from < len(chunks) else 0
    print(f"\nTotal time: {total_time/60:.0f} min")
    print(f"\nNext step — convert to grade cache:")
    print(f"  PYTHONPATH=src python3 -m scripts.convert_batch_results {merged}")


if __name__ == "__main__":
    main()
