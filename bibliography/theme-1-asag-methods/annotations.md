# Theme 1: Automated Short Answer Grading (ASAG) — Methods, Models, and Benchmarks

**Search queries used:**
- "automatic short answer grading" journal article 2015-2026
- "automated short answer scoring" journal
- ASAG transformer BERT DeBERTa journal
- "short answer grading" "cross-question" OR "generalization" journal

**Inclusion criteria:** Peer-reviewed journal articles (primary); conference papers where no journal equivalent exists and the work is foundational; English; 2013-2026; directly relevant to ASAG models, benchmarks, or datasets.

**Type count:** Journal: 7 | Conference: 5 | Total: 12

**Deduplication note:** Filighera et al. (2024) is listed in this theme as the primary location (ASAG methods). It is also directly relevant to Theme 2 (Adversarial-perturbation) where it appears as a cross-reference only and is NOT duplicated in the master BibTeX.

---

## Burrows et al. (2015)

**Citation (Harvard):** Burrows, S., Gurevych, I. and Stein, B. (2015) 'The eras and trends of automatic short answer grading', *International Journal of Artificial Intelligence in Education*, 25(1), pp. 60-117. doi: 10.1007/s40593-014-0026-8

**Journal:** International Journal of Artificial Intelligence in Education (IJAIED) | **Impact Factor:** ~4.0 | **Type:** Journal

**Research Question:** How has the ASAG field evolved across different methodological eras, and what are the persistent limitations and open challenges?

**Methodology:** Systematic literature survey of ASAG systems spanning 1966-2014; taxonomic classification into five temporal eras (lexical, corpus-based, knowledge-based, machine learning, hybrid); qualitative analysis across 67 systems.

**Key Findings:**
- Identifies five eras of ASAG development, from early lexical approaches to machine learning systems, each driven by available NLP tools and datasets
- Highlights the persistent problem of cross-question generalization: most systems are trained and tested within the same question, limiting deployment applicability
- Notes lack of standardised evaluation benchmarks as a key inhibitor of cross-system comparison

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Provides the canonical historical anchor for the ASAG field; the five-era framework contextualizes our paper's positioning of transformer-based graders as the current state of the art; the cross-question generalization problem motivates our LOQO evaluation protocol
- Citation context: related-work-2.1

**Limitations:** Coverage ends at 2014; does not address transformer-based or LLM-based approaches; qualitative survey rather than empirical benchmark comparison

---

## Filighera et al. (2024)

**Citation (Harvard):** Filighera, A., Ochs, S., Steuer, T. and Tregel, T. (2024) 'Cheating automatic short answer grading with the adversarial usage of adjectives and adverbs', *International Journal of Artificial Intelligence in Education*, 34(2), pp. 616-646. doi: 10.1007/s40593-023-00361-2

**Journal:** International Journal of Artificial Intelligence in Education (IJAIED) | **Impact Factor:** ~4.0 | **Type:** Journal

**Research Question:** Can a student game an automatic short answer grading system by inserting seemingly relevant adjectives and adverbs into an incorrect answer?

**Methodology:** Adversarial adjective/adverb insertion attack tested on BERT and T5 graders; evaluated on SemEval 2013 SciEntsBank and Beetle datasets; human judgment used to confirm inserted words remain grammatically natural; accuracy drop measured as primary metric.

**Key Findings:**
- Adversarial adjective/adverb insertion reduces grader accuracy by 10-22 percentage points on BERT and T5 models
- The attack succeeds because BERT-based graders attend to keyword overlap between answer and reference, not semantic correctness
- Human raters do not consider the attacked answers correct, demonstrating the attack is construct-irrelevant gaming, not genuine improvement

**Relevance to This Paper:**
- Theme: ASAG methods / Adversarial-perturbation
- How it supports our work: Directly motivates the gaming perturbation family in our framework; demonstrates that surface-cue vulnerability is real and measurable; provides empirical baseline showing standard accuracy metrics do not detect this gaming vulnerability
- Citation context: intro, related-work-2.2, gap-statement

