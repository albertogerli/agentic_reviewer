# 🌐 Configurazione Web Search

## Panoramica

Il sistema supporta **2 metodi** per la ricerca online:

1. **OpenAI Responses API** (Metodo Primario) ✅
   - Integrato nativamente in OpenAI
   - Chiamata API singola con web search incluso
   - **PROBLEMA**: Può andare in timeout o non essere disponibile per tutti gli account

2. **Tavily API** (Fallback Automatico) 🔄
   - API dedicata per web search
   - Più stabile e affidabile
   - Risultati restituiti all'agent per analisi

---

## 🚀 Setup Rapido

### **Opzione 1: Solo OpenAI (già attivo)**

```bash
# Già configurato!
export OPENAI_API_KEY="sk-..."
```

**Pro**: 
- ✅ Nessun setup aggiuntivo
- ✅ Integrazione nativa

**Contro**:
- ⚠️ Può andare in timeout (90s max)
- ⚠️ Potrebbe non essere disponibile per tutti gli account
- ⚠️ Se fallisce, fallback a esecuzione standard (senza web)

---

### **Opzione 2: OpenAI + Tavily (RACCOMANDATO)** ⭐

```bash
# 1. Installa Tavily
pip install tavily-python

# 2. Ottieni API key gratuita
# Vai su: https://tavily.com
# Registrati e ottieni API key (FREE tier: 1000 ricerche/mese)

# 3. Configura
export TAVILY_API_KEY="tvly-..."
```

**Pro**:
- ✅ Fallback automatico se OpenAI fallisce
- ✅ Più stabile e affidabile
- ✅ FREE tier generoso (1000 ricerche/mese)
- ✅ Sempre ottieni web search, anche se OpenAI timeout

**Flusso**:
```
OpenAI Responses API (90s timeout)
    ↓ Se timeout o errore
Tavily API (ricerca web dedicata)
    ↓ Se anche questo fallisce
Esecuzione standard (senza web)
```

---

## 📋 Installazione Completa

### 1. **Installa dipendenze**

```bash
# Nel terminale
cd /Users/albertogiovannigerli/Desktop/Università/Lezioni/AI/Sassari

# Installa Tavily
pip install tavily-python
```

### 2. **Ottieni Tavily API Key**

1. Vai su **https://tavily.com**
2. Click su "Get API Key" o "Sign Up"
3. Registrati (email + password)
4. Copia la tua API key (inizia con `tvly-...`)

### 3. **Configura Environment Variables**

**macOS/Linux** (permanente):
```bash
# Aggiungi a ~/.zshrc o ~/.bashrc
echo 'export TAVILY_API_KEY="tvly-YOUR-KEY-HERE"' >> ~/.zshrc
source ~/.zshrc
```

**Temporaneo (sessione corrente)**:
```bash
export TAVILY_API_KEY="tvly-YOUR-KEY-HERE"
```

**Verifica**:
```bash
echo $TAVILY_API_KEY
# Dovrebbe mostrare: tvly-...
```

---

## 🧪 Test del Sistema

### Test 1: Verifica Tavily

```python
# test_tavily.py
from tavily import TavilyClient
import os

api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=api_key)

result = client.search("latest AI developments 2024", max_results=3)
print(f"✅ Tavily funzionante! Trovati {len(result['results'])} risultati")
for r in result['results']:
    print(f"- {r['title']}: {r['url']}")
```

```bash
python3 test_tavily.py
```

### Test 2: Verifica Web Search nel Sistema

```bash
# Lancia Web UI
python3 web_ui.py

# Carica un documento
# Abilita "Enable iterative improvement" → "Enable Web Research"
# Nei log vedrai:

# SUCCESSO OpenAI:
INFO - 🌐 Executing Web_Researcher with WEB SEARCH
INFO - ✅ Web_Researcher OpenAI web search completed successfully

# FALLBACK Tavily:
WARNING - ⏱️ Web_Researcher OpenAI web search timed out after 90s
INFO - 🔄 Trying Tavily fallback for Web_Researcher
INFO - 🔍 Web_Researcher using Tavily web search
INFO - ✅ Tavily search completed for Web_Researcher
```

