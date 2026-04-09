# IFKAD 2026 Full Paper — Draft

> **Format target:** Calibri 10pt, A4, 2.54cm margins, fully justified.
> **Length:** 3,000–5,000 words including abstract, figures, references. Max 10 pages, 4MB.
> **References:** Harvard style. No footnotes, no endnotes.

---

## TITLE

Perturbation-First Robustness Evaluation of Automated Short Answer Grading: Quantifying the Hidden Fragility of Trained and Zero-Shot Graders

## AUTHORS

Ferdinando Sasso, Andrea De Mauro
LUISS Guido Carli University, Rome, Italy
fsasso@studenti.luiss.it
ademauro@luiss.it

## ABSTRACT

*[Word target: 300–400. To finalise once all configurations complete; current placeholder reflects results available as of writing.]*

Automated Short Answer Grading (ASAG) is increasingly deployed in high-stakes educational contexts, yet the dominant evaluation paradigm reports only agreement with human raters and overlooks an equally important quality dimension: robustness, the consistency of grading behaviour under controlled input transformations. We present a perturbation-first evaluation framework that quantifies robustness along three validity dimensions drawn from Messick's (1995) taxonomy: invariance (construct-irrelevant variance), sensitivity (construct underrepresentation), and gaming (adversarial manipulation). The framework comprises seven rule-based perturbation generators, two-gate quality validation, and four metrics — IVR_flip, IVR_absdelta, SSR_directional, ASR_thresholded — that compare the grader against itself rather than against gold labels, isolating robustness from accuracy. A dual-protocol design (Leave-One-Question-Out vs. within-question split) quantifies how trained graders degrade under cross-question generalisation. We apply the framework to the SemEval 2013 Beetle corpus (5,199 answers, 42 questions, 41,444 perturbations) and compare a hybrid ML baseline against zero-shot LLM graders (GPT-5.4 mini, Levels 0 and 1). Three findings stand out. First, the trained baseline exhibits a substantial robustness drop under cross-question evaluation: invariance violations rise from 17.9% to 33.7% (+15.8 percentage points), and gaming susceptibility from 11.5% to 18.8%. Standard within-question evaluations therefore overestimate operational reliability. Second, the zero-shot LLM is markedly more robust on invariance and sensitivity dimensions (IVR 0.243 vs 0.337; SSR 0.420 vs 0.140 — a threefold improvement) and substantially less vulnerable to gaming (ASR 0.067 vs 0.188). Third, providing the LLM with the reference answer (Level 1) reduces invariance violations by 45% but simultaneously increases gaming susceptibility by 76% — a non-obvious trade-off invisible to single-metric evaluation. We argue that perturbation-first, multi-dimensional evaluation should complement accuracy metrics in any responsible ASAG deployment, and provide an open-source framework to make this practical.

## KEYWORDS

Automated Short Answer Grading; Robustness Evaluation; Perturbation Testing; Large Language Models; Construct Validity

## PAPER TYPE

Academic Research Paper

---

## 1  Introduction

Automated Short Answer Grading (ASAG) systems evaluate free-text student responses against reference answers, assigning grades that ideally match expert human judgement. As these systems are increasingly deployed in high-stakes educational settings, the standard evaluation paradigm — reporting accuracy or Quadratic Weighted Kappa (QWK) against gold labels — reveals an important blind spot: a grader may achieve high agreement with human raters on clean test data yet behave erratically when inputs vary in superficial, meaning-preserving ways.

This fragility matters. A student who writes "the lamp illuminates" instead of "the bulb lights up" should receive the same grade; a student who inserts "not" into a correct answer should not. When graders fail these basic consistency checks, the resulting scores reflect surface-level artefacts rather than genuine understanding — a violation of construct validity that undermines the pedagogical purpose of assessment (Messick, 1989; Williamson et al., 2012). Recent work has documented that operational ASAG systems are surprisingly easy to mislead with simple adversarial inputs (Ding et al., 2020; Kumar et al., 2020; Filighera et al., 2024), yet such vulnerabilities remain absent from standard benchmarking practice.

We argue that robustness — the consistency of grading behaviour under controlled input transformations — should be evaluated alongside accuracy as a first-class quality dimension. To this end, we propose a perturbation-first evaluation framework built on three complementary perturbation families, each targeting a distinct validity threat: invariance perturbations (construct-irrelevant variance), sensitivity perturbations (construct underrepresentation), and gaming perturbations (adversarial manipulation).

