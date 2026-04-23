# Perturbation-First Robustness Evaluation of Automated Short Answer Grading: Quantifying the Hidden Fragility of Trained and Zero-Shot Graders

**Ferdinando Sasso, Andrea De Mauro**
LUISS Guido Carli University, Rome, Italy
fsasso@studenti.luiss.it, ademauro@luiss.it

---

## Abstract

Automated Short Answer Grading (ASAG) is increasingly deployed in high-stakes educational contexts, yet the dominant evaluation paradigm reports only agreement with human raters and overlooks an equally important quality dimension: robustness, the consistency of grading behaviour under controlled input transformations. We present a perturbation-first evaluation framework that quantifies robustness along three validity dimensions drawn from Messick's (1995) taxonomy: invariance (construct-irrelevant variance), sensitivity (construct underrepresentation), and gaming (adversarial manipulation). The framework comprises seven rule-based perturbation generators, two-gate quality validation, and four metrics (IVR_flip, IVR_absdelta, SSR_directional, ASR_thresholded) that compare the grader against itself rather than against gold labels, isolating robustness from accuracy. A dual-protocol design (Leave-One-Question-Out vs. within-question split) quantifies how trained graders degrade under cross-question generalisation. We apply the framework to the SemEval 2013 Beetle corpus (5,199 answers, 42 questions, 41,444 perturbations) and compare a hybrid ML baseline against zero-shot LLM graders (GPT-5.4 mini, Levels 0 and 1). Three findings stand out. First, the trained baseline exhibits a substantial robustness drop under cross-question evaluation: invariance violations rise from 17.9% to 33.7% (+15.8 percentage points), and gaming susceptibility from 11.5% to 18.8%. Standard within-question evaluations therefore overestimate operational reliability. Second, the zero-shot LLM is markedly more robust on invariance and sensitivity dimensions (IVR 0.243 vs 0.337; SSR 0.420 vs 0.140, a threefold improvement) and substantially less vulnerable to gaming (ASR 0.067 vs 0.188). Third, providing the LLM with the reference answer (Level 1) reduces invariance violations by 45% but simultaneously increases gaming susceptibility by 76%, a non-obvious trade-off invisible to single-metric evaluation. We argue that perturbation-first, multi-dimensional evaluation should complement accuracy metrics in any responsible ASAG deployment, and provide an open-source, pip-installable framework to make this practical.

**Keywords:** Automated Short Answer Grading; Robustness Evaluation; Perturbation Testing; Large Language Models; Construct Validity

**Paper type:** Academic Research Paper

---

## 1  Introduction

Automated Short Answer Grading (ASAG) systems evaluate free-text student responses against reference answers, assigning grades that ideally match expert human judgement. As these systems are increasingly deployed in high-stakes educational settings, the standard evaluation paradigm (reporting accuracy or Quadratic Weighted Kappa against gold labels) reveals an important blind spot: a grader may achieve high agreement with human raters on clean test data yet behave erratically when inputs vary in superficial, meaning-preserving ways.

This fragility matters. A student who writes "the lamp illuminates" instead of "the bulb lights up" should receive the same grade; a student who inserts "not" into a correct answer should not. When graders fail these basic consistency checks, the resulting scores reflect surface-level artefacts rather than genuine understanding, a violation of construct validity that undermines the pedagogical purpose of assessment (Messick, 1989; Williamson et al., 2012). Recent work has documented that operational ASAG systems are surprisingly easy to mislead with simple adversarial inputs (Ding et al., 2020; Kumar et al., 2020; Filighera et al., 2024), yet such vulnerabilities remain absent from standard benchmarking practice.

We argue that robustness (the consistency of grading behaviour under controlled input transformations) should be evaluated alongside accuracy as a first-class quality dimension. To this end, we propose a perturbation-first evaluation framework built on three complementary perturbation families, each targeting a distinct validity threat: invariance perturbations (construct-irrelevant variance), sensitivity perturbations (construct underrepresentation), and gaming perturbations (adversarial manipulation).

The framework introduces four metrics (IVR_flip, IVR_absdelta, SSR_directional, and ASR_thresholded) that quantify grader behaviour under each perturbation family. Crucially, these metrics compare the grader against itself (original vs. perturbed score), not against gold labels, thereby isolating robustness from accuracy.

To measure how robustness degrades under distributional shift for trained graders, we define a dual-protocol evaluation design. Protocol A (Leave-One-Question-Out) evaluates cross-question generalisation, where the grader faces questions unseen during training. Protocol B (within-question 80/20 split) evaluates in-distribution performance. The difference between protocols (the robustness drop) reveals how much consistency a trained grader loses when operating beyond its training distribution. Because zero-shot LLM graders do not undergo task-specific training, the dual-protocol distinction does not apply to them; their robustness is instead assessed through absolute metric values and direct comparison with the trained baseline.

We apply this framework to the SemEval 2013 Beetle dataset (5,199 student answers, 42 questions), evaluating a hybrid ML baseline and an LLM grader (GPT-5.4 mini) at two information levels. Our contributions are:

1. A perturbation-first evaluation framework with seven rule-based generators, two-gate quality validation, and four robustness metrics grounded in validity theory.
2. A dual-protocol design that quantifies robustness degradation under distribution shift for trained graders, revealing the extent to which standard within-question evaluations overestimate operational reliability.
3. A cross-paradigm robustness comparison between trained ML and zero-shot LLM graders across three validity dimensions, including a non-obvious trade-off introduced by reference-answer prompting that is invisible to single-metric evaluation.
4. An open-source, pip-installable Python package implementing the full pipeline, with a pluggable grader interface, deterministic seed isolation, and a command-line interface for practical adoption.

---

## 2  Theoretical Background

### 2.1  ASAG Methods and the Limits of Accuracy-Centred Evaluation

The ASAG literature spans nearly two decades of methodological progress, from early lexical and dependency-based approaches (Mohler et al., 2011) through neural architectures (Riordan et al., 2017) to transformer-based models (Sung et al., 2019) and sentence-BERT representations applied to out-of-sample questions (Condor et al., 2021). Burrows et al. (2015) provide the canonical taxonomy of the field. Across this trajectory, the dominant evaluation paradigm has reported agreement with human raters via accuracy, Quadratic Weighted Kappa, or correlation coefficients. As Heilman and Madnani (2015) showed, even the apparent quality of these agreement scores depends heavily on the composition of the training data, and the gap between in-distribution performance and operational reliability has long been a concern of the educational measurement community (Williamson et al., 2012; Deane, 2013).

### 2.2  Construct Validity as a Theoretical Foundation

The limits of agreement-based evaluation are best understood through the lens of construct validity, the degree to which an assessment measures what it claims to measure (Messick, 1989; Kane, 2006). Messick's unified validity framework identifies two principal threats. *Construct-irrelevant variance* occurs when scores are influenced by factors unrelated to the construct: a grader that penalises a correct answer because of a minor spelling error, for instance, is measuring something other than the targeted competence. *Construct underrepresentation* occurs when the assessment fails to capture meaningful aspects of the construct: a grader that does not detect a negation inverting an answer's meaning is failing to represent the construct adequately. To these, the educational measurement literature on automated scoring has added a third threat specific to algorithmic systems, *adversarial gaming*, in which surface-level manipulations such as keyword stuffing or fluent but incorrect elaboration artificially inflate scores (Williamson et al., 2012). Recent work has extended these classical concerns to AI-based scoring contexts (Ferrara and Qunbar, 2022; Dorsey and Michaels, 2022; Shermis, 2022), arguing that validity arguments must be reconstructed when scores are produced by opaque models.

### 2.3  Adversarial and Perturbation-Based Evaluation

Perturbation-based evaluation has become a standard methodology for assessing NLP model robustness. Ribeiro et al. (2020) introduced CheckList, a behavioural testing framework that systematically probes model capabilities through invariance, directional, and minimum functionality tests. Wang et al. (2022) survey the broader landscape of robustness measurement and improvement in NLP. The general adversarial-NLP literature provides a rich toolkit of attack strategies: gradient-based character flips (Ebrahimi et al., 2018), genetic synonym attacks (Alzantot et al., 2018), BERT-based word substitutions (Jin et al., 2020), and reading-comprehension distractors (Jia and Liang, 2017), most of which are unified by frameworks such as TextAttack (Morris et al., 2020). Belinkov and Bisk (2018) showed that even simple natural noise breaks neural translation, foreshadowing the kind of fragility we observe in ASAG.

Within automated scoring specifically, adversarial vulnerabilities have been documented but not systematically addressed. Ding et al. (2020) demonstrated that automatic content scoring systems could be fooled by inputs as crude as random character strings. Kumar et al. (2020) showed that simple adversarial perturbations are sufficient to attack the robustness of essay scoring systems. Filighera et al. (2024) extended this line of work to ASAG, demonstrating gaming attacks based on adversarial usage of adjectives and adverbs. These studies establish that ASAG systems are vulnerable, but each focuses on a single attack family or scoring system and none proposes a unified, multi-dimensional evaluation framework anchored to validity theory.

### 2.4  LLM-Based Scoring and Open Questions

The recent emergence of large language models has introduced a new paradigm in automated assessment, in which scoring is performed via zero-shot or few-shot prompting rather than supervised training. Mizumoto and Eguchi (2023) explored the potential of GPT-class models for essay scoring; Naismith et al. (2023) evaluated GPT-4 for discourse coherence; Latif and Zhai (2024) studied fine-tuned ChatGPT for scoring. These studies generally report encouraging accuracy figures but do not characterise robustness. Two questions are particularly pressing for the present work. First, whether the robustness drop documented for trained models also affects zero-shot LLM graders, given that they have no task-specific training distribution. Second, whether the kind of additional information typically supplied via prompting (e.g., a reference answer) interacts uniformly with all validity dimensions, or whether it produces trade-offs that cannot be detected through accuracy alone.

### 2.5  From Perturbation Families to Validity Threats

Our framework maps each perturbation family to a specific validity threat from the taxonomy outlined above:

- **Invariance perturbations** (synonym substitution, typo insertion) target construct-irrelevant variance. If a grader changes its score in response to a meaning-preserving surface change, it is measuring something other than the construct.
- **Sensitivity perturbations** (negation insertion, key concept deletion, semantic contradiction) target construct underrepresentation. If a grader fails to detect a meaning-altering change, it is not adequately capturing the construct.
- **Gaming perturbations** (rubric keyword echoing, fluent wrong extension) target the adversarial gaming threat. If a grader can be fooled by superficial manipulation, its scores lack defensibility for high-stakes use.

