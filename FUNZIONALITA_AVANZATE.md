# 🚀 Funzionalità Avanzate v3.0

## 📦 Novità Versione 3.0

Questa versione introduce funzionalità **professionali e production-ready**:

1. 📊 **Progress Bar Visive** - Tracking real-time del progresso
2. 🔔 **Notifiche Sistema** - Notifiche native macOS/Linux/Windows
3. 💾 **Pause/Resume** - Sistema di checkpoint per interruzione/ripresa
4. 🗄️ **Database Persistente** - Tracking completo di tutte le review
5. 📈 **Comparazione Versioni** - Confronto evoluzione documento nel tempo
6. 🕐 **Storia Sessioni** - Memoria tra sessioni e progetti

---

## 📊 1. Progress Bar Visive

### Cosa Sono?

Progress bar **real-time** che mostrano esattamente cosa sta facendo il sistema in ogni momento.

### Come Funzionano?

Il sistema mostra **due livelli** di progress:

#### 📍 Progress Generale
```
Overall Progress |████████████████            | 60/100 [01:23<00:55]
```

#### 📍 Progress Fase Corrente
```
  └─ Iteration 2: Review |███████             | 7/15
```

### Esempio Visivo

```
Overall Progress |████████░░░░░░░░░░░░░░░░░░░░| 30/100 [00:45<01:45]
  └─ Document Classification: Analyzing structure |██████░░░░| 6/10
```

### Informazioni Mostrate

- **Percentuale completamento** - Quanto manca alla fine
- **Tempo trascorso** - Da quanto è iniziato
- **Tempo rimanente** - ETA (Estimated Time of Arrival)
- **Fase corrente** - Cosa sta facendo ora
- **Velocità** - Steps per secondo

### Modalità Disponibili

#### Standard Mode
```
Phase 1: Document Analysis          [████████████░░░░░░░░] 60%
Phase 2: Agent Reviews               [░░░░░░░░░░░░░░░░░░░░]  0%
Phase 3: Report Generation           [░░░░░░░░░░░░░░░░░░░░]  0%
```

#### Iterative Mode  
```
Overall Progress                     [████████░░░░░░░░░░░░] 40%
  └─ Iteration 2: Review            [████████████████░░░░] 80%
```

#### Interactive Mode
```
Overall Progress                     [██████░░░░░░░░░░░░░░] 30%
  └─ Collecting User Input          [███████████████░░░░░] 75%
```

### Abilitazione

Progress bar sono **automaticamente abilitate** se hai installato `tqdm`:

```bash
pip install tqdm
```

Se `tqdm` non è disponibile, il sistema continua a funzionare ma **senza** progress bar visive (usa solo logging).

---

## 🔔 2. Notifiche Sistema

### Cosa Sono?

Notifiche **native del sistema operativo** che ti avvisano quando:
- ✅ Review completata
- ❌ Errore verificatosi
- 💾 Checkpoint salvato
- 🔄 Iterazione completata

### Supporto Multi-Piattaforma

| OS | Tipo Notifica | Supporto |
|----|---------------|----------|
| **macOS** | Notification Center | ✅ Nativo |
| **Linux** | notify-send | ✅ Con notify-send |
| **Windows** | Toast Notifications | ✅ Windows 10+ |

### Esempi Notifiche

#### Inizio Review
```
┌─────────────────────────────┐
│ Document Reviewer           │
├─────────────────────────────┤
│ Review Started              │
│                             │
│ Processing:                 │
│ Business Plan 2024.pdf      │
└─────────────────────────────┘
```

#### Review Completata
```
┌─────────────────────────────┐
│ Document Reviewer           │
├─────────────────────────────┤
│ Review Complete! ✅         │
│                             │
│ Business Plan 2024.pdf      │
│ Score: 87/100               │
│ Time: 18m 32s               │
└─────────────────────────────┘
```