The framework introduces four metrics — IVR_flip, IVR_absdelta, SSR_directional, and ASR_thresholded — that quantify grader behaviour under each perturbation family. Crucially, these metrics compare the grader against itself (original vs. perturbed score), not against gold labels, thereby isolating robustness from accuracy.

To measure how robustness degrades under distributional shift for trained graders, we define a dual-protocol evaluation design. Protocol A (Leave-One-Question-Out) evaluates cross-question generalisation, where the grader faces questions unseen during training. Protocol B (within-question 80/20 split) evaluates in-distribution performance. The difference between protocols — the robustness drop — reveals how much consistency a trained grader loses when operating beyond its training distribution. Because zero-shot LLM graders do not undergo task-specific training, the dual-protocol distinction does not apply to them; their robustness is instead assessed through absolute metric values and direct comparison with the trained baseline.

We apply this framework to the SemEval 2013 Beetle dataset (5,199 student answers, 42 questions), evaluating a hybrid ML baseline and an LLM grader (GPT-5.4 mini) at two information levels. Our contributions are:

1. A perturbation-first evaluation framework with seven rule-based generators, two-gate quality validation, and four robustness metrics grounded in validity theory.
2. A dual-protocol design that quantifies robustness degradation under distribution shift for trained graders, revealing the extent to which standard within-question evaluations overestimate operational reliability.
3. A cross-paradigm robustness comparison between trained ML and zero-shot LLM graders across three validity dimensions, including a non-obvious trade-off introduced by reference-answer prompting that is invisible to single-metric evaluation.

---

## 2  Theoretical Background

### 2.1  ASAG Methods and the Limits of Accuracy-Centred Evaluation

The ASAG literature spans nearly two decades of methodological progress, from early lexical and dependency-based approaches (Mohler et al., 2011) through neural architectures (Riordan et al., 2017) to transformer-based models (Sung et al., 2019) and sentence-BERT representations applied to out-of-sample questions (Condor et al., 2021). Burrows et al. (2015) provide the canonical taxonomy of the field. Across this trajectory, the dominant evaluation paradigm has reported agreement with human raters via accuracy, Quadratic Weighted Kappa, or correlation coefficients. As Heilman and Madnani (2015) showed, even the apparent quality of these agreement scores depends heavily on the composition of the training data, and the gap between in-distribution performance and operational reliability has long been a concern of the educational measurement community (Williamson et al., 2012; Deane, 2013).

### 2.2  Construct Validity as a Theoretical Foundation

The limits of agreement-based evaluation are best understood through the lens of construct validity — the degree to which an assessment measures what it claims to measure (Messick, 1989; Kane, 2006). Messick's unified validity framework identifies two principal threats. *Construct-irrelevant variance* occurs when scores are influenced by factors unrelated to the construct: a grader that penalises a correct answer because of a minor spelling error, for instance, is measuring something other than the targeted competence. *Construct underrepresentation* occurs when the assessment fails to capture meaningful aspects of the construct: a grader that does not detect a negation inverting an answer's meaning is failing to represent the construct adequately. To these, the educational measurement literature on automated scoring has added a third threat specific to algorithmic systems — *adversarial gaming*, in which surface-level manipulations such as keyword stuffing or fluent but incorrect elaboration artificially inflate scores (Williamson et al., 2012). Recent work has extended these classical concerns to AI-based scoring contexts (Ferrara and Qunbar, 2022; Dorsey and Michaels, 2022; Shermis, 2022), arguing that validity arguments must be reconstructed when scores are produced by opaque models.

### 2.3  Adversarial and Perturbation-Based Evaluation

Perturbation-based evaluation has become a standard methodology for assessing NLP model robustness. Ribeiro et al. (2020) introduced CheckList, a behavioural testing framework that systematically probes model capabilities through invariance, directional, and minimum functionality tests. Wang et al. (2022) survey the broader landscape of robustness measurement and improvement in NLP. The general adversarial-NLP literature provides a rich toolkit of attack strategies — gradient-based character flips (Ebrahimi et al., 2018), genetic synonym attacks (Alzantot et al., 2018), BERT-based word substitutions (Jin et al., 2020), and reading-comprehension distractors (Jia and Liang, 2017) — most of which are unified by frameworks such as TextAttack (Morris et al., 2020). Belinkov and Bisk (2018) showed that even simple natural noise breaks neural translation, foreshadowing the kind of fragility we observe in ASAG.

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

The evaluation framework follows a unidirectional pipeline: data loading, perturbation generation, grading, metric computation, and cross-protocol comparison. All data flows through validated immutable models (questions, answers, perturbations, grade results) to ensure reproducibility throughout the pipeline. The framework is implemented in Python and is publicly available as an open-source package.

