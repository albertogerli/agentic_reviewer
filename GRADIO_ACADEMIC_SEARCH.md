# 🌐 Academic Search in Gradio Web UI

Guida completa per usare il sistema di ricerca accademica nella Web UI.

---

## ✅ **Verifica Integrazione**

Il sistema di academic search è **completamente integrato** in Gradio:

```
✅ Checkbox "Enable Deep Review (Tier 3)" presente
✅ Parametro deep_review passato agli orchestratori
✅ Subject Matter Expert sempre attivo (Tier 2)
✅ Academic Researcher attivabile (Tier 3)
✅ Output visibile in tab "Agent Reviews"
✅ Logging completo per debugging
```

---

## 🚀 **Come Usarlo**

### **Step-by-Step:**

1. **Avvia Web UI**
   ```bash
   python web_ui.py
   ```
   
2. **Apri browser**
   ```
   http://localhost:7860
   ```

3. **Carica documento**
   - Drag & drop nell'area upload
   - Oppure click per selezionare file

4. **Configura Advanced Settings**
   - Click su "⚙️ Advanced Settings" per espandere
   - Cerca la sezione Deep Review

5. **Attiva Deep Review**
   ```
   ☑️ Enable Deep Review (Tier 3)
       Activate academic researcher + 20 specialist agents
       (slower but more thorough)
   ```

6. **Start Review**
   - Click su "🚀 Start Review"
   - Attendi completamento

7. **Visualizza Risultati**
   - Tab "🤖 Agent Reviews" → Dettagli agente per agente
   - Tab "📊 Dashboard" → Visualizzazione HTML interattiva
   - Tab "📄 Summary" → Report markdown
   - Tab "📥 Files" → Download JSON, MD, HTML

---

## 📊 **Interfaccia Utente**

### **Layout Completo:**

```
┌──────────────────────────────────────────────────────────────────┐
│ 🎯 AI Document Review System                                    │
│                                                                   │
│ 📄 Document Upload                                               │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Click to upload or drag and drop                           │  │
│ │ Supported: PDF, DOCX, TXT, MD                              │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ⚙️ Advanced Settings (click to expand)                          │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Output Language: [English ▼]                               │  │
│ │                                                             │  │
│ │ 📊 Iterative Mode (Advanced)                               │  │
│ │   ☐ Enable iterative improvement                          │  │
│ │   Max Iterations: [5]  Target Score: [85]                 │  │
│ │   ☐ Enable interactive mode                               │  │
│ │                                                             │  │
│ │ 🔬 Enable Deep Review (Tier 3)         ← ACADEMIC SEARCH!  │  │
│ │ ☐ Activate academic researcher + 20 specialist agents     │  │
│ │    (slower but more thorough)                              │  │
│ │                                                             │  │
│ │ 🔧 Enable Python Tools                                     │  │
│ │   ☐ Enable Python code execution for data validation      │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │                    🚀 Start Review                         │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ Progress: [████████████████████████] 100%                        │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ 📄 Summary │ 🤖 Agent Reviews │ 📊 Dashboard │ 📥 Files   │  │
│ └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Casi d'Uso**

### **Caso 1: Business Document (Standard Review)**

**Scenario:** Revisione di business proposal, report aziendale, marketing copy

**Settings:**
- ☐ Deep Review: **NON spuntare**
- ☐ Iterative: No
- ☐ Python Tools: No

**Risultato:**
```
• Tier 1: 5 core agents
• Tier 2: 12 document-specific agents
  ✅ Subject Matter Expert con web search
• Tempo: ~3-5 minuti
• Costo: moderato
```

**Output:**
- Analisi stile, coerenza, logica
- Verifica best practices (web search)
- Suggerimenti miglioramento

---

### **Caso 2: Research Paper (Deep Review)**

**Scenario:** Paper scientifico, thesis, technical report con claim accademici

**Settings:**
- ☑️ Deep Review: **SPUNTARE**
- ☐ Iterative: No
- ☐ Python Tools: Optional

**Risultato:**
```
• Tier 1: 5 core agents
• Tier 2: 12 document-specific agents
  ✅ Subject Matter Expert con web search
