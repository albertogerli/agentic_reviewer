#!/usr/bin/env python3
"""
Demo script to show how Generic Reviewer classifies documents
and selects appropriate agents WITHOUT making API calls.
"""

from pathlib import Path
import json

def simulate_classification(document_text: str, document_name: str) -> dict:
    """
    Simulate document classification based on content analysis.
    In real usage, this would be done by GPT-5.
    """
    text_lower = document_text.lower()
    
    # Simple keyword-based classification for demo
    classifications = {
        "business_proposal": {
            "keywords": ["proposal", "investment", "revenue", "market", "business model", "roi"],
            "agents": ["business_analyst", "financial_analyst", "risk_assessor", 
                      "competitor_analyst", "impact_assessor", "fact_checker"]
        },
        "scientific_paper": {
            "keywords": ["abstract", "methodology", "results", "conclusion", "hypothesis", "experiment"],
            "agents": ["methodology_expert", "data_analyst", "fact_checker", 
                      "logic_checker", "innovation_evaluator", "subject_matter_expert"]
        },
        "legal_document": {
            "keywords": ["contract", "agreement", "terms", "liability", "jurisdiction", "clause"],
            "agents": ["legal_expert", "risk_assessor", "logic_checker", 
                      "ethics_reviewer", "fact_checker"]
        },
        "marketing_content": {
            "keywords": ["brand", "campaign", "engagement", "audience", "conversion", "social media"],
            "agents": ["content_strategist", "seo_specialist", "ux_expert", 
                      "style_editor", "impact_assessor"]
        },
        "technical_documentation": {
            "keywords": ["api", "documentation", "configuration", "installation", "technical", "implementation"],
            "agents": ["technical_expert", "accessibility_expert", "style_editor", 
                      "security_analyst", "ux_expert"]
        }
    }
    
    # Score each category
    scores = {}
    for category, data in classifications.items():
        score = sum(1 for keyword in data["keywords"] if keyword in text_lower)
        scores[category] = score
    
    # Get best match
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    
    # Calculate confidence
    total_score = sum(scores.values())
    confidence = best_score / total_score if total_score > 0 else 0.5
    
    # Estimate complexity based on length and vocabulary
    words = document_text.split()
    complexity = min(1.0, len(words) / 5000)  # Longer = more complex
    
    return {
        "category": best_category,
        "subcategory": "general",
        "confidence": round(confidence, 2),
        "complexity": round(complexity, 2),
        "characteristics": [
            f"Document length: {len(words)} words",
            f"Detected type: {best_category.replace('_', ' ').title()}",
            f"Match score: {best_score}/{len(classifications[best_category]['keywords'])}"
        ],
        "suggested_agents": classifications[best_category]["agents"]
    }

def get_agent_info(agent_type: str) -> dict:
    """Get agent information from template library."""
    agents_info = {
        "methodology_expert": {"name": "Methodology Expert", "icon": "🔬"},
        "data_analyst": {"name": "Data Analyst", "icon": "📊"},
        "technical_expert": {"name": "Technical Expert", "icon": "⚙️"},
        "legal_expert": {"name": "Legal Expert", "icon": "⚖️"},
        "business_analyst": {"name": "Business Analyst", "icon": "💼"},
        "financial_analyst": {"name": "Financial Analyst", "icon": "💰"},
        "content_strategist": {"name": "Content Strategist", "icon": "🎯"},
        "style_editor": {"name": "Style Editor", "icon": "✍️"},
        "fact_checker": {"name": "Fact Checker", "icon": "🔍"},
        "ethics_reviewer": {"name": "Ethics Reviewer", "icon": "🛡️"},
        "security_analyst": {"name": "Security Analyst", "icon": "🔒"},
        "ux_expert": {"name": "UX Expert", "icon": "👥"},
        "seo_specialist": {"name": "SEO Specialist", "icon": "🔎"},
        "accessibility_expert": {"name": "Accessibility Expert", "icon": "♿"},
        "subject_matter_expert": {"name": "Subject Matter Expert", "icon": "🎓"},
        "logic_checker": {"name": "Logic Checker", "icon": "🧩"},
        "impact_assessor": {"name": "Impact Assessor", "icon": "💡"},
        "competitor_analyst": {"name": "Competitor Analyst", "icon": "🏆"},
        "risk_assessor": {"name": "Risk Assessor", "icon": "⚠️"},
        "innovation_evaluator": {"name": "Innovation Evaluator", "icon": "🚀"}
    }
    return agents_info.get(agent_type, {"name": agent_type, "icon": "📝"})