This mapping connects empirical perturbation metrics to established validity theory and addresses the gap, identified in Section 2.3, between adversarial NLP testing and educational measurement standards.

---

## 3  Methodology

### 3.1  Framework Architecture

The evaluation framework follows a unidirectional pipeline: data loading, perturbation generation, grading, metric computation, and cross-protocol comparison. All data flows through validated immutable models (questions, answers, perturbations, grade results) to ensure reproducibility throughout the pipeline. The framework is implemented in Python and is publicly available as an open-source package under the MIT licence.

### 3.2  Perturbation Generation

Seven rule-based generators produce up to ten perturbation variants per student answer, organised into three families. The following subsections describe each generator in detail.

**Invariance family.** Synonym substitution replaces content words (nouns, verbs, adjectives) with WordNet synonyms, producing up to two variants per answer. Synonyms are selected deterministically (alphabetically sorted) to ensure reproducibility. Eligibility criteria for substitution require the word to be at least four characters long, purely alphabetic, and tagged as a noun, verb, or adjective by a part-of-speech tagger. For each eligible word position, the first synonym (in alphabetical order) from WordNet is selected, ensuring that the same input always produces the same output regardless of platform or Python version. Typo insertion introduces a single character-level modification (adjacent swap, deletion, or duplication) into one content word. The target word and operation type are selected via a seeded random number generator, producing exactly one variant per answer.

**Sensitivity family.** Negation insertion adds "not" after auxiliary verbs or prepends "It is not true that" as a fallback, following a three-strategy cascade: (1) insert "not" after the first auxiliary verb (is, are, was, were, will, can, could, should, would, does, did, has, have, had); (2) replace the first simple domain verb with "does not [verb]", drawing from a curated list of 26 common science-domain verbs (flows, lights, connects, completes, opens, closes, conducts, etc.); (3) as a final fallback, prepend "It is not true that" with the first character of the original text lowercased. Key concept deletion removes one domain-relevant content word selected via seeded random sampling. A word is eligible for deletion if it is at least four characters long, purely alphabetic, and not in a stopword list. Semantic contradiction replaces domain terms with curated antonyms (e.g., "open" to "closed", "series" to "parallel") drawn from a 40-pair dictionary covering physics, biology, chemistry, and earth science vocabulary. Up to two variants are produced: the first and second match positions in the text. If no antonym match is found, the fallback "It is not true that..." formulation is used.

**Gaming family.** Rubric keyword echoing appends reference-answer keywords absent from the student response, simulating keyword stuffing. Two variants are produced with different keyword counts (3-4 and 5-6 keywords respectively), selected via seeded random sampling from the sorted set of unique reference-answer content words not already present in the student answer. Fluent wrong extension appends a confident but factually incorrect domain statement from a curated pool of 30 plausible-sounding misconceptions covering physics, biology, chemistry, and earth science. The statement is prefixed with a connecting phrase (e.g., "Furthermore,", "Additionally,") to produce fluent-sounding text that, despite being factually wrong, could appear to a surface-level scorer as an elaboration demonstrating additional knowledge.

### 3.3  Two-Gate Quality Validation

Invariance perturbations undergo two validation gates before acceptance. Gate 1 applies only to synonym substitution: candidate texts must achieve cosine similarity of at least 0.85 with the original, measured via sentence-BERT embeddings (all-MiniLM-L6-v2). The threshold is hard-coded at 0.85 to prevent threshold-shopping; this value was selected based on manual inspection of synonym substitution pairs and represents a conservative boundary that rejects cases where the chosen WordNet synonym introduces genuine semantic drift (e.g., technical terms whose WordNet synonyms do not carry the same meaning in the science domain). Gate 2 applies to all invariance types: candidates introducing new negation markers or antonyms not present in the original are rejected. The negation check uses a regular expression matching 17 negation forms (not, never, no, cannot, can't, won't, doesn't, isn't, aren't, wasn't, weren't, don't, didn't, haven't, hadn't, shouldn't, wouldn't, couldn't). The antonym check uses a dictionary that mirrors the contradiction map used in the sensitivity generators, comparing per-token sets between original and candidate to avoid false positives from words that legitimately appear in both texts. Rejected candidates are not regenerated; the rejection rate is reported as a research result, reflecting the inherent difficulty of producing valid invariance perturbations for short science answers.

### 3.4  Robustness Metrics

All metrics compare the grader's own score on the original answer against its score on the perturbed answer, isolating robustness from accuracy.

**IVR_flip** (Invariance Violation Rate, binary): the proportion of invariance pairs where the grader's score changed at all. Lower values indicate greater robustness.

**IVR_absdelta** (Invariance Violation Rate, continuous): the mean absolute score difference across invariance pairs. Captures violation magnitude, not just occurrence.

**SSR_directional** (Sensitivity Success Rate): the proportion of sensitivity pairs where the perturbed score strictly decreased. Higher values indicate the grader correctly detects meaning-altering changes. No-change counts as failure, since a sensitivity perturbation that does not alter the grade indicates the grader missed the modification.

**ASR_thresholded** (Adversarial Success Rate): the proportion of gaming pairs where the score crossed from below the passing threshold (0.5) to at or above it. Measures vulnerability to adversarial manipulation. Already-passing answers that increase further are excluded, ensuring that ASR captures only genuine below-to-above-threshold transitions rather than inflation of already-passing scores.

Scores are rounded to six decimal places before comparison to prevent IEEE 754 floating-point artefacts from producing false positive violations.

### 3.5  Dual-Protocol Evaluation

The dual-protocol design targets trained graders that learn question-specific patterns from data. It quantifies how much robustness these graders lose when encountering novel questions not seen during training.

**Protocol A (LOQO, Leave-One-Question-Out)** implements cross-question evaluation. For each of 42 questions, the grader is trained on answers from all other questions and tested on the held-out question's answers. A leakage diagnostic verifies that no held-out question text appears in the training data. This protocol measures robustness under distributional shift, the realistic deployment scenario where a grader must generalise to new questions.

**Protocol B (within-question 80/20)** implements in-distribution evaluation. For each question independently, answers are split into 80% train and 20% test using stratified sampling on gold labels. The grader is trained on the same question's answers, then tested. This protocol measures baseline robustness on familiar content, the optimistic scenario typically reported in ASAG literature.

**Robustness drop** is defined as the difference between Protocol A and Protocol B aggregate metrics. For invariance and gaming metrics (where higher indicates worse robustness), a positive drop signals degradation under distribution shift. For sensitivity (where higher indicates better detection), a negative drop signals degradation. The aggregate is a macro-average: each fold or question contributes equally regardless of test-set size, preventing large questions from dominating the result.

**Applicability to zero-shot graders.** The dual-protocol distinction is meaningful only for graders with a training phase. Zero-shot LLM graders receive an identical prompt regardless of how the data is split; they have no mechanism to internalise question-specific patterns from a training set. Consequently, their Protocol A and Protocol B results are expected to be statistically equivalent, differing only by sampling noise from the data partition. Rather than reporting a tautological drop of approximately zero, we evaluate LLM graders on their absolute robustness metrics and compare them directly against the trained baseline's Protocol A results, the most demanding evaluation condition.

### 3.6  Software Architecture and Public API

The framework is implemented as a Python package (`asag`) with a modular, pipeline-oriented architecture. The package is pip-installable and released under the MIT licence to support adoption and replication by other research groups. This section describes the software design in sufficient detail to enable independent reproduction and extension.

**Pipeline structure.** The package is organised into six subpackages reflecting the unidirectional data flow:

```
src/asag/
    loaders/        # Dataset loading and normalisation
    splitters/      # Protocol A (LOQO) and Protocol B (80/20) splitting
    graders/        # GraderInterface ABC + implementations
    perturbations/  # PerturbationEngine, generators, gates, cache
    metrics/        # MetricCalculator (IVR, SSR, ASR)
    evaluation/     # EvaluationEngine (orchestrates the full pipeline)
    schema/         # Pydantic models (QuestionRecord, AnswerRecord, etc.)
    infra/          # Configuration, seed management, storage, versioning
```

Each subpackage is self-contained: the loader produces validated data objects, the splitter partitions them, the grader scores them, the perturbation engine transforms them, the metric calculator compares original and perturbed scores, and the evaluation engine orchestrates the full workflow across protocols and folds.

**Immutable data models.** All data flowing through the pipeline is represented as Pydantic v2 models with `frozen=True` configuration, making every record immutable after construction. The four core models are:

- `QuestionRecord`: question text, rubric, reference answers, score scale, and corpus identifier.
- `AnswerRecord`: student answer text, gold label, normalised gold score in [0.0, 1.0], and a foreign key to its `QuestionRecord`.
- `PerturbationRecord`: perturbed text, perturbation family and type, generator identifier, seed, and a foreign key to its source `AnswerRecord`.
- `GradeResult`: label, normalised score in [0.0, 1.0], and confidence, with field validators enforcing the [0.0, 1.0] range at construction time.

This design prevents accidental mutation of data during pipeline execution and ensures that all records are JSON-serialisable for storage and reproducibility.

**Pluggable grader interface.** All graders implement the `GraderInterface` abstract base class, which requires two methods: a `grader_name` property returning a unique string identifier, and a `grade()` method accepting a question, an optional rubric, and a student answer and returning a `GradeResult`. The interface is deliberately minimal so that rule-based, transformer-based, and LLM-based graders can all conform without constraint on their internal logic. The current implementation includes `HybridGrader` (logistic regression on sentence-BERT embeddings plus handcrafted features) and `LLMGrader` (multi-vendor zero-shot prompting via OpenAI, Anthropic, or Google APIs). Adding a new grader requires implementing only these two methods.

**Determinism and seed isolation.** Reproducibility is enforced through three mechanisms. First, every component that involves randomness accepts a `SeedConfig` object specifying independent seeds for splitting, perturbation generation, and grading, rather than relying on a global random state. Second, WordNet synonyms are sorted alphabetically before selection, eliminating platform-dependent ordering variation. Third, reference answers are sorted in the loader to ensure deterministic behaviour downstream. These measures guarantee that given the same seeds, the entire pipeline produces identical results across runs, platforms, and Python versions.

**Basic usage.** The following code illustrates the minimal workflow for running a robustness evaluation:

```python
from asag.loaders.semeval2013 import SemEval2013Loader
from asag.perturbations.engine import PerturbationEngine
from asag.evaluation.engine import EvaluationEngine
from asag.graders.llm import LLMGrader

questions, answers = SemEval2013Loader().load()
grader = LLMGrader(provider="openai", model="gpt-5.4-mini", level=1)
engine = EvaluationEngine(grader=grader, questions=questions, answers=answers)
results = engine.run()
print(results.summary())
```

