# 💬 Modalità Interattiva - Guida Completa

## 🎯 Cos'è la Modalità Interattiva?

La **modalità interattiva** è una funzione avanzata che permette al sistema di **chiedere informazioni o file supplementari** all'utente durante il processo di miglioramento del documento.

### 🌟 Caratteristiche Principali

- 🤔 **Analisi Intelligente**: Il sistema identifica cosa manca o potrebbe migliorare il documento
- 📁 **Richiesta File**: Può chiedere Excel, PDF, Word, CSV e altri file
- 💬 **Domande Mirate**: Fa domande specifiche basate sul feedback degli agenti
- 🔄 **Integrazione Automatica**: Usa le tue risposte per migliorare il documento
- ⚡ **Supporto Multi-Formato**: Gestisce automaticamente vari formati file

---

## 🚀 Come Attivare

### Modalità Base (Non Interattiva)

```bash
python3 generic_reviewer.py documento.pdf --iterative
```

**Comportamento:** Il sistema migliora il documento solo con le informazioni disponibili.

### Modalità Interattiva

```bash
python3 generic_reviewer.py documento.pdf --iterative --interactive
```

**Comportamento:** Il sistema può chiedere informazioni/file aggiuntivi per migliorare ulteriormente.

---

## 📋 Tipi di Richieste

### 1️⃣ Richiesta Informazioni

Il sistema chiede **dati specifici** che mancano nel documento.

**Esempio:**
```
🤔 RICHIESTE DI INFORMAZIONI AGGIUNTIVE
================================================================================

1. (Richiesto)
   Domanda: Qual è stato il fatturato effettivo nel Q3 2023?
   Motivo: Il Data Validator ha trovato un'incongruenza nei calcoli
   La tua risposta (o INVIO per saltare):
   > 2.450.000 euro
   ✅ Informazione ricevuta!
```

### 2️⃣ Richiesta File Upload

Il sistema chiede **file esterni** (Excel, PDF, Word, etc.) con dati supplementari.

**Esempio:**
```
2. (Opzionale)
   Domanda: Puoi fornire il file Excel con le proiezioni finanziarie?
   Motivo: Per verificare tutti i calcoli e assicurare coerenza dei dati
   Tipo file: xlsx, csv
   Inserisci il path del file (o INVIO per saltare):
   > /Users/me/Desktop/proiezioni_2024.xlsx
   ✅ File caricato e processato!
```

### 3️⃣ Richiesta Chiarimenti

Il sistema chiede **spiegazioni** su punti poco chiari.

**Esempio:**
```
3. (Opzionale)
   Domanda: Cosa intendi esattamente con "strategia omnicanale"?
   Motivo: Il termine è usato ma non spiegato, potrebbe confondere i lettori
   La tua risposta (o INVIO per saltare):
   > Integrazione tra vendita online e punti vendita fisici
   ✅ Informazione ricevuta!
```

---

## 🔧 Formati File Supportati

### 📊 Excel / CSV
```python
Formati: .xlsx, .xls, .csv
Uso: Dati finanziari, tabelle, statistiche
Processamento: Estrae tutti i fogli e dati
```

### 📄 PDF
```python
Formati: .pdf
Uso: Documenti di riferimento, report
Processamento: Estrae testo completo
```

### 📝 Word
```python
Formati: .docx, .doc
Uso: Documenti supplementari, template
Processamento: Estrae testo con formattazione
```

### 📋 Testo
```python
Formati: .txt, .md, .json
Uso: Note, markdown, dati strutturati
Processamento: Legge contenuto diretto
```

---

## 💡 Casi d'Uso Reali

### Scenario 1: Business Plan con Dati Mancanti

#### Problema Identificato
```
Data Validator: "Le proiezioni finanziarie mostrano una crescita del 45%
ma mancano i dati storici per validare questa stima."
```

#### Richiesta Sistema
```
🤔 Domanda: Puoi fornire il file Excel con i dati storici degli ultimi 3 anni?
📁 Tipo file: xlsx, csv
💡 Motivo: Per validare la realisticità delle proiezioni di crescita
```

#### Tu Fornisci
```
> /Users/me/Documenti/storico_2021_2023.xlsx
```

#### Risultato
✅ Il sistema verifica i dati, conferma che la crescita è coerente, e migliora la sezione con analisi dettagliata.

---

### Scenario 2: Paper Scientifico con Calcoli Dubbi