#### Checkpoint Salvato
```
┌─────────────────────────────┐
│ Document Reviewer           │
├─────────────────────────────┤
│ Checkpoint Saved            │
│                             │
│ Business Plan 2024.pdf      │
│ Iteration 2 saved           │
│ Can resume later            │
└─────────────────────────────┘
```

#### Errore
```
┌─────────────────────────────┐
│ Document Reviewer           │
├─────────────────────────────┤
│ Review Error ❌             │
│                             │
│ Business Plan 2024.pdf      │
│ Error: API rate limit       │
└─────────────────────────────┘
```

### Configurazione

#### Abilitare/Disabilitare

```bash
# Abilitate di default
python3 generic_reviewer.py doc.pdf --iterative

# Disabilitate
python3 generic_reviewer.py doc.pdf --iterative --no-notifications
```

#### Setup Linux

```bash
# Installa notify-send (se non presente)
sudo apt-get install libnotify-bin  # Ubuntu/Debian
sudo dnf install libnotify            # Fedora
```

### Vantaggi

- ✅ **Lavora su altro** - Vieni notificato quando finisce
- ✅ **Multi-tasking** - Non devi tenere terminale aperto
- ✅ **Errori immediati** - Notifica istantanea se qualcosa va storto
- ✅ **Tracking iterazioni** - Notifica a ogni iterazione completata

---

## 💾 3. Sistema Pause/Resume

### Cosa Fa?

Permette di **interrompere** una review in corso e **riprenderla** successivamente esattamente da dove si era interrotta.

### Quando è Utile?

- 🔋 **Batteria scarica** - Salva e riprendi dopo ricarica
- 🌙 **Lavoro lungo** - Inizia ora, finisci domani
- ⚠️ **Problemi API** - Pausa se rate limit, riprendi dopo
- 💼 **Interruzioni** - Salva per meeting, riprendi dopo
- 🧪 **Testing** - Prova iterazioni una alla volta

### Come Funziona?

#### Salvataggio Automatico

Il sistema salva **checkpoint automatici** dopo ogni iterazione:

```
Iteration 1 completed → Checkpoint saved automatically
Iteration 2 completed → Checkpoint saved automatically
Iteration 3 completed → Checkpoint saved automatically
```

#### Pausa Manuale

Premi `Ctrl+C` in qualsiasi momento:

```bash
$ python3 generic_reviewer.py doc.pdf --iterative

Overall Progress |████████░░░░░░░░░░░░| 40%
  └─ Iteration 2: Review |████░░░░░░░░| 30%

^C  # Premi Ctrl+C

💾 Checkpoint saved: checkpoint_abc123
📝 You can resume with: --resume checkpoint_abc123
```

#### Ripresa

Usa il checkpoint ID per riprendere:

```bash
python3 generic_reviewer.py --resume checkpoint_abc123

💾 Loading checkpoint...
✅ Checkpoint loaded successfully
📍 Resuming from: Iteration 2 (30% complete)

Overall Progress |████████░░░░░░░░░░░░| 40%
  └─ Iteration 2: Review |████░░░░░░░░| 30%  ← Riprende da qui!
```

### Checkpoints Salvati

Ogni checkpoint contiene:

```json
{
  "checkpoint_id": "checkpoint_20241104_abc123",
  "document_hash": "abc123def456",
  "document_title": "Business Plan 2024",
  "current_iteration": 2,
  "current_phase": "Review",
  "state_data": {
    "document_text": "...",
    "reviews_completed": [...],
    "scores": [78, 84],
    "improvements_applied": [...],
    "user_inputs": {...}
  }
}
```

### Gestione Checkpoints

#### Listarli

```bash
python3 review_history.py checkpoints

💾 AVAILABLE CHECKPOINTS (3)
================================================================================
Checkpoint ID           Document                    Iteration  Phase
checkpoint_20241104...  Business Plan 2024          2          Review
checkpoint_20241103...  Research Paper AI           1          Improve
checkpoint_20241102...  Marketing Strategy          3          Final Reports
```

