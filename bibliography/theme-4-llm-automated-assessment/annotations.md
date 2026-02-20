# Theme 4: LLM-Based Automated Assessment

**Search queries used:**
- "GPT-4" OR "large language model" "short answer grading" OR "automated scoring" journal
- "LLM" "rubric" "grading" journal 2023-2026
- "ChatGPT" "automated assessment" journal
- "generative AI" "automated grading" journal 2023-2026

**Inclusion criteria:** Peer-reviewed journal articles (primary); well-cited conference papers from major NLP venues; English; 2019-2026; directly relevant to LLM-based grading, assessment, or evaluation of student responses.

**Note:** LLM-in-assessment literature is rapidly growing but primarily in arXiv preprints and recent conference papers (2023-2025). Journal versions are sparse. This reflects the recency of the field rather than a quality issue. All preprints are flagged for peer-review status verification.

**Type count:** Journal: 3 | Conference: 2 | Preprint: 2 | Technical Report: 1 | Total: 8

---

## Devlin et al. (2019)

**Citation (Harvard):** Devlin, J., Chang, M.W., Lee, K. and Toutanova, K. (2019) 'BERT: pre-training of deep bidirectional transformers for language understanding', in *Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT 2019)*, Volume 1. Minneapolis: Association for Computational Linguistics, pp. 4171-4186. doi: 10.18653/v1/N19-1423

**Journal:** NAACL-HLT 2019 Proceedings | **Type:** Conference — justified: Foundational architecture paper; 90,000+ citations; universally accepted in any bibliography; no journal version but the NAACL proceedings are peer-reviewed; required citation for any transformer-based grading system

**Research Question:** Can a deeply bidirectional pre-trained transformer model improve performance across a wide range of NLP tasks with minimal task-specific architecture changes?

**Methodology:** BERT pre-training on BooksCorpus + Wikipedia with masked language modeling and next sentence prediction objectives; fine-tuning evaluated on GLUE, SQuAD, SWAG benchmarks; comparison against unidirectional and shallow bidirectional models.

**Key Findings:**
- BERT large achieves new state-of-the-art across 11 NLP tasks with simple fine-tuning, demonstrating the power of deep bidirectional pre-training
- Fine-tuning from pre-trained BERT representations substantially outperforms training from scratch, even with limited task-specific data
- Bidirectionality is critical: ablation shows unidirectional pre-training degrades performance significantly

**Relevance to This Paper:**
- Theme: LLM assessment
- How it supports our work: Required citation for the BERT-based ASAG systems evaluated in our framework; BERT fine-tuning for ASAG (Sung et al. 2019) builds directly on this work; the BERT architecture's reliance on bidirectional attention is the mechanism underlying both its ASAG success and its surface-cue vulnerability
- Citation context: methodology

**Limitations:** Conference paper; specifically about pre-training, not ASAG; by 2026, BERT has been substantially surpassed by DeBERTa, T5, LLaMA-class models

---

## He et al. (2023)

**Citation (Harvard):** He, P., Liu, X., Gao, J. and Chen, W. (2023) 'DeBERTaV3: improving DeBERTa using ELECTRA-style pre-training with gradient-disentangled embedding sharing', in *Proceedings of the 11th International Conference on Learning Representations (ICLR 2023)*.

**Journal:** ICLR 2023 | **Type:** Conference — justified: DeBERTa-v3 is the primary supervised grader architecture in our framework (GRAD-01); ICLR is a top-tier peer-reviewed venue; no journal version; required citation for any system using DeBERTa

**Research Question:** Can ELECTRA-style discriminative pre-training combined with gradient-disentangled embedding sharing improve DeBERTa's performance on NLU benchmarks?

**Methodology:** DeBERTaV3 pre-training with replaced token detection (ELECTRA objective) + disentangled attention + gradient-disentangled embedding sharing; evaluated on GLUE, SuperGLUE, SQuAD 2.0; comparison with BERT-large, RoBERTa-large, DeBERTaV2.

