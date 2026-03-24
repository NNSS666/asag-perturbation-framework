# Stack Research

**Domain:** Perturbation-based ASAG evaluation framework (Python ML research)
**Researched:** 2026-02-20
**Confidence:** HIGH (all versions verified from PyPI as of research date)

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11.x | Runtime | Sweet spot: supported by every library below; 3.12+ has breaking C-extension issues with some older ML libs; 3.10 minimum required by PyTorch/transformers |
| PyTorch | 2.10.0 | Deep learning backbone | Project constraints specify PyTorch explicitly; non-negotiable for research reproducibility; native GPU support; dominant in academic ML |
| transformers (HuggingFace) | 5.2.0 | Load and fine-tune BERT/DeBERTa/ModernBERT graders | Canonical access to all encoder models; version 5.x adds full Trainer API for classification/regression fine-tuning; required by sentence-transformers |
| sentence-transformers | 5.2.3 | Semantic similarity features for hybrid grader | Wraps HuggingFace with sentence-level pooling; required for cosine similarity between student and reference answers in hybrid grader; well-maintained, actively released |
| datasets (HuggingFace) | 4.5.0 | Load SRA / SemEval 2013 benchmarks; manage custom dataset | Arrow-backed streaming avoids OOM on large datasets; built-in train/test split and map transforms; standard for NLP research pipelines |

### Grading Models

| Model | HuggingFace ID | Purpose | Why |
|-------|---------------|---------|-----|
| DeBERTa-v3-base | `microsoft/deberta-v3-base` | Primary supervised grader (fine-tuned classifier/regressor) | MEDIUM confidence: outperforms BERT/RoBERTa on classification tasks; DeBERTa-v3 uses ELECTRA pretraining with disentangled attention; best accuracy/compute tradeoff for ASAG classification as of 2024 research |
| ModernBERT-base | `answerdotai/ModernBERT-base` | Alternative supervised grader for comparison | HIGH confidence: released Dec 2024, 149M params, 2T token pretraining, 8192-context native length; faster than DeBERTa (4x on mixed lengths); 951K downloads/month on HuggingFace; 1,089+ fine-tunes |
| all-mpnet-base-v2 | `sentence-transformers/all-mpnet-base-v2` | Semantic similarity baseline for hybrid grader | HIGH confidence: SBERT top-performing English model; strong cosine-similarity scores for paraphrase detection; suitable for reference-answer alignment |

### LLM APIs (Perturbation Generation + LLM Grader)

| Library | Version | LLMs Accessed | Why |
|---------|---------|--------------|-----|
| litellm | 1.81.13 | GPT-4o, Claude Sonnet, Gemini Pro (single interface) | HIGH confidence: unified API surface for 100+ LLMs; avoids maintaining 3 separate SDK integrations; built-in cost tracking critical for budget-aware usage; token logging for reproducibility; active releases (multiple per week) |
| openai | 2.21.0 | GPT-4o / GPT-4o-mini | HIGH confidence: required for OpenAI models even when routing via litellm; current v2 SDK |
| anthropic | 0.83.0 | Claude 3.5 Sonnet / Claude 3 Haiku | HIGH confidence: Anthropic SDK; use haiku for cheap perturbation generation, sonnet for grading evaluation |
| google-genai | 1.64.0 | Gemini 2.0 Flash / Gemini Pro | HIGH confidence: replaces deprecated google-generativeai (EOL Nov 2025); unified Gemini+Vertex SDK; use `from google import genai` |

**LLM strategy:** Use litellm as the routing layer so model swaps don't require code changes. Log all prompts + completions to JSON files for reproducibility (academic requirement).

