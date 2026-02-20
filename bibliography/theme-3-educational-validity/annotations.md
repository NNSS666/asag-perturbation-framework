# Theme 3: Educational Assessment Validity and Reliability

**Search queries used:**
- "construct validity" "automated scoring" OR "automated grading" journal 2015-2026
- "reliability" "rubric" "automated assessment" journal
- "validity argument" "artificial intelligence" scoring journal
- "scoring rubric" validity "short answer" journal

**Inclusion criteria:** Peer-reviewed journal articles (strongly prioritized for this theme); English; 2015-2026 (Messick 1989 included as foundational exception); directly relevant to construct validity, assessment reliability, rubric-based scoring, or validity arguments for automated AI-based scoring.

**Type count:** Journal: 8 | Conference: 1 | Total: 9

---

## Ferrara and Qunbar (2022)

**Citation (Harvard):** Ferrara, S. and Qunbar, R. (2022) 'Validity arguments for AI-based automated scores: essay scoring as an illustration', *Journal of Educational Measurement*, 59(3), pp. 288-313. doi: 10.1111/jedm.12333

**Journal:** Journal of Educational Measurement (JEM) | **Impact Factor:** ~1.8 | **Type:** Journal

**Research Question:** What constitutes a validity argument for AI-based automated scoring, and what evidence is needed to support such arguments?

**Methodology:** Theoretical framework development applying Messick's (1989) validity theory and Kane's (2006) validity argument framework to AI-based scoring; essay scoring used as primary illustration; case analysis of existing automated scoring validation studies.

**Key Findings:**
- Validity arguments for AI-based scores must demonstrate that score variation reflects intended constructs (construct-relevant) not unintended features (construct-irrelevant variance)
- Existing AES validation studies focus on criterion-related validity (correlation with human scores) but neglect construct validity evidence — specifically, they do not test whether models score based on relevant content features
- The paper introduces the distinction between "construct-relevant scoring" and "construct-irrelevant scoring" as a key validity dimension for automated systems

**Relevance to This Paper:**
- Theme: Educational validity
- How it supports our work: Provides the theoretical vocabulary for our paper's central argument: standard ASAG evaluation (correlation with human grades) does not establish construct validity; our perturbation framework is a direct operationalization of Ferrara and Qunbar's call for construct-relevant scoring tests; IVR (invariance under meaning-preserving changes) and SSR (sensitivity to meaning-altering changes) directly test construct-relevant vs. construct-irrelevant feature reliance
- Citation context: intro, related-work-2.3, gap-statement

**Limitations:** Primarily theoretical; essay scoring illustration; no empirical test proposed; does not address short answer grading specifically; JEM audience is measurement specialists (may need bridging for NLP audience)

---

## Dorsey and Michaels (2022)

**Citation (Harvard):** Dorsey, D. and Michaels, H. (2022) 'Validity arguments meet artificial intelligence in innovative educational assessment', *Journal of Educational Measurement*, 59(3), pp. 270-287. doi: 10.1111/jedm.12330

**Journal:** Journal of Educational Measurement (JEM) | **Impact Factor:** ~1.8 | **Type:** Journal

**Research Question:** How should AI-based educational assessment systems be evaluated from a validity perspective, and what new challenges does AI create for the validity argument?

**Methodology:** Conceptual analysis of AI-in-assessment validity challenges; review of current automated scoring validation practice; framework extension from Kane (2006) interpretive argument to AI-specific validity dimensions; comparison with human scoring validity arguments.

**Key Findings:**
- AI-based scoring introduces new validity threats not present in human scoring: unexplained feature reliance, distributional shift vulnerability, and lack of interpretable scoring rationale
- Standard criterion-related validity evidence (correlation with human scores) is necessary but insufficient; AI systems must also show evidence of appropriate feature use
- The authors call for "construct-relevant features" testing as a validity requirement: AI scores should change when and only when the intended construct changes

**Relevance to This Paper:**
- Theme: Educational validity
- How it supports our work: Directly states the validity gap our paper fills: AI scoring systems are not tested for appropriate feature use (construct-relevant features); our three perturbation families operationalize exactly this test — invariance family tests stability under construct-irrelevant changes; sensitivity family tests responsiveness to construct-relevant changes; gaming family tests resistance to construct-irrelevant score inflation
- Citation context: related-work-2.3, gap-statement

