# 🔬 Academic Search Integration

Sistema di ricerca accademica integrato per verifica di claim scientifici e letteratura.

## 📚 **Cosa Fa**

Due livelli di ricerca accademica:

### **1. Subject Matter Expert con Web Search** (Tier 2)
- ✅ Sempre attivo
- 🌐 Usa OpenAI Responses API + Tavily
- 🎯 Verifica claim tecnici
- 📊 Controlla standard di settore
- 🔍 Trova sviluppi recenti

### **2. Academic Researcher** (Tier 3, `--deep-review`)
- 🔬 Semantic Scholar API per papers accademici
- 🌐 Web search per novità recenti
- 📖 Citazioni complete con DOI/arXiv
- 📈 Analisi citazioni e influenza
- 🧪 Confronto metodologie
- 📚 Gap nella letteratura

---

## 🚀 **Setup**

### **1. Installazione**

```bash
# Semantic Scholar è incluso nel progetto
# Nessuna installazione aggiuntiva necessaria!

# Opzionale: API key per rate limits più alti
export SEMANTIC_SCHOLAR_API_KEY="your_key_here"
```

### **2. Dipendenze**

```bash
# Già installate con requirements base
pip install requests
```

---

## 📖 **Utilizzo**

### **Modalità Standard** (Subject Matter Expert con web search)

```bash
python generic_reviewer.py document.pdf --output-language English
```

**Cosa succede:**
- ✅ `subject_matter_expert` attivo automaticamente (Tier 2)
- 🌐 Usa web search per verifiche
- 🎯 Ottimo per documenti tecnici/business

**Log:**
```
🌐 Executing Subject Matter Expert with WEB SEARCH
✅ Subject Matter Expert OpenAI web search completed successfully
```

### **Modalità Deep Review** (+ Academic Researcher)

```bash
python generic_reviewer.py document.pdf --deep-review --output-language English
```

**Cosa succede:**
- ✅ Tutti gli agenti Tier 1 + Tier 2 attivi
- 🔬 `academic_researcher` attivo (Tier 3)
- 📚 Semantic Scholar + Web Search combinati
- 📖 Citazioni accademiche complete

**Log:**
```
[TIER 3] Creating 15 deep-dive specialists (--deep-review active)
🔬 Executing Academic Researcher with ACADEMIC SEARCH
📚 Found 8 papers for query: 'machine learning transformers'
✅ Semantic Scholar search completed for Academic Researcher
✅ Web search also completed for Academic Researcher
```

---

## 🎯 **Esempi Pratici**

### **Esempio 1: Paper Scientifico**

```bash
python generic_reviewer.py research_paper.pdf --deep-review
```

**Output:**
- 📊 Subject Matter Expert verifica accuracy tecnica
- 🔬 Academic Researcher trova 10 papers correlati
- 📖 Citazioni con DOI, arXiv, conteggio citazioni
- 🧪 Confronto metodologie con letteratura recente
- ⚠️ Identificazione gap o claim non supportati

### **Esempio 2: Business Proposal**

```bash
python generic_reviewer.py proposal.pdf
```

**Output:**
- ✅ Subject Matter Expert verifica best practices
- 🌐 Web search per trend di mercato recenti
- ❌ Academic Researcher NON attivo (non necessario)

### **Esempio 3: Technical Document**

```bash
python generic_reviewer.py technical_spec.docx --deep-review
```

**Output:**
- ✅ Subject Matter Expert + Web Search (standard tecnici)
- 🔬 Academic Researcher + Semantic Scholar (ricerca cutting-edge)
- 📈 Papers su tecnologie emergenti
- 🔗 Link a implementazioni di riferimento

---

## 📊 **Cosa Fornisce Academic Researcher**

### **Per ogni paper trovato:**

```markdown
### [1] Attention Is All You Need
**Authors:** Vaswani, Ashish et al.
**Published:** NeurIPS 2017
**Citations:** 85432 (Influential: 12543)
**Fields:** Computer Science, Machine Learning, NLP
**DOI:** [10.5555/3295222.3295349](https://doi.org/10.5555/3295222.3295349)
**arXiv:** [1706.03762](https://arxiv.org/abs/1706.03762)
**Abstract:** The dominant sequence transduction models are based on 
complex recurrent or convolutional neural networks...
```

### **Analisi dell'agente:**