### 3.2  Perturbation Generation

Seven rule-based generators produce up to ten perturbation variants per student answer, organised into three families.

**Invariance family.** Synonym substitution replaces content words (nouns, verbs, adjectives) with WordNet synonyms, producing up to two variants per answer. Synonyms are selected deterministically (alphabetically sorted) to ensure reproducibility. Typo insertion introduces a single character-level modification (adjacent swap, deletion, or duplication) into one content word.

**Sensitivity family.** Negation insertion adds "not" after auxiliary verbs or prepends "It is not true that" as a fallback. Key concept deletion removes one domain-relevant content word selected via seeded random sampling. Semantic contradiction replaces domain terms with curated antonyms (e.g., "open" → "closed", "series" → "parallel") drawn from a 40-pair dictionary covering physics and biology vocabulary.

**Gaming family.** Rubric keyword echoing appends reference-answer keywords absent from the student response, simulating keyword stuffing. Fluent wrong extension appends a confident but factually incorrect domain statement from a curated pool of 30 plausible-sounding misconceptions.

### 3.3  Two-Gate Quality Validation

Invariance perturbations undergo two validation gates before acceptance. Gate 1 applies only to synonym substitution: candidate texts must achieve cosine similarity of at least 0.85 with the original, measured via sentence-BERT embeddings (all-MiniLM-L6-v2). Gate 2 applies to all invariance types: candidates introducing new negation markers or antonyms not present in the original are rejected. Rejected candidates are not regenerated; the rejection rate is reported as a research result, reflecting the inherent difficulty of producing valid invariance perturbations for short science answers.

### 3.4  Robustness Metrics

All metrics compare the grader's own score on the original answer against its score on the perturbed answer, isolating robustness from accuracy.

**IVR_flip** (Invariance Violation Rate, binary): the proportion of invariance pairs where the grader's score changed at all. Lower values indicate greater robustness.

**IVR_absdelta** (Invariance Violation Rate, continuous): the mean absolute score difference across invariance pairs. Captures violation magnitude, not just occurrence.

**SSR_directional** (Sensitivity Success Rate): the proportion of sensitivity pairs where the perturbed score strictly decreased. Higher values indicate the grader correctly detects meaning-altering changes. No-change counts as failure, since a sensitivity perturbation that does not alter the grade indicates the grader missed the modification.

**ASR_thresholded** (Adversarial Success Rate): the proportion of gaming pairs where the score crossed from below the passing threshold (0.5) to at or above it. Measures vulnerability to adversarial manipulation. Already-passing answers that increase further are excluded.

Scores are rounded to six decimal places before comparison to prevent IEEE 754 floating-point artefacts from producing false positive violations.

### 3.5  Dual-Protocol Evaluation

The dual-protocol design targets trained graders that learn question-specific patterns from data. It quantifies how much robustness these graders lose when encountering novel questions not seen during training.

**Protocol A (LOQO — Leave-One-Question-Out)** implements cross-question evaluation. For each of 42 questions, the grader is trained on answers from all other questions and tested on the held-out question's answers. A leakage diagnostic verifies that no held-out question text appears in the training data. This protocol measures robustness under distributional shift — the realistic deployment scenario where a grader must generalise to new questions.

**Protocol B (within-question 80/20)** implements in-distribution evaluation. For each question independently, answers are split into 80% train and 20% test using stratified sampling on gold labels. The grader is trained on the same question's answers, then tested. This protocol measures baseline robustness on familiar content — the optimistic scenario typically reported in ASAG literature.

**Robustness drop** is defined as the difference between Protocol A and Protocol B aggregate metrics. For invariance and gaming metrics (where higher indicates worse robustness), a positive drop signals degradation under distribution shift. For sensitivity (where higher indicates better detection), a negative drop signals degradation. The aggregate is a macro-average: each fold or question contributes equally regardless of test-set size, preventing large questions from dominating the result.

**Applicability to zero-shot graders.** The dual-protocol distinction is meaningful only for graders with a training phase. Zero-shot LLM graders receive an identical prompt regardless of how the data is split — they have no mechanism to internalise question-specific patterns from a training set. Consequently, their Protocol A and Protocol B results are expected to be statistically equivalent, differing only by sampling noise from the data partition. Rather than reporting a tautological drop of approximately zero, we evaluate LLM graders on their absolute robustness metrics and compare them directly against the trained baseline's Protocol A results — the most demanding evaluation condition.

---

## 4  Experimental Setup