• Tier 3: 15 deep-dive specialists
  ✅ Academic Researcher con Semantic Scholar!
• Tempo: ~8-12 minuti
• Costo: più alto (qualità premium)
```

**Output:**
- Tutto del caso standard +
- 📚 10 papers accademici correlati
- 📖 Citazioni formali (DOI/arXiv)
- 🧪 Gap letteratura identificati
- ⚠️ Claim non supportati evidenziati
- 📊 Confronto metodologie
- 💡 Suggerimenti citazioni aggiuntive

---

### **Caso 3: Research Paper + Iterative Improvement**

**Scenario:** Miglioramento iterativo di paper con ricerca accademica

**Settings:**
- ☑️ Deep Review: **SPUNTARE**
- ☑️ Iterative: **SPUNTARE**
  - Max Iterations: 3-5
  - Target Score: 85-90
- ☐ Interactive: Optional (per input utente)
- ☐ Python Tools: Optional

**Risultato:**
```
Iterazione 1:
• Academic Researcher trova gaps
• Score: 75/100
• Suggerimenti: aggiungere [1-5] citazioni

Iterazione 2:
• Documento migliorato automaticamente
• Academic Researcher verifica nuove citazioni
• Score: 85/100

Iterazione 3:
• Raffinamenti finali
• Score: 92/100 → Target superato!
```

**Output:**
- Dashboard con grafico evoluzione score
- Confronto versioni (cosa è cambiato)
- Miglior documento salvato
- Report dettagliato per iterazione
- Citazioni verificate in ogni iterazione

---

## 📖 **Output Agenti**

### **Subject Matter Expert (Tier 2, sempre attivo)**

```markdown
🎓 Subject Matter Expert Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Domain Expertise Analysis

### Technical Accuracy ✅
Your implementation follows industry best practices as verified 
through recent web sources (2024). The approach aligns with 
current standards.

Source: https://arxiv.org/abs/2307.08691 (verified via web search)

### Current Best Practices ⚠️
The document uses batch size 32, but recent benchmarks suggest 
64-128 for optimal performance on modern GPUs.

Recommendation: Update batch size or justify choice.
Source: NeurIPS 2024 proceedings

### State-of-the-Art Awareness ⚠️
No mention of FlashAttention2 optimization (March 2024), which 
provides 2-3x speedup for transformer attention.

Consider adding benchmark comparison or discussion.

### Industry Standards ✅
Compliant with IEEE 2894-2024 for model documentation.

### Expert Insights 💡
Consider discussing trade-offs between accuracy and inference 
speed, as this is a current hot topic in the field.
```

---

### **Academic Researcher (Tier 3, con --deep-review)**

```markdown
🔬 Academic Researcher Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Academic Literature Analysis

### Research Context
Found 10 highly relevant papers via Semantic Scholar database.

### Cited Papers Assessment ⚠️
Your paper cites 15 references:
- ✅ 10 highly relevant (>1000 citations each)
- ⚠️ 3 outdated (pre-2018) - consider updating
- ❌ 2 tangentially related - reconsider inclusion

### Missing Key Citations 🔍

Identified critical papers not cited:

[1] Dao, Tri; Fu, Daniel Y.; Ermon, Stefano; Rudra, Atri; Ré, 
    Christopher (2023). "FlashAttention-2: Faster Attention with 
    Better Parallelism and Work Partitioning"
    **arXiv:** 2307.08691
    **Citations:** 1,243 (Influential: 187)
    **Venue:** NeurIPS 2023
    **Why relevant:** Directly addresses your optimization claims.
    Your claim of "30% speedup" is consistent with their findings.

[2] Tay, Yi; Dehghani, Mostafa; Bahri, Dara; Metzler, Donald (2022).
    "Efficient Transformers: A Survey and Practical Guidelines"
    **DOI:** 10.1145/3530811
    **Citations:** 3,421 (Influential: 542)
    **Venue:** ACM Computing Surveys
    **Why relevant:** Comprehensive survey covering your domain.
    Essential background for efficient transformers.

