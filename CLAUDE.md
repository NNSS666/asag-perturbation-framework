# ASAG Perturbation Framework

Framework di valutazione robustezza per sistemi di Automated Short Answer Grading. Tesi magistrale LUISS (Sasso / De Mauro). Paper accettato a IFKAD 2026.

## Architettura

- Pipeline unidirezionale: `loaders/ → splitters/ → graders/ → perturbations/ → metrics/ → evaluation/`
- Tutto il codice vive in `src/asag/`. Entry point: `scripts/first_real_run.py`
- Ogni dato è un modello Pydantic v2 **frozen** (`QuestionRecord`, `AnswerRecord`, `PerturbationRecord`, `GradeResult`, `MetricResult`). Mai dict grezzi nel pipeline.
- I grader implementano `GraderInterface` ABC. Oggi solo `HybridGrader`; previsti DeBERTa, ModernBERT, GPT-4o.
- 7 generatori di perturbazione in 3 famiglie (invariance/sensitivity/gaming), orchestrati da `PerturbationEngine`.
- Due protocolli di valutazione: **A** (LOQO cross-question) e **B** (within-question 80/20).
- Il delta A-B è il "robustness drop" — metrica centrale della tesi.

## Comandi essenziali

```bash
# Test (dalla root)
pytest                    # tutti i 77 test
pytest -m "not slow"      # skip E2E

# Run esperimento completo (dalla root)
PYTHONPATH=src python -m scripts.first_real_run

# Self-test singolo modulo (esempio)
PYTHONPATH=src python -m asag.loaders.semeval2013
```

Il package NON è installabile via pip — serve sempre `PYTHONPATH=src`.

## Convenzioni codice

- **Python 3.9 obbligatorio:** usare `typing.Optional`, `typing.List`, `typing.Dict`, `typing.Tuple`. MAI sintassi `X | Y` o `list[X]`.
- **Modelli Pydantic:** sempre `frozen=True` via `model_config = ConfigDict(frozen=True)`.
- **Score normalizzati:** tutti in `[0.0, 1.0]`. Il mapping 5-way → float è in `schema/grade.py` (`LABEL_TO_SCORE`).
- **Confronti float:** arrotondare a 6 decimali (`SCORE_PRECISION = 6`) prima di confrontare. Mai `==` su float grezzi.
- **Seed isolation:** ogni componente ha il suo seed via `SeedConfig`. Non usare `set_global_seeds()` se puoi passare `random_state=` direttamente.
- **Gate rejection:** i candidati rifiutati NON vanno rigenerati. Il tasso di rifiuto è un risultato di ricerca.
- **Determinismo:** sinonimi WordNet ordinati alfabeticamente, reference answers sorted nel loader. Ogni output deve essere identico a parità di seed.
- **Docstring:** presenti ovunque con Args/Returns/Raises. Mantenere lo stile esistente.
- **Nessun import circolare:** `gates.py` duplica `NEGATION_PATTERN` da `hybrid.py` intenzionalmente per indipendenza dei moduli.

## Gotchas

- Gli split HuggingFace (`train`, `test_ua`, `test_uq`, `test_ud`) NON sono Protocol A/B. Il loader li concatena tutti. Non filtrarli mai per nome.
- `EvaluationEngine._grade_single()` prova `reference_answer=` come kwarg; se il grader non lo accetta, riprova senza. Rispettare questo pattern per nuovi grader.
- Gate 1 (SBERT cosine ≥ 0.85) si applica SOLO a `synonym_substitution`. I typo lo bypassano.
- Gate 2 (negazione/antonimi) si applica a TUTTA la famiglia invariance.
- `SSR_directional`: no-change conta come FAILURE (il grader non ha rilevato la perturbazione).
- `ASR_thresholded`: conta solo crossing da sotto a sopra 0.5. Risposte già passing che aumentano NON contano.
- Il file `evaluation_result.json` può essere molto grande (>50K token). Non leggerlo intero — usare offset/limit.

## Errori ricorrenti di Claude

_(Aggiungere qui regole man mano che emergono pattern di errore)_

## LifeOS sync

### Logging continuo
Dopo ogni modifica significativa (commit, file creato, decisione architetturale, bug risolto, task completato), appendi UNA riga a `CHANGELOG.md` in questa directory:
- Formato: `YYYY-MM-DD HH:MM — descrizione breve`
- Non chiedere conferma, fallo come parte del flusso di lavoro.
- IMPORTANTE: quando CHANGELOG.md supera le 200 righe, avvisa l'utente e suggerisci "sync + archivia changelog".

### Sync vault
Quando l'utente dice "sync":
1. Leggi CHANGELOG.md e aggiorna PROJECT_BRIEF.md con lo stato attuale del progetto
2. Aggiorna "/Users/nando/Desktop/Life OS/Progetti/tesi-asag/context.md" (stato, prossimi step)
3. Aggiorna "/Users/nando/Desktop/Life OS/Progetti/tesi-asag/log.md" (entry con data e riepilogo)
4. Aggiorna "/Users/nando/Desktop/Life OS/COCKPIT.md" (riga di stato sintetica del progetto)
5. Se CHANGELOG.md ha più di 200 righe, dopo il sync:
   - Sposta il contenuto in `_archive/changelog-YYYY-MM.md`
   - Ricrea CHANGELOG.md vuoto con solo l'header