### 4.1  Dataset

We use the SemEval 2013 Task 7 Beetle dataset (Dzikovska et al., 2013), comprising 5,199 student answers to 42 science questions about electrical circuits. Answers are labelled on a five-way scale: correct (42.0%), partially_correct_incomplete (23.1%), contradictory (27.0%), non_domain (5.0%), and irrelevant (2.9%). Labels are normalised to a continuous [0, 1] scale (correct = 1.0, partial = 0.5, others = 0.0) following the ASAG2024 benchmark convention.

### 4.2  Graders

**Hybrid ML baseline.** A logistic regression classifier trained on 388-dimensional feature vectors: four handcrafted linguistic features (lexical overlap, length ratio, negation flag, reference-token recall) concatenated with 384-dimensional sentence-BERT embeddings (Reimers and Gurevych, 2019; specifically, the all-MiniLM-L6-v2 model). Class weights are balanced to handle label imbalance. This configuration is broadly representative of strong feature-based ASAG baselines reported in the literature (Sung et al., 2019; Condor et al., 2021).

**LLM grader.** Zero-shot prompting of GPT-5.4 mini, evaluated at two information levels. Level 0 supplies the question and the student answer only; Level 1 additionally supplies the reference answer and instructs the model to compare the student response against it. Temperature is set to 0.0 for near-deterministic output, with a fixed seed for reproducibility. The model outputs a JSON object with a label and a confidence score; labels are mapped to the same [0, 1] scale as the gold labels. Because the LLM operates in a zero-shot regime with no task-specific training, the dual-protocol distinction does not alter its input; it is evaluated once and compared against the HybridGrader's Protocol A (cross-question) results.

### 4.3  Perturbation Statistics

The perturbation engine generated 41,444 perturbations across all seven types from 5,199 source answers, averaging 8.0 perturbations per answer (the theoretical maximum is 10). Gate 1 (SBERT cosine similarity < 0.85) rejected 40.3% of synonym substitution candidates, indicating that nearly half of WordNet synonym replacements produce semantically divergent texts in the science domain. Gate 2 (negation/antonym heuristic) provided additional filtering for meaning-inverting substitutions across all invariance types. The rejection rate is reported as a research result rather than a failure: it quantifies the inherent difficulty of producing valid invariance perturbations in technical domains and motivates the two-gate design.

---

## 5  Results

Results are organised in two parts. Section 5.1 presents the dual-protocol analysis of the trained HybridGrader, quantifying robustness degradation under distributional shift. Section 5.2 compares the trained baseline against the zero-shot LLM grader on absolute robustness metrics, including the effect of reference-answer availability.

### 5.1  Dual-Protocol Analysis: Robustness Drop of the Trained Grader

Table 1 reports the HybridGrader's aggregate robustness metrics under both evaluation protocols.

**Table 1. HybridGrader robustness metrics by evaluation protocol.**

| Metric | Protocol B (in-distribution) | Protocol A (cross-question) | Drop (A − B) |
|---|---|---|---|
| IVR_flip (↓) | 0.179 | 0.337 | **+0.158** |
| IVR_absdelta (↓) | 0.125 | 0.242 | **+0.118** |
| SSR_directional (↑) | 0.120 | 0.140 | +0.020 |
| ASR_thresholded (↓) | 0.115 | 0.188 | **+0.074** |

The HybridGrader exhibits substantial robustness degradation under cross-question evaluation. Invariance violations nearly double from Protocol B to Protocol A (IVR_flip: 0.179 → 0.337), indicating that when the grader faces questions not seen during training, it changes its score on meaning-preserving perturbations 33.7% of the time, compared to 17.9% when the grader has been trained on answers to the same question. The gaming vulnerability shows a parallel pattern: ASR rises from 11.5% to 18.8%, meaning adversarial keyword stuffing and fluent wrong extensions are 64% more effective on novel questions.

Sensitivity detection remains low under both protocols (SSR ≈ 0.13), suggesting that the HybridGrader's inability to detect meaning-altering perturbations is a structural limitation of feature-based scoring rather than a distributional shift effect — it misses negations, concept deletions, and contradictions regardless of whether it has seen the question before.

These findings demonstrate that within-question evaluations (Protocol B) substantially overestimate the operational robustness of trained ASAG systems. The robustness drop — particularly the +15.8 percentage point increase in IVR_flip and the +7.4 percentage point increase in ASR — quantifies the extent of this overestimation. Standard ASAG benchmarks, which typically report within-question performance, therefore provide an optimistic picture of how a deployed grader will behave on questions it has not been trained on.