#### Problema Identificato
```
Data Validator: "L'equazione 3 produce risultati che non corrispondono
alla Figura 2. Possibile errore nei parametri."
```

#### Richiesta Sistema
```
🤔 Domanda: Quali sono i valori corretti dei parametri α e β nell'equazione 3?
💡 Motivo: I valori attuali producono risultati inconsistenti
```

#### Tu Fornisci
```
> α = 0.85, β = 1.23 (rivisti dopo peer review)
```

#### Risultato
✅ Il sistema corregge l'equazione e rigenera la spiegazione con i valori corretti.

---

### Scenario 3: Report Tecnico con Grafici

#### Problema Identificato
```
Chart Analyzer: "Il grafico mostra trend di utilizzo ma manca il file
sorgente dei dati per verificare accuratezza."
```

#### Richiesta Sistema
```
🤔 Domanda: Puoi fornire il CSV con i dati di utilizzo mensile?
📁 Tipo file: csv, xlsx
💡 Motivo: Per verificare accuratezza del grafico e suggerire visualizzazioni migliori
```

#### Tu Fornisci
```
> /Users/me/Desktop/utilizzo_mensile.csv
```

#### Risultato
✅ Il sistema verifica i dati, conferma il grafico, e suggerisce un grafico aggiuntivo per le tendenze stagionali.

---

### Scenario 4: Proposta Commerciale con Referenze

#### Problema Identificato
```
Citation Validator: "Il documento cita un case study di successo ma
non fornisce dettagli o documentazione."
```

#### Richiesta Sistema
```
🤔 Domanda: Puoi fornire il PDF del case study citato?
📁 Tipo file: pdf, docx
💡 Motivo: Per includere dettagli specifici e rafforzare la credibilità
```

#### Tu Fornisci
```
> /Users/me/Documenti/case_study_cliente_X.pdf
```

#### Risultato
✅ Il sistema estrae i punti chiave del case study e integra esempi concreti nella proposta.

---

## 🎮 Workflow Completo

### Passo 1: Review Iniziale
```
📊 Gli agenti analizzano il documento
🔍 Identificano punti deboli, errori, dati mancanti
```

### Passo 2: Analisi Interattiva (se --interactive)
```
🤔 Il sistema analizza il feedback degli agenti
💡 Identifica cosa potrebbe chiedere all'utente
📋 Genera lista di richieste prioritizzate
```

### Passo 3: Interazione Utente
```
💬 Il sistema presenta le richieste
📁 Tu fornisci informazioni/file
✅ Il sistema processa i dati
```

### Passo 4: Miglioramento Integrato
```
🔧 Il sistema usa le tue risposte
📝 Applica miglioramenti mirati
⭐ Produce documento di qualità superiore
```

### Passo 5: Iterazioni Successive
```
🔄 Nelle iterazioni successive usa ancora i dati forniti
📈 Continua a raffinare basandosi su tutte le informazioni
```

---

## 🔍 Esempi di Output

### Con Informazioni Fornite

```markdown
## Proiezioni Finanziarie (Migliorate)

Sulla base dei dati storici forniti (2021-2023), che mostrano una crescita
media annua del 38%, la proiezione di crescita del 45% per il 2024 è
**realistica e sostenibile**.

Analisi dati storici:
- 2021: €1.2M (+32% YoY)
- 2022: €1.7M (+42% YoY)  
- 2023: €2.4M (+41% YoY)

La crescita superiore prevista per il 2024 è giustificata da:
1. Espansione nuovo mercato europeo
2. Lancio prodotto premium
3. Trend di mercato favorevole (+12% settore)

**Fonte dati:** storico_2021_2023.xlsx (verificato)
```

### Senza Informazioni (Modalità Non-Interattiva)

```markdown
## Proiezioni Finanziarie

Il piano prevede una crescita del 45% per il 2024.

**Nota:** La proiezione non è supportata da dati storici verificabili
nel documento.
```

**Differenza chiara!** Con la modalità interattiva il documento è molto più robusto e credibile.

---

## ⚙️ Opzioni Avanzate

### Combinare con Altre Opzioni

```bash
# Modalità completa: interattiva + iterativa + target alto
python3 generic_reviewer.py doc.pdf \
    --iterative \
    --interactive \
    --max-iterations 5 \
    --target-score 90 \
    --output-language Italian
```

### Solo Prima Iterazione

Il sistema chiede informazioni **solo alla prima iterazione**, poi usa quei dati per tutte le iterazioni successive.