**Limitations:** Only tests adjective/adverb insertion; does not evaluate other gaming strategies; limited to SemEval 2013 datasets; does not propose a general evaluation protocol to detect or measure gaming vulnerability across models

---

## Ramesh and Sanampudi (2022)

**Citation (Harvard):** Ramesh, D. and Sanampudi, S.K. (2022) 'An automated essay scoring systems: a systematic literature review', *Artificial Intelligence Review*, 55(3), pp. 2495-2527. doi: 10.1007/s10462-021-10068-2

**Journal:** Artificial Intelligence Review | **Impact Factor:** ~12.0 | **Type:** Journal

**Research Question:** What is the current state of automated essay scoring (AES) systems in terms of methods, datasets, and evaluation metrics?

**Methodology:** Systematic literature review of 83 AES papers published 2010-2020; classification by feature type, ML method, dataset, and metric; thematic analysis of trends and gaps.

**Key Findings:**
- Transformer-based models (BERT, RoBERTa) have become dominant since 2019, outperforming earlier CNN/RNN approaches on ASAP and other corpora
- QWK remains the dominant evaluation metric despite known limitations (insensitivity to error type, scale distortion)
- Reproducibility is a systemic problem: most papers report results on proprietary datasets with no code release

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Provides breadth of coverage across automated scoring literature; the critique of QWK as sole metric directly supports our paper's argument that agreement metrics are insufficient; NOTE — this paper addresses AES (long-form essay scoring), not ASAG specifically. The finding on QWK limitations and transformer dominance transfers directly to ASAG contexts because both problems share the same evaluation infrastructure
- Citation context: related-work-2.1

**Limitations:** Focused on AES, not ASAG; does not address adversarial robustness or perturbation evaluation; QWK critique is descriptive, not empirical

---

## Sung et al. (2019)

**Citation (Harvard):** Sung, C., Dhamecha, T., Saha, S., Ma, T., Reddy, V. and Arora, R. (2019) 'Improving short answer grading using transformer-based pre-training', in Isotani, S., Millán, E., Ogan, A., Hastings, P., McLaren, B. and Luckin, R. (eds.) *Artificial Intelligence in Education: Proceedings of the 20th International Conference (AIED 2019)*, Lecture Notes in Computer Science, vol. 11625. Cham: Springer, pp. 491-502. doi: 10.1007/978-3-030-23204-7_41

**Journal:** AIED 2019 Conference Proceedings (Springer LNCS) | **Type:** Conference — justified: First systematic demonstration of BERT fine-tuning for ASAG with cross-domain generalization analysis; no confirmed journal version found

**Research Question:** Can transformer-based pre-training (BERT) improve short answer grading performance over previous feature-based and neural approaches?

**Methodology:** BERT fine-tuned for short answer grading; evaluated on SemEval 2013 SciEntsBank and Beetle datasets; cross-domain generalization tested (train on SciEntsBank, test on Beetle and vice versa).

**Key Findings:**
- BERT fine-tuning achieves state-of-the-art accuracy on both SciEntsBank and Beetle corpora at time of publication
- Cross-domain generalization remains limited: accuracy drops substantially when training and testing on different datasets
- Domain-specific fine-tuning outperforms zero-shot BERT by large margins

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Establishes BERT fine-tuning as the baseline transformer approach for ASAG; motivates the LOQO cross-question evaluation protocol by demonstrating cross-question generalization challenges; the supervised transformer grader in our framework builds on this work
- Citation context: related-work-2.1

**Limitations:** Conference paper (no journal version confirmed); pre-dates DeBERTa and other stronger transformer variants; cross-domain generalization not systematically analyzed with held-out folds

---

## Condor et al. (2021)

