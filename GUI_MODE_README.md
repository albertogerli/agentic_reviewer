# 🖱️ GUI Mode - Interactive File Selection

## ✨ Nuova Funzionalità

Ora puoi lanciare `generic_reviewer.py` **senza argomenti** e il sistema aprirà finestre di dialogo grafiche per selezionare i file!

## 🚀 Come Funziona

### Lancio Semplicissimo

```bash
python3 generic_reviewer.py
```

**Fatto!** Il sistema si avvierà in modalità interattiva.

---

## 📋 Processo Passo-Passo

### 1️⃣ **Selezione Documento Principale**

```
📂 DOCUMENT SELECTION - Interactive Mode
======================================================================

A file dialog window will open to select your document.
Press ENTER to continue or type 'skip' to use command-line arguments...

> [PREMI INVIO]
```

**→ Si apre una finestra** per selezionare il documento da analizzare
- ✅ Supporta: PDF, TXT, MD, DOCX, DOC
- ✅ Finestra nativa del sistema operativo
- ✅ Preview del file (su macOS)

---

### 2️⃣ **Documenti di Riferimento (Opzionale)**

```
----------------------------------------------------------------------
📚 Do you want to add reference documents?
   (templates, guidelines, examples, data, etc.)

Press ENTER to skip, or type 'yes' to select references...

> yes
```

**Se scegli 'yes':**

```
📋 What type of reference documents are these?
  1. Template (document structure to follow)
  2. Guideline (rules and requirements)
  3. Example (sample documents)
  4. Data (supporting data/statistics)
  5. Style Guide (formatting/style rules)

Enter number [1-5] or press ENTER for 'Example':

> 1
```

**→ Si apre finestra per selezionare UNO O PIÙ file**
- 💡 **Tip**: Tieni premuto **Cmd** (Mac) o **Ctrl** (Windows/Linux) per selezioni multiple
- ✅ Supporta: PDF, Word, Excel, TXT, MD

---

### 3️⃣ **Batch Mode (Opzionale)**

```
----------------------------------------------------------------------
📁 Do you want to process a directory of documents (batch mode)?
   This will process all documents in a folder instead of a single file.

Press ENTER to skip, or type 'yes' to select a directory...

> yes
```

**→ Si apre finestra per selezionare una CARTELLA**
- ✅ Elabora tutti i documenti nella cartella
- ✅ Modalità parallela disponibile
- ✅ Report comparativo finale

---

### 4️⃣ **Modalità Iterativa (Auto-Prompt)**

```
💡 GUI Mode: Would you like to enable iterative improvement?
   (The system will improve the document through multiple iterations)

Type 'yes' to enable, or press ENTER to skip:

> yes
✅ Iterative mode enabled with interactive feedback

How many iterations? (default: 3, press ENTER to use default):

> 5
✅ Max iterations set to: 5
```

---

### 5️⃣ **Python Tools (Auto-Enabled)**

```
✅ Python tools enabled for advanced data validation
```

**Automaticamente abilitato** in modalità GUI per:
- ✅ Validazione calcoli matematici
- ✅ Verifica consistenza dati
- ✅ Analisi statistiche

---

## 🎯 Esempi di Utilizzo

### Scenario 1: Review Semplice

```bash
python3 generic_reviewer.py
```

1. **Premi INVIO** → Finestra si apre
2. **Seleziona il PDF** → `valmadrera.pdf`
3. **INVIO** per saltare references
4. **INVIO** per saltare batch mode
5. **INVIO** per review standard (no iterazioni)
6. **Parte l'analisi!** ✅

---

### Scenario 2: Review con Template

```bash
python3 generic_reviewer.py
```

1. **Premi INVIO** → Seleziona documento principale
2. **Digita 'yes'** per references
3. **Digita '1'** per tipo "Template"
4. **Seleziona template.pdf** (+ altri con Cmd/Ctrl)
5. **INVIO** per batch mode
6. **Digita 'yes'** per modalità iterativa
7. **Digita '3'** per 3 iterazioni
8. **Parte l'analisi con template compliance!** ✅

---

### Scenario 3: Batch Processing

```bash
python3 generic_reviewer.py
```

1. **Premi INVIO** → Seleziona un file qualsiasi (sarà ignorato)
2. **INVIO** per saltare references
3. **Digita 'yes'** per batch mode
4. **Seleziona cartella** con tutti i documenti
5. **Il sistema elabora TUTTI i file nella cartella!** ✅