**Limitations:** Theoretical/conceptual paper; essay scoring and licensure exam context; does not propose an empirical operationalization of the construct-relevant feature test; JEM audience

---

## Shermis (2022)

**Citation (Harvard):** Shermis, M.D. (2022) 'Anchoring validity evidence for automated essay scoring', *Journal of Educational Measurement*, 59(3), pp. 314-334. doi: 10.1111/jedm.12336

**Journal:** Journal of Educational Measurement (JEM) | **Impact Factor:** ~1.8 | **Type:** Journal

**Research Question:** How can automated essay scoring systems build a validity evidence base anchored in established assessment theory?

**Methodology:** Review and synthesis of validity evidence types (content, criterion, construct) as applied to AES systems; case study of operational AES programs (e-rater, Turnitin); empirical analysis of where current validation fails to meet Messick's (1989) standards.

**Key Findings:**
- Operational AES systems have accumulated extensive criterion-related validity evidence (correlation with human raters at 0.80-0.95) but limited construct validity evidence
- Content validity (are the scored features actually writing quality indicators?) is rarely tested; most AES features are selected empirically, not theoretically
- Shermis proposes a "validity anchoring" approach: explicitly mapping each model feature to an intended construct component before deployment

**Relevance to This Paper:**
- Theme: Educational validity
- How it supports our work: Reinforces the criterion-related-only validity problem; the "feature-to-construct" mapping Shermis proposes for AES is operationalized in our framework via perturbation testing — features that are construct-relevant should produce scoring changes only when the construct genuinely changes; NOTE — AES context; transferability to ASAG is direct because the construct validity problem (are features rubric-grounded?) is identical
- Citation context: related-work-2.3

**Limitations:** AES focus (not ASAG specifically); primarily descriptive; does not propose empirical tests; JEM audience may not be familiar with NLP/transformer methods

---

## Messick (1989)

**Citation (Harvard):** Messick, S. (1989) 'Validity', in Linn, R.L. (ed.) *Educational Measurement*, 3rd edn. Washington, DC: American Council on Education/Macmillan, pp. 13-103.

**Journal:** Book chapter in Educational Measurement (American Council on Education) | **Type:** Journal (book chapter — treated as peer-reviewed scholarly work) — exception: Pre-2015 foundational text; the unified validity framework in this chapter is the canonical theoretical foundation cited by all educational measurement scholars including Ferrara 2022, Dorsey 2022, and Shermis 2022

**Research Question:** What is validity in educational measurement, and how should validity evidence be collected and interpreted?

**Methodology:** Theoretical synthesis of validation theory; proposes unified validity framework incorporating content, criterion, construct, and consequential validity; refutes fragmented validity view (content validity, criterion validity as separate types).

**Key Findings:**
- Validity is unified: all forms of validity evidence (content, criterion, construct, consequential) contribute to a single overall validity judgment about score interpretation
- Construct validity is the central concept: score interpretations must be grounded in evidence that the measured construct is actually what varies when scores vary
- Construct-irrelevant variance (scores influenced by features outside the intended construct) is a validity threat even when criterion validity (correlation with other measures) is high

**Relevance to This Paper:**
- Theme: Educational validity
- How it supports our work: Provides the canonical theoretical grounding for our paper's central argument; "construct-irrelevant variance" is precisely what our perturbation tests measure — invariance perturbations test whether construct-irrelevant changes (paraphrase, style) affect scores; our framework is an empirical operationalization of Messick's construct validity requirements for ASAG
- Citation context: intro, related-work-2.3

**Limitations:** 1989 chapter; predates machine learning and AI-based scoring; extremely broad theoretical scope; the construct validity argument must be updated for algorithmic scoring contexts (which Ferrara 2022, Dorsey 2022 do)

---

## Kane (2006)

**Citation (Harvard):** Kane, M.T. (2006) 'Validation', in Brennan, R.L. (ed.) *Educational Measurement*, 4th edn. Westport, CT: American Council on Education/Praeger, pp. 17-64.

