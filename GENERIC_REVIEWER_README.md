# Generic Document Review System 🚀

## Overview

The **Generic Document Review System** is an AI-powered document analysis framework that automatically:
1. **Classifies** any type of document
2. **Dynamically creates** specialized review agents based on document type
3. **Executes** comprehensive multi-agent reviews
4. **Synthesizes** findings into actionable reports

Unlike traditional review systems that are limited to specific document types, this system adapts to **any document** - from scientific papers to business reports, legal contracts to marketing content.

---

## 🎯 Key Features

### Intelligent Document Classification
- Automatically identifies document type (13+ categories)
- Assesses complexity and characteristics
- Determines optimal review strategy

### Dynamic Agent Creation
The system includes **20 specialized agent types** that are dynamically selected:

| Agent Type | Icon | Purpose |
|------------|------|---------|
| Methodology Expert | 🔬 | Research methods, experimental design |
| Data Analyst | 📊 | Statistical analysis, data interpretation |
| Technical Expert | ⚙️ | Technical accuracy, implementation |
| Legal Expert | ⚖️ | Legal compliance, contract review |
| Business Analyst | 💼 | Business viability, strategy |
| Financial Analyst | 💰 | Financial planning, projections |
| Content Strategist | 🎯 | Messaging, audience targeting |
| Style Editor | ✍️ | Writing quality, clarity |
| Fact Checker | 🔍 | Accuracy verification, sources |
| Ethics Reviewer | 🛡️ | Ethical implications, compliance |
| Security Analyst | 🔒 | Security vulnerabilities, risks |
| UX Expert | 👥 | User experience, usability |
| SEO Specialist | 🔎 | Search optimization |
| Accessibility Expert | ♿ | Inclusive design, accessibility |
| Subject Matter Expert | 🎓 | Domain-specific expertise |
| Logic Checker | 🧩 | Argumentation, reasoning |
| Impact Assessor | 💡 | Significance, potential effects |
| Competitor Analyst | 🏆 | Competitive positioning |
| Risk Assessor | ⚠️ | Risk identification, mitigation |
| Innovation Evaluator | 🚀 | Novelty, creative value |

### Supported Document Types

The system recognizes and adapts to:
- **Scientific Papers** → Methodology, Data Analysis, Literature experts
- **Business Reports** → Business, Financial, Competitor analysts
- **Legal Documents** → Legal, Risk, Ethics experts
- **Technical Documentation** → Technical, Security, Accessibility experts
- **Marketing Content** → Content Strategy, SEO, UX experts
- **Blog Articles** → Style, Fact Checking, Impact experts
- **Academic Essays** → Logic, Subject Matter, Style experts
- **Code Documentation** → Technical, Accessibility, Style experts
- **Policy Documents** → Legal, Ethics, Impact experts
- **News Articles** → Fact Checking, Style, Ethics experts
- **Creative Writing** → Style, Innovation, Impact experts
- **And more...**

---

## 🚀 Quick Start

### Installation

```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

### Basic Usage

```bash
# Review any document
python3 generic_reviewer.py path/to/your/document.txt

# With custom title
python3 generic_reviewer.py document.pdf --title "My Document Title"

# Custom output directory
python3 generic_reviewer.py document.txt --output-dir my_reviews

