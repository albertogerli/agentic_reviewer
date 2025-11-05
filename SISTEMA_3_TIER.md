# 🎯 Sistema a 3 Tier - Agenti Intelligenti

## 📊 Panoramica

Sistema ispirato al paper reviewer con **selezione dinamica degli agenti** in 3 livelli.

**50+ Agenti Totali** (30 esistenti + 20 nuovi)

---

## 🔥 Tier System

### **TIER 1: Core Agents** (5 agenti - sempre attivi)
Agenti essenziali per qualsiasi review:

```
✅ SEMPRE ATTIVI (automatico)
```

| Agente | Icon | Complexity | Descrizione |
|--------|------|-----------|-------------|
| **style_editor** | ✍️ | 0.8 | Qualità della scrittura, chiarezza, grammatica |
| **consistency_checker** | 🔗 | 0.9 | Coerenza interna, terminologia |
| **fact_checker** | 🔍 | 0.7 | Verifica accuratezza fattuale |
| **logic_checker** | �� | 0.9 | Analisi argomentazioni e ragionamento |
| **technical_expert** | ⚙️ | 0.8 | Accuratezza tecnica e fattibilità |

**Tempo**: ~5-7 minuti  
**Costo**: ~50K tokens

---

### **TIER 2: Document-Specific Agents** (8-15 agenti - auto-selezionati)
Agenti scelti automaticamente dal classifier in base al tipo di documento:

```
✅ AUTO-SELEZIONATI dal classifier
```

#### Esempi per tipo documento:

**Paper Scientifico**:
- methodology_expert (0.9)
- data_analyst (0.8)
- citation_validator (0.6)
- peer_review_simulator (0.9 - se --deep-review)

**Business Proposal**:
- business_analyst (0.7)
- financial_analyst (0.8)
- market_intelligence (0.7)
- pitch_deck_critic (0.7 - se --deep-review)

**Contratto Legale**:
- legal_expert (0.9)
- contract_clause_analyzer (0.9 - se --deep-review)
- gdpr_compliance (0.8 - se --deep-review)
- regulatory_compliance (0.8 - se --deep-review)

**Marketing Content**:
- content_strategist (0.6)
- brand_voice (0.6)
- conversion_optimizer (0.6 - se --deep-review)
- social_media_strategist (0.5 - se --deep-review)

**Tempo**: +10-15 minuti  
**Costo**: +80-120K tokens

---

### **TIER 3: Deep-Dive Specialists** (20+ agenti - opzionale)
Agenti ultra-specializzati attivati SOLO con `--deep-review`:

```
⚠️ ATTIVATO CON --deep-review
```

#### 20 Nuovi Agenti Tier 3:

##### 📚 Academic/Research (4 agenti)
| Agente | Complexity | Descrizione |
|--------|-----------|-------------|
| **peer_review_simulator** | 0.9 | Simula peer review accademico formale |
| **literature_review_expert** | 0.8 | Valuta completezza rassegna letteraria |
| **grant_proposal_reviewer** | 0.8 | Specializzato in valutazione grant |
| **abstract_optimizer** | 0.7 | Ottimizza abstract per massimo impatto |

##### 💼 Business/Strategy (4 agenti)
| Agente | Complexity | Descrizione |
|--------|-----------|-------------|
| **pitch_deck_critic** | 0.7 | Esperto in presentazioni per investitori |
| **stakeholder_analyst** | 0.7 | Analizza impatto stakeholder |
| **strategic_alignment** | 0.8 | Verifica allineamento obiettivi/azioni |
| **market_intelligence** | 0.7 | Trend di mercato e competizione |

##### ⚖️ Legal/Compliance (4 agenti)
| Agente | Complexity | Descrizione |
|--------|-----------|-------------|
| **gdpr_compliance** | 0.8 | Specialista privacy GDPR |
| **contract_clause_analyzer** | 0.9 | Analizza clausole contrattuali critiche |
| **ip_expert** | 0.9 | Proprietà intellettuale e brevetti |
| **regulatory_compliance** | 0.8 | Conformità settoriale |

##### 🎨 Marketing/Communication (4 agenti)
| Agente | Complexity | Descrizione |
|--------|-----------|-------------|
| **brand_voice** | 0.6 | Coerenza tono e brand identity |
| **conversion_optimizer** | 0.6 | Ottimizza per conversione/CTA |
| **storytelling_expert** | 0.6 | Narrative ed emotional impact |
| **social_media_strategist** | 0.5 | Ottimizzazione social media |

##### 🔧 Technical/Specialized (4 agenti)
| Agente | Complexity | Descrizione |
|--------|-----------|-------------|
| **api_documentation_reviewer** | 0.7 | Documentazione API/tecniche |
| **sustainability_assessor** | 0.7 | Impatto ambientale/sostenibilità |
| **internationalization_expert** | 0.7 | Preparazione mercati internazionali |
| **crisis_communication** | 0.8 | Gestione comunicazione crisi |

**Tempo**: +20-30 minuti  
**Costo**: +150-250K tokens

---

## 🤖 Model Selection (come Paper System)

### Formula di Complessità:
```python
final_score = (document_complexity * 0.4) + (agent_complexity * 0.6)

if final_score >= 0.75:
    model = gpt-5       # Alta complessità
elif final_score >= 0.55:
    model = gpt-5-mini  # Media complessità
else:
    model = gpt-5-nano  # Bassa complessità
```

### Esempi:

**Documento Complesso (0.9) + Agent Complesso (0.9)**:
```
final_score = (0.9 × 0.4) + (0.9 × 0.6) = 0.90
→ gpt-5
```

**Documento Semplice (0.3) + Agent Semplice (0.5)**:
```
final_score = (0.3 × 0.4) + (0.5 × 0.6) = 0.42
→ gpt-5-nano
```