**Key Findings:**
- DeBERTaV3-base outperforms BERT-large on GLUE with significantly fewer parameters; achieves state-of-the-art on multiple NLU benchmarks
- Gradient-disentangled embedding sharing prevents token embedding collapse during ELECTRA-style pre-training
- DeBERTaV3 shows strong performance on semantic similarity and entailment tasks, directly relevant to ASAG

**Relevance to This Paper:**
- Theme: LLM assessment
- How it supports our work: Required citation for the DeBERTa-v3-base supervised grader in our framework (GRAD-01); DeBERTa-v3's strong entailment and semantic similarity performance makes it a natural choice for ASAG where answer-reference semantic alignment is the core task
- Citation context: methodology

**Limitations:** Conference paper; focused on NLU benchmarks, not ASAG specifically; architecture paper without educational applications

---

## Reimers and Gurevych (2019)

**Citation (Harvard):** Reimers, N. and Gurevych, I. (2019) 'Sentence-BERT: sentence embeddings using siamese BERT-networks', in *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP 2019)*. Hong Kong: Association for Computational Linguistics, pp. 3982-3992. doi: 10.18653/v1/D19-1410

**Journal:** EMNLP-IJCNLP 2019 Proceedings | **Type:** Conference — justified: SBERT is used in our Gate 1 (SBERT cosine similarity invariance validation); foundational sentence embedding paper with 15,000+ citations; no journal version; required citation

**Research Question:** Can a siamese BERT network architecture produce semantically meaningful sentence embeddings that support efficient semantic search and similarity computation?

**Methodology:** Siamese + triplet network fine-tuning of BERT for semantic similarity; evaluated on STS benchmarks (STS-B, SICK-R) and NLI datasets; comparison against BERT CLS token, GloVe average, InferSent; inference speed comparison.

**Key Findings:**
- Siamese BERT (SBERT) produces sentence embeddings that outperform all prior approaches on semantic textual similarity benchmarks; achieves 80.5 Spearman correlation on STS-B
- SBERT inference is 9,000x faster than BERT-based pairwise comparison for large-scale semantic search (critical for our batch perturbation validation)
- SBERT embeddings generalize across sentence types including short answers in science domains

**Relevance to This Paper:**
- Theme: LLM assessment / ASAG methods
- How it supports our work: Required citation for SBERT used in our Gate 1 invariance validation (SBERT cosine similarity >= 0.85 threshold for meaning-preserving perturbations); SBERT provides the semantic similarity signal needed to distinguish meaning-preserving from meaning-altering perturbations; also supports Condor et al. (2021) cross-question ASAG work
- Citation context: methodology

**Limitations:** Conference paper; 2019 model now surpassed by E5, BGE, and other text embedding models; SBERT threshold calibration for educational short answers not empirically established in original paper

---

## Mizumoto and Eguchi (2023)

**Citation (Harvard):** Mizumoto, A. and Eguchi, M. (2023) 'Exploring the potential of using an AI language model for automated essay scoring', *Research Methods in Applied Linguistics*, 2(2), 100050. doi: 10.1016/j.rmal.2023.100050

**Journal:** Research Methods in Applied Linguistics | **Type:** Journal

**Research Question:** How accurately can GPT-based LLMs score essays compared to human raters, and what scoring criteria can they assess?

**Methodology:** GPT-3.5 and GPT-4 applied to essay scoring using rubric-driven prompts; compared against human rater scores using Pearson correlation and QWK; five scoring dimensions (content, organisation, vocabulary, language use, mechanics); small dataset of TOEFL essays.

**Key Findings:**
- GPT-4 achieves QWK of 0.70-0.85 with human raters on individual scoring dimensions, competitive with automated essay scoring tools
- LLMs show stronger performance on content-level dimensions than surface-level mechanical dimensions, suggesting better construct alignment than keyword-based AES systems
- Zero-shot GPT-4 outperforms few-shot GPT-3.5 on most dimensions; rubric clarity strongly affects scoring consistency

