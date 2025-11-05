# System Comparison Guide

## Overview

You now have **TWO powerful review systems**:

1. **Scientific Paper Reviewer** (`main.py`) - Specialized for academic papers
2. **Generic Document Reviewer** (`generic_reviewer.py`) - Universal document analysis

---

## Quick Comparison Table

| Feature | Paper Reviewer | Generic Reviewer |
|---------|---------------|------------------|
| **Best For** | Scientific/academic papers | Any document type |
| **Document Types** | Research papers only | 13+ categories |
| **Agents** | Fixed 9 paper-specific agents | Dynamic 5-10 domain-specific agents |
| **Agent Types** | • Methodology Expert<br>• Results Analyst<br>• Literature Expert<br>• Structure & Clarity<br>• Impact & Innovation<br>• Contradiction Checker<br>• Ethics & Integrity<br>• AI Origin Detector<br>• Hallucination Detector | **20 agent types:**<br>• Business Analyst<br>• Financial Analyst<br>• Legal Expert<br>• Technical Expert<br>• Content Strategist<br>• SEO Specialist<br>• UX Expert<br>• Security Analyst<br>• Risk Assessor<br>• And 11 more... |
| **Classification** | Assumes scientific paper | AI-powered auto-classification |
| **Adaptability** | Single domain | Multi-domain adaptive |
| **Output** | Research-focused report | Context-appropriate report |

---

## When to Use Each System

### Use **Paper Reviewer** (`main.py`) for:

✅ **Scientific Research Papers**
- Peer review simulation
- Methodology evaluation
- Statistical analysis review
- Literature contextualization
- Academic rigor assessment

**Example Use Cases:**
```bash
# Review a research paper
python3 main.py research_paper.pdf

# With custom config
python3 main.py paper.pdf --config my_config.yaml --output-dir reviews
```

**What You Get:**
- 9 specialized academic reviews
- Methodology critique
- Statistical analysis
- Literature positioning
- AI authorship detection
- Hallucination detection
- Editorial decision (Accept/Revise/Reject)

---

### Use **Generic Reviewer** (`generic_reviewer.py`) for:

✅ **Business Documents**
- Business proposals
- Strategic plans
- Market analyses
- Financial reports

✅ **Legal Documents**
- Contracts
- Agreements
- Policy documents
- Compliance reviews

✅ **Technical Content**
- Technical documentation
- API documentation
- Architecture docs
- Code documentation

✅ **Marketing Content**
- Marketing plans
- Content strategies
- Campaign proposals
- Brand guidelines

✅ **General Content**
- Blog posts
- Articles
- Essays
- Reports

**Example Use Cases:**
```bash
# Review a business proposal
python3 generic_reviewer.py business_plan.pdf --title "Q4 Strategy"

# Review a contract
python3 generic_reviewer.py contract.pdf

# Review marketing content
python3 generic_reviewer.py campaign.txt --output-dir marketing_reviews
```

**What You Get:**
- Auto-classification of document type
- 5-10 relevant expert reviews (selected based on content)
- Domain-specific analysis
- Coordinator synthesis
- Final evaluation with ratings
- Context-appropriate recommendations

---

## Real-World Examples

### Example 1: Scientific Paper ✅ Use Paper Reviewer

**Document:** "Machine Learning Approach to Cancer Detection"

**Why Paper Reviewer:**
- Contains methodology section
- Has statistical analyses
- Includes literature review
- Academic/research context

**Expected Agents:**
- Methodology Expert → Evaluates experimental design
- Results Analyst → Reviews statistical significance
- Literature Expert → Assesses citations and positioning
- All 9 paper-specific agents

### Example 2: Business Proposal ✅ Use Generic Reviewer

**Document:** "ServiceAI Investment Proposal"

**Why Generic Reviewer:**
- Business context, not academic
- Financial projections
- Market analysis
- ROI considerations

**Auto-Selected Agents:**
- Business Analyst → Evaluates business model
- Financial Analyst → Reviews projections
- Risk Assessor → Identifies risks
- Competitor Analyst → Analyzes market position
- Impact Assessor → Assesses potential
- Fact Checker → Verifies claims

### Example 3: Technical Documentation ✅ Use Generic Reviewer

**Document:** "API Documentation v2.0"

**Why Generic Reviewer:**
- Technical content, not research
- Implementation details
- User guidance focus

**Auto-Selected Agents:**
- Technical Expert → Reviews accuracy
- Accessibility Expert → Checks usability
- Style Editor → Improves clarity
- Security Analyst → Identifies concerns
- UX Expert → Evaluates user experience

### Example 4: Legal Contract ✅ Use Generic Reviewer

**Document:** "Software License Agreement"

**Why Generic Reviewer:**
- Legal document
- Compliance requirements
- Risk assessment needed

**Auto-Selected Agents:**
- Legal Expert → Reviews compliance
- Risk Assessor → Identifies liabilities
- Logic Checker → Evaluates consistency
- Ethics Reviewer → Checks fairness
- Fact Checker → Verifies claims

---

## Decision Flowchart

```
Is your document a scientific/academic research paper?
│
├─ YES → Use Paper Reviewer (main.py)
│        ✅ Fixed 9 academic experts
│        ✅ Research methodology focus
│        ✅ Peer review simulation
│
└─ NO  → Use Generic Reviewer (generic_reviewer.py)
         ✅ Auto-classification
         ✅ Domain-specific agents
         ✅ Adaptive analysis
```

---

## Feature Comparison

### Paper Reviewer Strengths

🎯 **Specialized for Academia**
- Deep methodology analysis
- Statistical rigor assessment
- Literature contextualization
- AI-generated text detection
- Hallucination detection in claims
- Peer review simulation
- Journal-style editorial decisions

