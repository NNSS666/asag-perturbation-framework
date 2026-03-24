# ASAG Perturbation Framework

## Ultimo aggiornamento automatico
2026-03-17

## Cos'è
Un framework di valutazione basato su perturbazioni per sistemi di Automated Short Answer Grading (ASAG). Progetto di tesi magistrale alla LUISS Guido Carli (autore: Ferdinando Sasso, relatore: Prof. Andrea De Mauro), con abstract accettato alla conferenza IFKAD 2026 (Budapest, 1-3 luglio). Il framework genera 7 tipi di perturbazioni controllate sulle risposte degli studenti (sinonimi, typo, negazione, cancellazione concetti chiave, contraddizione semantica, keyword stuffing, estensione fluente errata) e misura se il grader reagisce correttamente, producendo metriche di robustezza (IVR, SSR, ASR) che complementano le tradizionali accuracy e QWK. Si rivolge a ricercatori in NLP educativo e a chiunque debba validare la robustezza di un sistema di valutazione automatica.

## Stack tecnico
- **Linguaggio:** Python 3.9+ (compatibilità esplicita in tutto il codebase)
- **Data modeling:** Pydantic v2 (modelli frozen/immutabili, validazione fail-fast)
- **Datasets:** HuggingFace `datasets` (caricamento da nkazi/Beetle e nkazi/SciEntsBank)
- **ML/Classificazione:** scikit-learn (LogisticRegression, StandardScaler, StratifiedShuffleSplit, LeaveOneGroupOut)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2, 384 dim)
- **NLP:** NLTK (WordNet, POS tagging, word_tokenize)
- **Numerica:** NumPy
- **Testing:** pytest (77 test, marker `slow` per E2E)
- **Serializzazione:** JSON / JSONL nativo
- **Nessun Docker, nessun database, nessun frontend** — puro Python scientifico

## Architettura
Il progetto segue un'architettura a pipeline modulare con 8 package sotto `src/asag/`:

```
schema/          → Modelli canonici (QuestionRecord, AnswerRecord, PerturbationRecord, GradeLabel)
                   Tutti i dati fluiscono come istanze Pydantic validate, mai dict grezzi.

loaders/         → Caricamento dataset via ABC pluggabile. SemEval2013Loader concatena
                   tutti gli split HF in un pool unico (nessun uso degli split originali).

splitters/       → Due protocolli di splitting:
                   Protocol A (LOQO) — leave-one-question-out cross-validation
                   Protocol B — within-question 80/20 stratificato
                   + diagnostica leakage per integrità scientifica.

graders/         → Interfaccia ABC (GraderInterface → GradeResult).
                   Implementato: HybridGrader (4 feature linguistiche + 384-dim SBERT
                   → 388-dim → StandardScaler + LogisticRegression).
                   Previsti: DeBERTa-v3, ModernBERT, GPT-4o.

perturbations/   → PerturbationEngine orchestra 7 generatori rule-based:
                   - Invariance: SynonymSubstitution (WordNet), TypoInsertion
                   - Sensitivity: NegationInsertion, KeyConceptDeletion, SemanticContradiction
                   - Gaming: RubricKeywordEchoing, FluentWrongExtension
                   Due gate di validazione (SBERT cosine ≥ 0.85, euristica negazione/antonimi)
                   + cache JSONL hash-keyed per idempotenza.

metrics/         → MetricCalculator con 4 metriche duali:
                   IVR_flip, IVR_absdelta, SSR_directional, ASR_thresholded.
                   MetricResult/MetricSuite come modelli Pydantic.

evaluation/      → EvaluationEngine orchestra l'intero loop:
                   split → fit grader → filtra perturbazioni su test set → grade → metriche
                   → aggregazione → robustness drop (delta Proto A - Proto B).

infra/           → Seeds isolati per componente (SeedConfig), storage JSONL/JSON,
                   run directory auto-named, cattura versioni librerie.
```

Il flusso dati è unidirezionale: Loader → Splitter → Grader.fit() → PerturbationEngine → Grader.grade() → MetricCalculator → EvaluationResult → JSON su disco.

