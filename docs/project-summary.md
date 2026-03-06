# Framework di Valutazione Perturbation-First per Sistemi ASAG
## Riepilogo del progetto — Stato al 2 marzo 2026

**Autori:** Ferdinando Sasso, Andrea De Mauro (LUISS Guido Carli)
**Destinazione:** IFKAD 2026 Conference + Tesi di laurea

---

## 1. Cos'e' questo progetto?

### Spiegazione ultra-basic

Immagina un professore che corregge i compiti degli studenti. Ora immagina che al posto del professore ci sia un software (un "grader automatico"). La domanda e': **questo software capisce davvero le risposte, oppure si fa fregare da trucchetti?**

Per scoprirlo, prendiamo le risposte degli studenti e le modifichiamo in modi controllati:

- **Modifiche innocue** (es. sostituire "circuito" con "circuito elettrico") — il voto NON dovrebbe cambiare
- **Modifiche che cambiano il significato** (es. aggiungere "non" a una frase) — il voto DOVREBBE cambiare
- **Trucchetti** (es. aggiungere parole tecniche a caso per sembrare piu' bravi) — il software NON dovrebbe farsi ingannare

Poi misuriamo: il software si comporta correttamente? Questo e' il cuore del progetto.

### Spiegazione tecnica

Il progetto implementa un framework di valutazione **perturbation-first** per sistemi ASAG (Automated Short Answer Grading). Invece di valutare i grader solo con metriche di agreement (accuracy, QWK), generiamo perturbazioni controllate delle risposte studentesche e misuriamo se i modelli di grading si comportano coerentemente rispetto a tre famiglie di perturbazioni:

1. **Invariance** — perturbazioni che preservano il significato (il voto deve restare uguale)
2. **Sensitivity** — perturbazioni che alterano il significato (il voto deve cambiare)
3. **Gaming** — tentativi di inflazione del punteggio (il grader non deve farsi ingannare)

La tesi e': le metriche tradizionali aggregate (accuracy, QWK) sono insufficienti per valutare i grader ASAG, e servono metriche complementari basate sulla robustezza.

---

## 2. I dataset utilizzati

### Spiegazione ultra-basic

Abbiamo preso due raccolte di compiti gia' corretti da esseri umani, usate nella ricerca internazionale:

- **Beetle**: 42 domande di fisica/circuiti elettrici, con 5.199 risposte di studenti
- **SciEntsBank**: 195 domande di scienze (biologia, chimica, scienze della terra), con 10.804 risposte

Ogni risposta ha gia' un voto "vero" dato da esseri umani (correct, partially correct, contradictory, irrelevant, non-domain). In totale: **237 domande, 16.003 risposte**.

### Spiegazione tecnica

Utilizziamo il dataset SemEval 2013 Task 7 (SRA), caricato da HuggingFace. I due corpora sono:

| Corpus | Domande | Risposte | Distribuzione label |
|--------|---------|----------|---------------------|
| Beetle | 42 | 5.199 | correct 42%, contradictory 27%, partial 23%, non_domain 5%, irrelevant 3% |
| SciEntsBank | 195 | 10.804 | correct 41%, irrelevant 25%, partial 24%, contradictory 10%, non_domain 0.4% |

I gold_score vengono normalizzati a [0.0, 1.0]: correct=1.0, partially_correct=0.5, tutto il resto=0.0. Questo permette confronti cross-dataset.

---

## 3. Le scelte di design e perche' hanno senso

### 3.1 Schema canonico a tre oggetti

**Ultra-basic:** Abbiamo definito tre "schede" standard per organizzare tutti i dati:
- **QuestionRecord** — la domanda del prof
- **AnswerRecord** — la risposta dello studente (con il voto corretto)
- **PerturbationRecord** — la versione modificata della risposta

**Tecnico:** Tre modelli Pydantic v2 frozen (immutabili dopo la creazione). Questo previene mutazioni accidentali e garantisce serializzazione JSON lossless. Ogni componente del sistema riceve istanze tipizzate, mai dict raw.

**Perche':** Senza uno schema esplicito, ogni fase della pipeline interpreterebbe i dati diversamente. Lo schema canonico e' il "contratto" che tiene tutto insieme.

### 3.2 Doppio protocollo di valutazione (A + B)

**Ultra-basic:** Valutiamo i grader in due modi diversi:
- **Protocollo A (LOQO):** Il software si allena su 41 domande e viene testato sulla 42esima. Poi ruota: si allena sulle altre 41 e testa su un'altra. Questo misura: "il software sa generalizzare a domande mai viste?"
- **Protocollo B (Within-Question):** Per ogni singola domanda, usiamo l'80% delle risposte per allenare e il 20% per testare. Questo misura: "il software funziona bene sulle domande che gia' conosce?"

Confrontare A e B ci dice quanto un grader "peggiora" quando vede domande nuove — il **robustness drop**.

**Tecnico:** Protocol A = Leave-One-Question-Out cross-validation. Protocol B = within-question stratified 80/20 split. Il confronto "robustness drop in shift" (delta Protocol A - Protocol B) quantifica la perdita di performance sotto distribution shift.

**Perche':** Un grader che funziona bene solo sulle domande note e' inutile in pratica. Il doppio protocollo separa la performance "in-distribution" da quella "cross-question", che e' il caso reale.

### 3.3 Tre famiglie di perturbazioni (non una sola)

**Ultra-basic:** Non basta fare UN tipo di modifica. Facciamo tre tipi diversi perche' testano cose diverse:
- Se cambio sinonimi e il voto cambia → il software e' fragile
- Se aggiungo "non" e il voto NON cambia → il software non capisce il significato
- Se aggiungo parole-fuffa e il voto sale → il software si fa fregare

**Tecnico:** Il design a tre famiglie deriva dalla tassonomia CheckList di Ribeiro et al. (ACL 2020, Best Paper): Invariance test -> IVR, Directional Expectation test -> SSR, Minimum Functionality Test -> ASR. La nostra innovazione e' applicare questo framework all'ASAG con metriche specifiche.

**Perche':** Gli studi esistenti testano una famiglia alla volta (solo adversarial, o solo parafrase). Nessuno ha un protocollo multi-famiglia con metriche complementari per ASAG. Questo e' il gap nella letteratura che il paper riempie.

### 3.4 Quattro metriche dual-form

**Ultra-basic:** Per ogni famiglia di perturbazione, misuriamo un numero che dice "quanto bene si comporta il grader":

| Metrica | Cosa misura | Esempio |
|---------|-------------|---------|
| **IVR_flip** | Quante volte il voto cambia quando NON dovrebbe | Se su 100 sinonimi il voto cambia 30 volte → IVR = 30% |
| **IVR_absdelta** | Di quanto cambia in media | Se il voto medio si sposta di 0.15 punti → IVR_abs = 0.15 |
| **SSR_directional** | Quante volte il voto scende quando DOVREBBE | Se aggiungo "non" e il voto scende 70 volte su 100 → SSR = 70% |
| **ASR_thresholded** | Quante volte un trucchetto riesce a far passare uno studente | Se 20 risposte insufficienti diventano sufficienti → ASR = 20% |

**Tecnico:**
- `IVR_flip`: proporzione di coppie invariance dove `round(orig,6) != round(pert,6)` — criterio binario strettissimo
- `IVR_absdelta`: media di `|orig - pert|` sulle coppie invariance — cattura la magnitudine
- `SSR_directional`: proporzione dove `pert < orig` con strict less-than — no-change = failure
- `ASR_thresholded`: proporzione dove `orig < 0.5 AND pert >= 0.5` — attraversamento soglia

**Perche':** Le forme "dual" (flip+absdelta, directional+thresholded) catturano sia il segnale binario ("e' successo?") che quello continuo ("di quanto?"). Usare solo una forma perderebbe informazione.

### 3.5 Two-Gate invariance validation

**Ultra-basic:** Quando generiamo sinonimi, dobbiamo essere sicuri che la modifica sia davvero innocua. Usiamo due "filtri":
- **Gate 1:** Un'intelligenza artificiale (SBERT) confronta la frase originale con quella modificata. Se la similarita' e' sotto l'85%, la scarta.
- **Gate 2:** Un controllo automatico verifica che non siano state introdotte negazioni o contrari accidentali.

Le perturbazioni scartate vengono contate — il tasso di scarto e' esso stesso un risultato di ricerca.

**Tecnico:** Gate 1 usa cosine similarity con all-MiniLM-L6-v2 (threshold 0.85, hard-coded per evitare threshold-shopping). Gate 2 usa regex pattern matching per negazioni + token-set comparison per antonym detection (confronta token originali vs candidati per evitare false positive). Gate 1 si applica SOLO a synonym_substitution (le typo hanno similarita' SBERT troppo bassa by design). Gate 2 si applica a tutta la famiglia invariance.

**Perche':** Senza i gate, perturbazioni "invariance" che in realta' cambiano il significato inquinerebbero la metrica IVR. I gate garantiscono la qualita' delle perturbazioni. Il tasso di scarto (~33% per synonym substitution al Gate 1) e' un risultato interessante per il paper.

### 3.6 Riproducibilita' deterministica

**Ultra-basic:** Se eseguiamo lo stesso esperimento due volte, otteniamo esattamente gli stessi risultati. Zero casualita'.

**Tecnico:** Ogni generatore usa `random.Random(seed)` locale, mai `random.seed()` globale. Il seed per-answer e' calcolato come `base_seed + hash(answer_id) % 2^31`, rendendo il risultato indipendente dall'ordine di iterazione. I sinonimi WordNet sono ordinati alfabeticamente. La cache JSONL e' keyed su MD5(text + type + seed).

**Perche':** La riproducibilita' e' un requisito non negoziabile per la ricerca accademica. Se i risultati cambiano ad ogni run, non sono pubblicabili.

### 3.7 Architettura pluggable

**Ultra-basic:** Il sistema e' fatto a "mattoncini" intercambiabili. Vuoi aggiungere un nuovo dataset? Scrivi un loader. Vuoi aggiungere un nuovo grader? Implementa l'interfaccia. Nient'altro cambia.

**Tecnico:** `DatasetLoader` ABC per i dataset, `GraderInterface` ABC per i grader, `PerturbationGenerator` ABC per i generatori. L'`EvaluationEngine` orchestra tutto senza conoscere le implementazioni concrete. L'aggiunta di un nuovo grader (Phase 4: transformer, Phase 5: LLM) richiede zero modifiche al motore di valutazione.

**Perche':** Il paper confrontera' almeno 3-4 modelli diversi (hybrid, DeBERTa, ModernBERT, GPT-4o). Se ogni modello richiedesse modifiche al motore, il codice sarebbe ingestibile.

---

## 4. Cosa e' stato costruito (fase per fase)

### Phase 0.1 — Ricerca bibliografica (completata 20/02/2026)

**Cosa:** Bibliografia sistematica di 43 paper organizzati in 4 temi, draft della sezione Related Work (~2000 parole), gap statement che nomina le tre metriche IVR/SSR/ASR.

**Risultato chiave:** 5 journal target su 9 hanno zero paper su ASAG adversarial → conferma la novita' del contributo.

### Phase 1 — Foundation (completata 20/02/2026)

**Cosa:** Schema a 3 oggetti, loader SemEval 2013, splitter Protocol A (LOQO) e Protocol B (within-question), diagnostica anti-leakage, infrastruttura (storage JSONL, seed management, version capture).

**Risultato chiave:** Beetle carica 42 domande / 5.199 risposte, SciEntsBank 195 domande / 10.804 risposte. La diagnostica leakage conferma zero contaminazione tra fold.

### Phase 2 — Metriche e Hybrid Grader (completata 21/02/2026)

**Cosa:** MetricCalculator con 4 metriche dual-form, HybridGrader (features linguistiche + SBERT embeddings + LogisticRegression), EvaluationEngine con loop Protocol A/B e robustness drop.

**Risultato chiave:** 13 unit test sulle metriche con valori hand-computed su dataset sintetico — tutti passano con tolleranza 1e-9. Il loop completo gira end-to-end su Beetle e SciEntsBank.

### Phase 3 — Perturbation Engine (completata 02/03/2026)

**Cosa:** 7 generatori di perturbazioni rule-based, Gate 1 (SBERT cosine) + Gate 2 (negation heuristic), PerturbationEngine orchestrator, cache deterministica, 77 test (67 unit + 10 E2E su Beetle).

**Risultato chiave:** Vedi sezione 5 per i primi risultati reali.

---

## 5. Primi risultati ottenuti

### 5.1 Generazione perturbazioni su dati reali

Su un campione di 20 risposte Beetle (3 domande):

| Dato | Valore |
|------|--------|
| Perturbazioni generate | 165 |
| Media per risposta | 8.2 (su 10 teoriche) |
| Tipi presenti | 7 su 7 |
| Famiglie presenti | 3 su 3 |

Distribuzione per tipo:

| Tipo | Famiglia | Numero | Note |
|------|----------|--------|------|
| synonym_substitution | invariance | 24 (su 40 possibili) | 33% scartati da Gate 1 |
| typo_insertion | invariance | 20 | Nessuno scartato |
| negation_insertion | sensitivity | 20 | |
| key_concept_deletion | sensitivity | 20 | |
| semantic_contradiction | sensitivity | 21 | |
| rubric_keyword_echoing | gaming | 40 | 2 varianti per risposta |
| fluent_wrong_extension | gaming | 20 | |

### 5.2 Tassi di scarto dei gate

| Gate | Tipo | Testati | Scartati | Tasso |
|------|------|---------|----------|-------|
| Gate 1 (SBERT cosine >= 0.85) | synonym_substitution | 36 | 12 | **33.3%** |
| Gate 2 (negation heuristic) | synonym_substitution | 24 | 0 | 0% |
| Gate 2 (negation heuristic) | typo_insertion | 20 | 0 | 0% |

**Interpretazione:** Un terzo delle sostituzioni sinonimiche viene scartato perche' cambia troppo il significato della frase a livello semantico (secondo SBERT). Questo e' un risultato interessante: mostra che la sostituzione "ingenua" di sinonimi non e' sempre meaning-preserving, e il gate e' necessario.

### 5.3 Esempio concreto di perturbazioni

Risposta originale di uno studente (Beetle, domanda sui circuiti):

> *"because terminal one and the positive terminal are connected"*

| Tipo | Testo perturbato |
|------|-----------------|
| synonym_substitution | "because **concluding** one and the positive terminal are connected" |
| typo_insertion | "**becase** terminal one and the positive terminal are connected" |
| negation_insertion | "because terminal one and the positive terminal are **not** connected" |
| key_concept_deletion | "~~because~~ terminal one and the positive terminal are connected" |
| semantic_contradiction | "because terminal one and the **negative** terminal are connected" |
| rubric_keyword_echoing | "...are connected **separated**" |
| fluent_wrong_extension | "...are connected **Furthermore, Mammals...**" |

### 5.4 Copertura dei test

| Suite | Test | Stato |
|-------|------|-------|
| Unit test generatori (test_generators.py) | 35 | Tutti OK |
| Unit test gate (test_gates.py) | 32 | Tutti OK |
| Unit test metriche (test_calculator.py) | 13 | Tutti OK |
| Smoke test HybridGrader (test_hybrid.py) | 6 | Tutti OK |
| E2E PerturbationEngine su Beetle (test_perturbation_engine.py) | 10 | Tutti OK |
| **Totale** | **96** | **Tutti OK** |

(I test E2E sull'EvaluationEngine con dati sintetici sono ulteriori 4 test marcati @slow, per un totale complessivo che arriva a ~100.)

---

## 6. Cosa manca (roadmap rimanente)

| Fase | Cosa | Dipendenza critica |
|------|------|--------------------|
| **Phase 4** | Fine-tuning DeBERTa-v3 + ModernBERT sotto LOQO, multi-seed | GPU |
| **Phase 5** | LLM grader (GPT-4o + altro), caching API, cost estimator, rubric sanitization | Budget API |
| **Phase 6** | Tabelle LaTeX, heatmap, dumbbell plot, Wilcoxon + Cliff's delta, Kendall's tau | — |

### Cosa possiamo gia' fare ora

Con le Phase 1-3 complete, possiamo gia':
- Generare perturbazioni per tutto il dataset (16.003 risposte x ~10 perturbazioni = ~160.000 perturbazioni)
- Valutare l'HybridGrader (il grader baseline) sotto entrambi i protocolli
- Ottenere i primi numeri IVR/SSR/ASR su dati reali con perturbazioni reali
- Misurare il robustness drop tra Protocol A e Protocol B

Quello che aggiungeranno le fasi successive:
- Phase 4 porta i grader transformer (DeBERTa, ModernBERT) — modelli "seri" da confrontare
- Phase 5 porta i grader LLM (GPT-4o) — il confronto piu' interessante per il paper
- Phase 6 produce gli output publication-ready (tabelle, grafici, test statistici)

---

## 7. Struttura del codice

```
src/asag/
  schema/          → QuestionRecord, AnswerRecord, PerturbationRecord
  loaders/         → DatasetLoader ABC + SemEval2013Loader
  splitters/       → Protocol A (LOQO), Protocol B (within-question), leakage check
  infra/           → Storage JSONL, seed management, run directories, config
  metrics/         → MetricCalculator (IVR/SSR/ASR dual-form), MetricResult
  graders/         → GraderInterface ABC, HybridGrader
  evaluation/      → EvaluationEngine (orchestra grading + metriche)
  perturbations/   → 7 generatori, Gate 1/2, GateLog, PerturbationEngine, cache

tests/
  metrics/         → 13 unit test con valori hand-computed
  graders/         → 6 smoke test HybridGrader
  evaluation/      → 4 E2E test (Beetle + SciEntsBank)
  test_generators.py → 35 test generatori
  test_gates.py      → 32 test gate
  test_perturbation_engine.py → 10 E2E test
```

**25 moduli Python, ~96 test, tutto passing.**

---

*Documento generato il 2 marzo 2026.*