🔬 **Fixed Expert Panel**
- Consistent 9-agent structure
- Known review dimensions
- Academic standards focus

### Generic Reviewer Strengths

🌐 **Universal Adaptability**
- Works with ANY document type
- Smart classification
- Context-aware agent selection
- Domain expertise matching

🎨 **Flexible Agent Library**
- 20 specialized agent types
- Dynamic combination
- Appropriate for document context
- Scalable agent system

💡 **Intelligent Selection**
- AI determines document type
- Selects 5-10 most relevant agents
- Optimizes review strategy
- Focuses resources effectively

---

## Output Comparison

### Both Systems Provide

✅ Individual expert reviews  
✅ Coordinator synthesis  
✅ Final evaluation  
✅ Markdown reports  
✅ JSON data exports  
✅ HTML dashboards  
✅ Comprehensive analysis  

### Paper Reviewer Specific Outputs

📄 **paper_info.json** - Extracted paper metadata  
📝 **review_report.md** - Academic-style peer review  
🎯 **executive_summary.md** - Research assessment  
✅/❌ **editorial_decision** - Accept/Revise/Reject  

### Generic Reviewer Specific Outputs

📋 **document_classification.json** - Type, complexity, characteristics  
📊 **Adaptive dashboard** - Context-specific visualization  
⚡ **Final evaluation** - Quality rating, readiness assessment  

---

## Performance & Cost

| Metric | Paper Reviewer | Generic Reviewer |
|--------|---------------|------------------|
| **Agents per Review** | 9 (fixed) | 5-10 (dynamic) |
| **Average Duration** | 5-8 minutes | 4-7 minutes |
| **Token Efficiency** | High (prompt caching) | High (prompt caching + adaptive) |
| **Cost per Review** | ~$2-5 | ~$1.50-4 (fewer agents when appropriate) |
| **Model Selection** | Complexity-based | Complexity + domain-based |

---

## Migration Between Systems

### From Paper Reviewer to Generic Reviewer

**When to migrate:**
- Expanding to non-academic documents
- Need domain-specific reviews
- Want flexible agent selection

**How:**
```bash
# Before (Paper Reviewer)
python3 main.py document.pdf

# After (Generic Reviewer)
python3 generic_reviewer.py document.pdf
```

**Benefits:**
- Works with any document
- More targeted reviews
- Potentially lower cost

### From Generic Reviewer to Paper Reviewer

**When to migrate:**
- Specifically reviewing research papers
- Need all 9 academic perspectives
- Want methodology deep-dive

**How:**
```bash
# Before (Generic Reviewer)
python3 generic_reviewer.py paper.pdf

# After (Paper Reviewer)
python3 main.py paper.pdf
```

**Benefits:**
- Deeper methodology analysis
- Full academic review suite
- Research-specific insights

---

## Can You Use Both?

**Absolutely!** Many users benefit from both:

### Combined Approach Example

**For a Research Paper:**
1. First, run **Generic Reviewer** → Get broad perspective
2. Then, run **Paper Reviewer** → Get deep academic analysis
3. Compare insights from both approaches

```bash
# Get broad analysis
python3 generic_reviewer.py paper.pdf --output-dir generic_review

# Get academic deep-dive
python3 main.py paper.pdf --output-dir paper_review

# Compare results
```

**Benefits:**
- Complementary perspectives
- Broader + deeper insights
- Cross-validation of findings

---

## Demo Mode

Both systems support demo mode for testing without API costs:

```bash
# Demo Generic Reviewer (no API calls)
python3 demo_generic_reviewer.py your_document.txt

# Shows:
# - How document would be classified
# - Which agents would be selected
# - Expected output structure
```

---

## Summary Recommendations

| Document Type | Recommended System | Why |
|---------------|-------------------|-----|
| Research Paper | **Paper Reviewer** | Specialized academic analysis |
| Business Proposal | **Generic Reviewer** | Business-focused agents |
| Legal Contract | **Generic Reviewer** | Legal expertise |
| Technical Docs | **Generic Reviewer** | Technical + UX focus |
| Marketing Content | **Generic Reviewer** | Marketing-specific agents |
| Blog Post | **Generic Reviewer** | Content + SEO focus |
| Financial Report | **Generic Reviewer** | Financial analysis |
| Mixed/Unknown | **Generic Reviewer** | Auto-classification |

---

## Quick Start Commands

### Paper Reviewer
```bash
# Scientific paper review
python3 main.py research_paper.pdf
```

### Generic Reviewer
```bash
# Any document review
python3 generic_reviewer.py document.pdf

# With title
python3 generic_reviewer.py doc.txt --title "My Document"

# Demo mode (no API)
python3 demo_generic_reviewer.py document.txt
```

---

## Questions?

**Q: Can Generic Reviewer handle scientific papers?**  
A: Yes! It will auto-classify as scientific paper and select appropriate agents (methodology, data analysis, etc.). However, Paper Reviewer provides deeper academic analysis with all 9 specialized agents.

**Q: Which is more cost-effective?**  
A: Generic Reviewer can be slightly cheaper as it adapts agent count to document needs (5-10 vs fixed 9). Both use prompt caching for efficiency.

**Q: Can I customize agent selection?**  
A: Yes! Both systems allow agent customization. Generic Reviewer's template library is particularly easy to extend with new agent types.

**Q: Which gives better results?**  
A: For academic papers, Paper Reviewer is superior. For all other documents, Generic Reviewer provides more relevant, targeted analysis.

---

**Bottom Line:**

- 📚 Academic research? → **Paper Reviewer**
- 📋 Everything else? → **Generic Reviewer**
- 🎯 Want both perspectives? → **Use Both!**

---

Enjoy your comprehensive document review system! 🚀