[3] Zhang, Wei et al. (2023). "Low-Resource Multilingual Models"
    **arXiv:** 2301.12345
    **Citations:** 892
    **Why relevant:** Similar problem setting to yours.

### Methodology Comparison 📊

Your approach resembles [3] Zhang et al. (2023) but differs in:

| Aspect           | Your Work | Zhang et al. | Implication |
|------------------|-----------|--------------|-------------|
| Training samples | 1M        | 10M          | Discuss tradeoff |
| Languages        | 50+       | 20           | Novel contribution |
| Architecture     | 12 layers | 24 layers    | Efficiency gain |
| Inference time   | <10ms     | ~50ms        | Major improvement |

**Recommendation:** Explicitly discuss these differences and 
justify your design choices.

### Literature Gaps Identified ✅

Your work fills an important gap:

**No prior work combines:**
1. Low-resource training (<1M samples)
2. High multilingual coverage (50+ languages)
3. Real-time inference (<10ms latency)

This is a **genuine research contribution**!

However, each component individually has been explored:
- Low-resource: [4] Lee et al. (2023)
- Multilingual: [5] Brown et al. (2022)
- Real-time: [1] Dao et al. (2023)

Your novelty is the combination and trade-off analysis.

### Conflicting Evidence ⚠️

Your claim of "95% accuracy on multilingual benchmark" conflicts 
with existing literature:

- [4] Smith et al. (2024): reports 89% on similar dataset
- [5] Lee et al. (2023): theoretical upper bound of 92%

**Possible explanations:**
1. Different evaluation protocol
2. Different test set
3. Overfitting concerns

**Recommendation:** 
- Re-verify experimental setup
- Provide detailed comparison with [4, 5]
- Discuss potential reasons for discrepancy
- Consider additional validation

### Research Trends (2024-2025) 📈

Emerging topics in your field:

1. **Mixture-of-Experts** (MoE) architectures
   - Trending in Q1 2025
   - Relevant papers: [6-8]
   - Consider positioning relative to MoE

2. **Quantization techniques**
   - Hot topic for efficiency
   - Your work could integrate these
   - See [9-11] for recent advances

3. **Multimodal transformers**
   - Future direction
   - Natural extension of your work
   - Discuss in "Future Work" section

### Additional References to Consider

Based on your topic, also consider citing:

[12] "Attention Mechanisms: A Survey" (2023, 2,100 citations)
[13] "Multilingual NLP Best Practices" (2024, 450 citations)
[14] "Real-Time ML Systems" (2023, 1,800 citations)

### Citation Network Analysis

Your citations form two clusters:
1. Transformer architectures (papers [1,2,7,8,9])
2. Multilingual NLP (papers [3,4,5,10,11])

**Missing bridge:** Few papers connecting both areas.
Consider adding [15] which bridges these topics.

### Reproducibility Concerns ⚠️

Missing details for reproducibility:
- Hyperparameter search strategy not described
- Training data sources not fully specified
- Code/model availability not mentioned

**Recommendation:** Add reproducibility checklist per 
NeurIPS guidelines.
```

---

## 🔍 **Log Output**

### **Console Logs Durante Review:**

```bash
2025-11-05 10:30:15,234 - paper_review_system - INFO - Processing document: research_paper.pdf
2025-11-05 10:30:15,235 - paper_review_system - INFO - Output Language: English
2025-11-05 10:30:15,236 - paper_review_system - INFO - Iterative: False
2025-11-05 10:30:15,237 - paper_review_system - INFO - Deep Review: True
2025-11-05 10:30:15,238 - paper_review_system - INFO - Python Tools: False

2025-11-05 10:30:20,123 - paper_review_system - INFO - Document classified as: scientific_paper
2025-11-05 10:30:20,124 - paper_review_system - INFO - Complexity: 0.85
2025-11-05 10:30:20,125 - paper_review_system - INFO - Detected language: en (confidence: 0.95)