---

## 4  Experimental Setup

### 4.1  Dataset

We use the SemEval 2013 Task 7 Beetle dataset (Dzikovska et al., 2013), comprising 5,199 student answers to 42 science questions about electrical circuits. Answers are labelled on a five-way scale: correct (42.0%), partially_correct_incomplete (23.1%), contradictory (27.0%), non_domain (5.0%), and irrelevant (2.9%). Labels are normalised to a continuous [0, 1] scale (correct = 1.0, partial = 0.5, others = 0.0) following the ASAG2024 benchmark convention.

The Beetle dataset is loaded from the HuggingFace mirror, which provides four pre-defined splits (train, test_ua, test_uq, test_ud). These splits are concatenated in the loader rather than used individually, because the Protocol A/B splitting logic is defined by the evaluation framework itself and the original HuggingFace splits do not correspond to either protocol. The loader also deduplicates and sorts reference answers for each question to ensure deterministic downstream behaviour.

### 4.2  Graders

**Hybrid ML baseline.** A logistic regression classifier trained on 388-dimensional feature vectors: four handcrafted linguistic features (lexical overlap, length ratio, negation flag, reference-token recall) concatenated with 384-dimensional sentence-BERT embeddings (Reimers and Gurevych, 2019; specifically, the all-MiniLM-L6-v2 model). Class weights are balanced to handle label imbalance. This configuration is broadly representative of strong feature-based ASAG baselines reported in the literature (Sung et al., 2019; Condor et al., 2021).

**LLM grader.** Zero-shot prompting of GPT-5.4 mini, evaluated at two information levels. Level 0 supplies the question and the student answer only; Level 1 additionally supplies the reference answer and instructs the model to compare the student response against it. Temperature is set to 0.0 for near-deterministic output, with a fixed seed for reproducibility. The model outputs a JSON object with a label and a confidence score; labels are mapped to the same [0, 1] scale as the gold labels. Because the LLM operates in a zero-shot regime with no task-specific training, the dual-protocol distinction does not alter its input; it is evaluated once and compared against the HybridGrader's Protocol A (cross-question) results. The full prompt templates are provided in Appendix B.

### 4.3  Perturbation Statistics

The perturbation engine generated 41,444 perturbations across all seven types from 5,199 source answers, averaging 8.0 perturbations per answer (the theoretical maximum is 10). Gate 1 (SBERT cosine similarity < 0.85) rejected 40.3% of synonym substitution candidates, indicating that nearly half of WordNet synonym replacements produce semantically divergent texts in the science domain. Gate 2 (negation/antonym heuristic) provided additional filtering for meaning-inverting substitutions across all invariance types. The rejection rate is reported as a research result rather than a failure: it quantifies the inherent difficulty of producing valid invariance perturbations in technical domains and motivates the two-gate design. Detailed gate rejection statistics broken down by perturbation type are provided in Appendix C.

---

## 5  Results

Results are organised in three parts. Section 5.1 presents the dual-protocol analysis of the trained HybridGrader, quantifying robustness degradation under distributional shift. Section 5.2 compares the trained baseline against the zero-shot LLM grader on absolute robustness metrics, including the effect of reference-answer availability. Section 5.3 analyses score distribution effects, including the floor effect that mechanically suppresses sensitivity detection rates.

### 5.1  Dual-Protocol Analysis: Robustness Drop of the Trained Grader

Table 1 reports the HybridGrader's aggregate robustness metrics under both evaluation protocols.

**Table 1. HybridGrader robustness metrics by evaluation protocol.**

| Metric | Protocol B (in-distribution) | Protocol A (cross-question) | Drop (A - B) |
|---|---|---|---|
| IVR_flip (lower is better) | 0.179 | 0.337 | **+0.158** |
| IVR_absdelta (lower is better) | 0.125 | 0.242 | **+0.118** |
| SSR_directional (higher is better) | 0.120 | 0.140 | +0.020 |
| ASR_thresholded (lower is better) | 0.115 | 0.188 | **+0.074** |

The HybridGrader exhibits substantial robustness degradation under cross-question evaluation. Invariance violations nearly double from Protocol B to Protocol A (IVR_flip: 0.179 to 0.337), indicating that when the grader faces questions not seen during training, it changes its score on meaning-preserving perturbations 33.7% of the time, compared to 17.9% when the grader has been trained on answers to the same question. The gaming vulnerability shows a parallel pattern: ASR rises from 11.5% to 18.8%, meaning adversarial keyword stuffing and fluent wrong extensions are 64% more effective on novel questions.

Sensitivity detection remains low under both protocols (SSR approximately 0.13), suggesting that the HybridGrader's inability to detect meaning-altering perturbations is a structural limitation of feature-based scoring rather than a distributional shift effect. It misses negations, concept deletions, and semantic contradictions regardless of whether it has seen the question before.

These findings demonstrate that within-question evaluations (Protocol B) substantially overestimate the operational robustness of trained ASAG systems. The robustness drop, particularly the +15.8 percentage point increase in IVR_flip and the +7.4 percentage point increase in ASR, quantifies the extent of this overestimation. Standard ASAG benchmarks, which typically report within-question performance, therefore provide an optimistic picture of how a deployed grader will behave on questions it has not been trained on.

### 5.2  Cross-Paradigm Comparison: Trained ML vs. Zero-Shot LLM

Because the zero-shot LLM grader receives an identical prompt regardless of the data split (see Section 3.5), we report its absolute robustness metrics and compare them against the HybridGrader's Protocol A results, the most demanding evaluation condition for the trained baseline. Table 2 summarises the comparison.

**Table 2. Cross-paradigm robustness comparison (HybridGrader at Protocol A; LLM zero-shot, single-run).**

| Metric | HybridGrader (A) | GPT-5.4 mini L0 | GPT-5.4 mini L1 |
|---|---|---|---|
| IVR_flip (lower is better) | 0.337 | 0.243 | **0.134** |
| IVR_absdelta (lower is better) | 0.242 | 0.126 | **0.071** |
| SSR_directional (higher is better) | 0.140 | 0.420 | **0.461** |
| ASR_thresholded (lower is better) | 0.188 | **0.067** | 0.118 |

**Finding 1: LLM graders are substantially more robust to surface-level variation.** GPT-5.4 mini Level 0 achieves IVR_flip of 0.243 versus 0.337 for the HybridGrader under Protocol A, a 28% relative reduction in invariance violations. With the reference answer available (Level 1), invariance violations fall further to 0.134, a 45% relative reduction over Level 0 and a 60% reduction over the HybridGrader baseline. The reference answer acts as a semantic anchor: surface variations that did not change meaning are recognised as such because the model has an explicit target to compare against.

**Finding 2: LLM graders detect meaning-altering perturbations far more effectively.** SSR_directional of 0.420 (Level 0) and 0.461 (Level 1) versus 0.140 for the HybridGrader represents an approximately threefold improvement. The HybridGrader misses 86% of negation insertions, concept deletions, and semantic contradictions; the LLM at Level 1 misses 54%. While neither achieves ceiling performance, the gap demonstrates that language understanding, rather than pattern matching on surface features, enables substantially better sensitivity detection. Adding the reference answer provides only a modest additional gain (+4 percentage points), suggesting that most of the LLM's sensitivity advantage stems from semantic processing rather than from access to a comparison target.

**Finding 3: Reference-answer availability introduces a non-obvious gaming trade-off.** The most surprising result is that providing the reference answer (Level 1) almost doubles gaming susceptibility relative to Level 0 (ASR 0.118 vs 0.067). This is a 76% relative increase in vulnerability to adversarial manipulation. The mechanism is intuitive in retrospect: the prompt instructs the model to compare the student answer against the reference. When the gaming perturbation injects keywords drawn from the reference answer into a wrong response, the model finds those keywords during the comparison and treats them as evidence of partial understanding. The reference answer thus inadvertently functions as a checklist that an adversarial student can copy from. Level 0, lacking this anchor, must judge the answer on its overall coherence and is correspondingly harder to game with surface-level keyword injection.

**Finding 4: Multi-metric evaluation reveals trade-offs invisible to any single metric.** Looking at any one metric in isolation produces a misleading picture. On invariance alone, Level 1 looks unambiguously better than Level 0. On sensitivity alone, both look comparable. On gaming alone, Level 0 is dramatically better. The full picture only emerges when all three dimensions are considered jointly: adding reference-answer information improves two validity dimensions while degrading a third. A practitioner choosing between L0 and L1 on the basis of accuracy or invariance alone would have no way of seeing the gaming cost they are incurring.

The same point applies to the trained baseline. If robustness were assessed using invariance metrics alone, the HybridGrader would appear reasonably robust under Protocol B (IVR_flip = 0.179). However, SSR_directional = 0.120 reveals that this apparent stability partly reflects indiscrimination: the grader assigns similar scores to original and perturbed answers not because it is robust, but because it is insensitive to meaning changes. The combination of low IVR and low SSR signals a grader that rarely changes its mind, even when it should. This pattern is only visible through multi-metric evaluation grounded in distinct validity threats.

### 5.3  Score Distribution Effects

To rule out the possibility that the LLM's lower IVR is an artefact of score compression rather than genuine robustness, we examined the LLM's label distribution. At Level 0, GPT-5.4 mini exhibits a conservative scoring pattern: 54.3% of answers receive the partially_correct_incomplete label (score 0.5), compared to 23.1% in the gold distribution. This compression toward the midpoint mechanically reduces IVR, since scores at 0.5 have less room to flip to a different value. At Level 1, the distribution becomes substantially more discriminative, closer to the gold distribution, yet IVR_flip continues to fall (0.243 to 0.134). This rules out the score-compression explanation: the LLM's invariance robustness reflects genuine semantic stability, not statistical artefact.

A symmetric artefact affects SSR_directional: answers already scored 0.0 cannot decrease further under sensitivity perturbations, mechanically producing SSR = 0% on those pairs regardless of grader quality. We term this the floor effect. Table 3 reports SSR with and without floor-affected pairs.

**Table 3. SSR floor-effect analysis: overall vs. restricted to answers with original score > 0.**

| Configuration | Pairs | Floor pairs (orig=0) | SSR overall | SSR non-floor (orig>0) | Delta |
|---|---|---|---|---|---|
| GPT-5.4 mini L0 | 13,155 | 3,012 (22.9%) | 0.423 | **0.549** | +12.6 pp |
| GPT-5.4 mini L1 | 12,309 | 4,219 (34.3%) | 0.480 | **0.731** | +25.0 pp |