## Stato attuale
**Implementato e funzionante:**
- Schema canonico completo con validazione Pydantic v2
- Loader SemEval 2013 (Beetle e SciEntsBank) da HuggingFace
- Entrambi i protocolli di splitting (A: LOQO, B: within-question) con diagnostica leakage
- HybridGrader (SBERT + feature linguistiche + LogisticRegression)
- Tutti 7 generatori di perturbazione rule-based
- Due gate di qualità (SBERT cosine, euristica negazione/antonimi)
- Cache perturbazioni con hash MD5
- MetricCalculator con tutte 4 le metriche
- EvaluationEngine con loop completo Protocol A + B e robustness drop
- Infrastruttura: seed management, storage, run directory, version tracking
- 77 test (unit + E2E)
- Prima run sperimentale completata: HybridGrader × Beetle (5.199 risposte, ~41K perturbazioni)
- Bibliografia sistematica con 33 voci annotate su 4 temi
- Methodology proposal (PDF) per IFKAD 2026

**Da fare (fasi successive):**
- Fase 4: Fine-tuning DeBERTa-v3-base e ModernBERT-base come grader transformer
- Fase 5: GPT-4o zero-shot con rubric prompt come grader LLM
- Fase 6: Analisi statistica e visualizzazioni dei risultati
- Estensione al corpus SciEntsBank (loader pronto, run non ancora eseguita)

## File e cartelle chiave
| File/Cartella | Descrizione |
|---|---|
| `src/asag/schema/records.py` | Modelli canonici: QuestionRecord, AnswerRecord, PerturbationRecord |
| `src/asag/loaders/semeval2013.py` | Loader SemEval 2013 da HuggingFace con deduplicazione e normalizzazione |
| `src/asag/graders/hybrid.py` | HybridGrader: feature extraction + SBERT + LogisticRegression (388-dim) |
| `src/asag/perturbations/engine.py` | PerturbationEngine: orchestra 7 generatori + gate + cache |
| `src/asag/perturbations/generators/` | 7 generatori (invariance.py, sensitivity.py, gaming.py) |
| `src/asag/perturbations/gates.py` | Gate 1 (SBERT cosine) + Gate 2 (negazione/antonimi) + GateLog |
| `src/asag/metrics/calculator.py` | MetricCalculator: IVR_flip, IVR_absdelta, SSR_directional, ASR_thresholded |
| `src/asag/evaluation/engine.py` | EvaluationEngine: loop completo Protocol A/B + robustness drop |
| `src/asag/splitters/` | Protocol A (LOQO), Protocol B (within-question), diagnostica leakage |
| `src/asag/infra/` | Seeds, storage JSONL/JSON, run directory, version tracking |
| `scripts/first_real_run.py` | Script per eseguire la pipeline completa su Beetle |
| `tests/` | 77 test unitari e E2E |
| `bibliography/` | 33 voci BibTeX + annotazioni su 4 temi + search methodology |
| `docs/methodology-proposal-en.pdf` | Proposta metodologica per IFKAD 2026 |
| `requirements.txt` | Dipendenze: pydantic, datasets, scikit-learn, numpy, sentence-transformers, nltk, pytest |

## Decisioni e pattern rilevanti
- **Modelli immutabili (frozen=True):** tutti i modelli Pydantic sono frozen per prevenire mutazioni accidentali nel pipeline.
- **Normalizzazione [0,1]:** tutti gli score sono normalizzati a float [0.0, 1.0] dal loader, indipendentemente dallo schema del dataset originale (5-way → {0.0, 0.5, 1.0}).
- **Nessun retry dopo gate rejection:** i candidati rifiutati dai gate NON vengono rigenerati. Il tasso di rifiuto è esso stesso un risultato di ricerca.
- **IEEE 754 protection:** confronti float con arrotondamento a 6 decimali (`SCORE_PRECISION = 6`) per evitare falsi positivi.
- **Seed isolation:** ogni componente (splitter, perturbation, training) ha il suo seed indipendente tramite `SeedConfig`, abilitando ablazioni controllate.
- **LOQO leakage check:** diagnostica automatica prima di ogni fold per verificare che il testo della domanda held-out non compaia nel training set.
- **Compatibilità Python 3.9:** uso esplicito di `typing.Optional`, `typing.List`, etc. (non sintassi `X | Y`).
- **Gate 1 bypass per typo:** i typo saltano Gate 1 (SBERT) perché lo shift di embedding è atteso ma non semanticamente significativo.
- **Fallback grading per LLM:** `_grade_single()` prova a passare `reference_answer` come kwarg; se il grader non lo accetta (TypeError), riprova senza.
- **Cache pre-gate:** le perturbazioni sono cachate prima dell'applicazione dei gate, garantendo che i cache hit producano gli stessi risultati di gate.
- **Sorting deterministico:** sinonimi WordNet ordinati alfabeticamente, reference answers ordinati nel loader, per garantire riproducibilità cross-platform.

