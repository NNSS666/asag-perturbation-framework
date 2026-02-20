---
title: "Related Work: Draft Literature Review Section"
paper: "IFKAD 2026 — Perturbation-Based Evaluation of Automated Short Answer Grading"
authors: "Ferdinando Sasso, Andrea De Mauro"
status: draft
last-updated: 2026-02-20
citation-format: Harvard
word-count: ~2100
---

# 2. Related Work

## 2.1 Automated Short Answer Grading: Models and Benchmarks

Automated Short Answer Grading (ASAG) has a history spanning several decades, though systematic evaluation methodology has advanced more slowly than model performance. Burrows et al. (2015) provide the canonical survey of the field, identifying five distinct eras of ASAG development from early lexical matching systems through corpus-based, knowledge-based, and machine learning approaches. Their taxonomy reveals a persistent limitation that transcends individual eras: most systems are trained and evaluated within the same question, substantially inflating performance estimates relative to deployment conditions. The cross-question generalisation problem identified by Burrows et al. (2015) remains unresolved in contemporary work and directly motivates the leave-one-question-out (LOQO) evaluation protocol adopted in the present study.

The transition from feature-based to deep learning approaches brought measurable performance gains on benchmark corpora. Mohler et al. (2011) established semantic similarity and dependency graph alignment as central ASAG approaches in the pre-transformer era, while Riordan et al. (2017) demonstrated that convolutional and recurrent architectures outperformed handcrafted feature baselines on the SemEval 2013 benchmark. The shift accelerated with the introduction of transformer pre-training. Sung et al. (2019) were among the first to systematically demonstrate that BERT fine-tuning achieves state-of-the-art accuracy on the SciEntsBank and Beetle corpora from SemEval 2013 Task 7 (Dzikovska et al., 2013), the shared task that established the canonical ASAG benchmark datasets. Despite their different origin, both datasets share a five-way classification scheme (correct, partially correct, contradictory, irrelevant, non-domain) and have been used in virtually every subsequent ASAG evaluation, making them the de facto standard. Korukonda et al. (2021) extended transformer-based grading to domain-adapted settings, finding that continued pre-training on in-domain text reduces but does not eliminate the cross-question generalisation gap — and, critically, that QWK scores on within-question evaluation overestimate cross-domain generalisability by ten to fifteen percentage points.

The most recent era of ASAG research has examined large language models as zero-shot and few-shot graders. Bai et al. (2024) conduct the most directly relevant comparison, evaluating GPT-3.5, GPT-4, and open-source LLMs against fine-tuned DeBERTa on the same SemEval 2013 datasets. They find that GPT-4 achieves competitive accuracy in zero-shot conditions but exhibits high variance across questions, particularly for domain-specific science items. Mizumoto and Eguchi (2023) and Latif et al. (2023) similarly demonstrate LLM grading competence on essay and short-answer tasks while documenting significant inconsistency rates under repeated evaluation — a dimension of reliability that aggregate agreement metrics such as QWK do not capture.

Across all eras, the field has converged on a narrow set of evaluation metrics: accuracy, F1, and quadratic weighted kappa (QWK). Ramesh and Sanampudi (2022) note in their systematic review of automated essay and short-answer scoring that QWK remains dominant despite known limitations — it is insensitive to the type of error a model makes, susceptible to scale distortion, and measures agreement rather than construct validity. The finding that evaluation methodology has not kept pace with model sophistication provides the empirical basis for the present paper's methodological contribution.

## 2.2 Adversarial and Perturbation-Based Evaluation of AI Systems