**Journal:** Book chapter in Educational Measurement (American Council on Education) | **Type:** Journal (book chapter) — exception: Pre-2015 foundational text; Kane's interpretive argument framework is cited by Ferrara 2022 and Dorsey 2022 as the primary validity argument structure for AI scoring

**Research Question:** How should test developers construct and evaluate validity arguments for score interpretations?

**Methodology:** Framework development for validity arguments (interpretive argument); proposes linking assumptions and inferences in a chain from observed performance to score meaning; guidelines for identifying validity threats.

**Key Findings:**
- Validity argument is a chain of inferences from performance (e.g., student answer) to intended score meaning (e.g., conceptual understanding); each inference must be supported by evidence
- Any factor that disrupts the inference chain — such as construct-irrelevant variance — undermines the validity argument
- Scoring inferences must be tested: does score variation reflect intended construct variation?

**Relevance to This Paper:**
- Theme: Educational validity
- How it supports our work: Provides the "inference chain" framing for ASAG validity: the inference from "student answer" to "score represents understanding" is broken when the grader relies on surface cues (adjective stuffing, keyword overlap); our perturbation tests empirically test the scoring inference link in the chain
- Citation context: related-work-2.3

**Limitations:** Book chapter; 2006 (pre-deep learning); theoretical framework without computational operationalization

---

## Zieky (2014)

**Citation (Harvard):** Zieky, M. (2014) 'An introduction to the use of evidence-centered design in test development', *Psicologia Educacional*, 20(1), pp. 7-20. doi: 10.17575/rpsicped.v20i1.497

**Journal:** Psicologia Educacional | **Type:** Journal

**Research Question:** How can evidence-centered design (ECD) be used to create principled, validity-grounded assessments?

**Methodology:** Conceptual introduction to ECD; describes the student model (what to measure), task model (what tasks elicit it), and evidence model (what responses indicate what competencies); examples from large-scale assessment programs.

**Key Findings:**
- ECD requires explicit specification of the student model before assessment design — what knowledge, skills, and abilities constitute the construct
- Evidence rules connect observable features of student responses to latent construct estimates; construct-irrelevant features should not appear in evidence rules
- ECD provides a framework for identifying when automated scoring evidence rules violate construct validity (e.g., grading based on essay length rather than content quality)

**Relevance to This Paper:**
- Theme: Educational validity
- How it supports our work: ECD's "evidence model" provides theoretical grounding for what grader features should and should not influence scores; our sensitivity perturbations test whether meaning-altering changes trigger appropriate score changes (correct evidence rules); our invariance perturbations test whether meaning-preserving changes correctly leave scores unchanged (no construct-irrelevant features)
- Citation context: related-work-2.3

**Limitations:** Introductory overview; does not address automated/AI scoring specifically; Portuguese journal (limited visibility in NLP community)

---

## Deane (2013)

**Citation (Harvard):** Deane, P. (2013) 'On the relation between automated essay scoring and modern views of the writing construct', *Assessing Writing*, 18(1), pp. 7-24. doi: 10.1016/j.asw.2012.10.002

**Journal:** Assessing Writing | **Impact Factor:** ~3.4 | **Type:** Journal

**Research Question:** How well do current automated essay scoring systems align with contemporary theories of writing as a construct?

**Methodology:** Theoretical analysis comparing AES scoring features (lexical, syntactic, coherence, discourse) against writing construct definitions from composition research; qualitative mapping of AES features to construct components.

**Key Findings:**
- AES systems capture surface writing features (vocabulary richness, sentence length, syntactic complexity) but miss higher-order writing qualities (argument structure, audience awareness, discourse coherence)
- The discrepancy between measured features and construct creates construct-irrelevant variance: systems reward surface features even when the intended construct is higher-order writing competence
- High-scoring AES features can be gamed by producing long, complex-structured but vacuous text

**Relevance to This Paper:**
- Theme: Educational validity
- How it supports our work: Establishes the construct-irrelevance problem empirically for AES, which directly parallels the ASAG problem; "gaming long, complex-structured but vacuous text" is the AES equivalent of adjective/adverb stuffing in ASAG (Filighera et al.); NOTE — AES focus; transferability to ASAG is direct for the gaming perturbation argument
- Citation context: related-work-2.3