#### Rimuoverli

```bash
# Checkpoint vengono automaticamente invalidati dopo completamento review
# O dopo 7 giorni di inattività
```

### Limitazioni

- ⚠️ **Modifiche documento** - Se modifichi il documento, checkpoint non valido
- ⚠️ **Configurazione diversa** - Deve usare stessa configurazione
- ⚠️ **Versione software** - Stessa versione del reviewer

---

## 🗄️ 4. Database Persistente

### Cosa Fa?

**Salva permanentemente** tutte le informazioni di ogni review in un database SQLite locale.

### Cosa Viene Salvato?

Ogni review salva:

```
✅ Document hash (per identificare documento)
✅ Title e project name
✅ Data e ora review
✅ Score finale
✅ Numero iterazioni
✅ Modalità (standard/iterative/interactive)
✅ Lingua output
✅ Numero miglioramenti applicati
✅ Issue counts (critical, moderate, minor)
✅ Numero agenti utilizzati
✅ Output directory
✅ Metadata custom (JSON)
```

### File Database

```bash
document_reviews.db  # Database SQLite locale

# Location
~/Desktop/Università/.../document_reviews.db

# Dimensione tipica
~100KB per 100 reviews
```

### Schema Database

#### Tabella: document_versions
```sql
CREATE TABLE document_versions (
    version_id TEXT PRIMARY KEY,
    document_hash TEXT NOT NULL,
    document_title TEXT NOT NULL,
    project_name TEXT,
    review_date TEXT NOT NULL,
    score REAL NOT NULL,
    iteration_number INTEGER,
    file_path TEXT,
    output_directory TEXT,
    review_mode TEXT,
    language TEXT,
    improvements_applied INTEGER,
    critical_issues INTEGER,
    moderate_issues INTEGER,
    minor_issues INTEGER,
    agent_count INTEGER,
    metadata TEXT,
    created_at TIMESTAMP
);
```

#### Tabella: checkpoints
```sql
CREATE TABLE checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    document_hash TEXT,
    document_title TEXT,
    checkpoint_date TEXT,
    current_iteration INTEGER,
    current_phase TEXT,
    state_data TEXT,
    can_resume INTEGER,
    created_at TIMESTAMP
);
```

#### Tabella: active_sessions
```sql
CREATE TABLE active_sessions (
    session_id TEXT PRIMARY KEY,
    document_hash TEXT,
    start_time TEXT,
    status TEXT,
    progress_percent REAL,
    current_phase TEXT,
    output_directory TEXT,
    updated_at TIMESTAMP
);
```

### Queries Utili

#### Review Recenti
```bash
python3 review_history.py recent --limit 10
```

#### Progetti
```bash
python3 review_history.py projects
```

#### Storia Documento
```bash
python3 review_history.py document <hash>
```

### Backup

```bash
# Backup database
cp document_reviews.db document_reviews_backup.db

# O usa export per backup JSON
python3 review_history.py export "My Project" backup.json
```

---

## 📈 5. Comparazione Versioni

### Cosa Fa?

Confronta **due versioni** dello stesso documento per vedere:
- 📊 Differenza score
- 🐛 Issue risolte
- ⏱️ Tempo tra versioni
- 📝 Miglioramenti applicati

### Come Usare

#### Trova Version IDs

```bash
python3 review_history.py project "My Business Plan"

📊 PROJECT: My Business Plan
================================================================================
...
📝 VERSION HISTORY (3 versions)

Version ID           Date              Score  Issues       Mode
v1_20241104_100000  2024-11-04 10:00  58.0   C:8 M:12 m:15  iterative
v1_20241104_120000  2024-11-04 12:00  84.0   C:2 M:4 m:8   interactive
v1_20241104_140000  2024-11-04 14:00  89.0   C:0 M:1 m:3   iterative
```