```markdown
## Literature Alignment
✅ Claim about transformer efficiency is supported by [1] Vaswani et al. (2017)
⚠️ Performance numbers differ from [3] recent benchmark (2024)
❌ No citation for "98% accuracy" - not found in literature

## Methodology Comparison
Your approach uses method X, similar to [2] but differs in:
- Parameter initialization strategy
- Training data scale (yours: 1M samples, theirs: 10M)

## Research Gaps
🔍 No recent work (2023-2025) addresses your specific use case
💡 Consider citing emerging work on efficient transformers [4,5]

## Suggested References
📖 Add: [6] "Efficient Transformers: A Survey" (2022, 3400 citations)
📖 Consider: [7] "Recent Advances in NLP" (2024, 150 citations)
```

---

## 🎛️ **Configurazione Agenti**

### **generic_reviewer.py** - Configurazione

```python
# TIER 2: Subject Matter Expert (sempre attivo)
"subject_matter_expert": {
    "name": "Subject Matter Expert",
    "icon": "🎓",
    "instructions": """...""",
    "use_web_search": True  # ← Web search enabled
}

# TIER 3: Academic Researcher (solo --deep-review)
"academic_researcher": {
    "name": "Academic Researcher",
    "icon": "🔬",
    "instructions": """...""",
    "use_academic_search": True,  # ← Semantic Scholar
    "use_web_search": True        # ← + Web search
}
```

### **Model Selection (Cost-Optimized)**

```python
AGENT_COMPLEXITY = {
    "subject_matter_expert": 0.9,   # High complexity
    "academic_researcher": 0.9,     # High complexity
}

# Con documento complexity 0.7:
# final_score = 0.7 * 0.4 + 0.9 * 0.6 = 0.82
# → gpt-5 (threshold >= 0.80)
```

**Entrambi usano GPT-5** per garantire qualità della ricerca!

---

## 🔍 **Flusso di Ricerca**

### **Academic Researcher Workflow:**

```
1. 🔬 SEMANTIC SCHOLAR API
   ├─ Search papers (last 5 years)
   ├─ Get top 10 by citations
   ├─ Extract metadata (DOI, arXiv, authors, venue)
   └─ Format for agent context

2. 🌐 WEB SEARCH (optional)
   ├─ OpenAI Responses API
   ├─ Query: "recent developments in [topic]"
   ├─ Timeout: 60 seconds
   └─ Combine with academic results

3. 🤖 AGENT ANALYSIS
   ├─ Receive: document + research data
   ├─ Verify claims against papers
   ├─ Identify gaps & conflicts
   └─ Suggest additional references
```

### **Fallback Strategy:**

```
Semantic Scholar
   ├─ Success → Continue to web search
   └─ Fail → Log warning, continue anyway

Web Search
   ├─ Success → Combine results
   ├─ Timeout (60s) → Use only Semantic Scholar
   └─ Fail → Use only Semantic Scholar

Combined Results
   ├─ Has results → Agent analyzes
   └─ No results → Standard execution (no research data)
```

---

## 📈 **Rate Limits & Performance**

### **Semantic Scholar API**

| Tier | Rate Limit | Setup |
|------|-----------|-------|
| **Free** | 1 req/sec | Nessuna API key necessaria |
| **With Key** | 10 req/sec | `export SEMANTIC_SCHOLAR_API_KEY="..."` |

**Nel codice:**
- ✅ Rate limiting automatico
- ✅ Retry logic
- ✅ Timeout handling
- ✅ Graceful degradation

### **Performance Tipica**

```
📊 Review Standard (15 agenti):
- Subject Matter Expert: +30s (web search)
- Totale: ~3-5 minuti

🔬 Deep Review (25 agenti + academic):
- Academic Researcher: +60s (Semantic Scholar + Web)
- Totale: ~8-12 minuti
```

---

## 🎓 **Semantic Scholar Features**

### **Supporta:**

✅ **Paper Search**: keywords, phrases, Boolean queries
✅ **Metadata Completi**: DOI, arXiv, venue, fields of study
✅ **Citation Data**: citation count, influential citations
✅ **Author Info**: author names and IDs
✅ **Related Papers**: recommendations algorithm
✅ **References & Citations**: chi cita, chi è citato
✅ **Year Filtering**: limita per range temporale
✅ **Field Filtering**: computer science, biology, etc.

### **Database Coverage:**

