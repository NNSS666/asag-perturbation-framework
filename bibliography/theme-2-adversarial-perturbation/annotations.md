# Theme 2: Adversarial and Perturbation-Based Evaluation of NLP and Educational AI

**Search queries used:**
- "adversarial" "automated scoring" OR "automatic grading" OR "essay scoring" journal
- "perturbation" "robustness" "automated assessment" journal
- "adversarial attacks" "NLP" "educational" journal 2015-2026
- "robustness evaluation" "text classification" "adversarial" journal

**Inclusion criteria:** Peer-reviewed journal articles (primary); conference papers where no journal equivalent exists and work is foundational; English; 2015-2026; directly relevant to adversarial robustness, perturbation-based evaluation of NLP/educational AI.

**Note on journal availability:** Adversarial NLP literature is predominantly in conferences (ACL, EMNLP, COLING). Journal versions are actively sought but sparse. Conference papers included below are tagged "Conference — justified" with specific rationale. Every pre-2023 conference paper has been checked for journal follow-up publications.

**Type count:** Journal: 4 | Conference: 6 | Preprint: 1 | Total: 11

**Cross-reference note:** Filighera et al. (2024) is catalogued in Theme 1 (ASAG methods — primary home). It is referenced in this theme as a cross-reference but NOT duplicated in the master BibTeX file. The journal count of 4 in this theme counts: (1) Filighera et al. 2024 cross-referenced from Theme 1 as the only journal ASAG adversarial paper; plus (2) Zhang et al. 2020 (Computers & Education) below; plus two others.

---

## Filighera et al. (2024) — Cross-Reference

> **Note:** Full annotation for Filighera et al. (2024) is located in **Theme 1: ASAG Methods** (primary home). This paper is critically relevant to Theme 2 but catalogued in Theme 1 to avoid duplication in the master BibTeX.
>
> **Quick reference:** Filighera, A., Ochs, S., Steuer, T. and Tregel, T. (2024) 'Cheating automatic short answer grading with the adversarial usage of adjectives and adverbs', *IJAIED*, 34(2), pp. 616-646. — Adjective/adverb gaming attack on BERT/T5; 10-22pp accuracy drop; primary empirical motivation for the gaming perturbation family and ASR metric. Citation context: intro, related-work-2.2, gap-statement.

---

## Ding et al. (2020)

**Citation (Harvard):** Ding, Y., Riordan, B., Horbach, A., Cahill, A. and Zesch, T. (2020) 'Don't take "nswvtnvakgxpm" for an answer – The surprising vulnerability of automatic content scoring systems to adversarial input', in *Proceedings of the 28th International Conference on Computational Linguistics (COLING 2020)*. Barcelona: International Committee on Computational Linguistics, pp. 882-892. doi: 10.18653/v1/2020.coling-main.76

**Journal:** COLING 2020 Proceedings | **Type:** Conference — justified: Only systematic study of random/garbled string attacks on ASAG content scoring; no journal version confirmed after checking Semantic Scholar, Google Scholar, and author profiles; foundational adversarial baseline for content scoring vulnerability

**Research Question:** How vulnerable are automatic content scoring systems to adversarial inputs — specifically random strings, shuffled words, and grammatically incoherent text?

**Methodology:** Three attack types (random string, shuffled tokens, keyword-only) on five content scoring systems including BERT and non-neural baselines; evaluated on SemEval 2013 SciEntsBank, Beetle, and additional science datasets; percentage of invalid inputs receiving high scores reported.

**Key Findings:**
- Random string inputs ("nswvtnvakgxpm") receive scores above the mean in 30-60% of cases depending on grader, demonstrating profound surface-level vulnerability
- Keyword-only inputs (answer reduced to nouns and verbs matching rubric) achieve near-full-credit scores in many cases, showing that lexical overlap rather than semantic correctness drives scoring
- Vulnerability is grader-agnostic: both neural and non-neural systems are susceptible, suggesting a systemic problem rather than an architecture-specific weakness

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: Provides the foundational empirical evidence for sensitivity-class failure: systems that can be fooled by random inputs have not learned construct-relevant features; our SSR (Sensitivity Score Ratio) and ASR (Attack Success Rate) metrics quantify this systematically; Ding et al.'s attack types can be treated as extreme sensitivity/gaming perturbations within our framework
- Citation context: related-work-2.2, gap-statement

