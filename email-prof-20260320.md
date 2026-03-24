Buongiorno Professore,

grazie ancora per il feedback dell'altra volta, è stato molto utile per ricalibrarci.

Le faccio un aggiornamento su quello che ho fatto e poi ho alcune domande prima di procedere.


COSA E' CAMBIATO DALL'ULTIMO AGGIORNAMENTO

Ho implementato un nuovo grader LLM (LLMGrader) che supporta tre provider (OpenAI, Anthropic, Google) e due livelli di informazione: Livello 0 (solo domanda + risposta studente, senza reference answer) e Livello 1 (con reference answer). Questo ci permette di fare esattamente il confronto contrastivo che ci ha suggerito: stessa architettura, variando il livello di contesto dato al grader.

Il framework è pronto per lanciare gli esperimenti. Le perturbazioni su Beetle (~41.000) sono già generate dalla volta scorsa, quindi i nuovi grader LLM possono essere valutati direttamente sugli stessi dati.

Ho messo da parte il fine-tuning di DeBERTa/ModernBERT come mi ha suggerito e ho riformulato le research question di conseguenza.


RESEARCH QUESTION AGGIORNATE

1. Le metriche di perturbazione (IVR, SSR, ASR) catturano dimensioni di qualità ortogonali rispetto alle metriche tradizionali di agreement (accuracy, QWK)?
2. Esiste un robustness drop sistematico tra valutazione in-distribution (within-question) e out-of-distribution (cross-question)?
3. L'accesso a informazioni di grading (reference answer) riduce la fragilità dei grader LLM alle perturbazioni?
4. La robustezza al perturbation testing correla con la capacità generale del modello misurata dai benchmark standard?

Le prime due le abbiamo già confermate con i dati dell'HybridGrader. Le ultime due sono le nuove, allineate al suo suggerimento.


SETUP SPERIMENTALE PREVISTO

4 modelli LLM di 3 vendor diversi:
- GPT-5.4 mini (OpenAI, budget)
- Gemini 2.5 Flash (Google, budget)
- Claude Haiku 4.5 (Anthropic, budget)
- GPT-5.4 (OpenAI, frontier)

Ciascuno testato con e senza reference answer, per un totale di 8 run sul dataset Beetle. Il costo stimato usando le Batch API (che dimezzano il prezzo) è circa $163.


DOMANDE

1. Per il paper IFKAD è sufficiente solo il dataset Beetle (~5.200 risposte) o serve anche SciEntsBank (~10.800 risposte)? SciEntsBank raddoppierebbe i costi API ma rafforzerebbe la generalizzabilità dei risultati.

2. Il setup con 4 modelli x 2 livelli le sembra adeguato, o preferisce aggiungere/togliere qualcosa?

3. Il costo degli esperimenti (~$163 per Beetle, ~$330 per entrambi i dataset) è a carico mio o esiste un budget dipartimentale per costi di ricerca?

4. L'abstract inviato a IFKAD menziona tre grader: "transformer-based rater, hybrid rater, rubric-driven LLM-based rater". Con il cambio di direzione verso i confronti contrastivi, vuole che manteniamo comunque un transformer fine-tuned per coerenza con l'abstract, o possiamo riformulare liberamente nel full paper?

5. Ho verificato che il full paper IFKAD va sottomesso entro il 2 maggio 2026, quindi abbiamo circa 6 settimane. Inizio subito a stendere la bozza in parallelo con gli esperimenti, così possiamo iterare. Le va bene?


CREDITI API PER LA RICERCA

Ho trovato che OpenAI, Anthropic e Google offrono programmi di crediti API gratuiti per la ricerca accademica:
- OpenAI: fino a $1.000 (Researcher Access Program, review trimestrale, la prossima è marzo)
- Anthropic: fino a $20.000 (AI for Science Program)
- Google: crediti Gemini per ricercatori accademici

Ho iniziato a compilare la domanda per OpenAI. Posso citarla come supervisore nella richiesta? Servirebbero il suo nome e la sua email istituzionale (ademauro@luiss.it) come co-investigator.


NOTA SUL FINE-TUNING (in risposta alla sua domanda)




SPIEGAZIONE DELLE RESEARCH QUESTION



PYTHON PACKAGE (in risposta alla sua idea)

L'idea di rendere il framework un pacchetto Python installabile è fattibile e il codebase è già strutturato per questo. Il codice è organizzato in moduli indipendenti (loaders, splitters, graders, perturbations, metrics, evaluation) con interfacce astratte e modelli Pydantic validati, quindi l'architettura è già quella di un package. In pratica servirebbe aggiungere un pyproject.toml per renderlo installabile via pip, una documentazione API pubblica, e qualche esempio d'uso. Un ricercatore potrebbe poi installarlo, caricare il proprio dataset, collegare il proprio grader (anche un LLM), e ottenere le metriche di robustezza con poche righe di codice. Per la conferenza lo terrei come contributo aggiuntivo da menzionare nel paper ("framework disponibile come open-source tool"), e lo rilascerei in forma completa per il journal.


Come sempre, se preferisce ne parliamo a voce.

Buona giornata,
Ferdinando