- 📚 **200M+ papers**
- 🔬 **All fields**: CS, Physics, Medicine, Biology, etc.
- 📖 **Sources**: arXiv, PubMed, IEEE, ACM, Springer, etc.
- 🆓 **Free**: no registration required
- 🚀 **Fast**: optimized API endpoints

---

## 🛠️ **Testing**

### **Test Semantic Scholar Module:**

```bash
python semantic_scholar.py
```

**Output:**
```
🧪 Testing Semantic Scholar API...

📚 Test 1: Searching papers about 'transformers in NLP'...
Found 5 papers

Top result:
Vaswani, Ashish et al. (2017). Attention Is All You Need. [85432 citations]
  Published in: NeurIPS
  arXiv: 1706.03762
  URL: https://arxiv.org/abs/1706.03762

📄 Test 2: Getting paper by DOI...
Found: BERT: Pre-training of Deep Bidirectional Transformers
Citations: 54321

📝 Test 3: Formatting papers for agent context...
## Academic Research Results (3 papers)

### [1] Attention Is All You Need
**Authors:** Vaswani, Ashish et al.
...

✅ All tests completed!
```

### **Test con Generic Reviewer:**

```bash
# Test senza Semantic Scholar (fallback)
python generic_reviewer.py test.pdf --deep-review

# Test con Semantic Scholar
python generic_reviewer.py test.pdf --deep-review
# Watch logs for: 🔬 Executing Academic Researcher with ACADEMIC SEARCH
```

---

## 🆚 **Confronto Agenti**

| Feature | Subject Matter Expert | Academic Researcher |
|---------|----------------------|---------------------|
| **Tier** | 2 (sempre attivo) | 3 (solo `--deep-review`) |
| **Model** | gpt-5 / gpt-5-mini | gpt-5 (sempre) |
| **Web Search** | ✅ OpenAI + Tavily | ✅ OpenAI + Tavily |
| **Academic DB** | ❌ | ✅ Semantic Scholar |
| **Citazioni** | Informali | Formali (DOI/arXiv) |
| **Focus** | Verifica tecnica | Letteratura accademica |
| **Output** | Best practices | Papers + citazioni |
| **Use Case** | Business/Tech docs | Scientific papers |
| **Costo** | ~0.76 final_score | ~0.82 final_score |

---

## 💡 **Best Practices**

### **Quando Usare `--deep-review`:**

✅ **SI** per:
- 📄 Scientific papers
- 🎓 Thesis/dissertation
- 🔬 Research proposals
- 📊 Technical reports con claim scientifici
- 🧪 Literature reviews

❌ **NO** per:
- 💼 Business proposals (troppo lento)
- 📧 Emails/blog posts
- 📝 Marketing copy
- 🎨 Creative writing
- ⚡ Quick reviews (usa standard mode)

### **Ottimizzare Performance:**

```bash
# Fast: solo Subject Matter Expert (web search)
python generic_reviewer.py doc.pdf

# Balanced: Tier 1 + 2 (include Subject Matter Expert)
python generic_reviewer.py doc.pdf

# Complete: Tier 1 + 2 + 3 (+ Academic Researcher)
python generic_reviewer.py doc.pdf --deep-review

# Maximum: tutti + iterative + interactive
python generic_reviewer.py doc.pdf --deep-review --iterative --interactive
```

---

## 🔧 **Troubleshooting**

### **"Semantic Scholar not available"**

```bash
# Verifica che semantic_scholar.py esista
ls semantic_scholar.py

# Verifica import
python -c "from semantic_scholar import SemanticScholarAPI; print('OK')"
```

### **"No papers found"**

- ✅ Query troppo specifica → rilassa keywords
- ✅ Year range troppo stretto → rimuovi filtro anno
- ✅ Typo nel query → correggi spelling

### **"Rate limit exceeded"**

```bash
# Ottieni API key gratuita (10x rate limit)
# https://www.semanticscholar.org/product/api

export SEMANTIC_SCHOLAR_API_KEY="your_key"
```

### **Performance lenta**

```bash
# Riduci numero papers
# In generic_reviewer.py, linea ~2714:
academic_result = execute_academic_research(agent.name, query, limit=5)  # ← da 10 a 5

# Oppure disabilita web search per academic researcher
# Rimuovi "use_web_search": True dal template
```

---

## 📊 **Esempi Output**

### **Subject Matter Expert Review:**