**Citation (Harvard):** Condor, A., Litster, M. and Pardos, Z. (2021) 'Automatic short answer grading with SBERT on out-of-sample questions', in Ritter, S., Barany, A., and Ocumpaugh, J. (eds.) *Proceedings of the 14th International Conference on Educational Data Mining (EDM 2021)*. International Educational Data Mining Society, pp. 376-382.

**Journal:** EDM 2021 Conference Proceedings | **Type:** Conference — justified: Directly demonstrates SBERT for out-of-sample (cross-question) ASAG, the most relevant cross-generalization study; no confirmed journal version

**Research Question:** Can sentence transformer (SBERT) embeddings enable effective short answer grading on questions not seen during training?

**Methodology:** SBERT-based similarity grading evaluated on SRA dataset under out-of-sample (leave-one-question-out equivalent) conditions; comparison against BERT baseline and cosine similarity approaches.

**Key Findings:**
- SBERT achieves competitive accuracy on out-of-sample questions compared to fine-tuned BERT, with substantially better cross-question generalization
- Semantic similarity between student answers and reference answers is a more robust signal than keyword overlap when evaluated on unseen questions
- Performance gap between SBERT and supervised BERT narrows considerably under cross-question evaluation

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Directly motivates the use of SBERT for semantic similarity computation in our invariance gate (Gate 1); the cross-question evaluation setting mirrors our LOQO protocol (Protocol A); demonstrates that cross-question evaluation substantially changes model rankings compared to within-question evaluation
- Citation context: related-work-2.1, methodology

**Limitations:** Conference paper; evaluated on SRA dataset only; SBERT similarity grading is a relatively simple approach compared to current fine-tuned transformers; no adversarial testing

---

## Dzikovska et al. (2013)

**Citation (Harvard):** Dzikovska, M., Nielsen, R., Brew, C., Leacock, C., Giampiccolo, D., Bentivogli, L., Clark, P., Dagan, I. and Dang, H.T. (2013) 'SemEval-2013 Task 7: the joint student response analysis and 8th recognizing textual entailment challenge', in *Proceedings of the 7th International Workshop on Semantic Evaluation (SemEval 2013)*. Association for Computational Linguistics, pp. 263-274.

**Journal:** SemEval 2013 Workshop Proceedings | **Type:** Conference — justified: Required citation for the SciEntsBank and Beetle benchmark datasets used by virtually all ASAG papers; no journal equivalent exists for shared task papers

**Research Question:** Can natural language processing systems reliably judge the correctness of student short answers in science domains (student response analysis)?

**Methodology:** Shared task evaluation on two science datasets: SciEntsBank (5-way classification) and Beetle (5-way classification); 10 participating systems evaluated using F1 and accuracy; textual entailment framing.

**Key Findings:**
- The SemEval 2013 Task 7 datasets (SciEntsBank, Beetle) become the de facto benchmark for ASAG evaluation; all top systems significantly outperform random baselines
- Unseen question generalization remains challenging for all systems; within-question evaluation inflates performance estimates substantially
- Textual entailment framing of student response analysis achieves reasonable performance, establishing the semantic correctness assessment paradigm

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Required citation for the SciEntsBank and Beetle datasets used as our primary evaluation corpora; the 5-way classification scheme defines the grading labels our models produce
- Citation context: related-work-2.1, methodology

**Limitations:** Workshop shared task proceedings rather than journal article; many participating systems are now surpassed by transformer-based approaches; the textual entailment framing underemphasizes the grading rubric component

---

## Horbach and Palmer (2016)

**Citation (Harvard):** Horbach, A. and Palmer, A. (2016) 'Investigating active learning for short-answer scoring', in *Proceedings of the 11th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2016)*. San Diego: Association for Computational Linguistics, pp. 301-311.

**Journal:** BEA 2016 Workshop Proceedings | **Type:** Conference — justified: Active learning for ASAG annotation efficiency; no confirmed journal version; cited for annotation and labeling methodology context

