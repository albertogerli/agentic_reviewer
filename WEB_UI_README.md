# 🌐 Web UI - User-Friendly Interface

## ✨ Panoramica

Interfaccia web professionale per il sistema di review, perfetta per utenti **non tecnici**!

### 🎯 Vantaggi

✅ **Zero CLI**: Interfaccia grafica intuitiva  
✅ **Drag & Drop**: Carica documenti facilmente  
✅ **Real-time**: Progress bar e status live  
✅ **Responsive**: Funziona su desktop e tablet  
✅ **Multi-language**: Interfaccia e output localizzabili  
✅ **No Installation**: Basta un browser web  

---

## 🚀 Quick Start

### 1️⃣ Installa Dipendenze

```bash
# Installa dipendenze web UI
pip install -r requirements_web.txt

# Oppure manualmente
pip install gradio>=4.0.0
```

### 2️⃣ Configura API Key

```bash
export OPENAI_API_KEY="sk-..."
```

### 3️⃣ Lancia l'Interfaccia

```bash
python3 web_ui.py
```

**Fatto!** Apri il browser su: http://localhost:7860

---

## 🖥️ Screenshots & Features

### Homepage
```
┌────────────────────────────────────────────┐
│  📄 AI Document Review System              │
│  Enterprise-grade document analysis        │
├────────────────────────────────────────────┤
│                                            │
│  1️⃣ Upload Document                        │
│  ┌──────────────────────────────────────┐ │
│  │  📁 Drag & Drop or Click to Upload  │ │
│  │     Supports: PDF, TXT, MD, DOCX    │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  2️⃣ Configuration                          │
│  Output Language: [Auto-detect ▼]         │
│                                            │
│  🔄 Iterative Mode (Advanced)  [▼]         │
│  🛠️ Advanced Options           [▼]         │
│  📚 Reference Documents        [▼]         │
│                                            │
│  3️⃣ Start Review                           │
│  [     🚀 Start Review      ]              │
│                                            │
└────────────────────────────────────────────┘
```

### Results View
```
┌────────────────────────────────────────────┐
│  📊 Results                                │
├────────────────────────────────────────────┤
│  ✅ Review Complete!                       │
│  ┌──────────┬──────────┬──────────────┐   │
│  │    3     │  82.5    │    +15.3     │   │
│  │Iterations│ Score/100│  Improvement │   │
│  └──────────┴──────────┴──────────────┘   │
│                                            │
│  [📋 Report] [🤖 Agents] [📊 Dashboard]    │
│  [📦 JSON] [📁 Files]                      │
│  ┌──────────────────────────────────────┐ │
│  │ 🌐 Web Researcher                    │ │
│  │ ───────────────────────────────────  │ │
│  │ Verified Claims (8/10):              │ │
│  │ ✅ "Market size $50M" → VERIFIED      │ │
│  │    Source: https://...               │ │
│  │                                      │ │
│  │ 📊 Data Validator                    │ │
│  │ ───────────────────────────────────  │ │
│  │ ✅ Revenue calculations: CORRECT      │ │
│  │    Python code executed              │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

---

## 📋 Guida Passo-Passo

### Per Utenti Non Tecnici

#### Step 1: Apri l'App
1. Qualcuno ha già lanciato il server per te
2. Apri Chrome/Firefox/Safari
3. Vai su: `http://localhost:7860`
4. Vedrai la homepage

#### Step 2: Carica Documento
1. Clicca su "Document" o drag & drop
2. Seleziona il tuo PDF/Word/TXT
3. Aspetta il caricamento (barra verde)

#### Step 3: Configura (Opzionale)
- **Output Language**: Scegli la lingua per i risultati
- **Iterative Mode**: Attiva per miglioramenti automatici
  - Max Iterations: Quante volte migliorare (3 è buono)
  - Target Score: Obiettivo qualità (85 è buono)