```markdown
## Domain Expertise Analysis

### Technical Accuracy ✅
Your implementation of transformer attention follows best practices 
as outlined in recent industry standards (source: 
https://arxiv.org/abs/2304.12345, verified via web search).

### Current Best Practices ⚠️
The paper uses batch size 32, but recent benchmarks (2024) suggest 
batch size 64-128 for optimal performance on modern GPUs.
Source: NeurIPS 2024 proceedings.

### Industry Standards Compliance ✅
Follows IEEE standards for model documentation (IEEE 2894-2024).

### State-of-the-Art Awareness ⚠️
No mention of recent FlashAttention2 optimization (March 2024),
which provides 2-3x speedup. Consider adding benchmark comparison.
```

### **Academic Researcher Review:**

```markdown
## Academic Literature Analysis

### Cited Papers Assessment ⚠️
Your paper cites 15 references:
- ✅ 10 are highly relevant (>1000 citations each)
- ⚠️ 3 are outdated (pre-2018) - consider updating
- ❌ 2 are tangentially related - reconsider inclusion

### Missing Key Citations 🔍
Your work on transformer optimization should cite:

[1] Dao, Tri (2023). FlashAttention-2: Faster Attention with Better 
    Parallelism and Work Partitioning
    **arXiv:** 2307.08691 | **Citations:** 1243
    **Why:** Directly relevant to your optimization claims

[2] Tay, Yi et al. (2022). Efficient Transformers: A Survey
    **DOI:** 10.1145/3530811 | **Citations:** 3421
    **Why:** Comprehensive survey covering your domain

### Methodology Comparison 📊
Your approach resembles [3] Zhang et al. (2023) but differs in:
- Training data scale: yours (1M) vs theirs (10M)
- Architecture: you use 12 layers, they use 24

Consider discussing these differences explicitly.

### Literature Gaps Identified 🎯
✅ No prior work addresses your specific combination of:
   - Low-resource training (<1M samples)
   - Multilingual support (50+ languages)
   - Real-time inference (<10ms)

This is a genuine research contribution!

### Conflicting Evidence ⚠️
Your claim of "95% accuracy" conflicts with:
- [4] Smith et al. (2024): reports 89% on similar dataset
- [5] Lee et al. (2023): theoretical upper bound of 92%

Recommendation: Re-verify experimental setup or discuss discrepancy.

### Research Trends 📈
Emerging topics in your field (2024):
- Mixture-of-Experts architectures (trending)
- Quantization for efficiency (hot topic)
- Multimodal transformers (future direction)

Consider positioning your work relative to these trends.
```

---

## 🚀 **Roadmap Futuro**

### **Prossime Feature:**

- [ ] PubMed integration (per medicina/biologia)
- [ ] arXiv direct API (per pre-prints recenti)
- [ ] Google Scholar scraping (via SerpAPI)
- [ ] CrossRef DOI lookup
- [ ] Citation network analysis
- [ ] Automated literature review generation
- [ ] Comparative analysis across multiple papers
- [ ] Trend detection in research fields

---

## 📚 **Risorse**

### **Semantic Scholar:**
- 📖 API Docs: https://api.semanticscholar.org/
- 🔑 API Key: https://www.semanticscholar.org/product/api
- 💬 Support: api-support@semanticscholar.org

### **Alternative Academic APIs:**
- 🏥 PubMed: https://www.ncbi.nlm.nih.gov/home/develop/api/
- 📑 arXiv: https://arxiv.org/help/api/
- 🔍 CrossRef: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- 📊 OpenCitations: https://opencitations.net/

---

## ✅ **Summary**

### **Cosa Hai Ora:**

1. ✅ **Subject Matter Expert** con web search (Tier 2, sempre attivo)
2. ✅ **Academic Researcher** con Semantic Scholar + Web (Tier 3, `--deep-review`)
3. ✅ **Semantic Scholar API** completamente integrato
4. ✅ **Fallback robusto**: Semantic Scholar → Web Search → Standard
5. ✅ **200M+ papers** accessibili gratuitamente
6. ✅ **Citazioni formali** con DOI/arXiv
7. ✅ **Cost-optimized** ma alta qualità (entrambi su gpt-5 quando complesso)

### **Comandi Veloci:**

```bash
# Standard: Subject Matter Expert + web search
python generic_reviewer.py doc.pdf

# Deep: + Academic Researcher + Semantic Scholar
python generic_reviewer.py doc.pdf --deep-review

# Test Semantic Scholar
python semantic_scholar.py
```

🎉 **Sistema di ricerca accademica completo e pronto all'uso!** 🔬