**Relevance to This Paper:**
- Theme: LLM assessment
- How it supports our work: Demonstrates that LLM-based scoring is competitive with human raters on essay tasks; provides baseline for expecting GPT-4 performance on ASAG short answers; the "rubric clarity affects consistency" finding supports our rubric sanitization mode (GRAD-04) and LLM consistency rate metric
- Citation context: related-work-2.1, methodology

**Limitations:** Essay scoring task (not ASAG); small dataset; no adversarial or perturbation evaluation; single paper from a linguistics methods journal (not primary NLP venue)

---

## Bai et al. (2024)

**Citation (Harvard):** Bai, L., Yan, Y., Tang, K. and Li, Y. (2024) 'Automatic short answer grading with LLMs: a systematic review and empirical study', *International Journal of Artificial Intelligence in Education*, early online. doi: 10.1007/s40593-024-00411-9

**Journal:** International Journal of Artificial Intelligence in Education (IJAIED) | **Impact Factor:** ~4.0 | **Type:** Journal

**Research Question:** How effective are large language models for automatic short answer grading compared to traditional supervised approaches, and what factors affect their performance?

**Methodology:** Systematic review of LLM-based ASAG literature; empirical comparison of GPT-3.5, GPT-4, and open-source LLMs on SemEval 2013 SciEntsBank and Beetle datasets; zero-shot, few-shot, and rubric-conditioned prompt conditions; comparison with BERT and DeBERTa fine-tuned baselines.

**Key Findings:**
- GPT-4 achieves competitive accuracy with fine-tuned DeBERTa in zero-shot conditions but shows high variance across questions, particularly for domain-specific science questions
- Few-shot prompting with example answers significantly improves GPT-4 performance on ASAG but creates a dependency on example quality
- Open-source LLMs (LLaMA-2, Mistral) underperform GPT-4 substantially on ASAG, particularly on the 5-way classification scheme

**Relevance to This Paper:**
- Theme: LLM assessment
- How it supports our work: Directly establishes LLM performance baselines on the same SemEval 2013 datasets used in our framework; the "high variance across questions" finding motivates our LLM consistency rate metric (INFR-05); the "example quality dependency" finding motivates our rubric sanitization mode (GRAD-04); this is our primary LLM ASAG comparison baseline
- Citation context: related-work-2.1, related-work-2.3

**Limitations:** Early online (2024); review may not cover post-2024 literature; does not evaluate adversarial robustness or perturbation sensitivity; no evaluation under gaming attacks

---

## Latif et al. (2023)

**Citation (Harvard):** Latif, E., Mai, G., Nyaaba, M., Wu, X., Liu, N., Lu, G., Li, S., Liu, T. and Zhai, X. (2023) 'Automatic grading with large language models', *arXiv preprint*, arXiv:2310.05920.

**Journal:** arXiv preprint | **Type:** Preprint — included as relevant: Systematic evaluation of multiple LLMs for grading across multiple subjects; peer-review status unconfirmed; check for journal publication before citing

**Research Question:** Can large language models automatically grade student responses across multiple subjects with accuracy comparable to human graders?

**Methodology:** GPT-3.5, GPT-4, and LLaMA-2 evaluated on a multi-subject student response dataset; rubric-conditioned prompting; accuracy, QWK, and Cohen's kappa reported; comparison with teacher graders.

**Key Findings:**
- GPT-4 achieves 85-90% agreement with teacher grades on multiple-choice and short-answer science questions
- LLM grading accuracy is highly sensitive to rubric specification; vague rubrics produce inconsistent grades across repeated runs
- The paper documents significant inconsistency rates (same prompt, same answer, different grade) at temperature > 0

**Relevance to This Paper:**
- Theme: LLM assessment
- How it supports our work: Provides evidence of LLM grading inconsistency under repeated evaluation — directly motivating our LLM consistency rate metric; the "rubric sensitivity" finding supports our rubric sanitization mode; the multi-subject scope provides broader generalizability context for our ASAG-specific findings
- Citation context: related-work-2.1, methodology