#### Step 4: Avvia
1. Clicca il pulsante **"🚀 Start Review"**
2. Vedrai una barra di progresso
3. Aspetta 1-5 minuti (dipende dal documento)

#### Step 5: Leggi Risultati

Hai **5 tab** con i risultati:

1. **📋 Report Tab**: Report aggregato completo e leggibile
2. **🤖 Agent Reviews Tab**: Report di OGNI SINGOLO agente (nuovo!)
   - Ogni agente mostrato separatamente
   - Icone colorate per tipo
   - Facile da navigare
3. **📊 Dashboard Tab**: Dashboard HTML interattivo (nuovo!)
   - Grafici e visualizzazioni
   - Click per aprire full-screen
   - Charts dinamici
4. **📦 JSON Tab**: Dati strutturati (per tecnici)
5. **📁 Files Tab**: Dove trovare tutti i file generati

#### Step 6: Scarica File
1. Vai su Files tab
2. Copia il percorso della cartella
3. Apri Finder/Explorer
4. Vai nella cartella `reviews/documento_TIMESTAMP/`
5. Trovi:
   - `dashboard.html` ← **Apri questo per visualizzazione migliore!**
   - `review_report.md` ← Report testuale
   - `review_results.json` ← Dati completi

---

## ⚙️ Opzioni Avanzate

### Iterative Mode 🔄

**Cosa fa**: Sistema migliora il documento attraverso più cicli

**Quando usarlo**:
- Documento da migliorare
- Vuoi suggerimenti di modifica
- Hai tempo (richiede più minuti)

**Parametri**:
- Max Iterations: 3-5 (default: 3)
- Target Score: 80-95 (default: 85)

### Python Tools 🛠️

**Cosa fa**: Valida calcoli matematici e dati

**Quando usarlo**:
- Documento con numeri
- Statistiche da verificare
- Calcoli finanziari

**Default**: ATTIVO (consigliato)

### Interactive Mode 💬

**Cosa fa**: Sistema può chiederti info aggiuntive

**Quando usarlo**:
- Hai informazioni extra
- Puoi monitorare il terminale
- Review molto dettagliata

**Attenzione**: Richiede supervisione!

### Reference Documents 📚

**Cosa fa**: Confronta documento con template/guidelines

**Quando usarlo**:
- Hai un template da seguire
- Vuoi check compliance
- Confronto con esempi

**File supportati**: PDF, Word, Excel, TXT

---

## 🌐 Modalità Condivisa (Public Link)

### Usa Caso: Condividi con Colleghi

```bash
python3 web_ui.py --share
```

Output:
```
🚀 Launching Document Review System Web UI
============================================================

📍 Local URL: http://localhost:7860
🌐 Public URL: https://abc123xyz.gradio.live

💡 Link is valid for 72 hours
💡 Share this link with your team!
```

**Vantaggi**:
- ✅ Colleghi accedono da remoto
- ✅ No VPN/configurazione
- ✅ Temporaneo e sicuro (72h)

**Attenzione**:
- ⚠️ Link pubblico (chiunque può accedere)
- ⚠️ Usa solo per team fidati
- ⚠️ Scade dopo 72 ore

---

## 🔧 Configurazione Personalizzata

### Cambia Porta

```bash
python3 web_ui.py --port 8080
```

Accedi su: http://localhost:8080

### Hosting su Server

```bash
# In production
python3 web_ui.py --port 80

# Con HTTPS (richiede nginx/certificati)
# Vedi: docs/production_deployment.md
```

---

## 🎨 Personalizzazione UI

### Modifica Tema

Edita `web_ui.py`:

```python
# Line ~450
with gr.Blocks(..., theme=gr.themes.Soft()) as app:
    # Cambia in:
    # theme=gr.themes.Glass()   # Stile glass
    # theme=gr.themes.Monochrome()  # Bianco/nero
    # theme=gr.themes.Base()    # Base pulito
```