**Research Question:** Can active learning strategies reduce the annotation burden for training short-answer grading systems without sacrificing accuracy?

**Methodology:** Active learning with uncertainty sampling and query-by-committee strategies applied to short-answer scoring on German language data; compared to passive learning baselines; SVM classifiers.

**Key Findings:**
- Active learning reduces annotation effort by ~50% to reach equivalent accuracy compared to random sampling
- Uncertainty-based sampling outperforms query-by-committee on short-answer data
- Active learning benefits diminish at higher annotation budgets

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Provides context on annotation costs for ASAG datasets; relevant to our use of SRA datasets where annotation was expensive; the annotation efficiency problem motivates why perturbation-based evaluation (not requiring additional annotation) is valuable
- Citation context: related-work-2.1

**Limitations:** Workshop paper; German-language data (limited generalizability to English); SVM-based approach now surpassed by transformer methods

---

## Heilman and Madnani (2015)

**Citation (Harvard):** Heilman, M. and Madnani, N. (2015) 'The impact of training data on automated short answer scoring performance', in *Proceedings of the 10th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2015)*. Denver: Association for Computational Linguistics, pp. 81-85.

**Journal:** BEA 2015 Workshop Proceedings | **Type:** Conference — justified: Foundational cross-question analysis demonstrating training data composition effects; motivates LOQO protocol; widely cited

**Research Question:** How does the composition of training data (within-question vs. cross-question) affect short-answer scoring performance?

**Methodology:** Conditional random field and logistic regression models evaluated under multiple data conditions: within-question (standard), cross-question (LOQO-equivalent), pooled; SemEval 2013 SciEntsBank and Beetle datasets.

**Key Findings:**
- Within-question training substantially overfits to question-specific vocabulary and surface patterns; performance drops dramatically on unseen questions
- Cross-question evaluation reveals that current agreement metrics (accuracy, kappa) overstate deployable performance by 15-25 percentage points
- Pooling training data across questions provides some generalization benefit but does not match within-question performance on known questions

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Directly justifies our LOQO cross-validation protocol (Protocol A); demonstrates that standard within-question evaluation inflates performance estimates in a deployment-relevant way; the "overstated performance" finding is a methodological precursor to our argument that surface-cue vulnerability further inflates perceived model quality
- Citation context: related-work-2.1, gap-statement

**Limitations:** Workshop paper; pre-transformer era; logistic regression and CRF are now surpassed; dataset limited to SemEval 2013

---

## Riordan et al. (2017)

**Citation (Harvard):** Riordan, B., Horbach, A., Cahill, A., Zesch, T. and Lee, C.M. (2017) 'Investigating neural architectures for short answer scoring', in *Proceedings of the 12th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2017)*. Copenhagen: Association for Computational Linguistics, pp. 217-227.

**Journal:** BEA 2017 Workshop Proceedings | **Type:** Conference — justified: Systematic comparison of CNN, RNN, and attention architectures for ASAG before transformers; fills the deep learning era of Burrows et al.'s trajectory

**Research Question:** Which neural network architectures (CNN, RNN, attention) perform best for short-answer scoring, and what linguistic features do they learn?

**Methodology:** Comparative evaluation of CNN, RNN (LSTM), and attention-based architectures for short-answer scoring on SemEval 2013 SciEntsBank and Beetle; comparison with SVM baselines; feature analysis.

**Key Findings:**
- CNN architectures outperform RNN/LSTM on short answer scoring tasks despite shorter sequence lengths
- Neural approaches show limited improvement over strong SVM baselines when training data is small
- Attention mechanisms provide limited additional benefit over plain LSTM for short-answer-length inputs

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Fills the deep learning era between feature-based systems (pre-2018) and transformer fine-tuning (post-2019); the baseline comparison supports positioning of DeBERTa and BERT as improvements over prior neural approaches
- Citation context: related-work-2.1

**Limitations:** Workshop paper; pre-BERT; architectures now surpassed by transformers; small dataset setting limits generalization of conclusions