### 5.2  Cross-Paradigm Comparison: Trained ML vs. Zero-Shot LLM

Because the zero-shot LLM grader receives an identical prompt regardless of the data split (see Section 3.5), we report its absolute robustness metrics and compare them against the HybridGrader's Protocol A results — the most demanding evaluation condition for the trained baseline. Table 2 summarises the comparison.

**Table 2. Cross-paradigm robustness comparison (HybridGrader at Protocol A; LLM zero-shot, single-run).**

| Metric | HybridGrader (A) | GPT-5.4 mini L0 | GPT-5.4 mini L1 |
|---|---|---|---|
| IVR_flip (↓) | 0.337 | 0.243 | **0.134** |
| IVR_absdelta (↓) | 0.242 | 0.126 | **0.071** |
| SSR_directional (↑) | 0.140 | 0.420 | **0.461** |
| ASR_thresholded (↓) | **0.118**\* | 0.067 | 0.118 |

\* HybridGrader Protocol A ASR is 0.188; the value 0.118 in the table is L1's ASR, shown here for comparison. The HybridGrader still has the highest ASR overall (0.188).

**Finding 1: LLM graders are substantially more robust to surface-level variation.** GPT-5.4 mini Level 0 achieves IVR_flip of 0.243 versus 0.337 for the HybridGrader under Protocol A — a 28% relative reduction in invariance violations. With the reference answer available (Level 1), invariance violations fall further to 0.134, a 45% relative reduction over Level 0 and a 60% reduction over the HybridGrader baseline. The reference answer acts as a semantic anchor: surface variations that did not change meaning are recognised as such because the model has an explicit target to compare against.

**Finding 2: LLM graders detect meaning-altering perturbations far more effectively.** SSR_directional of 0.420 (Level 0) and 0.461 (Level 1) versus 0.140 for the HybridGrader represents an approximately threefold improvement. The HybridGrader misses 86% of negation insertions, concept deletions, and semantic contradictions; the LLM at Level 1 misses 54%. While neither achieves ceiling performance, the gap demonstrates that language understanding — rather than pattern matching on surface features — enables substantially better sensitivity detection. Adding the reference answer provides only a modest additional gain (+4 percentage points), suggesting that most of the LLM's sensitivity advantage stems from semantic processing rather than from access to a comparison target.

**Finding 3: Reference-answer availability introduces a non-obvious gaming trade-off.** The most surprising result is that providing the reference answer (Level 1) almost doubles gaming susceptibility relative to Level 0 (ASR 0.118 vs 0.067). This is a 76% relative increase in vulnerability to adversarial manipulation. The mechanism is intuitive in retrospect: the prompt instructs the model to compare the student answer against the reference. When the gaming perturbation injects keywords drawn from the reference answer into a wrong response, the model finds those keywords during the comparison and treats them as evidence of partial understanding. The reference answer thus inadvertently functions as a checklist that an adversarial student can copy from. Level 0, lacking this anchor, must judge the answer on its overall coherence and is correspondingly harder to game with surface-level keyword injection.

**Finding 4: Multi-metric evaluation reveals trade-offs invisible to any single metric.** Looking at any one metric in isolation produces a misleading picture. On invariance alone, Level 1 looks unambiguously better than Level 0. On sensitivity alone, both look comparable. On gaming alone, Level 0 is dramatically better. The full picture only emerges when all three dimensions are considered jointly: adding reference-answer information improves two validity dimensions while degrading a third. A practitioner choosing between L0 and L1 on the basis of accuracy or invariance alone would have no way of seeing the gaming cost they are incurring.

The same point applies to the trained baseline. If robustness were assessed using invariance metrics alone, the HybridGrader would appear reasonably robust under Protocol B (IVR_flip = 0.179). However, SSR_directional = 0.120 reveals that this apparent stability partly reflects indiscrimination: the grader assigns similar scores to original and perturbed answers not because it is robust, but because it is insensitive to meaning changes. The combination of low IVR and low SSR signals a grader that rarely changes its mind — even when it should. This pattern is only visible through multi-metric evaluation grounded in distinct validity threats.

### 5.3  Score Distribution Effects

To rule out the possibility that the LLM's lower IVR is an artefact of score compression rather than genuine robustness, we examined the LLM's label distribution. At Level 0, GPT-5.4 mini exhibits a conservative scoring pattern: 54.3% of answers receive the partially_correct_incomplete label (score 0.5), compared to 23.1% in the gold distribution. This compression toward the midpoint mechanically reduces IVR, since scores at 0.5 have less room to flip to a different value. At Level 1, the distribution becomes substantially more discriminative — closer to the gold distribution — yet IVR_flip continues to fall (0.243 → 0.134). This rules out the score-compression explanation: the LLM's invariance robustness reflects genuine semantic stability, not statistical artefact.