### Aggiungi Logo

```python
# Dopo gr.Markdown("# 📄 AI Document Review System")
gr.Image("logo.png", height=100)
```

### Cambia Colori

Edita CSS in `create_ui()`:

```python
custom_css = """
.gradio-container {
    --primary-color: #your-color;
}
"""
```

---

## 📊 Confronto Modalità

| Feature | CLI | Web UI | API REST |
|---------|-----|--------|----------|
| **Facilità** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Velocità** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Automazione** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Per Non Tecnici** | ❌ | ✅ | ❌ |
| **Batch Processing** | ✅ | ⚠️ | ✅ |
| **Real-time Status** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🐛 Troubleshooting

### "System not initialized"

**Problema**: API key non configurata

**Soluzione**:
```bash
export OPENAI_API_KEY="sk-..."
# Riavvia web_ui.py
```

### Interfaccia non si apre

**Problema**: Porta già in uso

**Soluzione**:
```bash
# Usa porta diversa
python3 web_ui.py --port 7861
```

### Upload lento

**Problema**: File molto grande

**Soluzione**:
- Riduci dimensione PDF
- Usa formato TXT invece di PDF
- Estrai solo le pagine necessarie

### "Failed to read document"

**Problema**: Formato non supportato o corrotto

**Soluzione**:
- Controlla formato file
- Rimuovi password PDF
- Converti in TXT/MD

### Browser non supportato

**Problema**: Browser vecchio

**Soluzione**:
- Usa Chrome/Firefox/Safari moderno
- Aggiorna browser
- Prova modalità incognito

---

## 💡 Tips & Best Practices

### Per Risultati Migliori

✅ **DO**:
- Usa PDF con testo (non scansioni)
- Documenti < 50 pagine
- Lingua consistente
- Formato pulito

❌ **DON'T**:
- PDF scansionati (OCR lento)
- Documenti > 100 pagine
- Mix lingue senza motivo
- File corrotti/protetti

### Performance

🚀 **Velocizza**:
- Disabilita iterative se non serve
- Usa documenti più corti
- Una review alla volta

🐌 **Rallenta** (ma più completo):
- Abilita iterative (5+ min)
- Max iterations alto
- Interactive mode

---

## 🔜 Prossimi Sviluppi

### In Roadmap

- [ ] **Dashboard Live**: Aggiorna risultati in tempo reale
- [ ] **Multi-Upload**: Analizza più documenti contemporaneamente
- [ ] **Templates Salvati**: Salva configurazioni preferite
- [ ] **User Accounts**: Login e history personale
- [ ] **Collaborative**: Più utenti sullo stesso documento
- [ ] **Export Options**: PDF, Word, PowerPoint export
- [ ] **Mobile App**: Versione mobile nativa

---

## 📚 Risorse Addizionali

- **CLI Guide**: Per utenti tecnici che preferiscono terminale
- **API Documentation**: Per integrazione automatizzata
- **Admin Guide**: Setup server production
- **Troubleshooting**: Guida completa problemi comuni

---

## 🎉 Quick Commands

```bash
# Lancia interfaccia base
python3 web_ui.py

# Lancia con sharing pubblico
python3 web_ui.py --share

# Lancia su porta custom
python3 web_ui.py --port 8080

# Lancia in background
nohup python3 web_ui.py > ui.log 2>&1 &

# Stop server
# Ctrl+C o kill process
```

---

## ✅ Checklist Pre-Lancio

Prima di condividere con il team:

- [ ] OPENAI_API_KEY configurata
- [ ] requirements_web.txt installato
- [ ] Test con documento di prova
- [ ] Verifica output directory creata
- [ ] Dashboard HTML si apre correttamente
- [ ] Team ha accesso all'URL
- [ ] Documentazione condivisa

---

**Enjoy the user-friendly experience!** 🎨✨

Per supporto: controlla i log o contatta l'amministratore.