**Why the floor effect occurs.** SSR_directional is defined as the proportion of sensitivity pairs where the perturbed score is strictly lower than the original score. When the original answer already receives the minimum possible score of 0.0, the perturbed answer cannot score lower, regardless of how effectively the grader detects the meaning-altering perturbation. These floor pairs are "untestable" for the SSR metric: the sensitivity perturbation may have been correctly understood by the grader, but the metric cannot register this because the score has nowhere to go.

**Why Level 1 has more floor pairs.** The difference in floor pair proportions between L0 (22.9%) and L1 (34.3%) is a direct consequence of L1's greater discriminative power. When the LLM has access to the reference answer, it more frequently identifies incorrect student answers and assigns them a score of 0.0. This is, in itself, a desirable property: L1 is a more discriminating grader. However, it produces a paradoxical side effect for SSR measurement. By correctly assigning score 0.0 to more incorrect answers on the original (unperturbed) version, L1 simultaneously increases the proportion of pairs where the floor effect prevents SSR from registering a success, even when the grader would have correctly detected the perturbation.

**Corrected sensitivity detection rates.** After restricting the analysis to non-floor pairs (i.e., sensitivity pairs where the original score was greater than 0.0), the LLM's sensitivity detection is substantially stronger than headline figures suggest. At Level 1, the corrected SSR of 0.731 means that the grader correctly detects and responds to meaning-altering perturbations in 73.1% of cases where detection is measurable, compared to the uncorrected rate of 48.0%. The correction is larger for L1 (+25.0 percentage points vs. +12.6 percentage points for L0) precisely because L1's greater discriminative power produces more floor pairs. These corrected figures provide a fairer assessment of the LLM's actual semantic processing capability, stripped of the mechanical artefact introduced by the score floor.

The floor effect is not a flaw in the metric design per se, because SSR_directional is correct in counting floor pairs as "no decrease observed." Rather, it is a methodological consideration that researchers should report alongside headline SSR values. The analysis script is included in the repository (`scripts/analyze_floor_effect.py`) for full reproducibility.

### 5.4  Sensitivity Blindness Gradient

Section 5.2 reported the LLM's aggregate SSR as substantially better than the trained baseline's. Disaggregating SSR by perturbation type, however, reveals that the LLM's residual sensitivity failures are not uniform but follow a stable hierarchy.

**Table 4. Per-type miss rates with 95% bootstrap CI (10,000 resamples).** Miss rate is the percentage of sensitivity pairs in which the perturbed score equalled the original score (the grader did not respond to the perturbation).

| Grader | Deletion | Negation | Contradiction |
|---|---|---|---|
| L0 | 68.7% [67.4, 70.0] | 52.2% [50.8, 53.5] | 43.0% [41.7, 44.3] |
| L1 | 74.8% [73.6, 76.0] | 41.8% [40.5, 43.2] | 39.6% [38.3, 40.9] |

The pattern holds for both prompting levels: the grader is most blind to concept deletions, intermediate on negations, and least blind on outright contradictions. The 95% bootstrap CIs of the three types do not overlap within either grader, indicating that the gradient is not a sampling artefact.

**Statistical significance of the gradient.** To test whether the differences between perturbation types within each grader are statistically robust against the natural pairing of the data (each student answer is perturbed in multiple ways), we ran paired McNemar tests on the answers for which both perturbation types of a pair were graded. Table 5 reports the six within-grader comparisons.

**Table 5. McNemar paired tests on within-grader miss patterns.** *b* and *c* are the discordant cells (cases where exactly one of the two compared perturbation types was missed); χ² uses the Yates continuity correction.

| Grader | Comparison | n | b | c | χ² | p |
|---|---|---|---|---|---|---|
| L0 | deletion vs negation | 5,068 | 1,433 | 552 | 390 | <0.0001 |
| L0 | deletion vs contradiction | 5,068 | 1,751 | 392 | 861 | <0.0001 |
| L0 | negation vs contradiction | 5,199 | 1,045 | 568 | 140 | <0.0001 |
| L1 | deletion vs negation | 5,069 | 2,060 | 335 | 1,241 | <0.0001 |
| L1 | deletion vs contradiction | 5,069 | 2,139 | 293 | 1,400 | <0.0001 |
| L1 | negation vs contradiction | 5,199 | 633 | 512 | 13 | 0.0004 |

All six comparisons are significant at p<0.001. The very large χ² values for the L1 comparisons involving deletion (1,241 and 1,400) reflect the magnitude of the L1 deletion blindness relative to the other two types.

**The L1 deletion paradox.** A second pattern emerges across (rather than within) graders. Adding the reference answer (moving from L0 to L1) reduces the miss rate on negation by 10.4 pp (from 52.2% to 41.8%) and on contradiction by 3.4 pp (from 43.0% to 39.6%) — both consistent with the intuition that more grading information should yield better detection. On deletion, however, L1 *increases* the miss rate by 6.1 pp (from 68.7% to 74.8%). To test whether this paradoxical degradation is statistically robust on the same answer set, we ran a paired McNemar comparison of L0 vs L1 on the deletion pairs (one observation per answer, one perturbation per type per answer). The result, summarised in Table 6, confirms the paradox.

**Table 6. McNemar paired test of L0 vs L1 on each sensitivity type.** *b* counts pairs where only L0 missed; *c* counts pairs where only L1 missed. *c* > *b* indicates that L1 misses more often than L0.

| Type | n | b (L0 miss only) | c (L1 miss only) | χ² | p | Verdict |
|---|---|---|---|---|---|---|
| Negation | 5,199 | 1,185 | 648 | 157 | <0.0001 | L1 helps |
| **Deletion** | **5,068** | **745** | **1,050** | **51** | **<0.0001** | **L1 hurts (paradox)** |
| Contradiction | 5,199 | 1,030 | 849 | 17 | <0.0001 | L1 helps weakly |

The deletion paradox is statistically certain: out of the 1,795 pairs in which the two graders disagreed on the deletion outcome, L1 missed in 1,050 cases and L0 missed in 745 — a 305-pair excess of L1-only misses, far beyond what could plausibly arise from sampling.

**Qualitative characterisation of deletion blindness.** To characterise the mechanism behind the high deletion miss rate, we manually reviewed 30 randomly sampled missed-deletion cases (15 from L0 and 15 from L1, drawn with a fixed seed to support reproducibility from `runs/analysis/deletion_missed_cases_annotated.txt`). Each case was coded along two dimensions: the *category* of the deleted word (article/determiner, domain concept, verb, connective, other) and the *severity* of the meaning change (preserved, degraded, inverted). Aggregate counts are reported in Table 7.

**Table 7. Cross-tabulation of deleted-word category and meaning-change severity (n = 30; combined L0 + L1).**

| Category | preserved | degraded | inverted | Total |
|---|---:|---:|---:|---:|
| domain concept | 1 | 12 | 4 | **17 (57%)** |
| other (pronoun, quantifier, generic noun) | 5 | 1 | 2 | 8 (27%) |
| connective | 3 | 0 | 0 | 3 (10%) |
| verb | 1 | 0 | 1 | 2 (7%) |
| article/determiner | 0 | 0 | 0 | 0 (0%) |
| **Total** | **10 (33%)** | **13 (43%)** | **7 (23%)** | 30 |

Three patterns are visible in the cross-tabulation. First, **57% of missed deletions involve a domain-specific concept** (terminal, battery, circuit, voltage, bulb, path, gap, closed, open, positive, negative); the remaining 43% spans pronouns, quantifiers, generic nouns, connectives and verbs. Second, of the 17 missed domain-concept deletions, **16 (94%) were judged to degrade or invert the answer's meaning**; only one case (where the referent was fully transparent from the question) was meaning-preserved. Third, the three connective deletions (one occurrence of "because", two of "between") and most pronoun or expletive deletions ("both", "they", "there", "each", "where") were correctly judged meaning-preserved by the annotator and tolerated by the grader. The grader is therefore not exhibiting a benign tolerance of grammatical noise; it is failing precisely on the content-bearing words that distinguish a correct technical explanation from an incomplete or ill-formed one.

A representative inverted case from the L1 sample illustrates the failure mode at its most consequential: for the question "Why was bulb A on when switch Y was open and switch Z was closed?", the original answer "The battery is contained in *a closed path* with bulb a" (gold = correct, original score = 1.0) is perturbed by deleting "closed" to "The battery is contained in *a path* with bulb a", and the L1 grader assigns score 1.0 to the perturbed version as well. The closed/open distinction is the central conceptual axis of the Beetle physics task; the grader treats the modified and unmodified versions as equivalent. A second case from the same sample shows the same pattern with "open path" deleted to "path" in a different question (gold also correct, again preserved at score 1.0). Two more inverted cases involve the deletion of the head noun in a definitional answer ("voltage" deleted from "When the voltage changes to 0", and "difference" deleted from "Because it is the difference of the electrical state...") — here the sentence becomes syntactically broken, but the grader still preserves the original score because the surrounding domain tokens still match a plausible correct response.

**Reading the gradient honestly.** Miss rates in Table 4 include floor pairs (Section 5.3); floor adjustment lowers all three rates uniformly without changing the ordering. We emphasise that even at the bottom of the gradient — approximately 40% miss rate on contradiction in L1 — the failure rate represents a substantive deployment risk, not a "well-handled" condition. The structured nature of the gradient should be read as a description of *how* the model fails, not as evidence that any of the three types is robustly detected.

---

## 6  Discussion

### 6.1  The Overestimation Problem

The most consequential methodological finding of this study is that within-question evaluations overestimate the robustness of trained ASAG graders. The HybridGrader's IVR_flip nearly doubles when moving from Protocol B to Protocol A, and its gaming susceptibility rises by 64%. These are not marginal effects: a deployment decision based on Protocol B numbers would systematically underestimate how much grading inconsistency real students will encounter on novel questions, and how effective gaming attempts will be in practice.

This has direct implications for ASAG benchmarking practice. Reporting only within-question metrics, as is common in the literature, provides an optimistic picture that may not survive deployment. We recommend that any published ASAG evaluation include cross-question results alongside in-distribution ones, and that the difference between the two be reported explicitly as a robustness drop.

### 6.2  Why LLMs Are More Robust (and Where They Still Fail)