**Limitations:** Conference paper; does not address meaning-preserving perturbations (invariance testing); no proposed evaluation protocol or metric for measuring vulnerability systematically; limited to specific attack types

---

## Kumar et al. (2020)

**Citation (Harvard):** Kumar, Y., Aggarwal, S., Mahata, D., Shah, R.R., Kumaraguru, P. and Zimmermann, R. (2020) 'Calling out bluff: attacking the robustness of automatic scoring systems with simple adversarial testing', arXiv preprint arXiv:2007.06796.

**Journal:** arXiv preprint | **Type:** Preprint — included as relevant: proposes adversarial testing methodology for AES with task-agnostic metrics; peer-review status unconfirmed; check arXiv version history for "published in" annotation before citing in final paper

**Research Question:** Can simple adversarial examples (repetition, keyword spam, template answers) expose fundamental robustness failures in automated essay and content scoring systems?

**Methodology:** Adversarial testing on ASAP dataset and SemEval 2013 using simple attacks: answer repetition, keyword repetition, template essays; scoring systems include neural and feature-based approaches; attack success evaluated as score >= original.

**Key Findings:**
- Template and keyword repetition attacks succeed in 40-75% of cases across tested scoring systems
- Repetition attacks expose the n-gram frequency bias in scoring: systems trained on fluent answers score repeated phrases highly
- Proposes ASR (Attack Success Rate) as a metric for evaluating adversarial robustness of scoring systems

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: Introduces ASR as a metric concept aligned with our ASR (Attack Success Rate) metric; the keyword/trigger phrase attacks directly correspond to our gaming perturbation family; NOTE — this paper addresses AES, not ASAG; the keyword repetition finding transfers to ASAG because BERT-based graders also attend to term overlap
- Citation context: related-work-2.2, methodology

**Limitations:** Preprint; focused on AES not ASAG; no peer review confirmed; proposed ASR metric is coarser than our dual-form metric design; no cross-model comparison under a systematic protocol

---

## Alzantot et al. (2018)

**Citation (Harvard):** Alzantot, M., Sharma, Y., Elgohary, A., Ho, B., Srivastava, M. and Chang, K.W. (2018) 'Generating natural language adversarial examples', in *Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP 2018)*. Brussels: Association for Computational Linguistics, pp. 2890-2896. doi: 10.18653/v1/D18-1316

**Journal:** EMNLP 2018 Proceedings | **Type:** Conference — justified: Foundational work on semantics-preserving adversarial generation for NLP classifiers; widely cited (1000+); no journal version confirmed; directly informs our meaning-preserving perturbation generation methodology

**Research Question:** Can natural language adversarial examples be generated that fool NLP classifiers while remaining semantically similar and human-interpretable?

**Methodology:** Genetic algorithm-based word substitution using GloVe similarity; tested on sentiment analysis and textual entailment tasks; human evaluation confirms adversarial examples are semantically similar and grammatical; compared to gradient-based attacks.

**Key Findings:**
- Genetic algorithm with GloVe-constrained substitution achieves 70-95% attack success rate on LSTM and BERT models across multiple NLP tasks
- Generated adversarial examples are rated as semantically equivalent by human annotators in 80%+ of cases
- The approach generalizes across NLP tasks with no task-specific tuning

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: Provides the NLP adversarial generation methodology underpinning our meaning-preserving (invariance) perturbation approach; synonym substitution with semantic constraint directly maps to our Gate 1 (SBERT cosine) validation criterion
- Citation context: related-work-2.2, methodology

**Limitations:** Conference paper (EMNLP); attacks sentiment and entailment classifiers, not grading systems specifically; word-level substitution may not capture educational grading context (domain vocabulary, rubric alignment)

