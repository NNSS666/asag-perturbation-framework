# Theme 4: LLM-Based Automated Assessment

**Search queries used:**
- "GPT-4" OR "large language model" "short answer grading" OR "automated scoring" journal
- "LLM" "rubric" "grading" journal 2023-2026
- "ChatGPT" "automated assessment" journal
- "generative AI" "automated grading" journal 2023-2026

**Inclusion criteria:** Peer-reviewed journal articles (primary); well-cited conference papers from major NLP venues; English; 2019-2026; directly relevant to LLM-based grading, assessment, or evaluation of student responses.

**Note:** LLM-in-assessment literature is rapidly growing but primarily in arXiv preprints and recent conference papers (2023-2025). Journal versions are sparse. This reflects the recency of the field rather than a quality issue.

**Type count:** Journal: 3 | Conference: 2 | Technical Report: 1 | Total: 6

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

**Research Question:** How accurately can a GPT-based LLM score essays compared to human raters, and what scoring criteria can it assess?

**Methodology:** GPT-3 (text-davinci-003) applied to essay scoring on 12,100 TOEFL essays from the ETS Corpus of Non-Native Written English (TOEFL11); compared against benchmark proficiency levels; linguistic feature analysis of scoring patterns.

**Key Findings:**
- GPT-3 achieves moderate agreement with benchmark proficiency levels on essay scoring, demonstrating feasibility of LLM-based automated assessment
- LLM scoring patterns correlate with linguistic features (vocabulary richness, syntactic complexity) but show biases toward certain writing styles
- Rubric clarity and prompt engineering significantly affect scoring consistency

**Relevance to This Paper:**
- Theme: LLM assessment
- How it supports our work: Early demonstration that LLM-based scoring is feasible for educational assessment; the "rubric clarity affects consistency" finding supports our rubric sanitization mode and LLM consistency rate metric; provides context for the rapid improvement from GPT-3 to GPT-4 in scoring applications
- Citation context: related-work-2.1, methodology

**Limitations:** Essay scoring task (not ASAG); uses GPT-3 (text-davinci-003), now superseded; no adversarial or perturbation evaluation; single paper from a linguistics methods journal

---

## Latif and Zhai (2024)

**Citation (Harvard):** Latif, E. and Zhai, X. (2024) 'Fine-tuning ChatGPT for automatic scoring', *Computers and Education: Artificial Intelligence*, 6, 100210. doi: 10.1016/j.caeai.2024.100210

**Journal:** Computers and Education: Artificial Intelligence | **Type:** Journal

**Research Question:** Can fine-tuning ChatGPT (GPT-3.5) improve its automatic scoring performance compared to zero-shot and few-shot approaches?

**Methodology:** Fine-tuned GPT-3.5 evaluated on science student response datasets; comparison with zero-shot and few-shot GPT-3.5/GPT-4 and BERT-based baselines; rubric-conditioned prompting; accuracy, QWK, and Cohen's kappa reported.

**Key Findings:**
- Fine-tuned GPT-3.5 outperforms zero-shot GPT-4 on science response scoring, demonstrating that task-specific fine-tuning compensates for model scale differences
- LLM grading accuracy is highly sensitive to rubric specification; rubric clarity and example quality are key determinants of scoring consistency
- Fine-tuning reduces the inconsistency problem (same prompt, same answer, different grade) observed in zero-shot LLM scoring

**Relevance to This Paper:**
- Theme: LLM assessment
- How it supports our work: Published journal article providing LLM scoring baselines on educational assessment tasks; the rubric sensitivity finding supports our rubric sanitization mode; the fine-tuning vs. zero-shot comparison informs our LLM grader design choices; inconsistency reduction through fine-tuning motivates our LLM consistency rate metric
- Citation context: related-work-2.1, methodology

**Limitations:** Science response scoring (not specifically ASAG on SemEval datasets); GPT-3.5 fine-tuning (GPT-4 fine-tuning not yet available at time of study); no adversarial or perturbation evaluation

---

## Naismith et al. (2023)

**Citation (Harvard):** Naismith, B., Mulcaire, P. and Burstein, J. (2023) 'Automated evaluation of written discourse coherence using GPT-4', in *Proceedings of the 18th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2023)*. Toronto: Association for Computational Linguistics, pp. 394-403. doi: 10.18653/v1/2023.bea-1.32

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

*Note: This theme has 3 journal papers (Mizumoto & Eguchi 2023, Latif & Zhai 2024) out of 6 entries. The recency of LLM-in-assessment literature means most work is in conference form. Latif & Zhai 2024 is the key journal reference for fine-tuned LLM scoring.*

*AUDIT NOTE (2026-02-20): Removed Bai et al. 2024 (hallucinated — no IJAIED paper found) and Latif et al. 2023 (hallucinated — wrong arXiv ID, paper doesn't exist). Replaced with verified Latif & Zhai 2024 in Computers and Education: AI. Fixed Mizumoto model description (GPT-3, not GPT-3.5/4). Fixed Naismith DOI.*