The LLM grader's advantage on invariance and sensitivity dimensions is consistent with the explanation that semantic processing generalises across surface variations in ways that feature-based scoring cannot. The HybridGrader's fragility appears to stem from reliance on surface features (lexical overlap, embeddings of specific tokens) that change when surface form changes, even when meaning is preserved. The LLM, by contrast, processes the answer as language and is comparatively insensitive to whether "bulb" was replaced by "lamp" or "current" by a misspelling.

This is also why the LLM is dramatically better at detecting meaning-altering changes. A negation, a concept deletion, or an antonym substitution changes meaning while leaving most surface features intact. A feature-based scorer that has learned "answers containing these keywords are correct" will continue to score the perturbed answer as correct. A semantic processor recognises that the meaning has shifted.

However, even the LLM is not immune, and the specific failure pattern is instructive. We present two concrete examples drawn from the dataset that illustrate a consistent failure mode we term "keyword anchoring."

**Example 1.** For the question "What does a voltage reading of 0 tell you about the connection between a bulb terminal and the battery?", the student answer "the two terminals are connected" receives score 1.0 (correct). The negation perturbation produces "the two terminals are not connected", a statement with the opposite meaning. Yet GPT-5.4 mini at Level 0 still assigns 1.0. The model appears to anchor on the presence of the domain-relevant terms "terminals" and "connected" while failing to process the negation particle "not" that inverts their relationship.

**Example 2.** For the same question domain, the student answer "Because there was a gap between the positive battery terminal and terminal 1" (score 1.0) is perturbed to "Because there was not a gap between the positive battery terminal and terminal 1." Again, the LLM assigns score 1.0 to the negated version. Despite the insertion of "not" completely reversing the causal claim (the presence vs. absence of a gap), the model treats the answer as correct because the key domain terms ("gap", "positive battery terminal", "terminal 1") remain present.

**Why keyword anchoring occurs.** These examples suggest that even large language models can exhibit a form of keyword-based reasoning when the negated sentence retains high lexical overlap with a plausible correct answer. The mechanism is analogous to what cognitive scientists call the "Moses illusion" (Erickson and Mattson, 1981): when the surrounding context is sufficiently consistent with a correct answer, the anomalous element (in this case, the negation particle) is processed superficially or not at all. In the LLM context, this likely reflects the statistical regularity that sentences containing "terminals", "connected", and "gap" in the context of circuit questions are overwhelmingly correct in the model's training distribution. The negation particle, being a single short token among many domain-relevant ones, receives insufficient attention weight to override the strong positive signal from the keyword constellation.

This pattern recurs across multiple negation insertions in the dataset, suggesting that keyword anchoring is not an isolated failure but a systematic weakness. It is particularly concerning for high-stakes deployment because negation is precisely the kind of modification that a student might make inadvertently (by misunderstanding the question) or that a malicious actor might exploit (by inserting "not" into a correct answer to test the grader's attentiveness). The fact that even a frontier LLM fails on such a basic semantic operation underscores the importance of sensitivity testing as part of any robustness evaluation.

### 6.3  The Reference-Answer Trade-Off

The most pedagogically interesting finding is the reference-answer trade-off documented in Section 5.2. Adding the reference answer to the LLM prompt is the kind of intervention any practitioner would expect to improve grading: more information should yield better judgement. And it does, for invariance and sensitivity (in aggregate). But for gaming, the same intervention almost doubles vulnerability; and as Section 5.4 shows, it also degrades sensitivity detection on one specific perturbation type — concept deletion — even while improving it on the other two.

**A single mechanism, two trade-offs.** The mechanism deserves emphasis because it generalises beyond our specific prompt and explains both surprising effects under a single hypothesis. When the model is instructed to compare the student answer against a reference, the reference becomes the basis for the comparison: any token that overlaps with the reference is evidence of correctness in the model's reasoning. This token-level matching has two failure modes. (a) For *gaming*, an adversarial student who knows or can guess what the reference looks like — and in many real settings the rubric or reference is publicly available — can directly insert reference keywords into a wrong response and exploit the comparison. (b) For *deletion*, the same matching procedure is silently defeated by a different mechanism: when a domain concept is removed, the reference has no token to compare against for the missing word, while the surrounding tokens still match. The grader reads continued overlap as continued correctness and tolerates the omission. Substitutions and negations, by contrast, *replace* a token rather than removing it, so the comparison registers a discrepancy.

Reference-anchored prompting therefore fails on the same axis on which it succeeds: token-level matching helps detect substitutions and negations but cannot detect what is no longer present to be matched, and it also rewards keywords inserted by an adversary. Gaming vulnerability and deletion blindness are two faces of the same reliance on token overlap.

**Mitigations and their trade-offs.** We do not claim that this trade-off is unfixable. Prompt engineering, chain-of-thought instructions that require the model to assess internal coherence before keyword overlap, or few-shot examples demonstrating both gaming attempts and deletion artefacts could plausibly mitigate both failure modes simultaneously. The point is rather that the trade-offs exist at all, that they are invisible if one measures only invariance or only accuracy or even only aggregate sensitivity, and that perturbation-first multi-dimensional evaluation — disaggregated by perturbation type — is what surfaces them. The framework's contribution is detecting such trade-offs before deployment, regardless of which prompting strategy is ultimately chosen. The deletion-paradox interpretation should be treated as a working hypothesis: it is consistent with the observed pattern and with the qualitative review of Section 5.4, but a definitive test would require an ablation that controls token-overlap signal independently from semantic content (for example, by comparing prompts that withhold the reference but supply an external concept checklist). Such an ablation is left to future work.

### 6.4  Practitioner Implications

For institutions considering ASAG deployment, three concrete recommendations follow from these findings.

First, do not rely on within-question accuracy or QWK as the sole quality indicator. Run a perturbation evaluation across at least one invariance, one sensitivity, and one gaming generator before deployment. The cost is modest (perturbation generation is rule-based and grading is the same operation as live use) and the diagnostic value is high.

Second, when comparing prompting strategies for an LLM grader (e.g., with vs. without reference answer; zero-shot vs. few-shot), measure all three validity dimensions, not just one. A change that improves accuracy may simultaneously increase gaming exposure, as our Level 0 vs Level 1 comparison demonstrates.

Third, treat cross-question evaluation as the realistic deployment scenario for trained graders. Within-question performance describes the best case; cross-question performance describes what students will actually experience. More broadly, robustness sits alongside fairness as a precondition for the responsible deployment of automated scoring in education (Loukina et al., 2019): a grader that is unstable under meaning-preserving variation is also, by construction, a grader whose scores are unevenly distributed across superficially different but substantively equivalent answers.

### 6.5  Limitations

Several limitations bound the generality of these findings, and we discuss them here in greater detail than is typical for a conference paper, in keeping with the reproducibility goals of this work.

**Floor effect in SSR.** As documented in Section 5.3, the SSR_directional metric is mechanically suppressed for answers already scored 0.0. While we report corrected (non-floor) SSR values alongside headline figures, the floor effect means that the overall SSR numbers understate the grader's actual sensitivity detection capability. A metric design that accounts for floor effects natively (e.g., by restricting the SSR computation to answers with original score > 0) could be considered in future work, although the current design has the advantage of transparency: reporting both overall and corrected values makes the artefact visible.

**No human validation of perturbations.** The perturbation generators are rule-based and undergo automated quality gates, but we do not include a human annotation study validating that the generated perturbations preserve or alter meaning as intended. While the two-gate system provides automated quality assurance, edge cases inevitably exist (e.g., a synonym substitution that is semantically valid in general English but misleading in the specific science domain). A sample-based human annotation study with inter-annotator agreement metrics is planned for the journal extension of this work.

**Single dataset.** We evaluate on the Beetle corpus only, covering one science domain (electrical circuits). The SemEval 2013 Task 7 also includes the SciEntsBank corpus (covering a broader range of science topics), which is planned for the journal extension. Generalisation to other domains (humanities, mathematics, programming) and to datasets with different answer length distributions remains an open question.

**Single LLM tested.** Results in this paper come from GPT-5.4 mini at two prompting levels. Additional configurations — the frontier GPT-5.4 model (effect of model capability within the same vendor) and Gemini 2.5 Flash (cross-vendor consistency) — are left to future work. These would allow analysis of whether the patterns observed here (the reference-answer trade-off, the deletion paradox, the keyword-anchoring failure mode in Section 6.2) are model-specific or reflect more general properties of LLM-based grading.

**Single-rater qualitative coding.** The qualitative review of 30 missed-deletion cases (Section 5.4) was coded by a single annotator. A second-rater study with Cohen's kappa agreement is planned for the journal extension. The illustrative nature of the qualitative analysis is acknowledged; quantitative claims about the gradient and the L1 paradox rest on the n>5,000 statistical analysis of Section 5.4 (bootstrap CI, McNemar tests), not on the n=30 qualitative sample.

**The L1 deletion paradox is unfalsified, not yet confirmed.** Section 6.3 advances a single-mechanism hypothesis (token-level overlap) for both the gaming trade-off and the deletion paradox. This is consistent with the data and with the qualitative review, but a definitive causal test would require an ablation that holds token-overlap signal constant while varying semantic content of the reference. Such ablations are left to future work.

**No rubric in the SemEval dataset.** The Beetle corpus does not include structured per-question rubrics, so we use Level 0 vs. Level 1 prompting as a contrastive proxy for the effect of additional grading information. A structured rubric (specifying required concepts, acceptable phrasings, and common misconceptions) might produce different robustness profiles, and datasets with rubrics are an important direction for future work.

**Rule-based perturbations only.** All seven perturbation generators are rule-based, using deterministic transformations (synonym lookup, regex-based negation insertion, curated antonym dictionaries) rather than model-generated paraphrases. This design choice prioritises reproducibility and interpretability: every perturbation can be traced to a specific rule and seed. However, rule-based perturbations may underestimate the space of possible input variations. LLM-generated paraphrases, in particular, could surface vulnerabilities that rule-based approaches miss, such as complex syntactic restructuring or pragmatic reformulation. The framework architecture supports adding LLM-based generators alongside rule-based ones, and this extension is planned as future work.

---

## 7  Reproducibility and Package Documentation

The framework is released as an open-source Python package to support adoption, replication, and extension by other research groups. This section provides the information necessary to install, use, and extend the package.

### 7.1  Repository Structure

The repository is organised as follows:

```
asag-perturbation-framework/
    src/
        asag/
            __init__.py
            schema/
                records.py          # QuestionRecord, AnswerRecord, PerturbationRecord
                grade.py            # LABEL_TO_SCORE mapping, score constants
            loaders/
                base.py             # LoaderInterface ABC
                semeval2013.py      # SemEval 2013 Beetle/SciEntsBank loader
            splitters/
                protocol_a.py       # Leave-One-Question-Out splitter
                protocol_b.py       # Within-question 80/20 stratified splitter
                leakage.py          # Leakage diagnostic for Protocol A
            graders/
                base.py             # GraderInterface ABC, GradeResult model
                hybrid.py           # HybridGrader (logistic regression + SBERT)
                llm.py              # LLMGrader (OpenAI, Anthropic, Google)
            perturbations/
                engine.py           # PerturbationEngine (orchestrates all generators)
                gates.py            # Gate 1 (SBERT cosine) + Gate 2 (negation/antonym)
                cache.py            # Perturbation caching for expensive computations
                generators/
                    __init__.py     # PerturbationGenerator ABC
                    invariance.py   # SynonymSubstitution, TypoInsertion
                    sensitivity.py  # NegationInsertion, KeyConceptDeletion,
                                    # SemanticContradiction
                    gaming.py       # RubricKeywordEchoing, FluentWrongExtension
            metrics/
                calculator.py       # MetricCalculator (IVR, SSR, ASR computation)
                results.py          # MetricResult model
            evaluation/
                engine.py           # EvaluationEngine (full pipeline orchestration)
            infra/
                config.py           # Global configuration
                seeds.py            # SeedConfig for deterministic seed isolation
                run_dir.py          # Run directory management
                storage.py          # Result serialisation
                versions.py         # Dependency version tracking
    tests/                          # 77 unit and integration tests
    scripts/
        first_real_run.py           # Entry point for full experiment
        prepare_batch.py            # Prepare LLM batch API requests
        submit_batch.py             # Submit batch API jobs
        convert_batch_results.py    # Convert batch results to framework format
    pyproject.toml                  # Package metadata and dependencies
```

### 7.2  Installation

The package requires Python 3.9 or later and can be installed from source:

```bash
git clone https://github.com/fsasso/asag-perturbation-framework.git
cd asag-perturbation-framework
pip install -e .
```

For LLM grading support (which requires API client libraries for OpenAI, Anthropic, or Google), install the optional `llm` extras:

```bash
pip install -e ".[llm]"
```

Core dependencies include scikit-learn, sentence-transformers, pydantic (v2), nltk, and datasets (for HuggingFace loader access). The `[llm]` extras add openai, anthropic, and google-genai.

### 7.3  Adding a Custom Grader

To integrate a new grading system into the framework, implement the `GraderInterface` abstract base class:

```python
from asag.graders.base import GraderInterface, GradeResult

class MyTransformerGrader(GraderInterface):
    """Example custom grader wrapping a fine-tuned transformer."""

    def __init__(self, model_path: str):
        self._model = load_model(model_path)  # your loading logic

    @property
    def grader_name(self) -> str:
        return "my_transformer_v1"

    def grade(self, question, rubric, student_answer, **kwargs):
        prediction = self._model.predict(question, student_answer)
        return GradeResult(
            label=prediction.label,
            score=prediction.score,  # must be in [0.0, 1.0]
            confidence=prediction.confidence,
        )
```

The `EvaluationEngine` will call `grade()` for every original and perturbed answer, and the metric calculator will compare scores automatically. The `**kwargs` pattern allows the engine to optionally pass `reference_answer` when available; graders that do not use it can simply ignore the keyword argument.

### 7.4  Adding a Custom Dataset

To add a new dataset, implement a loader that returns `(List[QuestionRecord], List[AnswerRecord])`:

```python
from asag.schema.records import QuestionRecord, AnswerRecord

def load_my_dataset():
    questions = []
    answers = []
    for item in read_raw_data():
        q = QuestionRecord(
            question_id=item["id"],
            prompt=item["question_text"],
            reference_answers=item["references"],
        )
        questions.append(q)
        for student in item["student_answers"]:
            a = AnswerRecord(
                answer_id=student["id"],
                question_id=item["id"],
                student_answer=student["text"],
                gold_label=student["label"],
                gold_score=normalize_score(student["label"]),
            )
            answers.append(a)
    return questions, answers
```

The normalisation step (mapping dataset-specific labels to [0.0, 1.0] scores) is the loader's responsibility, ensuring that all downstream components operate on a common scale.

### 7.5  Running the Full Pipeline

The full pipeline can be executed via the entry point script:

```bash
PYTHONPATH=src python -m scripts.first_real_run
```

This script loads the Beetle dataset, initialises the configured graders, runs perturbation generation with quality gating, evaluates under both protocols (for trained graders), computes all four robustness metrics, and serialises results to a timestamped run directory. Results are stored as JSON files that can be loaded for further analysis.

### 7.6  Repository and Licence

The source code, data loaders, and analysis scripts are available at:

> https://github.com/fsasso/asag-perturbation-framework

The package is released under the MIT licence.

---

## 8  Conclusions

We have presented a perturbation-first evaluation framework for ASAG that quantifies robustness along three validity dimensions drawn from Messick's taxonomy. The framework comprises seven rule-based perturbation generators, two-gate quality validation, four metrics that compare the grader against itself, and a dual-protocol design that quantifies how trained graders degrade under cross-question generalisation.

Applied to the SemEval 2013 Beetle corpus, the framework yields three findings of practical and theoretical interest. First, a trained ML baseline exhibits a substantial robustness drop under cross-question evaluation (+15.8 percentage points on IVR_flip; +7.4 on ASR), demonstrating that standard within-question benchmarks systematically overestimate operational reliability. Second, a zero-shot LLM grader is markedly more robust on invariance and sensitivity dimensions and substantially less vulnerable to gaming, supporting the view that semantic processing generalises across surface variations in ways feature-based scoring cannot. Third, providing the LLM with a reference answer trades a 45% reduction in invariance violations for a 76% increase in gaming susceptibility, a non-obvious trade-off invisible to any single metric, surfaced by the multi-dimensional framework.

The floor-effect analysis (Section 5.3) reveals an additional methodological nuance: after correcting for answers already at score 0.0, the LLM's sensitivity detection at Level 1 reaches 73.1%, substantially higher than the headline 48.0%. This correction is larger for more discriminative graders, creating a paradox where better baseline grading performance mechanically suppresses the sensitivity metric. Researchers using SSR-style metrics should report both overall and floor-corrected values.

The analysis of specific negation failures (Section 6.2) identifies keyword anchoring as a persistent vulnerability even for frontier LLMs: when the negated sentence retains high lexical overlap with a plausible correct answer, the model processes the negation particle superficially. This finding suggests that negation handling should be a standard test case in any ASAG robustness evaluation.

These results support a broader argument: that robustness should be evaluated alongside accuracy as a first-class quality dimension for any ASAG system intended for high-stakes use, and that the evaluation should be multi-dimensional and grounded in established validity theory. The framework is open-source and designed to be applied to any prompting strategy or grader architecture, so that practitioners can detect trade-offs in their own deployment context before students encounter them.

---

## References

Alzantot, M., Sharma, Y., Elgohary, A., Ho, B.-J., Srivastava, M. and Chang, K.-W. (2018) 'Generating natural language adversarial examples', in *Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP 2018)*. Brussels: Association for Computational Linguistics, pp. 2890-2896.