#### Compara

```bash
python3 review_history.py compare v1_20241104_100000 v1_20241104_140000

📊 VERSION COMPARISON
================================================================================
Time Between Reviews: 4 hours

Metric              Version 1                Version 2
==================  =======================  =======================
Version ID          v1_20241104_100000       v1_20241104_140000
Date                2024-11-04 10:00         2024-11-04 14:00

Score               58.0/100                 89.0/100

Critical Issues     8                        0
Moderate Issues     12                       1
Minor Issues        15                       3

📈 IMPROVEMENTS

  Score Change: +31.0 points
  Critical Issues Resolved: 8
  Moderate Issues Resolved: 11
  Minor Issues Resolved: 12

  📈 Score improved!
```

### Visual Comparison Dashboard

Ogni progetto ha anche un **dashboard HTML** con:

```html
📊 Score Evolution Chart (line graph)
📈 Issue Resolution Chart (bar chart)
📋 Timeline (chronological view)
🎯 Best Version Highlight
```

---

## 🕐 6. Storia e Memoria tra Sessioni

### Progetto-Based Organization

Il sistema organizza review per **progetto**:

```
Project: "Business Plan 2024"
├─ Version 1 (2024-11-01) Score: 58
├─ Version 2 (2024-11-02) Score: 72  (+14)
├─ Version 3 (2024-11-03) Score: 84  (+12)
└─ Version 4 (2024-11-04) Score: 89  (+5)

Total improvement: +31 points over 4 days
```

### Assegnare a Progetto

```bash
# Con flag --project
python3 generic_reviewer.py doc.pdf \
    --iterative \
    --project "Business Plan 2024"

# Automatico se usi --title consistente
python3 generic_reviewer.py v1.pdf --title "My Proposal"
python3 generic_reviewer.py v2.pdf --title "My Proposal"  # Stesso progetto
```

### Visualizzare Storia Progetto

```bash
python3 review_history.py project "Business Plan 2024"

📊 PROJECT: Business Plan 2024
================================================================================
Document: business_plan_final.pdf
Total Versions: 4
First Review: 2024-11-01 10:00:00
Last Review: 2024-11-04 14:00:00
Best Score: 89.0/100 (version: v1_20241104...)
Total Improvement: +31.0 points
Total Iterations: 12

📝 VERSION HISTORY (4 versions)

Version ID           Date              Score  Issues       Mode       Iterations
==================  ================  =====  ===========  =========  ==========
v1_20241104_140000  2024-11-04 14:00  89.0   C:0 M:1 m:3  iterative  3
v1_20241103_120000  2024-11-03 12:00  84.0   C:2 M:4 m:8  interactive 3
v1_20241102_160000  2024-11-02 16:00  72.0   C:5 M:8 m:12 iterative  3
v1_20241101_100000  2024-11-01 10:00  58.0   C:8 M:12 m:15 standard  1
```

### Export Storia

```bash
python3 review_history.py export "Business Plan 2024" history.json

✅ Project 'Business Plan 2024' exported to: history.json
   4 versions exported
```

**Output JSON:**
```json
{
  "project_name": "Business Plan 2024",
  "export_date": "2024-11-04T15:00:00",
  "summary": {
    "document_title": "business_plan_final.pdf",
    "total_versions": 4,
    "best_score": 89.0,
    "score_improvement": 31.0,
    "date_range": {
      "first": "2024-11-01T10:00:00",
      "last": "2024-11-04T14:00:00"
    }
  },
  "versions": [...]
}
```

---

## 🎯 Casi d'Uso Pratici

### Caso 1: Review Lunga con Pause

```bash
# Giorno 1 - Mattina
python3 generic_reviewer.py business_plan.pdf \
    --iterative \
    --max-iterations 5 \
    --project "Q4 Plan"

[After iteration 2... need to go to meeting]
^C  # Ctrl+C

💾 Checkpoint saved: checkpoint_abc123

# Giorno 1 - Pomeriggio (dopo meeting)
python3 generic_reviewer.py --resume checkpoint_abc123

✅ Resumed! Continuing from iteration 3...

# Review completa
```