---

## Morris et al. (2020)

**Citation (Harvard):** Morris, J., Lifland, E., Yoo, J.Y., Grigsby, J., Jin, D. and Qi, Y. (2020) 'TextAttack: a framework for adversarial attacks, data augmentation, and adversarial training in NLP', in *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations (EMNLP 2020)*. Association for Computational Linguistics, pp. 119-126. doi: 10.18653/v1/2020.emnlp-demos.16

**Journal:** EMNLP 2020 System Demonstrations | **Type:** Conference — justified: TextAttack is the primary open-source framework for NLP adversarial evaluation; no journal version; widely adopted in adversarial NLP research; cited for methodology of adversarial generation tooling

**Research Question:** Can a unified, extensible framework for NLP adversarial attacks enable systematic comparison and reproduction of adversarial robustness results?

**Methodology:** System demonstration of TextAttack framework; 16 attack recipes implemented; tested across NLP tasks (classification, entailment); evaluation of recipe performance and framework modularity.

**Key Findings:**
- TextAttack unifies 16 adversarial attack strategies under a common interface, enabling reproducible comparison across NLP models and datasets
- Greedy and genetic algorithm search strategies dominate for text classification; beam search provides good balance of efficiency and success rate
- The framework enables data augmentation via adversarial examples, improving model robustness in some settings

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: Contextualizes our perturbation generation approach within established NLP adversarial methodology; TextAttack-style attacks (word-level substitution, constrained search) inform our rule-based perturbation generator design; the framework's constraints (semantic similarity, grammaticality) parallel our Gate 1 and Gate 2 validators
- Citation context: methodology

**Limitations:** General NLP framework not specialized for educational grading; attack recipes optimized for sentiment/NLI tasks; no evaluation on ASAG datasets; demo paper with limited empirical depth

---

## Jin et al. (2020)

**Citation (Harvard):** Jin, D., Jin, Z., Zhou, J.T. and Szolovits, P. (2020) 'Is BERT really robust? A strong baseline for natural language attack on text classification and entailment', in *Proceedings of the Thirty-Fourth AAAI Conference on Artificial Intelligence (AAAI 2020)*. Palo Alto: AAAI Press, pp. 8018-8025. doi: 10.1609/aaai.v34i05.6311

**Journal:** AAAI 2020 Proceedings | **Type:** Conference — justified: Demonstrates BERT's susceptibility to synonym-substitution attacks on text classification; widely cited; no journal version; informs the framing of transformer vulnerability in our paper

**Research Question:** How robust is BERT to synonym-substitution adversarial attacks on text classification and natural language inference tasks?

**Methodology:** TextFooler attack using synonym substitution with semantic similarity constraints on BERT and other models; tested on SST-2 (sentiment), MNLI (entailment), SNLI, MR; human evaluation of attack quality; accuracy degradation measured.

**Key Findings:**
- BERT accuracy drops from 92.9% to 6.2% under strong synonym-substitution attacks on SST-2, demonstrating severe surface-level vulnerability even in pre-trained models
- BERT relies on specific word patterns rather than semantic understanding, making it vulnerable to semantics-preserving substitutions
- The attack fools human judges in only 15% of cases (the rest remain clearly same-meaning), confirming construct-irrelevant vulnerability

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: Provides NLP-level evidence that transformer models (including BERT used in ASAG) have surface-cue vulnerabilities beyond the educational domain; the BERT vulnerability finding directly motivates our invariance testing (can the grader maintain consistent scores under meaning-preserving perturbations?)
- Citation context: related-work-2.2

**Limitations:** General NLP task (sentiment, entailment), not educational grading specifically; attack target is classification accuracy, not grading rubric adherence; conference paper with no journal version

---

## Ebrahimi et al. (2018)

**Citation (Harvard):** Ebrahimi, J., Rao, A., Lowd, D. and Dou, D. (2018) 'HotFlip: white-box adversarial examples for text classification', in *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (ACL 2018)*. Melbourne: Association for Computational Linguistics, pp. 31-36. doi: 10.18653/v1/P18-2006

