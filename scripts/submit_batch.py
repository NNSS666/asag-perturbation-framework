"""
Submit a JSONL file to OpenAI Batch API and optionally poll for completion.

Usage:
    # Submit a batch
    PYTHONPATH=src python3 -m scripts.submit_batch runs/batch_input/llm_openai_gpt-5.4-mini_level1.jsonl

    # Check status of a batch
    PYTHONPATH=src python3 -m scripts.submit_batch --status batch_abc123

    # Download results of a completed batch
    PYTHONPATH=src python3 -m scripts.submit_batch --download batch_abc123

    # Submit all pending batch files
    PYTHONPATH=src python3 -m scripts.submit_batch --all
"""

import argparse
import json
import sys
from pathlib import Path


def submit_batch(jsonl_path: str) -> str:
    """Upload JSONL and create a batch job. Returns batch ID."""
    from openai import OpenAI

    client = OpenAI()
    path = Path(jsonl_path)

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    # Count requests
    with open(path, "r") as f:
        n_requests = sum(1 for line in f if line.strip())

    print(f"Uploading {path.name} ({n_requests:,} requests)...")
    batch_file = client.files.create(
        file=open(path, "rb"),
        purpose="batch",
    )
    print(f"  File uploaded: {batch_file.id}")

    batch = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": path.stem},
    )
    print(f"  Batch created: {batch.id}")
    print(f"  Status: {batch.status}")

    # Save batch ID for later retrieval
    tracker_path = Path("runs") / "batch_jobs.jsonl"
    tracker_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tracker_path, "a") as f:
        f.write(json.dumps({
            "batch_id": batch.id,
            "file_id": batch_file.id,
            "source": str(path),
            "n_requests": n_requests,
        }) + "\n")
    print(f"  Tracked in {tracker_path}")

    return batch.id


def check_status(batch_id: str) -> None:
    """Check the status of a batch job."""
    from openai import OpenAI

    client = OpenAI()
    batch = client.batches.retrieve(batch_id)
    print(f"Batch: {batch.id}")
    print(f"  Status: {batch.status}")
    print(f"  Created: {batch.created_at}")
    if batch.request_counts:
        rc = batch.request_counts
        print(f"  Completed: {rc.completed}/{rc.total} ({rc.failed} failed)")
    if batch.output_file_id:
        print(f"  Output file: {batch.output_file_id}")
    if batch.error_file_id:
        print(f"  Error file: {batch.error_file_id}")


def download_results(batch_id: str) -> None:
    """Download results of a completed batch and save to runs/batch_output/."""
    from openai import OpenAI

    client = OpenAI()
    batch = client.batches.retrieve(batch_id)

    if batch.status != "completed":
        print(f"Batch {batch_id} is not completed yet (status: {batch.status})")
        sys.exit(1)

    if not batch.output_file_id:
        print("No output file available.")
        sys.exit(1)

    output_dir = Path("runs") / "batch_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use description from metadata as filename
    desc = (batch.metadata or {}).get("description", batch_id)
    output_path = output_dir / f"{desc}.jsonl"

    print(f"Downloading results to {output_path}...")
    content = client.files.content(batch.output_file_id)
    with open(output_path, "w") as f:
        f.write(content.text)

    # Count results
    n_results = sum(1 for line in content.text.strip().split("\n") if line.strip())
    print(f"  Downloaded {n_results:,} results")

    # Check for errors
    if batch.error_file_id:
        error_path = output_dir / f"{desc}_errors.jsonl"
        error_content = client.files.content(batch.error_file_id)
        with open(error_path, "w") as f:
            f.write(error_content.text)
        n_errors = sum(1 for line in error_content.text.strip().split("\n") if line.strip())
        if n_errors > 0:
            print(f"  {n_errors} errors saved to {error_path}")

    print(f"\nNext: convert results to grade cache:")
    print(f"  PYTHONPATH=src python3 -m scripts.convert_batch_results {output_path}")


def check_all() -> None:
    """Check status of all tracked batch jobs."""
    tracker_path = Path("runs") / "batch_jobs.jsonl"
    if not tracker_path.exists():
        print("No batch jobs tracked yet.")
        return

    from openai import OpenAI
    client = OpenAI()

    with open(tracker_path) as f:
        jobs = [json.loads(line) for line in f if line.strip()]

    print(f"{'Batch ID':<30} {'Source':<45} {'Status':<15} {'Progress'}")
    print("-" * 100)

    for job in jobs:
        batch = client.batches.retrieve(job["batch_id"])
        rc = batch.request_counts
        progress = f"{rc.completed}/{rc.total}" if rc else "?"
        source = Path(job["source"]).stem
        print(f"{job['batch_id']:<30} {source:<45} {batch.status:<15} {progress}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit/manage OpenAI Batch API jobs.")
    parser.add_argument("file_or_id", nargs="?", help="JSONL file to submit OR batch ID for --status/--download")
    parser.add_argument("--status", action="store_true", help="Check status of a batch")
    parser.add_argument("--download", action="store_true", help="Download results of a completed batch")
    parser.add_argument("--all", action="store_true", help="Check status of all tracked batches")
    args = parser.parse_args()

    if args.all:
        check_all()
    elif args.status and args.file_or_id:
        check_status(args.file_or_id)
    elif args.download and args.file_or_id:
        download_results(args.file_or_id)
    elif args.file_or_id and not args.status and not args.download:
        submit_batch(args.file_or_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
