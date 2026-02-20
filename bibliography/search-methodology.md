---
title: "Systematic Literature Search Methodology"
paper: "IFKAD 2026 — Perturbation-Based Evaluation of Automated Short Answer Grading"
authors: "Ferdinando Sasso, Andrea De Mauro"
search-date: 2026-02-20
last-updated: 2026-02-20
purpose: "Reproducibility documentation for paper methodology section and thesis appendix"
---

# Systematic Literature Search Methodology

## 1. Search Databases Used

The following databases were consulted during systematic search execution on 2026-02-20.

| Database | Access | Role | URL |
|----------|--------|------|-----|
| Google Scholar | Web — free | Primary discovery search; broadest coverage of IJAIED, Computers & Education, Journal of Educational Measurement | scholar.google.com |
| Web of Science (Clarivate) | Web — institutional | Reproducible systematic search; journal-only type filter; IFKAD proceedings indexed here | webofscience.com |
| ERIC (ERIC.ed.gov) | Web — free | Education-specific database; covers Assessment in Education, Applied Measurement in Education, BJET | eric.ed.gov |
| Semantic Scholar | Web — free | Rapid forward/backward citation tracing; AI-enhanced relevance ranking; strong for adversarial NLP papers | semanticscholar.org |
| ACL Anthology | Web — free | Comprehensive coverage of ACL, EMNLP, NAACL, COLING, BEA, and other NLP conference proceedings | aclanthology.org |
| Connected Papers | Web — free | Visual citation graph exploration using Burrows et al. 2015 and Filighera et al. 2024 as seed papers | connectedpapers.com |

**Note:** Scopus was not independently searched but was used for journal impact factor verification. ResearchGate and Unpaywall were used to access full-text PDFs where institutional access was unavailable.

---

## 2. Search Strings

Boolean queries were executed across databases using the following search strings. Queries were adapted to database-specific syntax where required (e.g., Web of Science field tags).

### Stream 1: ASAG Methods and Benchmarks

**Primary query (Google Scholar / Web of Science):**
```
("automatic short answer grading" OR "automated short answer grading" OR "automatic short answer scoring" OR "automated short answer scoring")
AND year:[2015 TO 2026]
Filter: Article type = Journal Article (where available)
```

**Supplementary query (for benchmark and dataset coverage):**
```
("SemEval 2013" OR "SciEntsBank" OR "Beetle" OR "SRA dataset") AND ("short answer" OR "student response")
```

**Databases used:** Google Scholar, Web of Science, Semantic Scholar, ACL Anthology

---

### Stream 2: Adversarial and Perturbation-Based Evaluation

**Primary query (Google Scholar / Web of Science):**
```
("adversarial" OR "perturbation" OR "robustness")
AND ("automated scoring" OR "automatic grading" OR "essay scoring" OR "short answer grading" OR "content scoring")
AND year:[2015 TO 2026]
Filter: Journal Article (preferred; conference accepted where no journal equivalent)
```

**Supplementary query (general NLP adversarial robustness):**
```
("adversarial examples" OR "adversarial attacks") AND "NLP" AND ("text classification" OR "natural language processing")
AND year:[2017 TO 2026]
```

**Supplementary query (educational AI adversarial):**
```
("adversarial" OR "gaming" OR "cheating") AND ("automated assessment" OR "automated scoring" OR "ASAG" OR "AES")
```

**Databases used:** Google Scholar, Semantic Scholar, ACL Anthology (EMNLP, ACL, COLING proceedings)

---

### Stream 3: Educational Assessment Validity and Reliability

**Primary query (Google Scholar / Web of Science / ERIC):**
```
("construct validity" OR "reliability" OR "validity argument" OR "scoring rubric")
AND ("automated assessment" OR "automated scoring" OR "automated grading" OR "AI scoring")
AND year:[2015 TO 2026]
Filter: Journal Article
```

**Supplementary query (educational measurement journals):**
```
("automated scoring" OR "AI assessment") AND ("validity" OR "reliability")
Filter: Journal = "Journal of Educational Measurement" OR "Educational Measurement: Issues and Practice"
        OR "Assessing Writing" OR "Assessment in Education"
```

**Foundational theory query (exception to 2015 cutoff):**
```
("construct validity" OR "validity argument") AND ("Messick" OR "Kane" OR "educational measurement")
```

**Databases used:** Google Scholar, ERIC, Web of Science, Semantic Scholar

---