The recognition that NLP models can achieve high accuracy on clean test sets while remaining brittle under input variation has generated a substantial literature on adversarial and perturbation-based evaluation. The defining contribution is Ribeiro et al. (2020), whose CheckList framework proposes three types of behavioural tests for NLP systems: Invariance tests (semantics-preserving perturbations should not change predictions), Directional Expectation tests (meaning-altering changes should produce predictable output changes), and Minimum Functionality Tests (basic competencies a model must demonstrate). Ribeiro et al. (2020) applied these tests to commercial NLP systems and found failures in all three categories across models including BERT-based systems. The three perturbation families in the present framework — invariance, sensitivity, and gaming — are a direct operationalisation of the CheckList taxonomy for the ASAG domain.

The broader adversarial NLP literature has established that transformer models are systematically vulnerable to word-level and character-level input perturbations. Alzantot et al. (2018) demonstrated that semantics-preserving synonym substitution could reduce LSTM and BERT classification accuracy by 50-90 percentage points, with human annotators rating the adversarial examples as meaning-equivalent in over 80% of cases. Jin et al. (2020) confirmed this finding specifically for BERT, reducing accuracy from 92.9% to 6.2% under synonym-substitution attack on sentiment classification while fooling human judges only 15% of the time — confirming that the vulnerability is construct-irrelevant (the meaning does not change but the model's output does). At the character level, Belinkov and Bisk (2018) showed that natural typos and character swaps severely degrade neural NLP models, while Ebrahimi et al. (2018) demonstrated that gradient-guided character-level flips could flip classifier decisions with minimal edit distance. Zou et al. (2023) synthesise this literature in a systematic survey of transformer robustness, concluding that multi-level testing across character, word, and sentence perturbations is required to characterise the full vulnerability profile of any model — a key design principle of the evaluation framework presented here.

Adversarial work specifically targeting educational AI systems is considerably sparser than the general NLP literature, and what exists is concentrated in conference proceedings rather than journals. Filighera et al. (2024) provide the most directly relevant study: inserting grammatically natural adjectives and adverbs into incorrect student answers reduces the accuracy of BERT and T5 graders on SciEntsBank and Beetle by 10 to 22 percentage points. Human raters do not consider the attacked answers correct, confirming that the attack exploits construct-irrelevant surface cues rather than genuine answer improvement. Ding et al. (2020) examined a more extreme form of vulnerability, finding that random strings and keyword-only inputs receive above-mean scores in 30–60% of cases across multiple content scoring systems, both neural and non-neural. Kumar et al. (2020) propose Attack Success Rate (ASR) as a metric for adversarial robustness of scoring systems and demonstrate that template and keyword-repetition attacks succeed in 40–75% of cases across automated scoring systems. Morris et al. (2020) contextualise this line of work within the TextAttack framework, which provides a unified interface for 16 adversarial attack strategies applicable to NLP classifiers.

The methodological gap in this body of work is consistent: each study tests individual attack types in isolation. None proposes a systematic multi-family perturbation protocol that simultaneously measures a system's stability under meaning-preserving perturbations, its sensitivity to meaning-altering perturbations, and its resistance to score-gaming perturbations, with complementary metrics that can be compared across grader architectures. Wang et al. (2022) note in their survey of NLP robustness that most evaluation practice measures accuracy on clean test sets only and that behavioural testing approaches remain a minority practice — a gap that the present paper addresses specifically for the ASAG domain.

## 2.3 Educational Assessment Validity and Reliability

The theoretical framework for evaluating whether automated scoring systems measure what they claim to measure derives from educational measurement scholarship rather than from NLP research. Messick (1989) established the unified validity framework in which construct validity is the central concept: score variation must be attributable to variation in the intended construct (student understanding) rather than to construct-irrelevant features (surface text properties). Any factor that causes scores to change without a corresponding change in the underlying construct constitutes construct-irrelevant variance and threatens the validity of score interpretations, even when criterion-related validity (correlation with human raters) is high. This theoretical distinction provides the foundation for the present paper's perturbation-based evaluation framework: invariance perturbations test whether construct-irrelevant text changes inappropriately alter scores, while sensitivity perturbations test whether construct-relevant changes appropriately trigger score changes.

Kane (2006) extended Messick's framework with the validity argument model, in which validity is treated as a chain of inferences from observed performance to intended score meaning. For ASAG, the chain requires that the inference from "student answer" to "score represents conceptual understanding" be supported by evidence that score variation reflects understanding rather than surface cues. Our perturbation tests are direct empirical tests of this scoring inference link.

Several scholars have applied validity frameworks specifically to AI-based automated scoring systems, consistently identifying the same gap. Ferrara and Qunbar (2022) argue that while existing AES validation studies have accumulated extensive criterion-related validity evidence, they neglect construct validity — they do not test whether score variation reflects construct-relevant content features. Dorsey and Michaels (2022) identify AI-based scoring as introducing new validity threats not present in human scoring, including unexplained feature reliance and distributional shift vulnerability, and call explicitly for "construct-relevant features testing" as a validity requirement. Shermis (2022) examines operational AES programs and finds that content validity — whether the features the model uses are genuinely writing quality indicators — is rarely tested. Taken together, Ferrara and Qunbar (2022), Dorsey and Michaels (2022), and Shermis (2022) establish a convergent scholarly position: criterion-related validity evidence alone is insufficient for AI-based scoring, yet it remains the dominant form of validation evidence in operational practice.

Williamson et al. (2012) anticipated this problem in a framework for evaluating and deploying automated scoring systems, identifying seven evaluation criteria that include not only human-machine agreement but also robustness to gaming and the ability to detect construct-irrelevant responses. The explicit inclusion of gaming robustness as an evaluation criterion directly anticipates our ASR metric. Loukina et al. (2019) demonstrate that construct-irrelevant features create simultaneous validity and fairness problems in automated scoring, as features not grounded in the intended construct may produce systematically biased scores across demographic groups. Deane (2013) shows for automated essay scoring that surface features captured by existing systems diverge substantially from higher-order construct definitions, and that such systems can be gamed by producing long, complex-structured but vacuous text — the essay-scoring equivalent of adjective stuffing in ASAG.

The convergence of these validity arguments with empirical adversarial findings points clearly to the gap this paper fills. Educational measurement theory has established what construct validity evidence requires; adversarial NLP research has demonstrated that ASAG systems are empirically vulnerable to construct-irrelevant perturbations; yet no prior work has operationalised construct validity testing for ASAG as a systematic, multi-family perturbation protocol with complementary metrics applicable across grader architectures.

---

## 3. The Research Gap This Study Fills

Automated Short Answer Grading systems have achieved substantial agreement with human raters on standard benchmark datasets such as SemEval 2013 Task 7 (Dzikovska et al., 2013), yet standard evaluation metrics — accuracy, F1, and quadratic weighted kappa — measure only aggregate agreement on clean test inputs. They do not distinguish between models that grade correctly because they understand the semantic content of a student response and models that grade correctly because they exploit surface-level lexical cues. Filighera et al. (2024) demonstrated that inserting grammatically natural adjectives and adverbs into incorrect student answers causes state-of-the-art BERT and T5 graders to accept them as correct, reducing accuracy by 10–22 percentage points. Ding et al. (2020) showed that even garbled or randomly shuffled inputs fool content scoring systems in a substantial proportion of cases. Taken together, these findings suggest that standard evaluation practice systematically overstates the reliability of ASAG systems under deployment conditions.

Educational measurement scholarship has established that automated scoring validity requires evidence of construct relevance — that score variation reflects variation in the intended construct, not construct-irrelevant features (Ferrara and Qunbar, 2022; Messick, 1989). Dorsey and Michaels (2022) and Williamson et al. (2012) explicitly identify gaming robustness and construct-relevant feature testing as required validation dimensions that existing practice neglects. No prior work has proposed a systematic, multi-family perturbation protocol that operationalises construct validity testing for ASAG by simultaneously measuring three complementary dimensions: a system's invariance under meaning-preserving perturbations (IVR — Invariance Violation Rate), its sensitivity to meaning-altering perturbations (SSR — Sensitivity Score Ratio), and its resistance to score-gaming perturbations (ASR — Attack Success Rate). Ribeiro et al.'s (2020) CheckList framework provides the methodological precedent for behavioural testing in NLP, but has not been applied to educational grading nor extended with grading-specific metrics. This paper fills that gap by proposing a three-family perturbation evaluation framework for ASAG graders, empirically demonstrating its diagnostic power across four grader architectures on the SemEval 2013 benchmark corpora, and showing that models with comparable QWK scores can differ substantially in construct-relevant grading behaviour as revealed by IVR, SSR, and ASR.

---

## References

Alzantot, M., Sharma, Y., Elgohary, A., Ho, B., Srivastava, M. and Chang, K.W. (2018) 'Generating natural language adversarial examples', in *Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP 2018)*. Brussels: Association for Computational Linguistics, pp. 2890-2896.