# Debug mode
python3 generic_reviewer.py document.txt --log-level DEBUG
```

### Supported File Formats
- Plain text (`.txt`)
- PDF (`.pdf`)
- Markdown (`.md`)
- Any text-based format

---

## 📋 How It Works

### Step-by-Step Process

```
┌─────────────────────────────────────┐
│  1. DOCUMENT CLASSIFICATION         │
│  AI analyzes document to determine: │
│  - Category & subcategory           │
│  - Complexity level                 │
│  - Key characteristics              │
│  - Required review aspects          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  2. AGENT SELECTION                 │
│  System dynamically creates 5-10    │
│  specialized agents based on        │
│  document type and needs            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  3. PARALLEL REVIEW EXECUTION       │
│  All agents review simultaneously   │
│  Each provides expert perspective   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  4. COORDINATOR SYNTHESIS           │
│  Integrates all reviews into        │
│  comprehensive assessment           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  5. FINAL EVALUATION                │
│  Overall quality rating             │
│  Readiness assessment               │
│  Priority recommendations           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  6. REPORT GENERATION               │
│  - JSON (machine-readable)          │
│  - Markdown (human-readable)        │
│  - HTML Dashboard (interactive)     │
└─────────────────────────────────────┘
```

---

## 📊 Output Structure

After review completion, you'll find in `output_paper_review/`:

```
output_paper_review/
├── document_classification.json          # Document type analysis
├── review_[agent_type].txt              # Individual agent reviews
├── review_coordinator.txt               # Synthesis
├── review_final_evaluator.txt           # Final judgment
├── review_results_[timestamp].json      # Complete results (JSON)
├── review_report_[timestamp].md         # Comprehensive report (Markdown)
└── dashboard_[timestamp].html           # Interactive dashboard (HTML)
```

### Key Files

**`document_classification.json`**
```json
{
  "category": "business_report",
  "subcategory": "quarterly_report",
  "confidence": 0.92,
  "complexity": 0.68,
  "characteristics": [
    "Financial data present",
    "Executive summary included",
    "Professional tone"
  ],
  "suggested_agents": [
    "business_analyst",
    "financial_analyst",
    "data_analyst",
    "fact_checker",
    "style_editor"
  ]
}
```

**Dashboard Features:**
- 📊 Visual overview with statistics
- 🎯 Color-coded evaluation status
- 📋 Expandable expert reviews
- 💡 Key insights highlighted
- 📈 Interactive navigation

---

## 🎨 Example Use Cases

### 1. Scientific Paper Review
```bash
python3 generic_reviewer.py research_paper.pdf --title "Novel ML Approach"
```
**Auto-selected agents:** Methodology Expert, Data Analyst, Literature Expert, Fact Checker, Logic Checker, Innovation Evaluator

### 2. Business Proposal Review
```bash
python3 generic_reviewer.py business_proposal.txt
```
**Auto-selected agents:** Business Analyst, Financial Analyst, Risk Assessor, Competitor Analyst, Impact Assessor

### 3. Legal Contract Review
```bash
python3 generic_reviewer.py contract.pdf
```
**Auto-selected agents:** Legal Expert, Risk Assessor, Ethics Reviewer, Fact Checker, Logic Checker

### 4. Marketing Content Review
```bash
python3 generic_reviewer.py campaign_content.txt
```
**Auto-selected agents:** Content Strategist, SEO Specialist, UX Expert, Style Editor, Impact Assessor

### 5. Technical Documentation Review
```bash
python3 generic_reviewer.py api_docs.md
```
**Auto-selected agents:** Technical Expert, Accessibility Expert, Style Editor, Security Analyst, UX Expert

---

## ⚙️ Configuration

### Model Selection
The system automatically selects appropriate GPT models based on:
- Document complexity
- Agent type requirements
- Task criticality

**Models Used:**
- `gpt-5` (powerful) - Complex analysis, critical decisions
- `gpt-5-mini` (standard) - General reviews
- `gpt-5-nano` (basic) - Simple assessments

### Custom Configuration

Create `config.yaml`:
```yaml
api_key: "your-api-key"
model_powerful: "gpt-5"
model_standard: "gpt-5-mini"
model_basic: "gpt-5-nano"
output_dir: "my_reviews"
max_parallel_agents: 8
agent_timeout: 600
temperature: 1.0
max_output_tokens: 16000
use_prompt_caching: true
```

---

## 🔧 Advanced Features

### Extending Agent Types

Add new agent types in `AgentTemplateLibrary.TEMPLATES`:

```python
"custom_agent": {
    "name": "Custom Agent",
    "icon": "🎨",
    "instructions": """Your custom agent instructions here..."""
}
```

### Custom Document Types

The classifier automatically detects new document types. To add specific handling:

1. Document will be classified by AI
2. Appropriate agents will be suggested
3. Review proceeds automatically

### Integration

Use as a Python module:

```python
from generic_reviewer import GenericReviewOrchestrator, Config
import asyncio

config = Config()
orchestrator = GenericReviewOrchestrator(config)

# Review a document
with open("document.txt", "r") as f:
    text = f.read()

results = asyncio.run(
    orchestrator.execute_review_process(text, "My Document")
)

print(results["final_evaluation"])
```

---

## 📈 Performance

**Typical Review Times:**
- Short document (< 5 pages): 2-4 minutes
- Medium document (5-20 pages): 4-8 minutes
- Long document (20-50 pages): 8-15 minutes
- Very long document (> 50 pages): 15-30 minutes

**Cost Efficiency:**
- Uses prompt caching (87.5% cost reduction)
- Parallel processing for speed
- Smart model selection (uses cheaper models when appropriate)

---

## 🆚 Comparison: Generic vs. Paper-Specific Reviewer

| Feature | Paper Reviewer | Generic Reviewer |
|---------|---------------|------------------|
| **Document Types** | Scientific papers only | Any document type |
| **Agent Selection** | Fixed 9 agents | Dynamic 5-10 agents |
| **Adaptability** | Single domain | Multi-domain |
| **Classification** | Assumes paper | Auto-classifies |
| **Use Cases** | Academic review | Business, legal, marketing, etc. |
| **Flexibility** | Low | High |

---

## 🤝 When to Use Which System

### Use **Paper Reviewer** (`main.py`) when:
- ✅ Reviewing scientific/academic papers
- ✅ Need all 9 specific paper-review agents
- ✅ Focused on research methodology

### Use **Generic Reviewer** (`generic_reviewer.py`) when:
- ✅ Reviewing any non-academic document
- ✅ Document type unknown/mixed
- ✅ Need domain-specific agents
- ✅ Business, legal, marketing content

---

## 🐛 Troubleshooting

### Issue: Classification seems wrong
**Solution:** The system learns from the document content. If misclassified:
1. Check document format/structure
2. Add more context in title
3. Review confidence score in output

### Issue: Missing agents I expected
**Solution:** The system selects agents based on document analysis. To force specific agents:
- Modify `AgentTemplateLibrary` priorities
- Adjust document classification logic

### Issue: Reviews too generic
**Solution:** 
- Increase document complexity in classification
- Use more powerful models in config
- Provide more detailed document content

---

## 📚 Further Development

### Planned Features
- [ ] Multi-language support
- [ ] Custom agent instruction templates
- [ ] Collaborative review modes
- [ ] Version comparison
- [ ] Incremental review (review only changes)
- [ ] API endpoint wrapper

### Contributing
Contributions welcome! Areas for improvement:
- Additional agent types
- Enhanced classification logic
- New output formats
- Performance optimizations

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built on the foundation of the Scientific Paper Review System, extended to support universal document analysis through intelligent agent selection and dynamic orchestration.

Powered by OpenAI GPT-5 models with advanced prompt caching and parallel processing.

---

## 📞 Support

For issues, questions, or suggestions:
- Check existing documentation
- Review example outputs
- Examine log files in debug mode

---

**Happy Reviewing! 📋✨**