### Caso 2: Tracking Miglioramento Documento

```bash
# Versione 1 - Draft iniziale
python3 generic_reviewer.py draft_v1.pdf \
    --project "Thesis Chapter 3"

Score: 62/100  
Issues: Critical: 12, Moderate: 18

# [Fai modifiche basate su feedback]

# Versione 2 - Dopo revisione
python3 generic_reviewer.py draft_v2.pdf \
    --project "Thesis Chapter 3"

Score: 78/100 (+16!)
Issues: Critical: 3, Moderate: 8

# Confronta versioni
python3 review_history.py project "Thesis Chapter 3"

📈 Improvement: +16 points
🐛 Critical issues resolved: 9
```

### Caso 3: Lavoro Notturno

```bash
# Lancia review lunga prima di andare a dormire
python3 generic_reviewer.py large_doc.pdf \
    --iterative \
    --max-iterations 10 \
    --interactive

# Sistema lavora tutta la notte
# Ti sveglia con notifica!

🔔 Review Complete! ✅
   large_doc.pdf
   Score: 91/100
   Time: 6h 23m
```

### Caso 4: Multiple Document Project

```bash
# Review multipli documenti stesso progetto
python3 generic_reviewer.py chapter1.pdf --project "My Book"
python3 generic_reviewer.py chapter2.pdf --project "My Book"
python3 generic_reviewer.py chapter3.pdf --project "My Book"

# Vedi storia completa progetto
python3 review_history.py project "My Book"

Total reviews: 3
Average score: 84.3/100
```

---

## 📊 7. Statistiche Globali

### Vedere Stats Complessive

```bash
python3 review_history.py stats

📊 OVERALL STATISTICS
================================================================================
Total Reviews: 47
Total Projects: 12

Score Statistics:
  Average Score: 79.3/100
  Highest Score: 94.5/100
  Lowest Score: 52.0/100

Review Modes:
  Iterative: 28 (59.6%)
  Interactive: 14 (29.8%)
  Standard: 5 (10.6%)

Languages:
  Italian: 32 (68.1%)
  English: 15 (31.9%)
```

---

## 🛠️ Installazione

### Dipendenze Richieste

```bash
# Installare tutte le funzionalità avanzate
pip install -r requirements_optional.txt

# O individuali
pip install tqdm          # Progress bars
pip install tabulate      # History tables
```

### Verificare Supporto Notifiche

```bash
# macOS: Automatico ✅

# Linux: Controlla notify-send
which notify-send
# Se non presente:
sudo apt-get install libnotify-bin

# Windows: Windows 10+ automatico ✅
```

---

## 🎮 Comandi Quick Reference

### Review con Tutte le Funzionalità

```bash
# Full-featured review
python3 generic_reviewer.py documento.pdf \
    --iterative \
    --interactive \
    --project "My Project" \
    --max-iterations 5 \
    --target-score 90

# Con notifiche disabilitate
python3 generic_reviewer.py documento.pdf \
    --iterative \
    --no-notifications
```

### Gestione Storia

```bash
# Recent reviews
python3 review_history.py recent

# All projects
python3 review_history.py projects

# Project details
python3 review_history.py project "Project Name"

# Compare versions
python3 review_history.py compare version_id_1 version_id_2

# List checkpoints
python3 review_history.py checkpoints

# Export project
python3 review_history.py export "Project Name" output.json

# Overall stats
python3 review_history.py stats
```

### Pause/Resume

```bash
# Durante review: Ctrl+C per pause
^C

# Resume
python3 generic_reviewer.py --resume checkpoint_id
```

---

## 🎓 Best Practices

### 1. Usa Progetti per Organizzare