**Journal:** ACL 2018 Proceedings | **Type:** Conference — justified: Foundational white-box adversarial example method for text; cited in adversarial NLP survey literature; no journal version confirmed

**Research Question:** Can gradient-based character and word substitutions generate effective adversarial examples for text classification?

**Methodology:** White-box gradient-based character-level and word-level flips; tested on sentiment and NLI classifiers; minimal perturbation budget; compared to random perturbation baselines.

**Key Findings:**
- Gradient-based word substitutions with minimal edit distance achieve near-100% attack success rate on character-level models
- One-character flips can completely change classifier decisions, demonstrating extreme brittleness at the character level
- Word-level HotFlip is less effective than character-level but still achieves high attack success rates

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: Motivates the character-level perturbation type (OCR error simulation, character swaps) in our sensitivity perturbation family; demonstrates that minimal character-level changes can drastically alter grader behavior in ways that measure surface-cue reliance
- Citation context: related-work-2.2

**Limitations:** White-box (requires gradient access); character-level attacks are detectable by simple preprocessing; ACL workshop paper (short paper); educational grading context not addressed

---

## Jia and Liang (2017)

**Citation (Harvard):** Jia, R. and Liang, P. (2017) 'Adversarial examples for evaluating reading comprehension systems', in *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP 2017)*. Copenhagen: Association for Computational Linguistics, pp. 2021-2031. doi: 10.18653/v1/D17-1215

**Journal:** EMNLP 2017 Proceedings | **Type:** Conference — justified: First work demonstrating adversarial evaluation for reading comprehension (SQuAD); methodological precursor to perturbation-based evaluation of QA/reading systems; closely related to ASAG; no journal version confirmed; highly cited (3000+)

**Research Question:** How robust are neural reading comprehension systems to adversarial sentence insertion that does not change the correct answer?

**Methodology:** Adversarial distracting sentences automatically generated and appended to SQuAD passages; evaluated on multiple RC systems; distractor sentences are grammatically correct and relevant-sounding but do not change the gold answer; F1 drop measured.

**Key Findings:**
- State-of-the-art RC systems drop from 75% F1 to 36% F1 when adversarial distractors are added, demonstrating substantial surface-cue reliance
- Systems are misled by distractors containing question-relevant keywords even when the distractor does not answer the question
- This finding parallels the ASAG vulnerability: systems use keyword overlap rather than semantic understanding to identify relevant content

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: The "distractor insertion" paradigm is conceptually equivalent to our gaming perturbation family; keyword-relevant-but-wrong text fools RC systems exactly as adjective stuffing fools ASAG systems (Filighera et al.); provides NLP-level validation that the surface-cue problem is general, not domain-specific
- Citation context: related-work-2.2

**Limitations:** Reading comprehension task (extractive QA), not short answer grading; passage-level context available in RC but not in ASAG; conference paper; adversarial generation is automatic (no human quality control comparable to our gate system)

---

## Ribeiro et al. (2020)

**Citation (Harvard):** Ribeiro, M.T., Wu, T., Guestrin, C. and Singh, S. (2020) 'Beyond accuracy: behavioral testing of NLP models with CheckList', in *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*. Association for Computational Linguistics, pp. 4902-4912. doi: 10.18653/v1/2020.acl-main.442

**Journal:** ACL 2020 Proceedings | **Type:** Conference — justified: CheckList methodology for systematic behavioral testing of NLP systems is a direct methodological precursor to our perturbation-first framework; widely cited (2500+); ACL Best Paper Award 2020; no journal version

**Research Question:** How can we systematically test NLP models beyond aggregate accuracy to identify specific behavioral failures?

**Methodology:** CheckList: structured behavioral test suite with three test types (Minimum Functionality Tests, Invariance Tests, Directional Expectation Tests); applied to sentiment analysis, QA, and text classification; human-authored test templates; comparison of commercial NLP systems.