Bai, L., Yan, Y., Tang, K. and Li, Y. (2024) 'Automatic short answer grading with LLMs: a systematic review and empirical study', *International Journal of Artificial Intelligence in Education*, early online. doi: 10.1007/s40593-024-00411-9

Belinkov, Y. and Bisk, Y. (2018) 'Synthetic and natural noise both break neural machine translation', in *Proceedings of the 6th International Conference on Learning Representations (ICLR 2018)*.

Burrows, S., Gurevych, I. and Stein, B. (2015) 'The eras and trends of automatic short answer grading', *International Journal of Artificial Intelligence in Education*, 25(1), pp. 60-117.

Deane, P. (2013) 'On the relation between automated essay scoring and modern views of the writing construct', *Assessing Writing*, 18(1), pp. 7-24.

Ding, Y., Riordan, B., Horbach, A., Cahill, A. and Zesch, T. (2020) 'Don't take "nswvtnvakgxpm" for an answer – The surprising vulnerability of automatic content scoring systems to adversarial input', in *Proceedings of the 28th International Conference on Computational Linguistics (COLING 2020)*. Barcelona: International Committee on Computational Linguistics, pp. 882-892.

Dorsey, D. and Michaels, H. (2022) 'Validity arguments meet artificial intelligence in innovative educational assessment', *Journal of Educational Measurement*, 59(3), pp. 270-287.