---

## 🚀 Utilizzo

### Modalità Standard (Tier 1 + Tier 2)
```bash
python3 generic_reviewer.py documento.pdf
```
- ✅ 5 core agents (Tier 1)
- ✅ 8-12 document-specific agents (Tier 2)
- ⏱️ Tempo: 15-20 minuti
- 💰 Costo: ~130-170K tokens

### Deep Review (Tier 1 + Tier 2 + Tier 3)
```bash
python3 generic_reviewer.py documento.pdf --deep-review
```
- ✅ 5 core agents (Tier 1)
- ✅ 8-12 document-specific agents (Tier 2)
- ✅ 5-10 deep-dive specialists (Tier 3)
- ⏱️ Tempo: 35-50 minuti
- 💰 Costo: ~280-420K tokens

---

## 📊 Confronto Modalità

| Modalità | Agenti | Tempo | Tokens | Quando Usare |
|----------|--------|-------|--------|--------------|
| **Standard** | 13-17 | 15-20min | 130-170K | Review standard, draft iniziali |
| **Deep Review** | 18-27 | 35-50min | 280-420K | Documenti critici, submission finali, audit completi |

---

## 💡 Best Practices

### Usa Standard quando:
- ✅ Prima revisione di draft
- ✅ Feedback rapido necessario
- ✅ Budget limitato
- ✅ Documento relativamente semplice

### Usa Deep Review quando:
- ⭐ Submission finale (paper, grant, contratto)
- ⭐ Documenti ad alto impatto
- ⭐ Audit completo richiesto
- ⭐ Conformità critica (legale, GDPR)
- ⭐ Presentazione investor-ready
- ⭐ Lancio prodotto importante

---

## 🎯 Tier 3 per Tipo Documento

### Paper Scientifico
```bash
--deep-review
```
Attiva:
- peer_review_simulator
- literature_review_expert
- (se grant: grant_proposal_reviewer)

### Business Proposal
```bash
--deep-review
```
Attiva:
- pitch_deck_critic
- stakeholder_analyst
- market_intelligence

### Contratto/Legal
```bash
--deep-review
```
Attiva:
- contract_clause_analyzer
- gdpr_compliance
- ip_expert
- regulatory_compliance

### Marketing Content
```bash
--deep-review
```
Attiva:
- conversion_optimizer
- brand_voice
- storytelling_expert
- social_media_strategist

---

## 📈 Log Output Esempio

```
[TIER 1] Creating 5 core agents (always active)
[TIER 2] Creating 9 document-specific agents
[TIER 3] Creating 6 deep-dive specialists (--deep-review active)
✅ Created 22 total agents for document review (Tier 1: 5, Tier 2: 9, Tier 3: 6)

Agent 'Style_Editor': complexity=0.80, doc=0.75, final=0.78 → gpt-5
Agent 'Fact_Checker': complexity=0.70, doc=0.75, final=0.72 → gpt-5-mini
Agent 'Pitch_Deck_Critic': complexity=0.70, doc=0.75, final=0.72 → gpt-5-mini
```

---

## 🎓 Esempi Pratici

### Esempio 1: Paper Submission
```bash
python3 generic_reviewer.py my_paper.pdf \
    --iterative \
    --max-iterations 3 \
    --target-score 90 \
    --deep-review \
    --enable-python-tools
```
**Risultato**:
- Tier 1: 5 core
- Tier 2: methodology_expert, data_analyst, citation_validator, subject_matter_expert
- Tier 3: peer_review_simulator, literature_review_expert
- **Totale**: ~15 agenti, review ultra-completa

### Esempio 2: Contratto Importante
```bash
python3 generic_reviewer.py contract.pdf \
    --deep-review \
    --output-lang Italian
```
**Risultato**:
- Tier 1: 5 core
- Tier 2: legal_expert, compliance_officer, risk_assessor
- Tier 3: contract_clause_analyzer, gdpr_compliance, ip_expert
- **Totale**: ~14 agenti, analisi legale profonda

### Esempio 3: Pitch Deck per Investitori
```bash
python3 generic_reviewer.py pitch_deck.pdf \
    --deep-review \
    --iterative \
    --target-score 95
```
**Risultato**:
- Tier 1: 5 core
- Tier 2: business_analyst, financial_analyst, content_strategist
- Tier 3: pitch_deck_critic, stakeholder_analyst, storytelling_expert
- **Totale**: ~14 agenti, ready per investitori

---

## 🔄 Iterative + Deep Review

Combinazione più potente:

```bash
python3 generic_reviewer.py document.pdf \
    --iterative \
    --max-iterations 5 \
    --target-score 95 \
    --deep-review \
    --interactive
```

**Processo**:
1. Tier 1+2+3 review iniziale (25+ agenti)
2. Identificazione miglioramenti
3. Raffinamento documento
4. Re-review con stesso team
5. Ripeti fino a score 95 o 5 iterazioni

**Tempo**: 2-4 ore  
**Risultato**: Documento publication-ready

---

## 🎉 Vantaggi Sistema 3-Tier

### 1. **Efficienza**
- Non sprechi risorse su agenti non necessari
- Paghi solo per ciò che serve

### 2. **Flessibilità**
- Standard per draft rapidi
- Deep per audit completi

### 3. **Qualità Scalabile**
- Tier 1+2: ottima qualità
- +Tier 3: eccellenza assoluta

### 4. **Cost Control**
- Standard: ~$2-4 per documento
- Deep: ~$5-10 per documento

### 5. **Intelligenza**
- Classifier sceglie agenti giusti
- Model selection ottimizzato
- Nessun agente ridondante

---

✅ **Sistema Attivo e Pronto all'Uso!**