Belinkov, Y. and Bisk, Y. (2018) 'Synthetic and natural noise both break neural machine translation', in *Proceedings of the 6th International Conference on Learning Representations (ICLR 2018)*.

Burrows, S., Gurevych, I. and Stein, B. (2015) 'The eras and trends of automatic short answer grading', *International Journal of Artificial Intelligence in Education*, 25(1), pp. 60-117.

Condor, A., Litster, M. and Pardos, Z. (2021) 'Automatic short answer grading with SBERT on out-of-sample questions', in *Proceedings of the 14th International Conference on Educational Data Mining (EDM 2021)*. International Educational Data Mining Society, pp. 376-382.

Deane, P. (2013) 'On the relation between automated essay scoring and modern views of the writing construct', *Assessing Writing*, 18(1), pp. 7-24.

Ding, Y., Riordan, B., Horbach, A., Cahill, A. and Zesch, T. (2020) 'Don't take "nswvtnvakgxpm" for an answer -- The surprising vulnerability of automatic content scoring systems to adversarial input', in *Proceedings of the 28th International Conference on Computational Linguistics (COLING 2020)*. Barcelona, pp. 882-892.

Dorsey, D. and Michaels, H. (2022) 'Validity arguments meet artificial intelligence in innovative educational assessment: a discussion and look forward', *Journal of Educational Measurement*, 59(3), pp. 267-271.

Dzikovska, M., Nielsen, R., Brew, C., Leacock, C., Giampiccolo, D., Bentivogli, L., Clark, P., Dagan, I. and Dang, H.T. (2013) 'SemEval-2013 Task 7: The joint student response analysis and 8th recognizing textual entailment challenge', in *Proceedings of the 7th International Workshop on Semantic Evaluation (SemEval 2013)*. Association for Computational Linguistics, pp. 263-274.

Ebrahimi, J., Rao, A., Lowd, D. and Dou, D. (2018) 'HotFlip: White-box adversarial examples for text classification', in *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (ACL 2018)*. Melbourne, pp. 31-36.

Erickson, T.D. and Mattson, M.E. (1981) 'From words to meaning: A semantic illusion', *Journal of Verbal Learning and Verbal Behavior*, 20(5), pp. 540-551.

Ferrara, S. and Qunbar, R. (2022) 'Validity arguments for AI-based automated scores: essay scoring as an illustration', *Journal of Educational Measurement*, 59(3), pp. 288-313.

Filighera, A., Ochs, S., Steuer, T. and Tregel, T. (2024) 'Cheating automatic short answer grading with the adversarial usage of adjectives and adverbs', *International Journal of Artificial Intelligence in Education*, 34(2), pp. 616-646.

Heilman, M. and Madnani, N. (2015) 'The impact of training data on automated short answer scoring performance', in *Proceedings of the 10th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2015)*. Denver: Association for Computational Linguistics, pp. 81-85.

Jia, R. and Liang, P. (2017) 'Adversarial examples for evaluating reading comprehension systems', in *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP 2017)*. Copenhagen, pp. 2021-2031.

Jin, D., Jin, Z., Zhou, J.T. and Szolovits, P. (2020) 'Is BERT really robust? A strong baseline for natural language attack on text classification and entailment', in *Proceedings of the Thirty-Fourth AAAI Conference on Artificial Intelligence (AAAI 2020)*. Palo Alto: AAAI Press, pp. 8018-8025.