Dzikovska, M., Nielsen, R., Brew, C., Leacock, C., Giampiccolo, D., Bentivogli, L., Clark, P., Dagan, I. and Dang, H.T. (2013) 'SemEval-2013 Task 7: the joint student response analysis and 8th recognizing textual entailment challenge', in *Proceedings of the 7th International Workshop on Semantic Evaluation (SemEval 2013)*. Association for Computational Linguistics, pp. 263-274.

Ebrahimi, J., Rao, A., Lowd, D. and Dou, D. (2018) 'HotFlip: white-box adversarial examples for text classification', in *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (ACL 2018)*. Melbourne: Association for Computational Linguistics, pp. 31-36.

Ferrara, S. and Qunbar, R. (2022) 'Validity arguments for AI-based automated scores: essay scoring as an illustration', *Journal of Educational Measurement*, 59(3), pp. 288-313.

Filighera, A., Ochs, S., Steuer, T. and Tregel, T. (2024) 'Cheating automatic short answer grading with the adversarial usage of adjectives and adverbs', *International Journal of Artificial Intelligence in Education*, 34(2), pp. 616-646.

Jin, D., Jin, Z., Zhou, J.T. and Szolovits, P. (2020) 'Is BERT really robust? A strong baseline for natural language attack on text classification and entailment', in *Proceedings of the Thirty-Fourth AAAI Conference on Artificial Intelligence (AAAI 2020)*. Palo Alto: AAAI Press, pp. 8018-8025.

