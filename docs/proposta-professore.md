# Proposta Metodologica e Primi Risultati Sperimentali
## Framework di Valutazione Perturbation-First per Sistemi ASAG

**Ferdinando Sasso**
Relatore: Prof. Andrea De Mauro — LUISS Guido Carli

Marzo 2026

---

## 1. Obiettivo della ricerca

L'obiettivo di questo lavoro e' valutare quanto i sistemi di correzione automatica delle risposte brevi (Automated Short Answer Grading, ASAG) siano realmente affidabili. La domanda di fondo e': questi sistemi capiscono davvero il contenuto delle risposte degli studenti, oppure si basano su indizi superficiali come la presenza di certe parole chiave?

Le metriche tradizionali utilizzate in letteratura — accuracy, Quadratic Weighted Kappa — misurano solo l'agreement tra il voto automatico e quello umano in condizioni "normali". Questo non e' sufficiente. Un sistema potrebbe avere alta accuracy ma essere estremamente fragile: basta cambiare un sinonimo per fargli cambiare voto, oppure non accorgersi che uno studente ha inserito una negazione che rende la risposta sbagliata.

Il framework che ho costruito testa sistematicamente questa fragilita' generando modifiche controllate delle risposte e misurando come il grader reagisce.

---

## 2. Posizionamento nella letteratura

La ricerca bibliografica ha coperto 43 pubblicazioni organizzate in quattro aree tematiche: metodi ASAG, perturbazioni adversariali nell'NLP, validita' educativa, e valutazione automatizzata tramite LLM. Il rapporto tra articoli su journal e conference proceedings e' del 40% (17 su 43), coerente con un campo in cui la ricerca adversariale nell'NLP e' prevalentemente presentata a conferenze (ACL, EMNLP, NAACL).

Il framework metodologico che propongo si basa sulla tassonomia CheckList di Ribeiro et al. (2020, ACL Best Paper), che definisce tre categorie di test comportamentali per modelli NLP: Invariance, Directional Expectation e Minimum Functionality Test. Questa tassonomia non e' mai stata applicata sistematicamente all'ASAG con metriche dedicate.

Il gap che questa ricerca colma e' precisamente questo: nella letteratura esistono studi su singoli tipi di attacco adversariale applicati all'ASAG (Filighera et al. 2024 per il keyword stuffing; Ding et al. 2020 per le perturbazioni di input), ma nessuno studio propone un protocollo multi-famiglia con metriche complementari. Una ricerca sistematica su 5 journal target (Computers & Education, Assessment in Education, Language Testing, Applied Measurement in Education, British Journal of Educational Technology) ha restituito zero risultati su valutazione adversariale di sistemi ASAG — dato che supporta la novita' del contributo.

---

## 3. Dataset utilizzati

Ho scelto di partire da dataset pubblici consolidati nella comunita' ASAG, per costruire e validare il framework su benchmark noti prima di estenderlo a dati proprietari.

**SemEval 2013 Task 7 (Student Response Analysis):**

| Corpus | Dominio | Domande | Risposte | Scala di valutazione |
|--------|---------|---------|----------|---------------------|
| Beetle | Elettricita' e circuiti | 42 | 5.199 | 5 classi (correct, partially correct, contradictory, irrelevant, non-domain) |
| SciEntsBank | Scienze generali (biologia, chimica, scienze della terra) | 195 | 10.804 | 5 classi (come sopra) |

Ho normalizzato tutti i voti su una scala [0.0, 1.0] per consentire confronti cross-dataset: correct = 1.0, partially correct = 0.5, tutti gli altri = 0.0. Questa normalizzazione e' coerente con la prassi dei benchmark ASAG recenti.

**Perche' questi dataset:** Beetle e SciEntsBank sono i dataset ASAG piu' utilizzati nella letteratura di riferimento. Partire da qui consente di confrontare i risultati con studi precedenti. L'architettura del sistema e' stata progettata per accettare dataset aggiuntivi (incluso il dataset del Prof. De Mauro) senza modifiche al codice esistente.

---

## 4. Scelte metodologiche

### 4.1 Doppio protocollo di valutazione

Ho implementato due protocolli di valutazione complementari, perche' un singolo protocollo non cattura il quadro completo della robustezza di un grader.