---

## 6  Discussion

### 6.1  The Overestimation Problem

The most consequential methodological finding of this study is that within-question evaluations overestimate the robustness of trained ASAG graders. The HybridGrader's IVR_flip nearly doubles when moving from Protocol B to Protocol A, and its gaming susceptibility rises by 64%. These are not marginal effects: a deployment decision based on Protocol B numbers would systematically underestimate how much grading inconsistency real students will encounter on novel questions, and how effective gaming attempts will be in practice.

This has direct implications for ASAG benchmarking practice. Reporting only within-question metrics — as is common in the literature — provides an optimistic picture that may not survive deployment. We recommend that any published ASAG evaluation include cross-question results alongside in-distribution ones, and that the difference between the two be reported explicitly as a robustness drop.

### 6.2  Why LLMs Are More Robust

The LLM grader's advantage on invariance and sensitivity dimensions is consistent with the explanation that semantic processing generalises across surface variations in ways that feature-based scoring cannot. The HybridGrader's fragility appears to stem from reliance on surface features (lexical overlap, embeddings of specific tokens) that change when surface form changes, even when meaning is preserved. The LLM, by contrast, processes the answer as language and is comparatively insensitive to whether "bulb" was replaced by "lamp" or "current" by a misspelling.

This is also why the LLM is dramatically better at detecting meaning-altering changes. A negation, a concept deletion, or an antonym substitution changes meaning while leaving most surface features intact. A feature-based scorer that has learned "answers containing these keywords are correct" will continue to score the perturbed answer as correct. A semantic processor recognises that the meaning has shifted.

### 6.3  The Reference-Answer Trade-Off

The most pedagogically interesting finding is the reference-answer trade-off documented in Section 5.2. Adding the reference answer to the LLM prompt is the kind of intervention any practitioner would expect to improve grading: more information should yield better judgement. And it does — for invariance and sensitivity. But for gaming, the same intervention almost doubles vulnerability.

The mechanism deserves emphasis because it generalises beyond our specific prompt. When the model is instructed to compare the student answer against a reference, the reference becomes the basis for the comparison. Any token that overlaps with the reference is evidence of correctness in the model's reasoning. An adversarial student who knows or can guess what the reference looks like — and in many real settings the rubric or reference is publicly available — can game this comparison directly.

We do not claim that this trade-off is unfixable. Prompt engineering, chain-of-thought instructions that require the model to assess internal coherence before keyword overlap, or few-shot examples demonstrating gaming attempts could plausibly mitigate it. The point is rather that the trade-off exists at all, that it is invisible if one measures only invariance or only accuracy, and that perturbation-first multi-dimensional evaluation is what surfaces it. The framework's contribution is detecting such trade-offs before deployment, regardless of which prompting strategy is ultimately chosen.

### 6.4  Practitioner Implications

For institutions considering ASAG deployment, three concrete recommendations follow from these findings.

First, do not rely on within-question accuracy or QWK as the sole quality indicator. Run a perturbation evaluation across at least one invariance, one sensitivity, and one gaming generator before deployment. The cost is modest — perturbation generation is rule-based and grading is the same operation as live use — and the diagnostic value is high.

Second, when comparing prompting strategies for an LLM grader (e.g., with vs. without reference answer; zero-shot vs. few-shot), measure all three validity dimensions, not just one. A change that improves accuracy may simultaneously increase gaming exposure, as our Level 0 vs Level 1 comparison demonstrates.

Third, treat cross-question evaluation as the realistic deployment scenario for trained graders. Within-question performance describes the best case; cross-question performance describes what students will actually experience. More broadly, robustness sits alongside fairness as a precondition for the responsible deployment of automated scoring in education (Loukina et al., 2019): a grader that is unstable under meaning-preserving variation is also, by construction, a grader whose scores are unevenly distributed across superficially different but substantively equivalent answers.

### 6.5  Limitations