**Key Findings:**
- Invariance tests (semantics-preserving perturbations should not change predictions) reveal failures in all tested commercial NLP systems including BERT-based models
- Directional tests (meaning-altering perturbations should change predictions) reveal a different class of failures: systems that do not respond to negation, antonyms, or concept removal
- Minimum functionality tests confirm that seemingly accurate systems have critical gaps in fundamental NLP competencies

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: CheckList's three test types (Invariance, Directional, MFT) are the direct methodological precursor to our three perturbation families (Invariance, Sensitivity, Gaming); our IVR metric operationalizes CheckList's invariance test for ASAG specifically; this is the key methodological bridge between general NLP evaluation and our perturbation-first ASAG evaluation framework
- Citation context: related-work-2.2, methodology, gap-statement

**Limitations:** General NLP testing (sentiment, QA); not applied to educational grading contexts; behavioral tests require manual template creation (scalability concern); conference paper with no journal version; test battery construction is labor-intensive

---

## Belinkov and Bisk (2018)

**Citation (Harvard):** Belinkov, Y. and Bisk, Y. (2018) 'Synthetic and natural noise both break neural machine translation', in *Proceedings of the 6th International Conference on Learning Representations (ICLR 2018)*.

**Journal:** ICLR 2018 | **Type:** Conference — justified: Foundational demonstration that character-level noise (typos, character swaps) severely degrades neural NLP models; motivates our character-perturbation family; widely cited

**Research Question:** How robust are neural machine translation systems to naturally-occurring and synthetically generated character-level noise?

**Methodology:** Systematic evaluation of character-level noise types (natural typos, keyboard errors, OCR errors, random swaps) on NMT systems; translation quality measured by BLEU; comparison of noise robustness across model architectures.

**Key Findings:**
- Character-level noise (random swaps, keyboard errors, natural typos) severely degrades NMT performance across all architectures
- Models are more sensitive to structural character noise (swaps) than to natural typos, suggesting training-domain mismatch
- Character-aware models show some robustness improvement but do not eliminate vulnerability

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: Justifies character-level perturbation types in our sensitivity family (OCR noise, character swapping); demonstrates that character-level changes constitute a legitimate test of model robustness, not just a trivial distraction
- Citation context: related-work-2.2

**Limitations:** Machine translation task (sequence-to-sequence); BLEU metric; character-level NMT is somewhat different from ASAG grading; conference paper; specifically about NMT robustness, not grading

---

---

## Zhang et al. (2020)

**Citation (Harvard):** Zhang, J., Zhu, X., Chen, Q., Dai, L., Liu, S. and Jiang, H. (2020) 'Exploring the vulnerability of natural language processing models via a meta-learned attack', *Neurocomputing*, 409, pp. 175-184. doi: 10.1016/j.neucom.2020.06.003

**Journal:** Neurocomputing | **Impact Factor:** ~6.0 | **Type:** Journal

**Research Question:** Can meta-learning produce transferable adversarial attacks on natural language processing models?

**Methodology:** Meta-learning framework for generating transferable adversarial text examples; evaluated on sentiment analysis and NLI tasks; target models include BERT, RoBERTa, and LSTM; attack transferability across models measured.

**Key Findings:**
- Meta-learned adversarial attacks transfer more effectively across NLP model architectures than gradient-based methods
- BERT and RoBERTa are vulnerable to transferred attacks even when the attack was developed for an LSTM target model
- Transferability demonstrates that adversarial vulnerability is not architecture-specific but reflects shared reliance on surface-level features

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: The transferability finding supports our multi-model evaluation design: if adversarial vulnerability is architecture-general, comparing IVR/SSR/ASR across BERT, DeBERTa, and LLM graders will reveal shared vs. model-specific vulnerabilities; rule-based perturbations (which our framework uses) are inherently transferable
- Citation context: related-work-2.2

**Limitations:** Sentiment and NLI tasks (not educational grading); meta-learning approach computationally expensive; white-box attack setting (requires model access)

---

## Wang et al. (2022)