**Perché?**
- ⏱️ Non interrumpe troppo il flusso
- 💾 I dati forniti sono riutilizzati
- 🎯 Focus su informazioni critiche

---

## 🎛️ Controllo Richieste

### Richieste Obbligatorie vs Opzionali

```
1. (Richiesto)  ← Informazione critica per miglioramento
   ...
   
2. (Opzionale) ← Migliorerebbe, ma non bloccante
   ...
```

### Saltare Richieste

Puoi sempre premere **INVIO** per saltare una richiesta:
```
La tua risposta (o INVIO per saltare):
> [INVIO]
⚠️  Informazione richiesta ma non fornita
```

Il sistema continuerà comunque, ma senza quella informazione.

---

## 📊 Processamento File

### Excel Multi-Sheet

Se carichi un file Excel con più fogli:
```
=== Sheet: Dati_2023 ===
  Mese    Vendite    Costi
  Gen     150000     80000
  Feb     165000     85000
  ...

=== Sheet: Dati_2024 ===
  Mese    Vendite    Costi
  Gen     180000     90000
  ...
```

Tutti i fogli vengono processati automaticamente!

### PDF Multi-Pagina

Tutto il testo viene estratto:
```
Page 1 content...
Page 2 content...
...
```

### CSV Grandi

Anche file CSV grandi (limitati a primi 10.000 caratteri nel context):
```
date,value,category
2023-01-01,125.5,sales
2023-01-02,142.3,sales
...
[Primi 10K caratteri usati per analisi]
```

---

## 🚨 Gestione Errori

### File Non Trovato
```
⚠️  File not found: /path/to/file.xlsx
```
**Soluzione:** Controlla il path e riprova.

### Formato Non Supportato
```
⚠️  Unsupported file type: .zip
```
**Soluzione:** Estrai il file o converti in formato supportato.

### Librerie Mancanti

Se manca una libreria (es. pandas per Excel):
```
⚠️  pandas library not available for Excel processing
```

**Soluzione:**
```bash
pip install pandas openpyxl  # Per Excel
pip install python-docx      # Per Word
```

---

## 💎 Best Practices

### 1. Prepara i File in Anticipo

Prima di lanciare la review:
```bash
mkdir ~/review_support_files
cp proiezioni.xlsx ~/review_support_files/
cp case_study.pdf ~/review_support_files/
```

### 2. Usa Path Assoluti

```bash
# Meglio
> /Users/me/Desktop/dati.xlsx

# Può dare problemi
> ../dati.xlsx
```

### 3. File Puliti e Organizzati

- Excel: Sheet con nomi chiari
- PDF: Testo selezionabile (non scansioni)
- CSV: Headers chiari, dati consistenti

### 4. Risposte Chiare

```bash
# Bene
> Il target di mercato sono PMI italiane nel settore manifatturiero

# Vago
> Aziende italiane
```

### 5. Non Esagerare

Il sistema chiede max 5 informazioni più importanti. Non sovraccaricare con file enormi.

---

## 📈 Impatto sulla Qualità

### Esempio Reale: Business Plan

**Senza Modalità Interattiva:**
- Score iniziale: 62/100
- Score finale (dopo 3 iter): 75/100
- Miglioramento: **+13 punti**

**Con Modalità Interattiva:**
- Score iniziale: 62/100
- User fornisce Excel + 3 risposte
- Score finale (dopo 3 iter): **88/100**
- Miglioramento: **+26 punti**

**Raddoppia il miglioramento!** 🚀

---

## 🔄 Confronto Modalità

| Feature | Standard | Iterativa | Interattiva + Iterativa |
|---------|----------|-----------|-------------------------|
| **Review iniziale** | ✅ | ✅ | ✅ |
| **Feedback agenti** | ✅ | ✅ | ✅ |
| **Miglioramento auto** | ❌ | ✅ | ✅ |
| **Iterazioni multiple** | ❌ | ✅ | ✅ |
| **Richiesta info utente** | ❌ | ❌ | ✅ |
| **Upload file esterni** | ❌ | ❌ | ✅ |
| **Qualità finale** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Quando Usare Modalità Interattiva?

### ✅ USA Quando:

- 📊 **Hai dati esterni** rilevanti (Excel, CSV, database)
- 📄 **Hai documenti di supporto** (case studies, references)
- 🎯 **Vuoi massima qualità** possibile
- ⏱️ **Hai tempo** per fornire informazioni
- 💼 **Documento importante** (presentazioni, proposte, papers)