**Limitations:** AES context; writing construct may differ from ASAG construct (factual accuracy vs. writing quality); journal is Assessing Writing (writing studies audience, not NLP/AI)

---

## Williamson et al. (2012)

**Citation (Harvard):** Williamson, D.M., Xi, X. and Breyer, F.J. (2012) 'A framework for evaluation and use of automated scoring', *Educational Measurement: Issues and Practice*, 31(1), pp. 2-13. doi: 10.1111/j.1745-3992.2011.00223.x

**Journal:** Educational Measurement: Issues and Practice (EMIP) | **Type:** Journal

**Research Question:** What framework should guide the evaluation and deployment decisions for automated scoring systems in high-stakes assessment?

**Methodology:** Framework development drawing on validity theory, operational experience with e-rater and other AES systems, and a review of automated scoring studies; proposes seven evaluation criteria for AS deployment.

**Key Findings:**
- Automated scoring evaluation must include evidence from seven domains: accuracy, fairness, ability to detect construct-irrelevant responses, scoring model transparency, human-machine score agreement, subgroup fairness, and robustness to gaming
- "Robustness to gaming" is explicitly listed as an evaluation criterion — the system should not increase scores for responses that insert keywords or add irrelevant content
- Current operational practice underweights robustness-to-gaming evidence compared to human-machine agreement evidence

**Relevance to This Paper:**
- Theme: Educational validity
- How it supports our work: Directly names robustness to gaming as an evaluation criterion for automated scoring — our ASR metric is an empirical operationalization of exactly this criterion; the seven-domain framework contextualizes our three-metric framework (IVR, SSR, ASR) as addressing validity dimensions that operational scoring evaluation currently neglects
- Citation context: related-work-2.3, gap-statement

**Limitations:** Framework paper; primarily descriptive; essay scoring context (e-rater, Turnitin); does not propose specific empirical tests; predates transformer-based models

---

## Loukina et al. (2019)

**Citation (Harvard):** Loukina, A., Madnani, N. and Cahill, A. (2019) 'The many dimensions of algorithmic fairness in educational applications', in *Proceedings of the Fourteenth Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2019)*. Florence: Association for Computational Linguistics, pp. 1-11. doi: 10.18653/v1/W19-4401

**Journal:** BEA 2019 Workshop Proceedings | **Type:** Conference — justified: Directly addresses algorithmic bias and fairness in automated scoring; highly relevant for validity framing; no journal version; workshop paper at ACL-affiliated venue

**Research Question:** What are the dimensions of algorithmic fairness that matter for educational NLP applications, and how can they be measured?

**Methodology:** Conceptual review of algorithmic fairness definitions applied to educational NLP (scoring, grading, feedback); empirical examination of score disparities by demographic group in an operational scoring system; bias measurement approaches reviewed.

**Key Findings:**
- Algorithmic fairness in educational scoring has multiple dimensions (demographic parity, equalized odds, calibration) that are mathematically incompatible — optimization for one reduces others
- Current automated scoring fairness evaluation focuses on group-level mean score differences but neglects item-level or response-level bias
- Construct-irrelevant features (e.g., dialect markers, cultural references) create systematic fairness violations in automated scoring

**Relevance to This Paper:**
- Theme: Educational validity
- How it supports our work: Demonstrates that construct-irrelevant features create both validity and fairness problems simultaneously; the gaming perturbation family in our framework tests construct-irrelevant score inflation, which is a fairness threat as well as a validity threat; contextualizes our framework within the broader automated assessment evaluation literature
- Citation context: related-work-2.3

**Limitations:** Workshop paper; fairness focus (not purely validity); demographic group analysis requires data on student demographics (not available in our public datasets)

---

*Note: This theme has strong journal coverage — 8 of 9 entries are peer-reviewed journal articles or peer-reviewed book chapters. The Journal of Educational Measurement (JEM) is represented by 3 papers (Ferrara 2022, Dorsey 2022, Shermis 2022), which is exactly what the search strategy targeted. Educational measurement journals (JEM, EMIP, Assessing Writing) provide the theoretical vocabulary for the paper's validity argument framing.*