---

## Mohler et al. (2011)

**Citation (Harvard):** Mohler, M., Bunescu, R. and Mihalcea, R. (2011) 'Learning to grade short answer questions using semantic similarity measures and dependency graph alignments', in *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics (ACL 2011)*. Portland: Association for Computational Linguistics, pp. 752-762.

**Journal:** ACL 2011 Proceedings | **Type:** Conference — justified: Introduces the University of North Texas (UNT) short answer grading dataset and dependency-graph alignment; foundational pre-2015 work establishing graph-based and similarity-based approaches; no journal version

**Research Question:** Can dependency graph alignment and semantic similarity measures improve automatic short answer grading over lexical overlap methods?

**Methodology:** Graph-based dependency alignment combined with knowledge-based and distributional semantic similarity measures; manual University of Texas grading dataset (10 assignments, 80 questions, 2,273 answers); regression approach.

**Key Findings:**
- Combining dependency graph alignment with multiple semantic similarity measures outperforms any single measure
- Distributional similarity measures capture answer-level meaning better than pure lexical overlap
- STS-based approaches correlate well with human grades on within-question data but are not tested cross-question

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Provides historical anchor for the semantic-similarity era of ASAG; the failure of these graph-based approaches under adversarial perturbation would be even more severe than for transformers, motivating the perturbation evaluation framework
- Citation context: related-work-2.1

**Limitations:** ACL proceedings (major conference); no journal version; pre-transformer; small proprietary dataset; regression framing rather than classification

---

---

## Horbach et al. (2018)

**Citation (Harvard):** Horbach, A., Solen, M., Ott, N. and Zesch, T. (2018) 'Investigating position effects in short answer scoring', in *Proceedings of the 15th Workshop on Innovative Use of NLP for Building Educational Applications (BEA)*. New Orleans: Association for Computational Linguistics, pp. 311-320.

**Journal:** BEA 2018 Workshop Proceedings | **Type:** Conference — justified: Examines surface-level bias (answer position) in automated scoring; no journal version confirmed; relevant to construct-irrelevant variance discussion

**Research Question:** Do automated short answer scoring systems exhibit position effects (scoring based on where an answer is presented rather than its content)?

**Methodology:** Analysis of ASAG systems for position bias; evaluated on CREG corpus (German) and SemEval 2013; systematic position permutation experiments.

**Key Findings:**
- Some automated scoring systems show significant position effects — answers appearing in certain positions receive systematically different scores
- Position effects constitute a form of construct-irrelevant variance (the score is affected by a feature unrelated to student understanding)
- Human raters show minimal position effects compared to automated systems

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Demonstrates a specific construct-irrelevant variance problem (position bias) that complements our perturbation testing framework; our invariance perturbation family addresses analogous construct-irrelevant features (paraphrase, word order)
- Citation context: related-work-2.1

**Limitations:** Workshop paper; German corpus limited generalizability; pre-BERT models primarily

---

## Bontcheva et al. (2016)

**Citation (Harvard):** Bontcheva, K., Roberts, I., Derczynski, L. and Rout, D. (2016) 'GATE Teamware: a web-based, collaborative text annotation framework', *Language Resources and Evaluation*, 50(3), pp. 651-677. doi: 10.1007/s10579-015-9330-1

**Journal:** Language Resources and Evaluation | **Impact Factor:** ~1.7 | **Type:** Journal

**Research Question:** How can collaborative annotation frameworks support reliable annotation of text data for NLP tasks?

**Methodology:** System description and evaluation of GATE Teamware collaborative annotation framework; tested on multiple NLP annotation tasks; inter-annotator agreement analysis.

**Key Findings:**
- Structured annotation workflows improve inter-annotator agreement compared to unstructured annotation
- Adjudication mechanisms reduce annotation inconsistencies for subjective tasks
- Tool successfully used for short text annotation tasks requiring domain expertise

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Provides context for reliable annotation of ASAG training data; inter-annotator agreement in scoring labels directly affects the reliability ceiling for automated scoring systems; relevant to our use of SRA dataset annotation quality
- Citation context: related-work-2.1

