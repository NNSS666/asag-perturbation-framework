# Analisi preliminare — da cancellare

## Dati disponibili (5 aprile 2026)
- HybridGrader: run completa con fix grader-vs-grader
- GPT-5.4 mini L0: **run completa** (perturbazioni + originali + metriche Protocol A+B)
- Mancano: GPT-5.4 mini L1, GPT-5.4 L0/L1, Gemini 2.5 Flash L0/L1

---

## Confronto diretto: HybridGrader vs GPT-5.4 mini L0

| Metrica | Hybrid A | Hybrid B | Hybrid Drop | GPT-5.4m A | GPT-5.4m B | GPT-5.4m Drop |
|---|---|---|---|---|---|---|
| IVR_flip | 0.337 | 0.179 | **+0.158** | 0.243 | 0.256 | -0.013 |
| IVR_absdelta | 0.242 | 0.125 | **+0.118** | 0.126 | 0.133 | -0.006 |
| SSR_directional | 0.140 | 0.120 | +0.020 | 0.420 | 0.423 | -0.003 |
| ASR_thresholded | 0.188 | 0.115 | **+0.074** | 0.067 | 0.066 | +0.002 |

---

## 5 Findings chiave

### F1: L'LLM non ha robustness drop
I delta A-B del GPT-5.4 mini sono tutti ~0.01. Questo e' atteso (zero-shot, niente training) ma e' un risultato importante: **conferma che il robustness drop dell'HybridGrader viene dal training, non da un artefatto del protocollo**. L'LLM e' il "controllo" sperimentale.

### F2: L'LLM e' piu' robusto per invariance (IVR)
IVR_flip: 0.243 (LLM) vs 0.337 (Hybrid) su Protocol A. L'LLM cambia voto il 24.3% delle volte su perturbazioni invariance, l'Hybrid il 33.7%. Ma attenzione: parte di questa robustezza potrebbe essere "banale" — l'LLM vota spesso 0.5, quindi il voto cambia meno.

### F3: L'LLM rileva 3x piu' perturbazioni sensitivity (SSR)
SSR: 0.420 (LLM) vs 0.140 (Hybrid). **Questo e' il finding piu' forte.** L'HybridGrader rileva solo il 14% delle perturbazioni che cambiano significato (negazione, cancellazione, contraddizione). L'LLM ne rileva il 42%. Il grader ML e' quasi cieco alle modifiche semantiche.

### F4: L'LLM e' quasi immune al gaming (ASR)
ASR: 0.067 (LLM) vs 0.188 (Hybrid). Solo il 6.7% degli attacchi gaming (keyword stuffing, fluent wrong) ingannano l'LLM, vs 18.8% per l'Hybrid. L'LLM non si fa imbrogliare da parole chiave aggiunte.

### F5: Il framework multi-metrica rivela pattern invisibili alle metriche tradizionali
Se misurassimo solo IVR (robustezza a perturbazioni invariance), l'HybridGrader sembrerebbe "abbastanza robusto" (IVR_flip=0.179 su Protocol B). Ma SSR=0.120 rivela che e' fragile in modo diverso: non cambia voto nemmeno quando DOVREBBE. Un grader che dice sempre la stessa cosa appare "robusto" per IVR ma e' inutile per SSR. **Servono entrambe le metriche per distinguere robustezza genuina da indiscriminazione.**

---

## Distribuzione voti GPT-5.4 mini L0

| Label | Gold (Beetle) | GPT-5.4m L0 |
|---|---|---|
| correct | 42.0% | 8.4% |
| partially_correct_incomplete | 23.1% | 54.3% |
| contradictory | 27.0% | 15.5% |
| irrelevant | 2.9% | 21.5% |
| non_domain | 5.0% | 0.2% |

Score medio: Gold = 0.575, GPT-5.4m L0 = 0.356

Pattern: senza reference answer, GPT-5.4 mini e' estremamente conservativo. "Partially correct" diventa il default (54.3%). Questo spiega in parte l'IVR basso: se il grader vota 0.5 sia sull'originale che sulla perturbazione, non c'e' flip.

---

## Anticipazioni per le run mancanti

### RQ3 (reference answer aiuta la robustezza?)
L0 e' conservativo → L1 con reference dovrebbe discriminare meglio → IVR potrebbe salire (piu' flips perche' il grader ora distingue) ma SSR dovrebbe salire ancora di piu' (rileva meglio le perturbazioni). Il rapporto IVR/SSR dira' se la reference migliora davvero la robustezza o solo la discriminazione.

### RQ4 (modello piu' potente = piu' robusto?)
GPT-5.4 frontier discrimina meglio di mini → probabile IVR piu' alto (piu' flips) ma anche SSR piu' alto. La domanda e': il rapporto migliora? Il modello frontier e' sia piu' accurato che piu' robusto, o deve fare un trade-off?

### Cross-vendor (Gemini 2.5 Flash)
Confronto con GPT-5.4 mini (stesso tier cost-efficient, vendor diverso). Se i pattern sono simili, il framework e' robusto cross-vendor. Se differiscono, rivela che l'architettura del modello conta per la robustezza.

---

## Note tecniche
- 3 cache miss durante l'evaluation (risposte con caratteri speciali non matchati). Impatto trascurabile su 41K+ coppie.
- Perturbazioni rigenerate con seed MD5 (fix 4) — alcune diverse dalla run precedente. Non impatta la validita' dei risultati.
- Tempo totale run GPT-5.4 mini L0: ~390 min (~6.5h)

---

*File temporaneo — cancellare dopo completamento risultati*