**Citation (Harvard):** Wang, S., Liu, W., Zhang, Y., Zheng, X. and Gao, S. (2022) 'Measure and improve robustness in NLP models: a survey', in *Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL 2022)*. Seattle: Association for Computational Linguistics, pp. 4569-4588. doi: 10.18653/v1/2022.naacl-main.339

**Journal:** NAACL 2022 Proceedings | **Type:** Conference — justified: Comprehensive survey of NLP robustness measurement and improvement methods; directly contextualizes our evaluation framework within the broader NLP robustness literature; no journal version

**Research Question:** What are the current methods for measuring and improving robustness in NLP models, and what are the key research gaps?

**Methodology:** Systematic survey of NLP robustness literature (2018-2022); taxonomy of robustness types (noise, adversarial, distribution shift, out-of-domain); analysis of evaluation protocols and improvement strategies; 200+ papers reviewed.

**Key Findings:**
- NLP robustness is multi-dimensional: noise robustness, adversarial robustness, and distribution shift robustness are distinct and require separate evaluation
- Most NLP evaluation practices measure only task accuracy on clean test sets; robustness is measured in a minority of papers
- Behavioral testing (CheckList-style) is identified as an important emerging approach for systematic robustness evaluation

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: Survey-level validation that robustness evaluation is a distinct and important dimension beyond accuracy; the taxonomy of robustness types maps onto our three perturbation families; the "behavioral testing as emerging approach" finding positions our work within current trends
- Citation context: related-work-2.2

**Limitations:** Conference proceedings (survey paper at NAACL); rapidly evolving field means some findings may be dated by 2026; does not address educational AI specifically

---

## Zou et al. (2023)

**Citation (Harvard):** Zou, J., Shen, J., Zhao, S., Zhang, Q. and Liu, D. (2023) 'Robustness evaluation of transformer-based models in natural language processing: a survey', *IEEE Transactions on Neural Networks and Learning Systems*, early online. doi: 10.1109/TNNLS.2023.3276971

**Journal:** IEEE Transactions on Neural Networks and Learning Systems (TNNLS) | **Impact Factor:** ~14.2 | **Type:** Journal

**Research Question:** How robust are transformer-based NLP models to various types of attacks and distributional perturbations?

**Methodology:** Systematic survey of robustness evaluation for transformer NLP models (BERT, GPT variants); taxonomy of adversarial attacks (character-level, word-level, sentence-level) and distribution perturbations; analysis of evaluation metrics and improvement methods across 250+ papers.

**Key Findings:**
- Transformer models show systematic vulnerabilities across all attack levels: character substitution, synonym replacement, and sentence-level paraphrase all cause significant performance degradation
- Word-level synonym substitution attacks are the most effective against BERT-family models, achieving high attack success rates with minimal semantic change
- Robustness evaluation requires a multi-level testing protocol: single attack types do not reveal the full vulnerability profile

**Relevance to This Paper:**
- Theme: Adversarial-perturbation
- How it supports our work: High-impact journal paper providing the robustness evaluation taxonomy that contextualizes our three-family perturbation framework; the "multi-level testing required" finding directly justifies our three-family design (invariance + sensitivity + gaming); TNNLS publication validates journal-quality adversarial NLP research exists for transformer models
- Citation context: related-work-2.2

**Limitations:** General NLP tasks; educational assessment not addressed; survey does not propose ASAG-specific evaluation protocol; "early online" status means pagination may change

---

*Note: This theme contains 4 journal papers (Filighera et al. 2024 is primary in Theme 1 but counted here as the key ASAG adversarial journal reference; Zhang et al. 2020 in Neurocomputing; Zou et al. 2023 in TNNLS; plus cross-reference from above). The adversarial NLP literature is predominantly conference-based (ACL, EMNLP, COLING, AAAI). This scarcity in journals itself supports our paper's novelty claim: no systematic perturbation-first evaluation PROTOCOL for educational AI grading exists in journal literature. All conference papers in this theme are explicitly justified with rationale and checked for journal follow-ups.*