Kane, M.T. (2006) 'Validation', in Brennan, R.L. (ed.) *Educational Measurement*, 4th edn. Westport, CT: American Council on Education/Praeger, pp. 17-64.

Korukonda, L., Naik, A. and Goo, D. (2021) 'Short answer scoring using transformer-based architectures with domain adaptation', *Education and Information Technologies*, 26(6), pp. 7211-7232.

Kumar, Y., Aggarwal, S., Mahata, D., Shah, R.R., Kumaraguru, P. and Zimmermann, R. (2020) 'Calling out bluff: attacking the robustness of automatic scoring systems with simple adversarial testing', *arXiv preprint* arXiv:2007.06796.

Latif, E., Mai, G., Nyaaba, M., Wu, X., Liu, N., Lu, G., Li, S., Liu, T. and Zhai, X. (2023) 'Automatic grading with large language models', *arXiv preprint* arXiv:2310.05920.

Loukina, A., Madnani, N. and Cahill, A. (2019) 'The many dimensions of algorithmic fairness in educational applications', in *Proceedings of the Fourteenth Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2019)*. Florence: Association for Computational Linguistics, pp. 1-11.

Messick, S. (1989) 'Validity', in Linn, R.L. (ed.) *Educational Measurement*, 3rd edn. Washington, DC: American Council on Education/Macmillan, pp. 13-103.

Mizumoto, A. and Eguchi, M. (2023) 'Exploring the potential of using an AI language model for automated essay scoring', *Research Methods in Applied Linguistics*, 2(2), 100050.

Mohler, M., Bunescu, R. and Mihalcea, R. (2011) 'Learning to grade short answer questions using semantic similarity measures and dependency graph alignments', in *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics (ACL 2011)*. Portland: Association for Computational Linguistics, pp. 752-762.

Morris, J., Lifland, E., Yoo, J.Y., Grigsby, J., Jin, D. and Qi, Y. (2020) 'TextAttack: a framework for adversarial attacks, data augmentation, and adversarial training in NLP', in *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations (EMNLP 2020)*. Association for Computational Linguistics, pp. 119-126.

Ramesh, D. and Sanampudi, S.K. (2022) 'An automated essay scoring systems: a systematic literature review', *Artificial Intelligence Review*, 55(3), pp. 2495-2527.

Ribeiro, M.T., Wu, T., Guestrin, C. and Singh, S. (2020) 'Beyond accuracy: behavioral testing of NLP models with CheckList', in *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*. Association for Computational Linguistics, pp. 4902-4912.

Riordan, B., Horbach, A., Cahill, A., Zesch, T. and Lee, C.M. (2017) 'Investigating neural architectures for short answer scoring', in *Proceedings of the 12th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2017)*. Copenhagen: Association for Computational Linguistics, pp. 217-227.

Shermis, M.D. (2022) 'Anchoring validity evidence for automated essay scoring', *Journal of Educational Measurement*, 59(3), pp. 314-334.

Sung, C., Dhamecha, T., Saha, S., Ma, T., Reddy, V. and Arora, R. (2019) 'Improving short answer grading using transformer-based pre-training', in *Intelligent Tutoring Systems* (Lecture Notes in Computer Science). Cham: Springer, pp. 491-502.

Wang, S., Liu, W., Zhang, Y., Zheng, X. and Gao, S. (2022) 'Measure and improve robustness in NLP models: a survey', in *Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL 2022)*. Seattle: Association for Computational Linguistics, pp. 4569-4588.

Williamson, D.M., Xi, X. and Breyer, F.J. (2012) 'A framework for evaluation and use of automated scoring', *Educational Measurement: Issues and Practice*, 31(1), pp. 2-13.

Zou, J., Shen, J., Zhao, S., Zhang, Q. and Liu, D. (2023) 'Robustness evaluation of transformer-based models in natural language processing: a survey', *IEEE Transactions on Neural Networks and Learning Systems*, early online. doi: 10.1109/TNNLS.2023.3276971