## Contenuti e copy (se presenti)
Non ci sono sales page, email, landing page o contenuti marketing. Il progetto è puramente accademico. I contenuti testuali presenti sono:
- `README.md`: documentazione tecnica del progetto con tabella risultati preliminari
- `docs/methodology-proposal-en.pdf`: proposta metodologica formale per la conferenza IFKAD 2026
- `Abstract IFKAD 2026 - Ferdinando Sasso, Andrea De Mauro.docx`: abstract conferenza (nel .gitignore)
- `bibliography/`: literature review draft, annotazioni su 4 temi tematici, BibTeX master con 33 voci
- `bibliography/search-methodology.md`: documentazione della strategia di ricerca sistematica (6 database, stringhe di ricerca, criteri inclusione/esclusione)

## Dati e tracking (se presenti)
Nessuna configurazione di analytics, pixel, tracking o A/B test. Il "tracking" è limitato a:
- **Version tracking:** `infra/versions.py` cattura le versioni di 8 librerie (pydantic, datasets, scikit-learn, numpy, torch, transformers, sentence-transformers, openai) + Python + piattaforma a ogni run.
- **Run directory:** ogni esperimento produce una directory sotto `runs/` con nome auto-generato contenente `evaluation_result.json`.
- **Experiment config:** `infra/config.py` serializza la configurazione completa (corpus, seeds, protocollo) in `config.json`.

## Problemi e debito tecnico
- **Duplicazione NEGATION_PATTERN:** lo stesso regex è duplicato in `graders/hybrid.py` e `perturbations/gates.py` (scelta documentata per indipendenza dei moduli, ma introduce rischio di drift).
- **Duplicazione CONTRADICTION_MAP / ANTONYM_MAP:** mappe simili in `sensitivity.py` e `gates.py` con purpose diverso ma contenuto quasi identico.
- **Duplicazione STOPWORDS:** definite separatamente in `sensitivity.py` e `gaming.py`.
- **evaluation_result.json molto grande:** il file della prima run è >52K token JSON perché include risultati per-fold e per-question dettagliati. Nessuna compressione o summary separata.
- **Nessun `setup.py` / `pyproject.toml`:** il package `asag` non è installabile via pip; va usato con `PYTHONPATH=src`.
- **`.agents/` e `.planning/` non nel gitignore:** queste directory di tooling sono presenti come untracked files.
- **Nessuna CI/CD:** nessun GitHub Actions, nessun linting automatico, nessun pre-commit hook.
- **Nessun type checking:** nessun mypy o pyright configurato, nonostante i type hint siano presenti ovunque.
- **`struttura-progetto.html`:** file HTML orfano nella root, apparentemente una visualizzazione della struttura del progetto.

## Domande aperte
- Il corpus **SciEntsBank** è stato mai eseguito con la pipeline completa, o solo Beetle finora?
- Per le fasi 4-5 (DeBERTa, ModernBERT, GPT-4o), ci sono già configurazioni, script, o notebook in preparazione altrove?
- L'abstract IFKAD è stato rivisto dopo il feedback dei reviewer? Qual è la deadline per la versione finale del paper?
- C'è un motivo per cui il package non ha un `pyproject.toml`? Prevedi di renderlo installabile?
- Il file `struttura-progetto.html` è ancora utile o può essere rimosso?
- Ci sono vincoli di budget/API per la fase GPT-4o (costi OpenAI)?
- I risultati della prima run (HybridGrader × Beetle) sono considerati definitivi o preliminari?