---

## 🔄 Modalità Compatibili

### GUI Mode (Nuovo!)

```bash
python3 generic_reviewer.py
# Finestre interattive! 🖱️
```

### Command-Line Mode (Come Prima)

```bash
python3 generic_reviewer.py documento.pdf --iterative --enable-python-tools
# Nessuna finestra, puri argomenti CLI
```

### Hybrid Mode

```bash
python3 generic_reviewer.py --iterative --max-iterations 5
# Finestra si apre per selezionare il file, ma usa le opzioni CLI fornite
```

---

## ⌨️ Scorciatoie da Tastiera

| Azione | Comando |
|--------|---------|
| **Saltare tutto e uscire** | Digita `skip` alla prima domanda |
| **Usare default/Saltare** | Premi **INVIO** senza digitare nulla |
| **Confermare** | Digita `yes`, `y`, `si`, o `sì` |
| **Selezione multipla** | **Cmd** (Mac) o **Ctrl** (Win/Linux) + Click |

---

## 🎨 File Supportati

### Documenti Principali
- ✅ PDF (`.pdf`)
- ✅ Text (`.txt`, `.md`)
- ✅ Word (`.docx`, `.doc`)

### Documenti di Riferimento
- ✅ PDF, Word, Excel
- ✅ Text, Markdown
- ✅ Qualsiasi formato testuale

---

## 🐛 Troubleshooting

### "GUI dialogs not available (tkinter not installed)"

**Soluzione macOS:**
```bash
# tkinter è incluso con Python di sistema
# Se usi conda/homebrew:
conda install -c anaconda tk
```

**Soluzione Linux:**
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo yum install python3-tkinter  # RedHat/CentOS
```

**Soluzione Windows:**
- tkinter è incluso nell'installer Python standard
- Reinstalla Python selezionando "tcl/tk and IDLE"

---

### La finestra non si apre / si apre dietro

**Soluzione:**
- La finestra usa `topmost=True` per apparire in primo piano
- Su macOS: controlla Preferenze Sistema → Sicurezza → Accessibilità
- Prova a cliccare sull'icona Python nel Dock

---

### Voglio tornare al vecchio modo CLI

**Nessun problema!** Basta fornire il documento come argomento:

```bash
python3 generic_reviewer.py documento.pdf
# Nessuna finestra, parte direttamente
```

---

## 💡 Tips & Tricks

### Velocità Massima
```bash
python3 generic_reviewer.py
# INVIO, seleziona file, INVIO, INVIO, INVIO
# 4 tasti per lanciare l'analisi!
```

### Massima Potenza
```bash
python3 generic_reviewer.py
# Seleziona documento
# yes → seleziona template
# yes → abilita iterative
# 5 → imposta 5 iterazioni
# Ottieni review enterprise-grade!
```

### Solo Selezione File, Poi CLI
```bash
python3 generic_reviewer.py --iterative --max-iterations 3 --target-score 90
# Seleziona file con GUI
# Ma usa le opzioni CLI specificate
```

---

## 📊 Output

L'output è **identico** alla modalità CLI:

```
valmadrera_20251104_235959/
├── document_original.txt
├── document_final.txt
├── review_results.json
├── review_report.md
├── dashboard.html
└── logs/
```

---

## 🎉 Vantaggi

✅ **Zero memorizzazione** di percorsi file
✅ **Finestre native** del sistema operativo  
✅ **Preview dei file** (su macOS)  
✅ **Selezioni multiple** con Cmd/Ctrl  
✅ **100% compatibile** con modalità CLI  
✅ **Auto-enable** delle feature avanzate  
✅ **Workflow guidato** passo-passo  

---

## 🚀 Quick Start

**Per iniziare SUBITO:**

```bash
cd /Users/albertogiovannigerli/Desktop/Università/Lezioni/AI/Sassari
python3 generic_reviewer.py
```

**Premi INVIO quando chiesto, seleziona il tuo file, e sei pronto!** 🎯

---

## 📝 Note

- Se lanci senza argomenti → **GUI Mode**
- Se lanci con argomenti → **CLI Mode** (come prima)
- Puoi sempre digitare `skip` per tornare a CLI
- Python tools e iterative mode sono **suggeriti** in GUI ma opzionali

**Enjoy the new GUI experience!** 🎨✨