2025-11-05 10:30:22,456 - paper_review_system - INFO - [TIER 1] Creating 5 core agents (always active)
2025-11-05 10:30:22,457 - paper_review_system - INFO - [TIER 2] Creating 12 document-specific agents
2025-11-05 10:30:22,458 - paper_review_system - INFO - [TIER 3] Creating 15 deep-dive specialists (--deep-review active)

2025-11-05 10:30:25,789 - paper_review_system - DEBUG - Agent 'subject_matter_expert': complexity=0.90, doc=0.85, final=0.88 → gpt-5
2025-11-05 10:30:25,790 - paper_review_system - DEBUG - Agent 'academic_researcher': complexity=0.90, doc=0.85, final=0.88 → gpt-5

2025-11-05 10:30:26,123 - paper_review_system - INFO - ✅ Created 32 total agents for document review

2025-11-05 10:31:15,456 - paper_review_system - INFO - 🌐 Executing Subject Matter Expert with WEB SEARCH
2025-11-05 10:31:45,789 - paper_review_system - INFO - ✅ Subject Matter Expert OpenAI web search completed successfully

2025-11-05 10:32:10,123 - paper_review_system - INFO - 🔬 Executing Academic Researcher with ACADEMIC SEARCH
2025-11-05 10:32:12,456 - paper_review_system - INFO - 🔬 Academic Researcher using Semantic Scholar for academic research
2025-11-05 10:32:18,789 - paper_review_system - INFO - 📚 Found 10 papers for query: 'machine learning transformers'
2025-11-05 10:32:18,790 - paper_review_system - INFO - ✅ Semantic Scholar search completed for Academic Researcher
2025-11-05 10:32:40,123 - paper_review_system - INFO - ✅ Web search also completed for Academic Researcher

2025-11-05 10:38:25,456 - paper_review_system - INFO - ✅ All agent reviews completed
2025-11-05 10:38:30,789 - paper_review_system - INFO - 📊 Generated review dashboard
2025-11-05 10:38:31,123 - paper_review_system - INFO - ✅ Review completed successfully
```

---

## 💰 **Performance & Costi**

### **Standard Review (Deep Review OFF)**

```
Tier 1: 5 core agents
Tier 2: 12 document-specific (include Subject Matter Expert)

Subject Matter Expert:
• Usa web search (OpenAI Responses API)
• final_score = 0.88 → gpt-5
• Overhead: +30 secondi

Tempo totale: ~3-5 minuti
Costo: ~$1.50-2.50
```

### **Deep Review (Deep Review ON)**

```
Tier 1: 5 core agents
Tier 2: 12 document-specific (Subject Matter Expert)
Tier 3: 15 specialists (Academic Researcher)

Subject Matter Expert:
• Web search attivo
• Tempo: ~30s

Academic Researcher:
• Semantic Scholar search (10 papers)
• Web search (recent developments)
• final_score = 0.88 → gpt-5 (sempre)
• Overhead: +60 secondi

Tempo totale: ~8-12 minuti
Costo: ~$3-4
```

### **Deep + Iterative (3 iterazioni)**

```
Iterazione 1: Deep review completo (~10 min)
Iterazione 2: Deep review completo (~10 min)
Iterazione 3: Deep review completo (~10 min)

Tempo totale: ~30-40 minuti
Costo: ~$9-12

Output:
• Dashboard evoluzione score
• Confronto 3 versioni
• Miglior documento salvato
• Report dettagliato
```

---

## ⚙️ **Configurazione Opzionale**

### **Semantic Scholar API Key (Opzionale)**

Per rate limits più alti:

```bash
# Ottieni API key gratuita
# https://www.semanticscholar.org/product/api

# Configura
export SEMANTIC_SCHOLAR_API_KEY="your_api_key_here"

# Benefici:
# Free tier:  1 request/sec
# With key:  10 requests/sec (10x più veloce!)
```

### **OpenAI API Key (Richiesta)**

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

### **Tavily API Key (Opzionale, fallback)**

```bash
export TAVILY_API_KEY="your_tavily_key"
```

---

## 🧪 **Testing**

### **Test 1: Verifica Integrazione**

```bash
python test_academic_search.py
```

**Output atteso:**
```
✅ PASSED     Semantic Scholar Module
✅ PASSED     Generic Reviewer Integration
✅ PASSED     Agent Execution Flow