Several limitations bound the generality of these findings. We evaluate on a single dataset (Beetle) covering one science domain. The Beetle corpus does not include structured per-question rubrics, so we use Level 0 vs. Level 1 prompting as a contrastive proxy for the effect of additional grading information; structured rubrics may behave differently and remain future work. We test a single LLM model (GPT-5.4 mini) at the time of writing; results for the frontier GPT-5.4 model and for Gemini 2.5 Flash, which are part of the planned experimental design, will allow analysis of model capability and cross-vendor consistency. Perturbations are rule-based; LLM-generated paraphrases might surface additional vulnerabilities. Finally, we do not include a human validation study of perturbation quality in this version of the paper; a sample-based annotation study with inter-annotator agreement is planned for the journal extension.

---

## 7  Conclusions

We have presented a perturbation-first evaluation framework for ASAG that quantifies robustness along three validity dimensions drawn from Messick's taxonomy. The framework comprises seven rule-based perturbation generators, two-gate quality validation, four metrics that compare the grader against itself, and a dual-protocol design that quantifies how trained graders degrade under cross-question generalisation.

Applied to the SemEval 2013 Beetle corpus, the framework yields three findings of practical and theoretical interest. First, a trained ML baseline exhibits a substantial robustness drop under cross-question evaluation (+15.8 percentage points on IVR_flip; +7.4 on ASR), demonstrating that standard within-question benchmarks systematically overestimate operational reliability. Second, a zero-shot LLM grader is markedly more robust on invariance and sensitivity dimensions and substantially less vulnerable to gaming, supporting the view that semantic processing generalises across surface variations in ways feature-based scoring cannot. Third, providing the LLM with a reference answer trades a 45% reduction in invariance violations for a 76% increase in gaming susceptibility — a non-obvious trade-off invisible to any single metric, surfaced by the multi-dimensional framework.

These results support a broader argument: that robustness should be evaluated alongside accuracy as a first-class quality dimension for any ASAG system intended for high-stakes use, and that the evaluation should be multi-dimensional and grounded in established validity theory. The framework is open-source and designed to be applied to any prompting strategy or grader architecture, so that practitioners can detect trade-offs in their own deployment context before students encounter them.

---

## References

Alzantot, M., Sharma, Y., Elgohary, A., Ho, B.-J., Srivastava, M. and Chang, K.-W. (2018) 'Generating natural language adversarial examples', in *Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP 2018)*. Brussels: Association for Computational Linguistics, pp. 2890–2896.

Belinkov, Y. and Bisk, Y. (2018) 'Synthetic and natural noise both break neural machine translation', in *Proceedings of the 6th International Conference on Learning Representations (ICLR 2018)*.

Burrows, S., Gurevych, I. and Stein, B. (2015) 'The eras and trends of automatic short answer grading', *International Journal of Artificial Intelligence in Education*, 25(1), pp. 60–117.

Condor, A., Litster, M. and Pardos, Z. (2021) 'Automatic short answer grading with SBERT on out-of-sample questions', in *Proceedings of the 14th International Conference on Educational Data Mining (EDM 2021)*. International Educational Data Mining Society, pp. 376–382.

Deane, P. (2013) 'On the relation between automated essay scoring and modern views of the writing construct', *Assessing Writing*, 18(1), pp. 7–24.

Ding, Y., Riordan, B., Horbach, A., Cahill, A. and Zesch, T. (2020) 'Don't take "nswvtnvakgxpm" for an answer — The surprising vulnerability of automatic content scoring systems to adversarial input', in *Proceedings of the 28th International Conference on Computational Linguistics (COLING 2020)*. Barcelona, pp. 882–892.

Dorsey, D. and Michaels, H. (2022) 'Validity arguments meet artificial intelligence in innovative educational assessment', *Journal of Educational Measurement*, 59(3), pp. 270–287.

Dzikovska, M., Nielsen, R., Brew, C., Leacock, C., Giampiccolo, D., Bentivogli, L., Clark, P., Dagan, I. and Dang, H.T. (2013) 'SemEval-2013 Task 7: The joint student response analysis and 8th recognizing textual entailment challenge', in *Proceedings of the 7th International Workshop on Semantic Evaluation (SemEval 2013)*. Association for Computational Linguistics, pp. 263–274.

Ebrahimi, J., Rao, A., Lowd, D. and Dou, D. (2018) 'HotFlip: White-box adversarial examples for text classification', in *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (ACL 2018)*. Melbourne, pp. 31–36.

Ferrara, S. and Qunbar, R. (2022) 'Validity arguments for AI-based automated scores: essay scoring as an illustration', *Journal of Educational Measurement*, 59(3), pp. 288–313.

Filighera, A., Ochs, S., Steuer, T. and Tregel, T. (2024) 'Cheating automatic short answer grading with the adversarial usage of adjectives and adverbs', *International Journal of Artificial Intelligence in Education*, 34(2), pp. 616–646.