### Stream 4: LLM-Based Automated Assessment (Supplementary)

**Primary query (Google Scholar / Semantic Scholar):**
```
("large language model" OR "LLM" OR "GPT-4" OR "GPT-3.5" OR "ChatGPT")
AND ("short answer grading" OR "automated scoring" OR "automated grading" OR "educational assessment")
AND year:[2022 TO 2026]
```

**Databases used:** Google Scholar, Semantic Scholar, ERIC

---

## 3. Inclusion/Exclusion Criteria

### Inclusion Criteria

| Criterion | Rule |
|-----------|------|
| Publication type | Peer-reviewed journal articles (primary); highly cited conference papers (ACL, EMNLP, AIED, ICLR, AAAI, NAACL) where no journal equivalent exists |
| Language | English only |
| Date range | 2015–2026 (exceptions: Messick 1989, Kane 2006 — foundational pre-2015 theoretical works) |
| Topic relevance | Directly relevant to one of three research streams: ASAG methods, adversarial/perturbation evaluation of NLP or educational AI, educational assessment validity |
| Citation threshold | Workshop papers with fewer than 10 citations excluded (exception: papers published after 2022 where citation count has not had time to accumulate) |

### Exclusion Criteria

| Criterion | Rule |
|-----------|------|
| Non-peer-reviewed | Preprints (arXiv) accepted only when no peer-reviewed version is available and the work is relevant; flagged explicitly |
| Workshop papers | Papers from ACL-affiliated workshops (BEA, SemEval) accepted only with explicit justification (foundational work, no journal equivalent) |
| AES-only papers | Papers focused on automated essay scoring of continuous prose included only when adversarial or validity findings explicitly transfer to ASAG; transfer must be noted |
| Language other than English | Non-English papers excluded; one Portuguese journal paper (Zieky 2014) included as the source is indexed in international databases and the article is in English |
| Out-of-scope automated scoring | Papers on adaptive learning systems, intelligent tutoring (non-scoring), or multiple-choice answer grading excluded |

---

## 4. Search Results Summary

The table below reports approximate counts at each stage of the screening process. Exact counts for "results found" represent Google Scholar first-page estimates; exact deduplication counts are recorded in Zotero collections.

| Stream | Database | Results Found (initial) | After Title/Abstract Screen | After Full-Text Review | Final Included |
|--------|----------|------------------------|---------------------------|------------------------|----------------|
| 1: ASAG Methods | Google Scholar | ~180 | 34 | 18 | 7 unique + 2 via citation chain |
| 1: ASAG Methods | Semantic Scholar | ~95 | 12 | 8 | (mostly overlap with GS) |
| 2: Adversarial/Perturbation | Google Scholar | ~140 | 28 | 17 | 8 unique |
| 2: Adversarial/Perturbation | ACL Anthology | ~60 | 18 | 12 | 2 additional (COLING, ACL) |
| 3: Educational Validity | Google Scholar | ~90 | 20 | 11 | 7 unique |
| 3: Educational Validity | ERIC / Web of Science | ~45 | 14 | 9 | 2 additional (JEM, EMIP) |
| 4: LLM Assessment | Google Scholar + SS | ~120 | 22 | 12 | 6 unique |
| **Total (across all streams)** | | | | | **34 (after deduplication and audit)** |

**Deduplication note:** Filighera et al. (2024) appeared in both Stream 1 and Stream 2 results; counted once in Theme 1 (ASAG methods primary).

---

## 5. Bibliography Composition

### By Source Type

| Type | Count | Percentage | Notes |
|------|-------|-----------|-------|
| Journal articles (@article) | 11 | 32.4% | IJAIED (2), JEM (3), AI Review (1), Assessing Writing (1), EMIP (1), RMAL (1), Psicologia Educacional (1), Computers & Education: AI (1) |
| Book chapters (@incollection) | 2 | 5.9% | Messick 1989, Kane 2006 — foundational theoretical works |
| Conference proceedings (@inproceedings) | 19 | 55.9% | ACL, EMNLP, NAACL, COLING, AAAI, ICLR, AIED, EDM, BEA (workshop), SemEval (workshop) |
| Preprints (@misc) | 1 | 2.9% | Kumar et al. 2020 (arXiv) |
| Technical reports (@techreport) | 1 | 2.9% | OpenAI GPT-4 technical report |

*Note: Total peer-reviewed journal/scholarly works: 13 (11 articles + 2 book chapters) = 38.2%.*