### Statistical Testing

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| scipy | 1.17.0 | Wilcoxon signed-rank, Mann-Whitney U, Friedman test | HIGH confidence: gold standard for non-parametric tests; use for comparing IVR/SSR/ASR scores across graders; `scipy.stats.wilcoxon`, `scipy.stats.friedmanchisquare` |
| pingouin | 0.5.5 | Effect sizes (Cohen's d, rank-biserial r) alongside p-values | HIGH confidence: extends scipy with automatic effect size computation; one call returns p-value + effect size + confidence intervals; critical for paper reporting |
| scikit-learn | 1.8.0 | QWK, Cohen's kappa, accuracy, precision/recall | HIGH confidence: `sklearn.metrics.cohen_kappa_score(weights='quadratic')` for QWK; standard classification metrics for grader baselines |

### Data Science / Utilities

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| pandas | 3.0.1 | Dataset loading, result aggregation, metric tables | HIGH confidence: per-question breakdown tables, cross-fold aggregation; requires Python >=3.11 |
| numpy | 2.4.2 | Array ops, score arrays, aggregation | HIGH confidence: underlying computation layer for all statistical ops |
| tqdm | ~4.67 | Progress bars for perturbation loops and evaluation runs | Standard; no alternative needed |

### Visualization

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| matplotlib | 3.10.8 | Publication-quality figures (bar charts, heatmaps, confusion matrices) | HIGH confidence: academic standard; fine-grained control over every plot element; 300 DPI export for papers |
| seaborn | 0.13.2 | Statistical visualization (distribution plots, violin plots, grouped bars) | HIGH confidence: builds on matplotlib; produces publication-ready figures in fewer lines; `seaborn.heatmap` for per-question metric matrices |

### Rule-Based Perturbation

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| spaCy | ~3.8.x | POS tagging, dependency parsing, NER for rule-based perturbations | HIGH confidence: fast industrial-grade NLP; required for adjective/adverb insertion (Filighera et al. 2024 methodology), synonym substitution targeting content words only, stopword removal |
| nltk | ~3.9 | WordNet synonym lookup for lexical perturbations | MEDIUM confidence: WordNet is the canonical source for rule-based synonym substitution; download `wordnet` and `averaged_perceptron_tagger` corpora |

### Experiment Management

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| hydra-core | 1.3.2 (stable) | Hierarchical config management for experiment runs | MEDIUM confidence: stable at 1.3.2; dev pre-release 1.4.0 not recommended for research reproducibility; compose per-experiment YAML overrides without touching code; seed, model, perturbation-family configs |
| python-dotenv | ~1.0 | Load API keys from .env files | Standard; keeps secrets out of config files and git history |

---

## Installation

```bash
# Python 3.11 recommended (use pyenv or conda)
# conda create -n asag python=3.11
# conda activate asag

# Core ML
pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu
# For GPU: replace cpu with cu124 or cu128 depending on CUDA version

pip install transformers==5.2.0
pip install sentence-transformers==5.2.3
pip install datasets==4.5.0

# Grading models are loaded on-demand from HuggingFace Hub (no separate install)

# LLM APIs
pip install litellm==1.81.13
pip install openai==2.21.0
pip install anthropic==0.83.0
pip install google-genai==1.64.0

# Statistical testing
pip install scipy==1.17.0
pip install pingouin==0.5.5
pip install scikit-learn==1.8.0

# Data science
pip install pandas==3.0.1
pip install numpy==2.4.2
pip install tqdm

# Visualization
pip install matplotlib==3.10.8
pip install seaborn==0.13.2

# Rule-based perturbation
pip install spacy==3.8.*
python -m spacy download en_core_web_sm

pip install nltk
python -c "import nltk; nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"

# Experiment management
pip install hydra-core==1.3.2
pip install python-dotenv

# Dev tools
pip install pytest black isort
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|------------------------|
| litellm (unified LLM router) | Individual SDK per provider (openai + anthropic + google-genai directly) | Only if litellm overhead is unacceptable or you're using exactly one LLM provider; for multi-LLM comparison research, litellm is strictly better |
| DeBERTa-v3-base | RoBERTa-base | RoBERTa is faster and uses less GPU RAM; acceptable if compute is severely constrained; DeBERTa outperforms on classification tasks |
| DeBERTa-v3-base | ModernBERT-base | ModernBERT is newer (Dec 2024), faster, and 8k context; for ASAG (short answers), context length is irrelevant; benchmarks show DeBERTa still leads on controlled comparisons (Timoneda et al. 2025) |
| hydra-core | argparse / plain YAML | Use argparse only for very simple scripts; Hydra is worth the learning curve for experiment reproducibility at research scale |
| pingouin | statsmodels | statsmodels is more comprehensive but harder API; pingouin returns effect sizes automatically alongside p-values, which is exactly what paper tables need |
| spaCy | NLTK alone | NLTK lacks fast dependency parsing needed for accurate adjective/adverb insertion; spaCy is faster and more accurate for POS-based perturbation targeting |
| seaborn 0.13.2 | plotly | Plotly is interactive; academic papers need static rasterized figures; matplotlib/seaborn export to PDF/PNG at 300 DPI cleanly |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| google-generativeai | EOL November 30, 2025; no longer maintained | `google-genai` (the unified Google GenAI SDK) |
| TensorFlow / Keras | Project constraints specify PyTorch; TF ecosystem diverges from HuggingFace transformers ecosystem; mixing causes dependency conflicts | PyTorch + HuggingFace transformers |
| nlpaug | Last substantial update 2022; dependency conflicts with transformers 5.x; issues filed as of 2025 without resolution | spaCy + NLTK for rule-based; LLM APIs for semantic perturbations |
| TextAttack | Designed for adversarial attack research (NLP model robustness against character-level/word-level attacks), not semantic invariance testing; overkill dependency tree | Custom perturbation engine using spaCy + LLMs |
| langchain | Heavyweight framework with significant abstraction overhead; adds unpredictable complexity; not needed when litellm already provides multi-LLM routing | litellm directly |
| hydra-core 1.4.0.dev1 | Pre-release; not stable; last stable is 1.3.2 (Feb 2023); dev release may introduce breaking config changes | hydra-core==1.3.2 |
| BERT-base-uncased | Outperformed by DeBERTa-v3 and ModernBERT on classification; no reason to use original BERT in 2026 | DeBERTa-v3-base or ModernBERT-base |
| pandas < 2.0 | Copy-on-write semantics changed in 2.0+; mixing old and new pandas code causes silent data mutation bugs | pandas 3.0.1 |

---

## Stack Patterns by Variant

**For the supervised transformer grader:**
- Use `transformers.AutoModelForSequenceClassification` with DeBERTa-v3-base or ModernBERT-base
- Fine-tune with `transformers.Trainer` for classification (correct/incorrect/partially correct) or regression (score)
- Load SRA/SemEval via `datasets` library; tokenize with `AutoTokenizer`
- LOQO cross-validation: implement as manual k-fold loop (Trainer doesn't natively support leave-one-question-out)

**For the hybrid grader (linguistic features + embeddings):**
- Extract cosine similarity between student and reference answer using sentence-transformers (`all-mpnet-base-v2`)
- Extract handcrafted features via spaCy: token overlap ratio, dependency parse match, named entity overlap
- Combine in a scikit-learn pipeline: `sklearn.pipeline.Pipeline` with `StandardScaler` + `LogisticRegression` or `GradientBoostingClassifier`

**For the LLM rubric grader:**
- Route all calls through litellm: `litellm.completion(model="gpt-4o", ...)` / `litellm.completion(model="claude-3-5-sonnet-20241022", ...)`
- Store all prompt templates in Hydra config YAML files
- Log every API response (model, version, temperature, prompt, completion) to JSONL for reproducibility

**For perturbation generation:**
- Rule-based (deterministic): implement directly with spaCy POS tags + NLTK WordNet; seed with Python `random.seed(42)` for reproducibility
- LLM-assisted (semantic): route through litellm; use temperature=0.7 with a fixed seed where supported; store all outputs

**For statistical testing of metrics:**
- Use `scipy.stats.wilcoxon` for paired comparisons (same questions, different graders)
- Use `scipy.stats.friedmanchisquare` for multi-grader omnibus test
- Use `pingouin.wilcoxon` when you need rank-biserial effect size automatically
- Use `sklearn.metrics.cohen_kappa_score(weights='quadratic')` for QWK

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| torch==2.10.0 | Python >=3.10, CUDA 12.4/12.8 | For CPU-only: `--index-url https://download.pytorch.org/whl/cpu` |
| transformers==5.2.0 | torch>=2.0, Python>=3.10 | v5.x breaks some v4.x Trainer API patterns; use new API |
| sentence-transformers==5.2.3 | transformers>=4.34.0 (supports v5), torch>=1.11 | v5 ST added Transformers v5 support in 5.2.1 |
| datasets==4.5.0 | Python>=3.9 | Requires fsspec, pyarrow; no conflict with torch |
| scikit-learn==1.8.0 | Python>=3.11, numpy, scipy | Requires Python 3.11+; do not install on Python 3.10 |
| pandas==3.0.1 | Python>=3.11 | Requires Python 3.11+; compatible with numpy 2.x |
| numpy==2.4.2 | Python>=3.11 | numpy 2.x has C ABI changes; avoid mixing with older scipy/sklearn |
| scipy==1.17.0 | Python>=3.11, numpy>=2.3 | Use >=1.14 for updated `wilcoxon` with continuity correction |
| hydra-core==1.3.2 | Python>=3.8; omegaconf>=2.3 | Do NOT upgrade to 1.4.0.dev1; stable API required for reproducibility |

**Python version recommendation: 3.11.x**
- 3.10 is the minimum for torch/transformers but fails scikit-learn 1.8.0 and pandas 3.x (both require 3.11+)
- 3.12+ is still creating occasional issues with compiled C extensions
- 3.11 satisfies all library requirements simultaneously

---

## Sources

- [PyPI: torch 2.10.0](https://pypi.org/project/torch/) — version and Python requirements verified
- [PyPI: transformers 5.2.0](https://pypi.org/project/transformers/) — version and Python requirements verified
- [PyPI: sentence-transformers 5.2.3](https://pypi.org/project/sentence-transformers/) — version, Transformers v5 support confirmed
- [PyPI: datasets 4.5.0](https://pypi.org/project/datasets/) — version verified
- [PyPI: scikit-learn 1.8.0](https://pypi.org/project/scikit-learn/) — version, Python 3.11+ requirement confirmed
- [PyPI: litellm 1.81.13](https://pypi.org/project/litellm/) — version verified
- [PyPI: openai 2.21.0](https://pypi.org/project/openai/) — version verified
- [PyPI: anthropic 0.83.0](https://pypi.org/project/anthropic/) — version verified
- [PyPI: google-genai 1.64.0](https://pypi.org/project/google-genai/) — version verified; google-generativeai EOL confirmed
- [PyPI: scipy 1.17.0](https://pypi.org/project/scipy/) — version, Python 3.11+ requirement confirmed
- [PyPI: pingouin 0.5.5](https://pypi.org/project/pingouin/) — version verified via pip index
- [PyPI: pandas 3.0.1](https://pypi.org/project/pandas/) — version verified
- [PyPI: numpy 2.4.2](https://pypi.org/project/numpy/) — version verified
- [PyPI: matplotlib 3.10.8](https://pypi.org/project/matplotlib/) — version verified
- [PyPI: seaborn 0.13.2](https://pypi.org/project/seaborn/) — version verified
- [PyPI: hydra-core 1.3.2](https://pypi.org/project/hydra-core/) — 1.3.2 stable, 1.4.0.dev1 pre-release noted
- [HuggingFace: ModernBERT-base](https://huggingface.co/answerdotai/ModernBERT-base) — availability, download count, architecture confirmed
- [Gemini API Libraries Docs](https://ai.google.dev/gemini-api/docs/libraries) — google-generativeai EOL confirmed, google-genai recommended
- [Filighera et al. 2024 (Semantic Scholar)](https://www.semanticscholar.org/paper/Cheating-Automatic-Short-Answer-Grading:-On-the-of-Filighera-Ochs/81c7c95af48aa7402fecc7f7a948fbb02b468c8f) — adversarial adjective/adverb perturbation methodology
- [ModernBERT vs DeBERTaV3 (ACL 2025)](https://aclanthology.org/2025.ijcnlp-long.164.pdf) — controlled benchmark comparison

---

*Stack research for: Perturbation-based ASAG Evaluation Framework*
*Researched: 2026-02-20*