Heilman, M. and Madnani, N. (2015) 'The impact of training data on automated short answer scoring performance', in *Proceedings of the 10th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2015)*. Denver: Association for Computational Linguistics, pp. 81–85.

Jia, R. and Liang, P. (2017) 'Adversarial examples for evaluating reading comprehension systems', in *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP 2017)*. Copenhagen, pp. 2021–2031.

Jin, D., Jin, Z., Zhou, J.T. and Szolovits, P. (2020) 'Is BERT really robust? A strong baseline for natural language attack on text classification and entailment', in *Proceedings of the Thirty-Fourth AAAI Conference on Artificial Intelligence (AAAI 2020)*. Palo Alto: AAAI Press, pp. 8018–8025.

Kane, M.T. (2006) 'Validation', in Brennan, R.L. (ed.) *Educational Measurement*. 4th edn. Westport, CT: American Council on Education/Praeger, pp. 17–64.

Kumar, Y., Aggarwal, S., Mahata, D., Shah, R.R., Kumaraguru, P. and Zimmermann, R. (2020) 'Calling out bluff: Attacking the robustness of automatic scoring systems with simple adversarial testing', *arXiv preprint* arXiv:2007.06796.

Latif, E. and Zhai, X. (2024) 'Fine-tuning ChatGPT for automatic scoring', *Computers and Education: Artificial Intelligence*, 6, p. 100210.

Loukina, A., Madnani, N. and Cahill, A. (2019) 'The many dimensions of algorithmic fairness in educational applications', in *Proceedings of the 14th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2019)*. Florence: Association for Computational Linguistics, pp. 1–11.

Messick, S. (1989) 'Validity', in Linn, R.L. (ed.) *Educational Measurement*. 3rd edn. Washington, DC: American Council on Education/Macmillan, pp. 13–103.

Mizumoto, A. and Eguchi, M. (2023) 'Exploring the potential of using an AI language model for automated essay scoring', *Research Methods in Applied Linguistics*, 2(2), p. 100050.

Mohler, M., Bunescu, R. and Mihalcea, R. (2011) 'Learning to grade short answer questions using semantic similarity measures and dependency graph alignments', in *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics (ACL 2011)*. Portland, pp. 752–762.

Morris, J.X., Lifland, E., Yoo, J.Y., Grigsby, J., Jin, D. and Qi, Y. (2020) 'TextAttack: A framework for adversarial attacks, data augmentation, and adversarial training in NLP', in *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations (EMNLP 2020)*. Association for Computational Linguistics, pp. 119–126.

Naismith, B., Mulcaire, P. and Burstein, J. (2023) 'Automated evaluation of written discourse coherence using GPT-4', in *Proceedings of the 18th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2023)*. Toronto, pp. 394–403.

Reimers, N. and Gurevych, I. (2019) 'Sentence-BERT: Sentence embeddings using Siamese BERT-networks', in *Proceedings of EMNLP-IJCNLP 2019*. Hong Kong: Association for Computational Linguistics, pp. 3982–3992.

Ribeiro, M.T., Wu, T., Guestrin, C. and Singh, S. (2020) 'Beyond accuracy: Behavioral testing of NLP models with CheckList', in *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*. Association for Computational Linguistics, pp. 4902–4912.

Riordan, B., Horbach, A., Cahill, A., Zesch, T. and Lee, C.M. (2017) 'Investigating neural architectures for short answer scoring', in *Proceedings of the 12th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2017)*. Copenhagen: Association for Computational Linguistics, pp. 217–227.

Shermis, M.D. (2022) 'Anchoring validity evidence for automated essay scoring', *Journal of Educational Measurement*, 59(3), pp. 314–334.

Sung, C., Dhamecha, T.I., Saha, S., Ma, T., Reddy, V. and Arora, R. (2019) 'Improving short answer grading using transformer-based pre-training', in *Proceedings of the 20th International Conference on Artificial Intelligence in Education (AIED 2019)*. Lecture Notes in Computer Science, vol. 11625. Cham: Springer, pp. 491–502.

Wang, S., Liu, W., Zhang, Y., Zheng, X. and Gao, S. (2022) 'Measure and improve robustness in NLP models: A survey', in *Proceedings of NAACL 2022*. Seattle: Association for Computational Linguistics, pp. 4569–4588.

Williamson, D.M., Xi, X. and Breyer, F.J. (2012) 'A framework for evaluation and use of automated scoring', *Educational Measurement: Issues and Practice*, 31(1), pp. 2–13.