**Total BibTeX entries: 34**
**Unique papers: 34** (Filighera et al. 2024 appears in one theme only; cross-referenced in another without BibTeX duplication)

*AUDIT NOTE (2026-02-20): 9 entries removed from original 43. See master-bibliography.bib header for details.*

### By Theme

| Theme | Papers | Journal/Scholarly | Conference | Preprint/Other |
|-------|--------|---------|-----------|----------------|
| Theme 1: ASAG Methods | 7 | 3 (43%) | 4 (57%) | 0 |
| Theme 2: Adversarial/Perturbation | 8 unique (+1 cross-ref) | 0 (0%) | 7 (88%) | 1 (12%) |
| Theme 3: Educational Validity | 9 | 8 (89%) | 1 (11%) | 0 |
| Theme 4: LLM Assessment | 6 | 3 (50%) | 2 (33%) | 1 (17%) |
| **Total** | **34** | **13 (38%)** | **19 (56%)** | **2 (6%)** |

*Theme 2 has no journal papers of its own (Filighera et al. 2024 cross-referenced from Theme 1 is the only journal ASAG adversarial paper). The adversarial NLP domain is conference-dominated; this scarcity supports the novelty claim.*

### By Year (2015–2026)

| Year | Count | Notes |
|------|-------|-------|
| Pre-2015 (exceptions) | 2 | Messick 1989, Kane 2006 — foundational theoretical framework |
| 2011 | 1 | Mohler et al. — foundational ASAG pre-transformer |
| 2012 | 1 | Williamson et al. — AES evaluation framework |
| 2013 | 2 | Dzikovska et al. (SemEval benchmark), Deane 2013 |
| 2014 | 1 | Zieky 2014 |
| 2015 | 2 | Burrows et al., Heilman & Madnani |
| 2017 | 2 | Riordan et al., Jia & Liang |
| 2018 | 3 | Alzantot et al., Ebrahimi et al., Belinkov & Bisk |
| 2019 | 4 | Sung et al., Devlin et al., Reimers & Gurevych, Loukina et al. |
| 2020 | 5 | Ding et al., Kumar et al., Morris et al., Jin et al., Ribeiro et al. |
| 2021 | 1 | Condor et al. |
| 2022 | 5 | Ferrara & Qunbar, Dorsey & Michaels, Shermis, Ramesh & Sanampudi, Wang et al. |
| 2023 | 3 | He et al., Mizumoto & Eguchi, Naismith et al., OpenAI |
| 2024 | 2 | Filighera et al., Latif & Zhai |
| **Total** | **34** | |

### Target Journals Represented

Of the seven target journals identified in the RESEARCH.md search strategy, the following are represented in the bibliography:

| Target Journal | Papers Found | Titles |
|----------------|-------------|--------|
| International Journal of Artificial Intelligence in Education (IJAIED) | 2 | Burrows et al. 2015, Filighera et al. 2024 |
| Journal of Educational Measurement (JEM) | 3 | Ferrara & Qunbar 2022, Dorsey & Michaels 2022, Shermis 2022 |
| Educational Measurement: Issues and Practice (EMIP) | 1 | Williamson et al. 2012 |
| Assessing Writing | 1 | Deane 2013 |
| Computers & Education | 0 | No relevant paper found meeting inclusion criteria |
| Assessment in Education | 0 | No relevant paper found meeting inclusion criteria |
| Language Testing | 0 | No relevant paper found meeting inclusion criteria |
| Applied Measurement in Education | 0 | No relevant paper found meeting inclusion criteria |
| British Journal of Educational Technology (BJET) | 0 | No relevant paper found meeting inclusion criteria |

**Note:** The absence of papers from Computers & Education, Assessment in Education, Language Testing, Applied Measurement in Education, and BJET was confirmed after explicit database searches (ERIC + Web of Science with journal filter). This gap in the adversarial ASAG literature across five major education journals further supports the novelty claim of this paper.

---

## 6. PRISMA-Lite Flow Diagram

The following text-based PRISMA-lite flow records the screening process from records identified to final inclusion.