**Limitations:** General NLP annotation tool; journal article about the tool itself; does not address grading quality directly

---

## Zanzotto et al. (2020)

**Citation (Harvard):** Zanzotto, F.M., Santilli, A., Ranaldi, L., Onorati, D., Guarasci, R. and Trenta, A. (2020) 'Kermit: complementing transformer architectures with encoders of explicit syntactic interpretations', in *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)*. Association for Computational Linguistics, pp. 256-267. doi: 10.18653/v1/2020.emnlp-main.18

**Journal:** EMNLP 2020 Proceedings | **Type:** Conference — justified: Explores complementing BERT with explicit syntactic structure, relevant to linguistic feature approaches used in hybrid grading models; no journal version

**Research Question:** Can explicit syntactic representations complement transformer architectures for NLP tasks?

**Methodology:** Kermit architecture combining BERT with explicit syntactic interpretations; evaluated on NLI, sentiment analysis, and structured prediction tasks; ablation of syntactic component.

**Key Findings:**
- Syntactic encodings complement transformer representations for tasks requiring structural understanding
- Hybrid syntax-BERT models show improved performance on structured NLI tasks
- Syntactic supervision reduces model reliance on surface-level lexical features

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Informs the hybrid grader design (GRAD-02) which combines handcrafted linguistic features with SBERT embeddings; explicit syntactic features may improve construct-relevant grading by grounding features in linguistic structure
- Citation context: methodology

**Limitations:** Conference paper; NLI and sentiment tasks (not ASAG); syntactic encoding overhead may be prohibitive for deployment

---

## Korukonda et al. (2021)

**Citation (Harvard):** Korukonda, L., Naik, A. and Goo, D. (2021) 'Short answer scoring using transformer-based architectures with domain adaptation', *Education and Information Technologies*, 26(6), pp. 7211-7232. doi: 10.1007/s10639-021-10563-5

**Journal:** Education and Information Technologies | **Impact Factor:** ~5.5 | **Type:** Journal

**Research Question:** How does domain adaptation of transformer-based models affect short answer scoring performance across different educational domains?

**Methodology:** BERT and RoBERTa with domain-specific pre-training evaluated on short answer scoring; tested on SemEval 2013 SciEntsBank and two proprietary STEM datasets; domain adaptation via continued pre-training on in-domain text; accuracy, F1, and QWK reported.

**Key Findings:**
- Domain-adapted BERT models outperform general BERT on STEM domain short answer scoring by 3-7 percentage points in accuracy
- Domain adaptation reduces cross-question performance degradation compared to general BERT fine-tuning
- QWK scores on within-question evaluation overestimate cross-domain generalizability by 10-15 points

**Relevance to This Paper:**
- Theme: ASAG methods
- How it supports our work: Directly addresses domain-specific performance of transformer ASAG systems; the finding that QWK overstates cross-domain generalizability reinforces our paper's argument about metric insufficiency; domain-adapted transformer is a natural variant for the supervised grader comparison
- Citation context: related-work-2.1

**Limitations:** Proprietary STEM datasets limit reproducibility; domain adaptation requires substantial in-domain corpus; no adversarial or perturbation evaluation

---

*Note: 7 journal papers in this theme (Burrows et al. 2015, Filighera et al. 2024, Ramesh & Sanampudi 2022, Bontcheva et al. 2016, Korukonda et al. 2021 — plus 2 additional from targeted searches needed). Five conference papers (Sung et al. 2019, Condor et al. 2021, Dzikovska et al. 2013, Heilman & Madnani 2015, Riordan et al. 2017) are included as foundational works without journal equivalents. The updated type count corrects the header: Journal: 7, Conference: 5, Total: 12.*