def demo_document_review(file_path: str):
    """Demonstrate document review process."""
    print("=" * 80)
    print("GENERIC DOCUMENT REVIEWER - DEMO MODE")
    print("=" * 80)
    print()
    
    # Read document
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        document_text = f.read()
    
    document_name = path.stem.replace('_', ' ').title()
    
    print(f"📄 Document: {document_name}")
    print(f"📏 Length: {len(document_text):,} characters ({len(document_text.split())} words)")
    print()
    
    # Classify document
    print("🔍 [STEP 1] DOCUMENT CLASSIFICATION")
    print("-" * 80)
    classification = simulate_classification(document_text, document_name)
    
    print(f"   Category:      {classification['category'].replace('_', ' ').title()}")
    print(f"   Subcategory:   {classification['subcategory'].title()}")
    print(f"   Confidence:    {classification['confidence']:.0%}")
    print(f"   Complexity:    {classification['complexity']:.2f} / 1.0")
    print()
    print("   Key Characteristics:")
    for char in classification['characteristics']:
        print(f"   • {char}")
    print()
    
    # Show selected agents
    print("🤖 [STEP 2] SELECTED REVIEW AGENTS")
    print("-" * 80)
    print(f"   {len(classification['suggested_agents'])} specialized agents will review this document:")
    print()
    
    for i, agent_type in enumerate(classification['suggested_agents'], 1):
        info = get_agent_info(agent_type)
        print(f"   {i}. {info['icon']}  {info['name']}")
    
    print()
    print("   Plus:")
    print("   🎯  Review Coordinator (synthesizes all reviews)")
    print("   ⚡  Final Evaluator (provides overall judgment)")
    print()
    
    # Show process flow
    print("⚙️  [STEP 3] REVIEW PROCESS FLOW")
    print("-" * 80)
    print()
    print("   All agents review in parallel → Coordinator synthesizes")
    print("   → Final Evaluator provides judgment → Reports generated")
    print()
    
    # Show expected outputs
    print("📊 [STEP 4] EXPECTED OUTPUTS")
    print("-" * 80)
    print()
    print("   When run with API key, the system will generate:")
    print()
    print("   1. 📋 document_classification.json - Classification details")
    print(f"   2. 📝 review_[agent].txt - {len(classification['suggested_agents'])} expert reviews")
    print("   3. 🎯 review_coordinator.txt - Synthesis of all reviews")
    print("   4. ⚡ review_final_evaluator.txt - Final judgment")
    print("   5. 📄 review_report_[timestamp].md - Comprehensive markdown report")
    print("   6. 🌐 dashboard_[timestamp].html - Interactive HTML dashboard")
    print("   7. 💾 review_results_[timestamp].json - Complete data (machine-readable)")
    print()
    
    # Show sample output structure
    print("📁 OUTPUT STRUCTURE")
    print("-" * 80)
    output_structure = {
        "document_info": {
            "title": document_name,
            "type": classification
        },
        "reviews": {agent: f"[Detailed review from {get_agent_info(agent)['name']}]" 
                   for agent in classification['suggested_agents']},
        "coordinator_assessment": "[Comprehensive synthesis of all reviews]",
        "final_evaluation": "[Overall quality rating and recommendations]"
    }
    
    print()
    print(json.dumps(output_structure, indent=2)[:500] + "...")
    print()
    
    # Instructions
    print("=" * 80)
    print("🚀 TO RUN FOR REAL:")
    print("=" * 80)
    print()
    print("1. Set your OpenAI API key:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print()
    print("2. Run the generic reviewer:")
    print(f"   python3 generic_reviewer.py {file_path}")
    print()
    print("3. Wait 5-10 minutes for comprehensive analysis")
    print()
    print("4. View results in output_paper_review/ directory")
    print()
    print("=" * 80)
    print("✅ DEMO COMPLETED")
    print("=" * 80)

def main():
    """Main demo function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 demo_generic_reviewer.py <document_file>")
        print()
        print("Examples:")
        print("  python3 demo_generic_reviewer.py example_business_proposal.txt")
        print("  python3 demo_generic_reviewer.py your_document.pdf")
        return
    
    demo_document_review(sys.argv[1])

if __name__ == "__main__":
    main()