---

## 📊 Log Dettagliati

### **Scenario 1: OpenAI Funziona**
```
INFO - 🌐 Executing Web_Researcher with WEB SEARCH
INFO - ✅ Web_Researcher OpenAI web search completed successfully
INFO - Agent Web_Researcher completed - Tokens: 15000
```
✅ **Tutto ok**, nessun fallback necessario

---

### **Scenario 2: OpenAI Timeout → Tavily Fallback**
```
INFO - 🌐 Executing Web_Researcher with WEB SEARCH
WARNING - ⏱️ Web_Researcher OpenAI web search timed out after 90s
WARNING - OpenAI web search failed: OpenAI Responses API timeout
INFO - 🔄 Trying Tavily fallback for Web_Researcher
INFO - 🔍 Web_Researcher using Tavily web search
INFO - ✅ Tavily search completed for Web_Researcher
INFO - Agent Web_Researcher completed - Tokens: 12000
```
✅ **Tavily ha salvato la situazione!**

---

### **Scenario 3: Entrambi Falliscono → Standard Execution**
```
INFO - 🌐 Executing Web_Researcher with WEB SEARCH
WARNING - OpenAI web search failed: [errore]
INFO - 🔄 Trying Tavily fallback for Web_Researcher
WARNING - Tavily also failed: ⚠️ Tavily API key not found
INFO - All web search methods failed - falling back to standard execution
INFO - Agent Web_Researcher completed - Tokens: 10000
```
⚠️ **Web search non disponibile**, ma sistema continua

---

## 🔧 Troubleshooting

### **Problema**: OpenAI sempre in timeout

**Causa**: Responses API non disponibile o lenta per il tuo account

**Soluzione**: Installa Tavily (vedi sopra)

---

### **Problema**: `Tavily API key not found`

```bash
# Verifica che sia impostata
echo $TAVILY_API_KEY

# Se vuoto, imposta:
export TAVILY_API_KEY="tvly-YOUR-KEY"

# Test:
python3 -c "import os; print(os.getenv('TAVILY_API_KEY'))"
```

---

### **Problema**: `TavilyClient not found`

```bash
# Installa:
pip install tavily-python

# Verifica:
python3 -c "from tavily import TavilyClient; print('✅ Tavily installato')"
```

---

### **Problema**: Tavily rate limit

**Free tier**: 1000 ricerche/mese

Se superi:
```
ERROR - Tavily search failed: Rate limit exceeded
```

**Soluzioni**:
1. Upgrade a piano pagato (https://tavily.com/pricing)
2. Disabilita web research per documenti semplici
3. Attendi il reset mensile

---

## 💰 Costi

### **OpenAI Responses API**
- Incluso nel costo normale delle API calls
- Nessun costo aggiuntivo
- ⚠️ Ma può non essere disponibile

### **Tavily API**
| Piano | Ricerche/Mese | Prezzo |
|-------|---------------|--------|
| **Free** | 1,000 | $0 |
| **Basic** | 10,000 | $29/mese |
| **Pro** | 50,000 | $99/mese |

**Raccomandazione**: 
- Sviluppo: **Free** (1000 ricerche = ~50-100 documenti)
- Produzione: **Basic** ($29/mese)

---

## 🎯 Conclusione

### **Setup Minimo** (già attivo)
```bash
export OPENAI_API_KEY="sk-..."
# Web search funziona, ma può andare in timeout
```

### **Setup Raccomandato** ⭐
```bash
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
pip install tavily-python

# Web search robusto con fallback automatico!
```

---

## 📞 Supporto

**Issue OpenAI Responses API**: https://community.openai.com  
**Tavily Documentation**: https://docs.tavily.com  
**Tavily Support**: support@tavily.com

---

✅ **Sistema pronto per web search robusto!** 🚀