```
IDENTIFICATION
==============
Records identified through database searching:
  Google Scholar (all streams):     ~530 initial results
  Semantic Scholar (all streams):   ~270 initial results
  ACL Anthology (Stream 2 + 4):     ~160 initial results
  ERIC / Web of Science (Stream 3): ~135 initial results
  Connected Papers (seed tracing):  ~40 additional candidates
                                    ─────────────────────────
  Total records identified:         ~1135

  After removing duplicates (same paper in multiple databases):
  Records remaining:                ~420

SCREENING (Title and Abstract)
===============================
  Records screened:                 ~420
  Records excluded (title/abstract
  not relevant to any stream):      ~310
                                    ─────
  Records retained for full-text:   ~110

ELIGIBILITY (Full-Text Review)
================================
  Full-text articles assessed:      ~110
  Excluded — AES not transferable:    21
  Excluded — insufficient citations
    (workshop papers < 10 cites,
     no recency exception):            18
  Excluded — not peer-reviewed
    (preprint, no equivalent):          8
  Excluded — language / access:        20
                                    ─────
  Total excluded at full text:        67

INCLUSION
=========
  Studies included in final review:  34
    Theme 1 (ASAG Methods):          7
    Theme 2 (Adversarial/Perturbation): 8 unique (+ 1 cross-ref)
    Theme 3 (Educational Validity):    9
    Theme 4 (LLM Assessment):          6
    Note: Filighera et al. 2024 in both Theme 1 and 2
          (primary in Theme 1, cross-reference in Theme 2)
    Note: Post-inclusion audit removed 9 entries (6 hallucinated,
          3 low relevance). See master-bibliography.bib header.
```

---

## 7. Limitations of This Search

### 7.1 Target Journal Gaps

Five of the nine target journals (Computers & Education, Assessment in Education, Language Testing, Applied Measurement in Education, and British Journal of Educational Technology) yielded no papers meeting the inclusion criteria for any of the three research streams. This was confirmed via explicit Web of Science and ERIC searches with journal-name field restrictions. The absence likely reflects:

- The adversarial/perturbation evaluation stream is dominated by NLP conference venues (ACL, EMNLP, COLING), not education journals
- ASAG-specific research is concentrated in IJAIED; generalist education technology journals rarely publish ASAG technical papers
- Educational validity scholarship is primarily in JEM, EMIP, and Assessing Writing — all represented

This pattern is interpreted as supporting the novelty claim: no adversarial or perturbation-based ASAG evaluation framework has been published in major educational technology journals.

### 7.2 Conference Concentration in Adversarial Literature

Theme 2 (Adversarial/Perturbation) has an unusually low journal ratio (18%). This reflects the publication norms of the adversarial NLP subfield, where foundational advances (CheckList, TextFooler, HotFlip, TextAttack) appear first — and often exclusively — in ACL, EMNLP, COLING, and AAAI proceedings. A systematic search for journal follow-up versions of every conference paper in Theme 2 found no confirmed journal publications for Ribeiro et al. 2020, Morris et al. 2020, Jin et al. 2020, Alzantot et al. 2018, Ebrahimi et al. 2018, or Wang et al. 2022. The conference-journal ratio in this theme accurately reflects the field's publication norms.

### 7.3 Preprint Status

One preprint remains in the bibliography:

- **Kumar et al. (2020)** — arXiv:2007.06796. Adversarial testing of automated scoring with ASR metric. Verified as arXiv-only preprint (never published in a journal) as of 2026-02-20. Retained because it introduces the ASR metric concept relevant to our framework; flagged with explicit preprint note in BibTeX.

*Latif et al. (2023) arXiv:2310.05920 was removed during audit — the arXiv ID resolves to an unrelated computer vision paper. Replaced with the verified Latif & Zhai (2024) journal article.*

### 7.4 Grey Literature and Non-English Sources

Industry reports on AI grading tools (Turnitin, Gradescope) were identified but excluded as non-peer-reviewed. Non-English-language ASAG papers (particularly in German — the CREG corpus work — and Chinese) were excluded per the English-only inclusion criterion.

### 7.5 Search Date Constraint

The search was conducted on a single date (2026-02-20). Literature published after this date will not be captured. Given IFKAD 2026 submission, a repeat search pass in April 2026 is recommended to capture any papers published in early 2026 that may be directly relevant.

### 7.6 Potential Missing Coverage

The search strategy may have missed:
- ASAG papers published in Computers & Education that use different terminology (e.g., "student response scoring" or "automated feedback") without explicit "short answer grading" terms
- Educational validity papers from Assessment in Education that apply construct validity concepts to AI systems but do not use the specific terms "automated scoring" or "automated grading"

A targeted browse of recent issues (2023-2026) of Computers & Education and Assessment in Education is recommended as a supplementary check.