Kane, M.T. (2006) 'Validation', in Brennan, R.L. (ed.) *Educational Measurement*. 4th edn. Westport, CT: American Council on Education/Praeger, pp. 17-64.

Kumar, Y., Bhatia, M., Kabra, A., Li, J.J., Jin, D. and Shah, R.R. (2020) 'Calling out bluff: Attacking the robustness of automatic scoring systems with simple adversarial testing', *arXiv preprint* arXiv:2007.06796.

Latif, E. and Zhai, X. (2024) 'Fine-tuning ChatGPT for automatic scoring', *Computers and Education: Artificial Intelligence*, 6, p. 100210.

Loukina, A., Madnani, N. and Cahill, A. (2019) 'The many dimensions of algorithmic fairness in educational applications', in *Proceedings of the 14th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2019)*. Florence: Association for Computational Linguistics, pp. 1-10.

Messick, S. (1989) 'Validity', in Linn, R.L. (ed.) *Educational Measurement*. 3rd edn. Washington, DC: American Council on Education/Macmillan, pp. 13-103.

Mizumoto, A. and Eguchi, M. (2023) 'Exploring the potential of using an AI language model for automated essay scoring', *Research Methods in Applied Linguistics*, 2(2), p. 100050.

Mohler, M., Bunescu, R. and Mihalcea, R. (2011) 'Learning to grade short answer questions using semantic similarity measures and dependency graph alignments', in *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics (ACL 2011)*. Portland, pp. 752-762.

Morris, J.X., Lifland, E., Yoo, J.Y., Grigsby, J., Jin, D. and Qi, Y. (2020) 'TextAttack: A framework for adversarial attacks, data augmentation, and adversarial training in NLP', in *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations (EMNLP 2020)*. Association for Computational Linguistics, pp. 119-126.

Naismith, B., Mulcaire, P. and Burstein, J. (2023) 'Automated evaluation of written discourse coherence using GPT-4', in *Proceedings of the 18th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2023)*. Toronto, pp. 394-403.

Reimers, N. and Gurevych, I. (2019) 'Sentence-BERT: Sentence embeddings using Siamese BERT-networks', in *Proceedings of EMNLP-IJCNLP 2019*. Hong Kong: Association for Computational Linguistics, pp. 3982-3992.

Ribeiro, M.T., Wu, T., Guestrin, C. and Singh, S. (2020) 'Beyond accuracy: Behavioral testing of NLP models with CheckList', in *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*. Association for Computational Linguistics, pp. 4902-4912.

Riordan, B., Horbach, A., Cahill, A., Zesch, T. and Lee, C.M. (2017) 'Investigating neural architectures for short answer scoring', in *Proceedings of the 12th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2017)*. Copenhagen: Association for Computational Linguistics, pp. 159-168.

Shermis, M.D. (2022) 'Anchoring validity evidence for automated essay scoring', *Journal of Educational Measurement*, 59(3), pp. 314-337.

Sung, C., Dhamecha, T.I. and Mukhi, N. (2019) 'Pre-training BERT on domain resources for short answer grading', in *Proceedings of the 20th International Conference on Artificial Intelligence in Education (AIED 2019)*. Lecture Notes in Computer Science, vol. 11625. Cham: Springer, pp. 469-481.

Wang, X., Wang, H. and Yang, D. (2022) 'Measure and improve robustness in NLP models: A survey', in *Proceedings of NAACL 2022*. Seattle: Association for Computational Linguistics, pp. 4569-4586.

Williamson, D.M., Xi, X. and Breyer, F.J. (2012) 'A framework for evaluation and use of automated scoring', *Educational Measurement: Issues and Practice*, 31(1), pp. 2-13.

---

## Appendix A: Full Perturbation Type Descriptions

This appendix provides detailed descriptions of all seven perturbation generators, including examples drawn from the Beetle dataset.

### A.1  Synonym Substitution (Invariance)

**Purpose.** Test whether the grader is robust to meaning-preserving word replacements.

**Mechanism.** For each word in the student answer, the generator checks whether the word is eligible for substitution: it must be at least four characters long, purely alphabetic, and tagged as a noun, verb, or adjective by the NLTK part-of-speech tagger. For each eligible word, WordNet synonyms are retrieved and sorted alphabetically. The first synonym (excluding the original word and multi-word expressions) is selected as the replacement. Up to two variants are produced by substituting at the first and second eligible word positions respectively.

**Example.**
- Original: "The bulb lights up because current flows through the circuit."
- Variant 1: "The bulb *illuminates* up because current flows through the circuit." (lights -> illuminates at position 1)
- Variant 2: "The bulb lights up because *stream* flows through the circuit." (current -> stream at position 2)

**Quality gate.** Gate 1 (SBERT cosine similarity >= 0.85) applies. Candidates where the synonym shifts the embedding below the threshold are rejected. Gate 2 (negation/antonym check) also applies.

**Variants per answer:** up to 2.

### A.2  Typo Insertion (Invariance)

**Purpose.** Test whether the grader is robust to minor character-level noise, simulating natural typing errors.

**Mechanism.** One content word (at least four characters, purely alphabetic) is selected via a seeded random number generator. One of three character-level operations is applied: (0) swap two adjacent characters, (1) delete one character, or (2) duplicate one character. The position within the word is also randomly determined.

**Example.**
- Original: "The battery provides voltage to the circuit."
- Variant: "The battery *provdies* voltage to the circuit." (adjacent swap at position 4 of "provides")

**Quality gate.** Gate 1 does not apply to typo insertion (typos naturally shift embeddings slightly, but this is the intended test). Gate 2 (negation/antonym check) applies.

**Variants per answer:** 1.

### A.3  Negation Insertion (Sensitivity)

**Purpose.** Test whether the grader detects the insertion of a negation that inverts the sentence meaning.

**Mechanism.** Three strategies are attempted in order: (1) insert "not" after the first auxiliary verb found in the text (is, are, was, were, will, can, could, should, would, does, did, has, have, had); (2) if no auxiliary verb is found, replace the first simple domain verb with "does not [verb]", drawing from a curated list of 26 common science-domain verbs (flows, lights, connects, completes, opens, closes, conducts, carries, moves, transfers, converts, increases, decreases, changes, causes, produces, requires, contains, allows, prevents, stores, absorbs, reflects, emits, dissolves, evaporates, melts, freezes); (3) as a final fallback, prepend "It is not true that" to the lowercased original text.

**Example.**
- Original: "The bulb is in a closed circuit."
- Variant: "The bulb is *not* in a closed circuit." (strategy 1: "not" inserted after "is")

- Original: "Current flows through the wire."
- Variant: "Current *does not* flows through the wire." (strategy 2: domain verb replacement)

**Quality gate.** No quality gate applies (sensitivity perturbations are expected to change meaning).

**Variants per answer:** 1.

### A.4  Key Concept Deletion (Sensitivity)

**Purpose.** Test whether the grader detects the removal of a domain-critical content word.

**Mechanism.** All non-stopword content words of at least four characters are identified. One is selected for removal via a seeded random number generator. The remaining tokens are rejoined.

**Example.**
- Original: "The voltage across the battery terminal is zero."
- Variant: "The voltage across the battery is zero." (deleted "terminal")

**Quality gate.** No quality gate applies.

**Variants per answer:** 1.

### A.5  Semantic Contradiction (Sensitivity)

**Purpose.** Test whether the grader detects the replacement of a domain term with its semantic opposite.

**Mechanism.** The generator scans the student answer for any word matching a key in a curated antonym dictionary of 40 pairs covering physics, biology, chemistry, and earth science vocabulary. Matches are found via case-insensitive word-boundary regular expressions. Up to two variants are produced from the first two match positions. If no match is found, the fallback "It is not true that..." formulation is used.

**Antonym dictionary (selected pairs):** open/closed, increase/decrease, positive/negative, series/parallel, connect/disconnect, complete/incomplete, conduct/insulate, absorb/reflect, expand/contract, solid/liquid, producer/consumer, predator/prey, oxidize/reduce, endothermic/exothermic, acidic/basic, anode/cathode, bright/dim, more/less, faster/slower, larger/smaller.

**Example.**
- Original: "The circuit is an open circuit so no current flows."
- Variant 1: "The circuit is a *closed* circuit so no current flows." (open -> closed)

**Quality gate.** No quality gate applies.

**Variants per answer:** up to 2.

### A.6  Rubric Keyword Echoing (Gaming)

**Purpose.** Simulate a keyword-stuffing attack in which an adversarial student appends reference-answer terms to an incorrect response to inflate the score.

**Mechanism.** Content words from the reference answer (at least four characters, non-stopword, alphabetic) that are absent from the student answer are identified and sorted. Two variants are produced: variant 0 appends 3-4 randomly sampled keywords; variant 1 appends 5-6 randomly sampled keywords. If no unique reference keywords exist (i.e., the student answer already contains all reference terms), no variants are produced.

**Example.**
- Reference answer: "A closed path is created through the circuit allowing current to flow."
- Student answer (incorrect): "I don't know."
- Variant 1: "I don't know. *allowing circuit closed path*" (4 keywords appended)
- Variant 2: "I don't know. *allowing circuit closed created current path*" (6 keywords appended)

**Quality gate.** No quality gate applies (gaming perturbations are adversarial by design).

**Variants per answer:** up to 2.

### A.7  Fluent Wrong Extension (Gaming)

**Purpose.** Test whether the grader can distinguish factual correctness from confident-sounding prose. Simulates a student who elaborates with authoritative but incorrect statements.

**Mechanism.** One statement is randomly selected from a curated pool of 30 plausible-sounding misconceptions covering physics, biology, chemistry, and earth science. The statement is prefixed with a connecting phrase (e.g., "Furthermore,", "Additionally,", "Moreover,", "Also,", "In addition,") and appended to the student answer.

**Example misconceptions in the pool:**
- "This is because electrical resistance causes current to flow faster through thinner wires."
- "The voltage across an open switch is always zero."
- "Parallel circuits always have higher total resistance than series circuits."
- "Photosynthesis primarily occurs in the root cells of plants."
- "Ionic bonds form when two nonmetal atoms share electrons equally."

**Example.**
- Original: "The bulb lights up."
- Variant: "The bulb lights up. *Furthermore, Parallel circuits always have higher total resistance than series circuits.*"

**Quality gate.** No quality gate applies.

**Variants per answer:** 1.

---

## Appendix B: Prompt Templates for LLM Grader