```bash
# Bene: Progetti specifici
--project "Business Plan Q4 2024"
--project "PhD Thesis - Chapter 3"
--project "Client Proposal - Acme Corp"

# Male: Progetti generici
--project "Documents"
--project "Work"
```

### 2. Review Lunghe → Abilita Tutto

```bash
python3 generic_reviewer.py doc.pdf \
    --iterative \
    --interactive \
    --max-iterations 5  # Progress bar + Notifiche automatiche
```

### 3. Checkpoint Regolari

Il sistema salva automaticamente dopo ogni iterazione, ma puoi sempre fare `Ctrl+C` per salvare manualmente.

### 4. Monitora Storia

```bash
# Controlla regolarmente miglioramenti
python3 review_history.py project "My Project"
```

### 5. Backup Database

```bash
# Backup settimanale
cp document_reviews.db backups/db_$(date +%Y%m%d).db
```

---

## 🚀 Architettura Tecnica

### Componenti

```
generic_reviewer.py          # Main reviewer (integrato)
├─ document_tracker.py       # Database & persistence
├─ progress_notifier.py      # Progress bars & notifications
└─ review_history.py         # History CLI tool

document_reviews.db          # SQLite database
├─ document_versions         # All reviews
├─ checkpoints              # Pause/resume data
└─ active_sessions          # Real-time tracking
```

### Data Flow

```
Review Start
    ↓
Create Session in DB
    ↓
Show Progress Bar
    ↓
For Each Iteration:
    ├─ Update Progress
    ├─ Save Checkpoint
    └─ Notify if Complete
    ↓
Save Final Version to DB
    ↓
Send Completion Notification
    ↓
Close Progress Bar
```

---

## 💡 Tips & Tricks

### Trick 1: Auto-Resume Last

```bash
# Get last checkpoint
LAST_CP=$(python3 review_history.py checkpoints | head -3 | tail -1 | awk '{print $1}')

# Resume
python3 generic_reviewer.py --resume $LAST_CP
```

### Trick 2: Score History Graph

```bash
# Export and plot with external tools
python3 review_history.py export "My Project" data.json
# Use data.json with plotting tools (matplotlib, Excel, etc.)
```

### Trick 3: Notification Sound

On macOS, add sound to notifications:
```bash
# Edit progress_notifier.py _send_macos method:
display notification "..." with title "..." sound name "Glass"
```

### Trick 4: Progress in Different Terminal

```bash
# Start review in one terminal
python3 generic_reviewer.py doc.pdf --iterative &
PID=$!

# Check progress in another terminal
tail -f *.log  # View logs
# Or check database
python3 -c "from document_tracker import *; ..."
```

---

## 🎉 Conclusione

### v3.0 Porta:

1. 📊 **Visibilità completa** - Sai sempre cosa sta succedendo
2. 🔔 **Notifiche intelligenti** - Vieni avvisato quando serve
3. 💾 **Resilienza** - Pause/resume per qualsiasi interruzione
4. 🗄️ **Memoria permanente** - Nessuna review persa mai più
5. 📈 **Insight evoluzione** - Vedi come migliora il documento nel tempo
6. 🎯 **Production-ready** - Pronto per uso professionale

### Next Steps

```bash
# 1. Installa dipendenze
pip install -r requirements_optional.txt

# 2. Prova progress bar
python3 generic_reviewer.py doc.pdf --iterative

# 3. Testa pause/resume
# Durante review premi Ctrl+C, poi resume

# 4. Esplora history
python3 review_history.py recent
python3 review_history.py stats

# 5. Usa per progetto reale!
python3 generic_reviewer.py important_doc.pdf \
    --iterative --interactive --project "Real Project"
```

---

**Sistema ora enterprise-grade con tracking completo e resilienza totale! 🚀🗄️📊**

**Versione:** 3.0  
**Data:** 2024-11-04  
**Status:** Production Ready ✅