### ❌ NON Usare Quando:

- ⚡ **Hai fretta** e vuoi risultati rapidi
- 📝 **Documento semplice** (email, memo brevi)
- 🤷 **Non hai dati aggiuntivi** da fornire
- 🔄 **Prima bozza esplorativa**

---

## 💻 Comandi Completi

### Quick Reference

```bash
# Modalità base
python3 generic_reviewer.py documento.pdf

# Con iterazioni (automatico)
python3 generic_reviewer.py documento.pdf --iterative

# Con interazione (massima qualità)
python3 generic_reviewer.py documento.pdf --iterative --interactive

# Personalizzato
python3 generic_reviewer.py documento.pdf \
    --iterative \
    --interactive \
    --max-iterations 5 \
    --target-score 90 \
    --output-language Italian \
    --title "Business Plan 2024"
```

---

## 🎓 Tips & Tricks

### 1. Prepara Risposte in Anticipo

Se sai già cosa potrebbe servire, crea un file di note:
```
notes.txt:
- Budget 2024: €500K
- Team size: 12 persone
- Target market: PMI con 50-250 dipendenti
```

### 2. Nomi File Descrittivi

```bash
# Bene
dati_finanziari_Q1_Q4_2023.xlsx
case_study_successo_cliente_TechCorp.pdf

# Male
dati.xlsx
doc.pdf
```

### 3. Testa Prima in Modalità Non-Interattiva

```bash
# Prima prova senza --interactive
python3 generic_reviewer.py doc.pdf --iterative

# Vedi cosa viene richiesto nel feedback
# Poi rilancia con --interactive avendo i file pronti
python3 generic_reviewer.py doc.pdf --iterative --interactive
```

### 4. Usa Tab-Completion

In zsh/bash, usa TAB per completare i path:
```bash
Inserisci il path del file:
> /Users/me/Des[TAB] → /Users/me/Desktop/
```

---

## 📦 Installazione Dipendenze

Per supportare tutti i formati:

```bash
# Excel/CSV
pip install pandas openpyxl

# Word
pip install python-docx

# PDF (già incluso nel progetto)
pip install PyPDF2

# Tutto insieme
pip install pandas openpyxl python-docx PyPDF2
```

---

## 🎉 Esempio Completo End-to-End

### Setup
```bash
cd ~/Desktop/my_project
mkdir support_files
cp financial_data.xlsx support_files/
cp market_research.pdf support_files/
```

### Esecuzione
```bash
python3 generic_reviewer.py business_plan.pdf \
    --iterative \
    --interactive \
    --max-iterations 3 \
    --target-score 85 \
    --output-language Italian
```

### Interazione
```
🤔 RICHIESTE DI INFORMAZIONI AGGIUNTIVE
================================================================================

1. (Richiesto)
   Domanda: Puoi fornire i dati finanziari dettagliati per Q1-Q4 2023?
   Motivo: Per validare le proiezioni di crescita menzionate
   Tipo file: xlsx, csv
   > ~/Desktop/my_project/support_files/financial_data.xlsx
   ✅ File caricato!

2. (Opzionale)
   Domanda: Hai una ricerca di mercato che supporta il TAM di €50M?
   Motivo: Per rafforzare l'analisi di mercato
   Tipo file: pdf, docx
   > ~/Desktop/my_project/support_files/market_research.pdf
   ✅ File caricato!

3. (Opzionale)
   Domanda: Chi sono i competitor principali e le loro quote di mercato?
   > Competitor A (35%), Competitor B (28%), noi (12%), altri (25%)
   ✅ Info ricevuta!
```

### Risultato
```
✅ Iterative review completed successfully!
📈 Quality improvement: +28.5 points
⭐ Best iteration: #3
🎯 Final score: 89.5/100

📁 Files created:
   - business_plan_20241104_100000/
     ├── iterative_dashboard_*.html
     ├── document_best_version_iter3.txt
     ├── iterative_results_*.json
     └── ...
```

---

## 🚀 Prossimi Passi

Ora che hai capito la modalità interattiva:

1. ✅ Prepara i tuoi documenti di supporto
2. ✅ Installa le librerie necessarie
3. ✅ Lancia il primo test con `--interactive`
4. ✅ Fornisci le informazioni richieste
5. ✅ Confronta i risultati con/senza modalità interattiva

---

**La modalità interattiva trasforma il sistema da reviewer passivo a collaboratore attivo! 🤖🤝👤**