Total: 3/3 tests passed
🎉 All tests passed! Academic search is ready to use.
```

### **Test 2: Web UI End-to-End**

```bash
# 1. Avvia Web UI
python web_ui.py

# 2. Nel browser (http://localhost:7860):
#    - Carica documento test
#    - Spunta "Enable Deep Review"
#    - Start Review
#    - Verifica output in "Agent Reviews"

# 3. Controlla log per:
#    [TIER 3] Creating 15 deep-dive specialists
#    🔬 Executing Academic Researcher with ACADEMIC SEARCH
#    📚 Found X papers
```

---

## 🔧 **Troubleshooting**

### **Problema: "Semantic Scholar not available"**

**Causa:** Modulo non importato

**Soluzione:**
```bash
# Verifica che semantic_scholar.py esista
ls semantic_scholar.py

# Test import
python -c "from semantic_scholar import SemanticScholarAPI; print('OK')"
```

### **Problema: Rate limit 429**

**Causa:** Troppe richieste a Semantic Scholar

**Soluzione:**
```bash
# Opzione 1: Ottieni API key (gratuita)
export SEMANTIC_SCHOLAR_API_KEY="your_key"

# Opzione 2: Aspetta 1 minuto e riprova
```

### **Problema: "No papers found"**

**Causa:** Query troppo specifica o typo

**Soluzione:**
- Sistema usa fallback automatico a web search
- Nessuna azione richiesta
- Log mostrerà: "Semantic Scholar search yielded no results"
- "✅ Web search also completed" → fallback attivo

### **Problema: Checkbox non visibile**

**Causa:** Advanced Settings non espanso

**Soluzione:**
- Click su "⚙️ Advanced Settings"
- Scroll verso il basso
- Cerca "🔬 Enable Deep Review (Tier 3)"

### **Problema: Academic Researcher non in output**

**Causa:** Deep Review non spuntato

**Soluzione:**
- Verifica checkbox "Enable Deep Review" sia ☑️
- Controlla log per: "Deep Review: True"
- Se dice "False", riprova spuntando il checkbox

---

## 📚 **Risorse**

### **Documentazione**

- `ACADEMIC_SEARCH_README.md` - Guida completa academic search
- `SISTEMA_3_TIER.md` - Sistema tier agents
- `WEB_RESEARCH_README.md` - Web search configuration
- `WEB_UI_README.md` - Web UI general guide

### **Test Scripts**

- `test_academic_search.py` - Test integrazione
- `semantic_scholar.py` - Test standalone Semantic Scholar
- `test_web_search.py` - Test web search

### **API Documentation**

- Semantic Scholar: https://api.semanticscholar.org/
- OpenAI Responses: https://platform.openai.com/docs/api-reference/responses
- Tavily: https://tavily.com/docs

---

## ✅ **Summary**

### **Stato Integrazione:**

```
✅ Academic search COMPLETAMENTE integrato in Gradio Web UI
✅ Checkbox "Enable Deep Review (Tier 3)" funzionale
✅ Subject Matter Expert (Tier 2) sempre attivo con web search
✅ Academic Researcher (Tier 3) attivabile via checkbox
✅ Output formattato in tab "Agent Reviews"
✅ Semantic Scholar API integrato (200M+ papers)
✅ Fallback robusto (Semantic Scholar → Web → Standard)
✅ Logging completo per debugging
✅ Supporto modalità iterativa
✅ Test suite completo (3/3 passed)
```

### **Quick Start:**

```bash
# 1. Avvia
python web_ui.py

# 2. Apri browser
http://localhost:7860

# 3. Carica documento

# 4. Espandi Advanced Settings

# 5. Spunta "Enable Deep Review"

# 6. Start Review

# 7. Goditi i risultati con citazioni accademiche! 🔬
```

---

🎉 **Il sistema è pronto all'uso! Divertiti con la ricerca accademica automatizzata!** 📚