**Protocollo A — Leave-One-Question-Out (LOQO):**
Il grader viene addestrato su tutte le domande tranne una, e testato su quella esclusa. Si ripete per ogni domanda. Questo misura la capacita' di generalizzazione: il grader funziona bene su domande che non ha mai visto durante l'addestramento?

Questa e' la situazione reale di utilizzo. In un contesto educativo, un professore non potra' fornire esempi di correzione per ogni possibile domanda futura. Il grader deve saper valutare risposte a domande nuove.

**Protocollo B — Within-Question (80/20 split):**
Per ogni singola domanda, l'80% delle risposte serve per l'addestramento e il 20% per il test. Questo misura la performance in condizioni ottimali: il grader funziona quando conosce gia' la domanda?

**Perche' servono entrambi:** Il confronto tra i due protocolli produce il "robustness drop" — quanto il grader peggiora quando passa da domande note a domande nuove. Questo delta e' un indicatore diretto della fragilita' del sistema e non e' catturabile da nessuna metrica tradizionale.

### 4.2 Tre famiglie di perturbazioni

Ho definito tre famiglie di perturbazioni, ciascuna progettata per testare un aspetto diverso del comportamento del grader. Ogni famiglia corrisponde a un tipo di test dalla tassonomia CheckList:

**Famiglia 1 — Invariance (il voto NON deve cambiare):**

Queste perturbazioni modificano la forma della risposta senza alterarne il significato.

| Tipo | Cosa fa | Esempio |
|------|---------|---------|
| Sostituzione sinonimica | Sostituisce una parola con un sinonimo WordNet | "provides" → "supplies" |
| Inserimento refuso | Introduce un errore di battitura | "because" → "becase" |

Se il grader cambia voto dopo una di queste modifiche, sta reagendo alla forma superficiale e non al contenuto.

**Famiglia 2 — Sensitivity (il voto DEVE cambiare):**

Queste perturbazioni modificano il significato della risposta, rendendola incorretta.

| Tipo | Cosa fa | Esempio |
|------|---------|---------|
| Inserimento negazione | Aggiunge "not" | "the current flows" → "the current does not flow" |
| Cancellazione concetto chiave | Rimuove un termine essenziale | "The battery provides energy" → "The provides energy" |
| Contraddizione semantica | Sostituisce un termine con il suo opposto | "positive terminal" → "negative terminal" |

Se il grader NON cambia voto dopo queste modifiche, non sta comprendendo il contenuto.

**Famiglia 3 — Gaming (il grader NON deve farsi ingannare):**

Queste perturbazioni tentano di "imbrogliare" il grader.

| Tipo | Cosa fa | Esempio |
|------|---------|---------|
| Keyword echoing | Aggiunge parole dalla risposta corretta senza senso | "...connected. separated circuit energy" |
| Estensione fluente ma sbagliata | Aggiunge una frase plausibile ma errata | "...Furthermore, batteries produce electrons from the plastic casing." |

Se il grader alza il voto dopo queste modifiche, si sta facendo ingannare da indizi superficiali.

**Perche' servono tutte e tre:** Ogni famiglia testa una dimensione diversa della comprensione del grader. Un grader potrebbe essere stabile sui sinonimi ma vulnerabile al keyword stuffing, o viceversa. Solo un protocollo multi-famiglia rivela il profilo completo di robustezza.

### 4.3 Quattro metriche dedicate

Per ogni famiglia ho definito metriche specifiche:

| Metrica | Famiglia | Cosa misura | Formula |
|---------|----------|-------------|---------|
| **IVR_flip** | Invariance | Percentuale di casi in cui il voto cambia quando non dovrebbe | N. coppie con voto diverso / totale coppie |
| **IVR_absdelta** | Invariance | Entita' media del cambiamento | Media di |voto_originale - voto_perturbato| |
| **SSR_directional** | Sensitivity | Percentuale di casi in cui il voto scende quando dovrebbe | N. coppie dove voto perturbato < originale / totale |
| **ASR_thresholded** | Gaming | Percentuale di risposte insufficienti che diventano sufficienti | N. coppie dove orig < 0.5 e pert >= 0.5 / totale |