This appendix reproduces the exact prompt templates used for the LLM grader (GPT-5.4 mini) in our experiments. The grader uses a system prompt that defines the task and output format, paired with a user prompt that provides the specific question and answer. Two user prompt variants correspond to Level 0 (no reference answer) and Level 1 (with reference answer).

### B.1  System Prompt (shared by both levels)

```
You are an expert educational assessor grading student answers to science
questions. You must classify each student answer into exactly one of these
categories:
- correct: The answer fully addresses the question with accurate information.
- partially_correct_incomplete: The answer is partially correct but missing
  key concepts.
- contradictory: The answer contradicts the expected correct answer.
- irrelevant: The answer is off-topic and does not address the question.
- non_domain: The answer is outside the subject domain entirely.

Respond with ONLY a JSON object in this exact format:
{"label": "<one of the five labels above>", "confidence": <float between 0.0
and 1.0>}
Do not include any other text.
```

### B.2  User Prompt, Level 0 (no reference answer)

```
Question: {question}

Student answer: {student_answer}

Classify the student answer.
```

### B.3  User Prompt, Level 1 (with reference answer)

```
Question: {question}

Reference answer (correct): {reference_answer}

Student answer: {student_answer}

Classify the student answer by comparing it to the reference answer.
```

### B.4  Label Mapping and Response Parsing

The LLM's JSON response is parsed with the following processing steps:

1. **Markdown fence removal.** If the response begins with triple backticks (a common LLM output artefact), the fences are stripped.
2. **Label normalisation.** The raw label string is lowercased and matched against an alias table that maps common variations to canonical labels. For example, "incorrect" and "wrong" both map to "contradictory"; "partial" maps to "partially_correct_incomplete"; "off-topic" and "off topic" map to "irrelevant".
3. **Score mapping.** Canonical labels are mapped to normalised scores using the same scale as the gold labels: correct = 1.0, partially_correct_incomplete = 0.5, contradictory = 0.0, irrelevant = 0.0, non_domain = 0.0.
4. **Confidence clamping.** The confidence value is clamped to [0.0, 1.0].
5. **Parse failure handling.** If the response cannot be parsed as valid JSON on the first attempt, the grader retries once with an explicit instruction to output valid JSON. If the retry also fails, a fallback result is returned with label "irrelevant", score 0.0, and confidence 0.0.

### B.5  API Configuration

All API calls use temperature 0.0 for near-deterministic output. For OpenAI, a fixed seed parameter (seed=42) is additionally passed. Maximum output tokens are set to 100 (sufficient for the short JSON response). Exponential backoff with up to 5 retries handles rate limiting and transient API errors.

---

## Appendix C: Gate Rejection Statistics by Perturbation Type

This appendix reports the two-gate quality validation statistics for invariance perturbations.

### C.1  Gate 1: SBERT Cosine Similarity Threshold

Gate 1 applies exclusively to synonym substitution candidates. A candidate is rejected if its sentence-BERT cosine similarity with the original text falls below 0.85.

| Metric | Value |
|---|---|
| Synonym substitution candidates tested | Total candidates before Gate 1 |
| Rejection rate | **40.3%** |

The 40.3% rejection rate indicates that nearly half of all WordNet synonym replacements produce texts that are semantically divergent from the original in the science domain. This high rejection rate reflects a well-known limitation of WordNet: its synsets group words by dictionary definitions that may not hold in specialised technical contexts. For example, a WordNet synonym for "current" (in the electrical sense) might be "stream" or "flow" (which are synonyms in a hydrological context but misleading in a circuit-domain answer). The SBERT-based gate detects such semantic drift and rejects the candidate, even when the substitution is lexically valid.

Gate 1 does not apply to typo insertion candidates. Typos naturally produce character-level noise that shifts SBERT embeddings slightly, but this shift is precisely the property being tested (whether the grader is robust to such noise). Applying Gate 1 to typos would filter out the perturbations we wish to evaluate.

### C.2  Gate 2: Negation and Antonym Heuristic

Gate 2 applies to all invariance family types (synonym substitution and typo insertion). It rejects candidates that introduce new negation markers or new antonyms not present in the original text.

The negation check matches 17 negation forms: not, never, no, cannot, can't, won't, doesn't, isn't, aren't, wasn't, weren't, don't, didn't, haven't, hadn't, shouldn't, wouldn't, couldn't. The check compares per-token negation sets between the original and candidate: a negation marker in the candidate that was not in the original triggers rejection.

The antonym check uses a dictionary mirroring the 40-pair contradiction map from the sensitivity generators. If any antonym value appears in the candidate but was not present in the original, the candidate is rejected. This catches cases where a synonym substitution inadvertently introduces a meaning-inverting word (e.g., replacing "complete" with a WordNet synonym that happens to be "incomplete").

Gate 2 functions as a safety net for cases that Gate 1 might miss: two sentences can have high cosine similarity despite one containing a negation that inverts the meaning, because SBERT embeddings are computed over the full sentence and a single negation token has a small effect on the aggregate embedding vector. Gate 2's token-level checking catches these edge cases.

### C.3  Combined Gate Effect

The two gates operate sequentially. Gate 1 first filters synonym substitution candidates by embedding similarity. Gate 2 then filters all surviving invariance candidates (from both synonym substitution and typo insertion) by negation/antonym detection. A candidate must pass both gates to be included in the final perturbation set.

The combined effect of the two gates is to ensure that all invariance perturbations in the final dataset are genuinely meaning-preserving: they are semantically close to the original (Gate 1) and do not introduce meaning inversions (Gate 2). The rejected candidates are not regenerated, and the rejection rates are reported as research results quantifying the inherent difficulty of producing valid invariance perturbations in technical domains.

---

## Appendix D: Qualitative Analysis of Deletion Failures

This appendix details the manual review introduced in Section 5.4. The goal is to characterise the *mechanism* underlying the deletion miss rate — that is, to understand which kinds of word the grader is willing to overlook and what semantic damage that overlooking causes.

### D.1  Sampling Procedure

From the missed-deletion cases identified in the L0 and L1 grade caches (i.e., pairs in which the perturbed score equalled the original score and the original score was strictly greater than zero), we drew a fixed-seed random sample of 15 cases per grader (30 total). Sampling code is committed at `scripts/extract_deletion_cases.py` (random seed = 42) and the resulting case file at `runs/analysis/deletion_missed_cases.txt`. Selecting only non-floor cases removes the sampling artefact in which an answer with original score 0 cannot decrease further regardless of the grader's behaviour.

### D.2  Coding Scheme

Each case was annotated by the author along two dimensions:

- **Category of the deleted word**: `article` (articles, determiners), `domain_concept` (technical Beetle vocabulary: terminal, battery, voltage, circuit, current, switch, bulb, path, gap, plus polar markers closed, open, positive, negative), `verb` (main or auxiliary), `connective` (prepositions, conjunctions: because, and, between, where, etc.), or `other` (pronouns, modifying adverbs, deictics, quantifiers like both/each/always, generic nouns).
- **Severity of meaning change**: `meaning_preserved` (a human grader would not penalise the answer; the deletion is benign), `meaning_degraded` (less precise or partial loss but recoverable from context), or `meaning_inverted` (meaning seriously broken, lost or contradicted).

Each case was given a one-line rationale explaining the choice. The full annotated file is in the repository at `runs/analysis/deletion_missed_cases_annotated.txt` together with a tabular summary at `runs/analysis/deletion_review_summary.md`.

### D.3  Aggregate Counts

The cross-tabulation of category by severity, summed across L0 and L1 (n = 30), is reproduced in Section 5.4 (Table 7). The headline figures: 17 cases (57%) involved deletion of a domain concept, of which 16 (94%) were judged degraded or inverted; the 3 connective deletions and 5 of the 8 "other" deletions were correctly judged preserved. The cleanest pattern is the contrast between the two extremes: domain-concept deletions are almost always non-benign in this sample, while connective deletions are always benign.

### D.4  Selected Cases

To support transparent inspection, we list six representative cases (three "preserved", three "inverted") drawn from the 30-case sample. Numbering follows the position in the random sample.

**Preserved cases (the grader is right not to penalise).**

- *L0 [1]* — Q: "How does a damaged bulb compare to an open switch?" Original: "they both creat gaps in the path" (gold = correct). Deleted: `both`. Perturbed: "they creat gaps in the path". The pronoun "they" already encodes plurality; "both" is redundant emphasis and the meaning is intact.
- *L0 [8]* — Q: "Explain why you got a voltage reading of 1.5 for terminal 1 and the positive terminal." Original: "Because the positive circuit has a voltage of 1.5 volts." Deleted: `Because`. The causal marker is dropped but the explanation content is intact; a human grader would accept this in answer to "explain why".
- *L1 [4]* — Q: "Why was bulb C off when switch Z was open?" Deleted: `because` between two clauses. The two facts are still asserted and the logical relation is inferable.

**Inverted cases (the grader should penalise but does not).**

- *L1 [5]* — Q: "Why was bulb A on when switch Y was open and switch Z was closed?" Original: "The battery is conatained in *a closed path* with bulb a" (gold = correct, score 1.0). Deleted: `closed`. Perturbed: "The battery is conatained in *a path* with bulb a", L1 score = 1.0. The closed/open distinction is the central conceptual axis of the Beetle physics task.
- *L1 [11]* — Q: "What is voltage?" Original: "a measure of the strength of electricity" (gold = contradictory, original score = 0.5). Deleted: `strength`. Perturbed: "a measure of the of electricity", L1 score = 0.5. The head noun is removed and the surface fragment "measure of the of electricity" is broken; the proposed definition has no content left, but the grader continues to register the original tokens.
- *L0 [11]* — Q: "Finally, consider finding a burned out light bulb in a long string of lights..." Original: "When the voltage changes to 0." (gold = contradictory, original score = 0.5). Deleted: `voltage`. Perturbed: "When the changes to 0.", L0 score = 0.5. The subject of the change is removed; the answer's diagnostic content (voltage going to 0) is lost.

### D.5  Limitations of the Qualitative Analysis

The analysis is illustrative, not inferential. It is single-rater (no second-rater Cohen's kappa), based on n = 30, and its purpose is to characterise a mechanism rather than to estimate population proportions. Quantitative claims about the sensitivity blindness gradient and the L1 deletion paradox rely on the n > 5,000 statistical analysis of Section 5.4 (bootstrap CI, paired McNemar tests), not on this qualitative review. A full second-rater study with inter-annotator agreement is planned for the journal extension, together with an ablation that distinguishes the contribution of token-overlap signal from semantic content of the reference.