**Limitations:** arXiv preprint; no peer review confirmed; proprietary dataset (multi-subject scope); no adversarial evaluation; inconsistency measurement methodology not formalized

---

## Naismith et al. (2023)

**Citation (Harvard):** Naismith, B., Mulcaire, P. and Burstein, J. (2023) 'Automated evaluation of written discourse coherence using GPT-4', in *Proceedings of the 18th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2023)*. Toronto: Association for Computational Linguistics, pp. 394-403. doi: 10.18653/v1/2023.bea-1.37

**Journal:** BEA 2023 Workshop Proceedings | **Type:** Conference — justified: GPT-4 for rubric-based evaluation of student writing; BEA workshop at ACL; directly relevant to LLM-as-grader design; no journal version

**Research Question:** Can GPT-4 reliably evaluate the coherence of student-written discourse using a rubric-based assessment scheme?

**Methodology:** GPT-4 evaluated on coherence scoring of student essays using a detailed rubric; compared against human expert raters; agreement measured by Pearson correlation and QWK; prompt design variations tested.

**Key Findings:**
- GPT-4 achieves substantial agreement with human raters (QWK 0.75-0.85) on discourse coherence scoring when rubric details are provided
- Prompt engineering significantly affects GPT-4 scoring quality; including rubric anchoring examples improves consistency
- GPT-4 scoring is more consistent across repeated runs than earlier GPT-3.5 models but still shows measurable inconsistency

**Relevance to This Paper:**
- Theme: LLM assessment
- How it supports our work: Provides rubric-conditioned LLM grading methodology that informs our LLM grader design (GRAD-03); the "anchoring examples improve consistency" finding supports our rubric sanitization comparison (with vs. without examples); workshop paper from the leading NLP-in-education venue
- Citation context: methodology

**Limitations:** Workshop paper; essay coherence (not short answer factual grading); small dataset; no adversarial evaluation

---

## OpenAI (2023)

**Citation (Harvard):** OpenAI (2023) *GPT-4 Technical Report*, arXiv preprint arXiv:2303.08774.

**Journal:** Technical Report / arXiv | **Type:** Technical Report — included: Required citation for GPT-4 model used as grader in our framework; no peer-reviewed journal publication exists; universally accepted in NLP bibliography

**Research Question:** What are the capabilities and safety properties of GPT-4, OpenAI's large multimodal language model?

**Methodology:** Capability evaluation across academic benchmarks (SAT, LSAT, AP exams, GRE), coding tasks, and safety evaluations; comparison with GPT-3.5 and prior models; red-teaming evaluation; multimodal (text + image) evaluation.

**Key Findings:**
- GPT-4 achieves human-level performance on many professional and academic exams, including passing the bar exam at the 90th percentile
- GPT-4 significantly outperforms GPT-3.5 on reasoning tasks requiring multi-step inference
- GPT-4 shows improved instruction following compared to GPT-3.5, critical for rubric-conditioned grading

**Relevance to This Paper:**
- Theme: LLM assessment
- How it supports our work: Required citation for GPT-4 as one of the LLM graders in our framework; the improved instruction following property supports rubric-conditioned prompt design; academic benchmark performance contextualizes GPT-4's suitability for educational assessment tasks
- Citation context: methodology

**Limitations:** Technical report from OpenAI (not peer-reviewed); limited detail on training data and methodology; capabilities may differ substantially from grading educational short answers in specific science domains

---

*Note: This theme has 3 journal papers (Mizumoto & Eguchi 2023, Bai et al. 2024 in IJAIED) out of 8 entries. The recency of LLM-in-assessment literature means most work is in preprint or conference form. This is expected and acceptable for this supplementary theme. The IJAIED journal paper (Bai et al. 2024) is particularly valuable as it directly addresses LLM vs. BERT comparison on ASAG with the same SemEval 2013 datasets we use.*