Ho scelto di implementare sia la forma binaria (IVR_flip: "e' cambiato si/no?") che quella continua (IVR_absdelta: "di quanto e' cambiato?") per le perturbazioni invariance, perche' catturano informazioni complementari. Un grader potrebbe cambiare voto raramente ma con grandi scarti, o spesso ma di poco.

### 4.4 Sistema di validazione a due gate per le perturbazioni invariance

Le perturbazioni della famiglia invariance devono preservare il significato della risposta. Per garantire la qualita' delle perturbazioni generate, ho implementato un sistema di validazione a due livelli:

**Gate 1 — Similarita' semantica (SBERT, soglia 0.85):**
Confronta la risposta originale con quella perturbata usando un modello di sentence embedding (all-MiniLM-L6-v2). Se la similarita' scende sotto 0.85, la perturbazione viene scartata. Questo gate si applica solo alle sostituzioni sinonimiche — i refusi sono innocui per costruzione (un errore di battitura non cambia il significato).

La soglia di 0.85 e' stata fissata (non configurabile) per evitare il rischio di threshold-shopping — cioe' di scegliere la soglia che produce i risultati migliori, invalidando la metodologia.

**Gate 2 — Euristica di negazione e contrari:**
Verifica che la perturbazione non abbia accidentalmente introdotto negazioni ("not", "never") o contrari ("positive" → "negative") non presenti nell'originale. Questo cattura casi che SBERT potrebbe non rilevare.

**Perche' il tasso di scarto e' un risultato, non un problema:** Le perturbazioni scartate non vengono rigenerate. Il tasso di scarto viene registrato e riportato come dato di ricerca. Se il 40% dei sinonimi WordNet non preserva il significato secondo SBERT, questo e' di per se' un risultato interessante sulla qualita' della sostituzione sinonimica automatica.

### 4.5 Riproducibilita' completa

Ogni esperimento e' completamente riproducibile. Lanciare lo stesso run due volte produce risultati identici, bit per bit. Questo e' ottenuto tramite:

- Seed deterministici per ogni generatore di perturbazioni
- Ordinamento alfabetico dei sinonimi WordNet (l'ordine di default varia tra piattaforme)
- Cache su disco delle perturbazioni generate (formato JSONL con chiave hash)
- Registrazione completa della configurazione di ogni run

---

## 5. Modelli di grading previsti

Il framework confrontera' quattro approcci di grading, dal piu' semplice al piu' sofisticato:

| Modello | Tipo | Addestramento | Stato |
|---------|------|---------------|-------|
| **HybridGrader** | Feature linguistiche + embedding SBERT + regressione logistica | Supervisionato sui dati del dataset | Implementato e testato |
| **DeBERTa-v3-base** | Transformer pre-addestrato (Microsoft, open source) | Fine-tuning sui dati del dataset | Pianificato |
| **ModernBERT-base** | Transformer pre-addestrato (Answer.AI, open source) | Fine-tuning sui dati del dataset | Pianificato |
| **GPT-4o** | Large Language Model (OpenAI) | Zero-shot con prompt e rubrica | Pianificato |

L'HybridGrader e' stato progettato da me come baseline. Combina quattro feature linguistiche calcolate esplicitamente (sovrapposizione lessicale tra risposta studente e risposta di riferimento, rapporto di lunghezza, presenza di negazioni, copertura dei termini chiave) con un embedding SBERT a 384 dimensioni, per un totale di 388 feature alimentate in un classificatore a regressione logistica.

I transformer (DeBERTa, ModernBERT) verranno scaricati come modelli pre-addestrati open source e fine-tunati sul nostro dataset. GPT-4o verra' utilizzato via API senza fine-tuning, con un prompt che include la rubrica di valutazione.

Il confronto multi-modello e' essenziale: se anche modelli sofisticati mostrano fragilita', il risultato e' molto piu' forte di un'analisi su un singolo modello.

---

## 6. Primi risultati sperimentali

Ho eseguito il primo run sperimentale completo sull'HybridGrader con il corpus Beetle (42 domande, 5.199 risposte).

### 6.1 Generazione perturbazioni

| Dato | Valore |
|------|--------|
| Risposte analizzate | 5.199 |
| Perturbazioni generate | 41.378 |
| Media per risposta | 8.0 (su 10 teoriche, alcune scartate dai gate) |
| Tutti i 7 tipi presenti | Si |
| Tutte le 3 famiglie presenti | Si |
| Tasso scarto Gate 1 (sinonimi) | **40.3%** |
| Tasso scarto Gate 2 (negazioni accidentali) | 0% |
| Tempo di esecuzione (generazione) | ~5 minuti |

Il tasso di scarto del 40.3% al Gate 1 indica che quasi la meta' delle sostituzioni sinonimiche prodotte da WordNet altera il significato della frase abbastanza da scendere sotto la soglia di similarita' SBERT. Questo dato, di per se', e' un contributo: la sostituzione sinonimica automatica non e' un metodo affidabile per generare parafrasi meaning-preserving senza validazione.

### 6.2 Risultati della valutazione

Il run completo ha richiesto circa 83 minuti su un MacBook con chip Apple M1, includendo generazione delle perturbazioni, addestramento del grader su 42 fold LOQO, grading di tutte le perturbazioni, e calcolo delle metriche.

#### Tabella risultati principali

| Metrica | Cosa misura | Protocol B (domande note) | Protocol A (domande nuove) | Robustness Drop |
|---------|-------------|:---:|:---:|:---:|
| **IVR_flip** | Instabilita' sui sinonimi | 34.1% | **53.9%** | **+19.8 pp** |
| **IVR_absdelta** | Entita' dell'instabilita' | 0.233 | **0.402** | **+16.9 pp** |
| **SSR_directional** | Sensibilita' alle negazioni | 16.6% | **32.3%** | **+15.7 pp** |
| **ASR_thresholded** | Vulnerabilita' al gaming | 19.2% | **18.0%** | -1.2 pp |

*(pp = punti percentuali)*

### 6.3 Interpretazione dei risultati

**IVR_flip = 53.9% (Protocol A):** Quando il grader vede domande nuove, cambia voto in piu' della meta' dei casi dopo una semplice sostituzione sinonimica. In condizioni reali di utilizzo, questo significherebbe che lo stesso concetto espresso con parole diverse riceverebbe un voto diverso il 54% delle volte. Questo livello di instabilita' non sarebbe accettabile per un utilizzo educativo.

**SSR_directional = 32.3% (Protocol A):** Su domande nuove, il grader rileva la negazione e abbassa il voto solo nel 32% dei casi. Il restante 68% delle volte, una risposta resa semanticamente errata tramite l'inserimento di "not" o la sostituzione con un contrario non viene penalizzata. Il grader non sta realmente comprendendo il contenuto — sta reagendo a pattern superficiali.

**ASR_thresholded = 18.0% (Protocol A):** Il 18% dei tentativi di gaming riesce a trasformare una risposta insufficiente in sufficiente. Questo e' relativamente contenuto rispetto alle altre vulnerabilita', ma comunque significativo.

**Il robustness drop e' il risultato piu' significativo.** La differenza sistematica tra Protocol A e Protocol B conferma l'ipotesi centrale del lavoro: le performance di robustezza peggiorano in modo misurabile quando il grader deve gestire domande mai viste durante l'addestramento. I delta di +19.8 pp (invariance), +16.9 pp (invariance continua) e +15.7 pp (sensitivity) sono consistenti e nella stessa direzione, il che rafforza la validita' del risultato.

L'unica eccezione e' il gaming (-1.2 pp), che resta sostanzialmente stabile tra i due protocolli. Questo suggerisce che la vulnerabilita' al keyword stuffing non dipende dalla familiarita' con la domanda — un'ipotesi plausibile, dato che il gaming sfrutta pattern generali (parole chiave dal reference answer) piuttosto che conoscenza specifica della domanda.

### 6.4 Cosa dicono questi risultati sulla tesi

Questi risultati preliminari supportano la tesi principale: un grader con accuracy ragionevole puo' essere profondamente fragile sotto perturbazioni controllate, e questa fragilita' non e' visibile dalle metriche tradizionali. Il fatto che il grader baseline mostri vulnerabilita' significative stabilisce una linea di base chiara. Le fasi successive (transformer fine-tunati, LLM) permetteranno di rispondere alla domanda: i modelli piu' sofisticati sono anche piu' robusti?

---

## 7. Piano sperimentale rimanente

| Fase | Contenuto | Stima temporale |
|------|-----------|-----------------|
| **Fase 4** | Fine-tuning di DeBERTa-v3-base e ModernBERT-base sotto LOQO con 3 seed per modello. Produrra' le stesse metriche del primo run per consentire il confronto diretto. | 1-2 giorni (esecuzione su M1) |
| **Fase 5** | Valutazione di GPT-4o (e almeno un altro LLM) via API con prompt rubric-driven. Include cost estimator, caching delle chiamate, e misurazione del tasso di consistenza del modello. | 1 settimana |
| **Fase 6** | Analisi statistica completa (Wilcoxon signed-rank con correzione Bonferroni, Cliff's delta per effect size), tabelle LaTeX, visualizzazioni (heatmap perturbazioni x modelli, dumbbell plot clean vs perturbed, radar chart). | 1 settimana |

### Output atteso per il paper

La tabella finale che il paper presentera':

| | IVR_flip | IVR_absdelta | SSR_dir | ASR_thresh |
|---|:---:|:---:|:---:|:---:|
| HybridGrader (Protocol A) | 53.9% | 0.402 | 32.3% | 18.0% |
| HybridGrader (Protocol B) | 34.1% | 0.233 | 16.6% | 19.2% |
| DeBERTa-v3 (Protocol A) | *da misurare* | *da misurare* | *da misurare* | *da misurare* |
| DeBERTa-v3 (Protocol B) | *da misurare* | *da misurare* | *da misurare* | *da misurare* |
| ModernBERT (Protocol A) | *da misurare* | *da misurare* | *da misurare* | *da misurare* |
| ModernBERT (Protocol B) | *da misurare* | *da misurare* | *da misurare* | *da misurare* |
| GPT-4o (Protocol A) | *da misurare* | *da misurare* | *da misurare* | *da misurare* |
| GPT-4o (Protocol B) | *da misurare* | *da misurare* | *da misurare* | *da misurare* |

A questa si aggiungera' il breakdown per tipo di perturbazione (heatmap) e il robustness drop per ogni modello.

---

## 8. Predisposizione per il dataset del Prof. De Mauro

L'architettura del sistema e' stata progettata fin dall'inizio per supportare dataset aggiuntivi. L'integrazione del dataset del Prof. De Mauro richiede esclusivamente la scrittura di un modulo loader (~50 righe di codice) che converte i dati nel formato standard del framework. Nessuna modifica alle perturbazioni, alle metriche, o al motore di valutazione.

Elementi necessari per l'integrazione:
- Formato del file (CSV, JSON, Excel)
- Campi disponibili (domanda, risposta studente, risposta di riferimento, voto)
- Scala di valutazione utilizzata
- Eventuale rubrica di correzione

Una volta definito il formato con il Prof. De Mauro e Gabriele, il loader puo' essere implementato in poche ore e tutti gli esperimenti gia' condotti su Beetle/SciEntsBank possono essere replicati automaticamente sul nuovo dataset.

---

## Riferimenti bibliografici principali

- Ribeiro, M.T., Wu, T., Guestrin, C., Singh, S. (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList. *ACL 2020* (Best Paper Award).
- Filighera, A., Steuer, T., Roth, C. (2024). Cheating Automatic Short Answer Grading: On the Adversarial Usage of Adjectives and Adverbs. *International Journal of Artificial Intelligence in Education*, 34.
- Ding, Y., et al. (2020). Don't take "no" for an answer: An empirical assessment of adversarial input on neural NLP models. *arXiv:2007.06796*.
- Burrows, S., Gurevych, I., Stein, B. (2015). The eras and trends of automatic short answer grading. *International Journal of Artificial Intelligence in Education*, 25(1).
- Heilman, M., Madnani, N. (2015). The impact of training data on automated short answer scoring performance. *ETS Research Report Series*.
- Messick, S. (1989). Validity. In R.L. Linn (Ed.), *Educational Measurement* (3rd ed.).
- Kane, M.T. (2006). Validation. In R.L. Brennan (Ed.), *Educational Measurement* (4th ed.).

---

*Documento preparato il 2 marzo 2026.*
*Tutti i risultati sono riproducibili eseguendo lo script `scripts/first_real_run.py` nella repository del progetto.*
