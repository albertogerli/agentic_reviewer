"""
Generic Document Review System
Analyzes any type of document, dynamically creates appropriate review agents,
and produces comprehensive assessments.

Version 3.0 - Enterprise Features:
- Agent Tools (real Python execution)
- Multi-document batch processing
- Reference context system
- Progress tracking & notifications
- Database tracking & history
- Pause/resume functionality
"""

import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging
import sys

# Import base classes from main
from main import (
    Config, Agent, AsyncAgent, FileManager, 
    setup_logging, system_health_check
)
from openai import AsyncOpenAI

# Import v3.0 features (optional - graceful degradation if not available)
try:
    from agent_tools import (
        get_tool_registry,
        execute_agent_with_tools,
        create_data_validator_instructions_with_tools
    )
    AGENT_TOOLS_AVAILABLE = True
except ImportError:
    AGENT_TOOLS_AVAILABLE = False
    logging.warning("Agent Tools not available - install for Python execution")

try:
    from multi_document_processor import (
        MultiDocumentProcessor,
        CrossDocumentAnalyzer,
        DocumentInfo,
        BatchResult
    )
    MULTI_DOC_AVAILABLE = True
except ImportError:
    MULTI_DOC_AVAILABLE = False
    logging.warning("Multi-document processing not available")

try:
    from reference_context import (
        ReferenceContextManager,
        ReferenceAugmentedPrompt
    )
    REFERENCE_CONTEXT_AVAILABLE = True
except ImportError:
    REFERENCE_CONTEXT_AVAILABLE = False
    logging.warning("Reference context not available")

try:
    from document_tracker import DocumentTracker, DocumentVersion
    DATABASE_TRACKING_AVAILABLE = True
except ImportError:
    DATABASE_TRACKING_AVAILABLE = False
    logging.warning("Database tracking not available")

try:
    from progress_notifier import (
        ReviewProgressOrchestrator,
        SystemNotifier
    )
    PROGRESS_TRACKING_AVAILABLE = True
except ImportError:
    PROGRESS_TRACKING_AVAILABLE = False
    logging.warning("Progress tracking not available - install tqdm")

try:
    from web_research_agent import (
        WebResearchAgent,
        execute_web_research_agent,
        create_web_researcher_instructions,
        create_fact_checker_instructions,
        WEB_RESEARCH_AVAILABLE
    )
except ImportError:
    WEB_RESEARCH_AVAILABLE = False
    logging.warning("Web research not available - Responses API features disabled")

# Try to import Tavily as backup web search
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logging.debug("Tavily not available - install for backup web search")

# Semantic Scholar import (optional)
try:
    from semantic_scholar import SemanticScholarAPI, format_papers_for_agent
    SEMANTIC_SCHOLAR_AVAILABLE = True
except ImportError:
    SEMANTIC_SCHOLAR_AVAILABLE = False
    logging.debug("Semantic Scholar not available - academic_researcher will use web search only")

logger = setup_logging()


def execute_tavily_research(agent_name: str, query: str, api_key: Optional[str] = None) -> str:
    """
    Fallback web research using Tavily API.
    
    Args:
        agent_name: Name of the agent
        query: Research query
        api_key: Tavily API key (optional, reads from env if not provided)
    
    Returns:
        Formatted research results
    """
    if not TAVILY_AVAILABLE:
        return "⚠️ Tavily not available. Install with: pip install tavily-python"
    
    try:
        import os
        tavily_key = api_key or os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            return "⚠️ Tavily API key not found. Set TAVILY_API_KEY environment variable."
        
        client = TavilyClient(api_key=tavily_key)
        
        # Perform search
        logger.info(f"🔍 {agent_name} using Tavily web search")
        response = client.search(query, max_results=5)
        
        # Format results
        results = []
        results.append(f"# Web Research Results for {agent_name}\n")
        results.append(f"Query: {query}\n")
        
        if response.get('results'):
            for i, result in enumerate(response['results'], 1):
                results.append(f"\n## Source {i}: {result.get('title', 'N/A')}")
                results.append(f"URL: {result.get('url', 'N/A')}")
                results.append(f"Content: {result.get('content', 'N/A')}\n")
        else:
            results.append("\n⚠️ No results found")
        
        logger.info(f"✅ Tavily search completed for {agent_name}")
        return '\n'.join(results)
        
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return f"⚠️ Tavily search error: {str(e)}"


def execute_academic_research(agent_name: str, query: str, limit: int = 10) -> str:
    """
    Execute academic research using Semantic Scholar API.
    
    Args:
        agent_name: Name of the agent
        query: Research query
        limit: Maximum number of papers to retrieve
    
    Returns:
        Formatted research results with paper details
    """
    if not SEMANTIC_SCHOLAR_AVAILABLE:
        logger.warning("Semantic Scholar not available - install semantic_scholar.py module")
        return "⚠️ Semantic Scholar not available. Academic search disabled."
    
    try:
        logger.info(f"🔬 {agent_name} using Semantic Scholar for academic research")
        
        # Initialize API (no key required for basic usage)
        api = SemanticScholarAPI()
        
        # Search papers (recent 5 years by default)
        import datetime
        current_year = datetime.datetime.now().year
        papers = api.search_papers(
            query=query,
            limit=limit,
            year_range=(current_year - 5, current_year)
        )
        
        if not papers:
            logger.info(f"No papers found, trying without year filter")
            # Try without year filter
            papers = api.search_papers(query=query, limit=limit)
        
        # Format for agent
        if papers:
            formatted = format_papers_for_agent(papers, max_papers=limit)
            logger.info(f"✅ Found {len(papers)} academic papers for {agent_name}")
            return formatted
        else:
            logger.info(f"No academic papers found for query: {query}")
            return f"# Academic Research Results\n\nNo relevant papers found for: '{query}'"
        
    except Exception as e:
        logger.error(f"Academic research failed: {e}")
        return f"⚠️ Academic research error: {str(e)}"


@dataclass
class DocumentType:
    """Classification of document type with metadata."""
    category: str  # e.g., "scientific_paper", "business_report", "legal_document"
    subcategory: str  # e.g., "research_article", "quarterly_report", "contract"
    confidence: float  # 0.0-1.0
    complexity: float  # 0.0-1.0
    characteristics: List[str]  # Key features identified
    suggested_agents: List[str]  # Agent types needed for this document
    detected_language: str  # Language of the document (e.g., "Italian", "English")
    language_confidence: float  # Confidence in language detection
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "subcategory": self.subcategory,
            "confidence": self.confidence,
            "complexity": self.complexity,
            "characteristics": self.characteristics,
            "suggested_agents": self.suggested_agents,
            "detected_language": self.detected_language,
            "language_confidence": self.language_confidence
        }

@dataclass
class DocumentScore:
    """Quality score for a document version."""
    overall_score: float  # 0.0-100.0
    dimension_scores: Dict[str, float]  # Individual aspect scores
    critical_issues: int  # Number of critical problems
    moderate_issues: int  # Number of moderate problems
    minor_issues: int  # Number of minor problems
    strengths: List[str]  # Key strengths identified
    weaknesses: List[str]  # Key weaknesses identified
    iteration: int  # Which iteration produced this score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "dimension_scores": self.dimension_scores,
            "critical_issues": self.critical_issues,
            "moderate_issues": self.moderate_issues,
            "minor_issues": self.minor_issues,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "iteration": self.iteration
        }
    
    def is_better_than(self, other: 'DocumentScore') -> bool:
        """Check if this score is better than another."""
        if self.critical_issues < other.critical_issues:
            return True
        elif self.critical_issues == other.critical_issues:
            if self.overall_score > other.overall_score:
                return True
        return False

@dataclass
class IterationResult:
    """Results from a single iteration."""
    iteration_number: int
    document_version: str  # The improved document text
    reviews: Dict[str, str]  # Reviews from all agents
    score: DocumentScore  # Quality score
    improvements_applied: List[str]  # List of improvements made
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration_number": self.iteration_number,
            "document_length": len(self.document_version),
            "reviews_count": len(self.reviews),
            "score": self.score.to_dict(),
            "improvements_applied": self.improvements_applied,
            "timestamp": self.timestamp
        }

class DocumentClassifier:
    """Analyzes documents to determine type and appropriate review strategy."""
    
    def __init__(self, config: Config, enable_web_research: bool = None, disable_web_research: bool = False):
        self.config = config
        self.client = AsyncOpenAI(api_key=config.api_key) if config.api_key else None
        self.force_web_research = enable_web_research  # Force enable if True
        self.disable_web_research = disable_web_research  # Disable if True
    
    async def classify_document(self, document_text: str) -> DocumentType:
        """
        Analyze document and determine its type, complexity, language, and review needs.
        """
        if not self.client:
            logger.warning("No OpenAI client, using default classification")
            return self._default_classification()
        
        try:
            # Take a substantial sample of the document
            sample = document_text[:12000]
            
            prompt = f"""You are an expert document analyst. Analyze the provided document sample and classify it comprehensively.

Your analysis should determine:
1. Main category (scientific_paper, business_report, legal_document, technical_documentation, marketing_content, blog_article, book_chapter, academic_essay, code_documentation, policy_document, news_article, creative_writing, financial_statement, presentation, training_material, medical_record, grant_proposal, white_paper, case_study, product_specification, other)
2. Subcategory (more specific classification within the main category)
3. Confidence level (0.0-1.0) in your classification
4. Complexity score (0.0-1.0) - considering technical depth, sophistication, specialization
5. Document language (Italian, English, Spanish, French, German, Portuguese, Chinese, Japanese, etc.)
6. Language confidence (0.0-1.0) - how certain you are about the language
7. Key characteristics (list of notable features: writing style, structure, purpose, audience, etc.)
8. Suggested review aspects (what types of reviews would be most valuable for this document)

Based on the suggested review aspects, propose specific reviewer types from this list:
- methodology_expert (for research methods, experimental design)
- data_analyst (for statistical analysis, data interpretation)
- data_validator (for numerical verification, calculations, chart analysis using Python)
- web_researcher (for online fact verification, statistics validation, web sources - USE FOR: market data, statistics, company info, technical specs, industry trends)
- fact_checker (for accuracy, citations, claims verification with web search)
- technical_expert (for technical accuracy, implementation details)
- legal_expert (for legal compliance, contract terms)
- business_analyst (for business viability, market analysis)
- financial_analyst (for financial aspects, budgets, projections)
- content_strategist (for messaging, audience targeting)
- style_editor (for writing quality, clarity, consistency)
- plagiarism_detector (for originality, proper attribution, duplicate content)
- ethics_reviewer (for ethical implications, compliance)
- security_analyst (for security concerns, vulnerabilities)
- ux_expert (for user experience, usability)
- seo_specialist (for search optimization, discoverability)
- accessibility_expert (for inclusivity, accessibility)
- subject_matter_expert (for domain-specific expertise)
- logic_checker (for logical consistency, argumentation)
- impact_assessor (for potential impact, significance)
- competitor_analyst (for competitive landscape, differentiation)
- risk_assessor (for risks, limitations, concerns)
- innovation_evaluator (for novelty, creativity, innovation)
- readability_analyst (for text complexity, audience appropriateness)
- citation_validator (for reference accuracy, citation style)
- consistency_checker (for internal consistency, terminology)
- visual_designer (for visual design, layout, presentation quality)
- translation_quality (for translation accuracy, localization)
- cultural_sensitivity (for cultural appropriateness, inclusiveness)
- time_series_analyst (for temporal data, trends, forecasting)
- chart_analyzer (for graph/chart quality, data visualization)

IMPORTANT: For documents containing verifiable claims (statistics, market data, company info, financial figures, technical specs), 
ALWAYS include 'web_researcher' and/or 'fact_checker' to verify information online.

Return your analysis as a JSON object with these keys:
- category (string)
- subcategory (string)
- confidence (float 0.0-1.0)
- complexity (float 0.0-1.0)
- detected_language (string, e.g., "Italian", "English")
- language_confidence (float 0.0-1.0)
- characteristics (array of strings)
- suggested_agents (array of strings from the list above, select 6-12 most relevant)

--- DOCUMENT SAMPLE ---
{sample}
--- END OF SAMPLE ---

Return ONLY the JSON object, no additional text."""

            response = await self.client.chat.completions.create(
                model=self.config.model_standard,
                messages=[
                    {"role": "system", "content": "You are an expert document classification system. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                response_format={"type": "json_object"},
                max_completion_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            doc_type = DocumentType(
                category=result.get("category", "other"),
                subcategory=result.get("subcategory", "general"),
                confidence=float(result.get("confidence", 0.7)),
                complexity=float(result.get("complexity", 0.5)),
                characteristics=result.get("characteristics", []),
                suggested_agents=result.get("suggested_agents", []),
                detected_language=result.get("detected_language", "English"),
                language_confidence=float(result.get("language_confidence", 0.8))
            )
            
            # Auto-add web research for documents with verifiable claims
            doc_type = self._auto_select_web_research(doc_type, document_text)
            
            logger.info(f"Document classified as: {doc_type.category}/{doc_type.subcategory} "
                       f"(confidence: {doc_type.confidence:.2f}, complexity: {doc_type.complexity:.2f})")
            logger.info(f"Detected language: {doc_type.detected_language} (confidence: {doc_type.language_confidence:.2f})")
            logger.info(f"Suggested agents: {', '.join(doc_type.suggested_agents)}")
            
            return doc_type
            
        except Exception as e:
            logger.error(f"Error classifying document: {e}")
            return self._default_classification()
    
    def _auto_select_web_research(self, doc_type: DocumentType, document_text: str) -> DocumentType:
        """
        Automatically add web research agents for documents with verifiable claims.
        Respects CLI flags: --enable-web-research (force) or --disable-web-research (block).
        """
        if not WEB_RESEARCH_AVAILABLE:
            logger.debug("Web research not available, skipping auto-selection")
            return doc_type
        
        # Check CLI override flags
        if self.disable_web_research:
            logger.info("🚫 Web research disabled by user (--disable-web-research)")
            return doc_type
        
        # Check if web research is already suggested
        has_web_researcher = "web_researcher" in doc_type.suggested_agents
        has_fact_checker = "fact_checker" in doc_type.suggested_agents
        
        # If force enabled, add immediately
        if self.force_web_research:
            if not has_web_researcher and not has_fact_checker:
                doc_type.suggested_agents.append("web_researcher")
                doc_type.suggested_agents.append("fact_checker")
                logger.info("✅ Web research FORCED by user (--enable-web-research)")
            return doc_type
        
        # Categories that typically have verifiable claims
        categories_with_claims = [
            "business_report", "business_proposal", "financial_statement", 
            "market_research", "white_paper", "case_study", "grant_proposal",
            "technical_documentation", "product_specification", "scientific_paper",
            "policy_document", "news_article", "press_release"
        ]
        
        # Check if web research is already suggested
        has_web_researcher = "web_researcher" in doc_type.suggested_agents
        has_fact_checker = "fact_checker" in doc_type.suggested_agents
        
        # Sample document for indicators of verifiable claims
        sample = document_text[:3000].lower()
        
        # Indicators that suggest verifiable claims
        claim_indicators = [
            # Numbers and statistics
            '%', 'percent', 'million', 'billion', 'thousand', '$', '€', '£',
            # Market/business terms
            'market', 'revenue', 'growth', 'sales', 'profit', 'valuation',
            'competitor', 'industry', 'trend', 'forecast', 'projection',
            # Company/organization info
            'company', 'corporation', 'founded', 'headquartered', 'ceo',
            # Technical specs
            'specification', 'performance', 'benchmark', 'capacity',
            # Research terms
            'study', 'research', 'survey', 'report', 'data', 'analysis',
            # Time-sensitive info
            '2024', '2025', 'recent', 'latest', 'current'
        ]
        
        # Count indicators in document
        indicator_count = sum(1 for indicator in claim_indicators if indicator in sample)
        
        # Decision logic
        should_add_web_research = False
        
        # Strong indicators: category match + multiple indicators
        if doc_type.category in categories_with_claims and indicator_count >= 5:
            should_add_web_research = True
            logger.info(f"🌐 Auto-selecting web research: Category '{doc_type.category}' + {indicator_count} claim indicators")
        
        # Medium indicators: many claim indicators regardless of category
        elif indicator_count >= 10:
            should_add_web_research = True
            logger.info(f"🌐 Auto-selecting web research: {indicator_count} claim indicators found")
        
        # Specific subcategories that always benefit from web research
        elif doc_type.subcategory in ["market_analysis", "competitive_analysis", 
                                      "industry_report", "financial_forecast",
                                      "business_plan", "investment_pitch"]:
            should_add_web_research = True
            logger.info(f"🌐 Auto-selecting web research: Subcategory '{doc_type.subcategory}' requires fact verification")
        
        # Add agents if needed
        if should_add_web_research:
            if not has_web_researcher and not has_fact_checker:
                # Add both for comprehensive verification
                doc_type.suggested_agents.append("web_researcher")
                doc_type.suggested_agents.append("fact_checker")
                logger.info("✅ Added Web_Researcher and Fact_Checker agents automatically")
            elif not has_web_researcher:
                doc_type.suggested_agents.append("web_researcher")
                logger.info("✅ Added Web_Researcher agent automatically")
            elif not has_fact_checker:
                doc_type.suggested_agents.append("fact_checker")
                logger.info("✅ Added Fact_Checker agent automatically")
        
        return doc_type
    
    def _default_classification(self) -> DocumentType:
        """Fallback classification when analysis fails."""
        return DocumentType(
            category="general_document",
            subcategory="unknown",
            confidence=0.5,
            complexity=0.5,
            characteristics=["Could not analyze"],
            suggested_agents=["content_strategist", "style_editor", "fact_checker", "logic_checker", "impact_assessor"],
            detected_language="English",
            language_confidence=0.5
        )

class AgentTemplateLibrary:
    """Library of agent instruction templates for different review types."""
    
    # Agent tier classification (inspired by paper review system)
    # TIER 1: Core agents (always active) - essential for any review
    # TIER 2: Document-specific agents (auto-selected based on type) - most comprehensive
    # TIER 3: Deep-dive specialists (optional, --deep-review flag) - ultra-specialized
    
    AGENT_TIERS = {
        # TIER 1: Core Agents (5-7 agents, always active)
        "style_editor": 1,
        "consistency_checker": 1,
        "fact_checker": 1,
        "logic_checker": 1,
        "technical_expert": 1,
        
        # TIER 2: Document-Specific Agents (suggested by classifier, 8-15 agents)
        "methodology_expert": 2,
        "data_analyst": 2,
        "legal_expert": 2,
        "business_analyst": 2,
        "financial_analyst": 2,
        "content_strategist": 2,
        "ethics_reviewer": 2,
        "security_analyst": 2,
        "ux_expert": 2,
        "subject_matter_expert": 2,
        "impact_assessor": 2,
        "citation_validator": 2,
        "risk_assessor": 2,
        "compliance_officer": 2,
        "innovation_evaluator": 2,
        "quality_assurance": 2,
        "data_validator": 2,
        "web_researcher": 2,
        "market_intelligence": 2,
        "strategic_alignment": 2,
        "brand_voice": 2,
        
        # TIER 3: Deep-Dive Specialists (optional, activated with --deep-review)
        "seo_specialist": 3,
        "accessibility_expert": 3,
        "peer_review_simulator": 3,
        "academic_researcher": 3,  # NEW: Deep academic search
        "literature_review_expert": 3,
        "grant_proposal_reviewer": 3,
        "abstract_optimizer": 3,
        "pitch_deck_critic": 3,
        "stakeholder_analyst": 3,
        "gdpr_compliance": 3,
        "contract_clause_analyzer": 3,
        "ip_expert": 3,
        "regulatory_compliance": 3,
        "conversion_optimizer": 3,
        "storytelling_expert": 3,
        "social_media_strategist": 3,
        "api_documentation_reviewer": 3,
        "sustainability_assessor": 3,
        "internationalization_expert": 3,
        "crisis_communication": 3,
    }
    
    # Agent complexity scores (for model selection, like paper system)
    AGENT_COMPLEXITY = {
        # Core agents (high complexity)
        "style_editor": 0.8,
        "consistency_checker": 0.9,
        "fact_checker": 0.7,
        "logic_checker": 0.9,
        "technical_expert": 0.8,
        
        # Document-specific (varied complexity)
        "methodology_expert": 0.9,
        "data_analyst": 0.8,
        "legal_expert": 0.9,
        "business_analyst": 0.7,
        "financial_analyst": 0.8,
        "content_strategist": 0.6,
        "ethics_reviewer": 0.7,
        "security_analyst": 0.8,
        "ux_expert": 0.6,
        "subject_matter_expert": 0.9,
        "impact_assessor": 0.7,
        "citation_validator": 0.6,
        "risk_assessor": 0.8,
        "compliance_officer": 0.8,
        "innovation_evaluator": 0.7,
        "quality_assurance": 0.6,
        "data_validator": 0.9,
        "web_researcher": 0.7,
        "market_intelligence": 0.7,
        "strategic_alignment": 0.8,
        "brand_voice": 0.6,
        
        # Deep-dive specialists (medium-high complexity)
        "seo_specialist": 0.5,
        "accessibility_expert": 0.6,
        "peer_review_simulator": 0.9,
        "academic_researcher": 0.9,  # NEW: High complexity for academic search
        "literature_review_expert": 0.8,
        "grant_proposal_reviewer": 0.8,
        "abstract_optimizer": 0.7,
        "pitch_deck_critic": 0.7,
        "stakeholder_analyst": 0.7,
        "gdpr_compliance": 0.8,
        "contract_clause_analyzer": 0.9,
        "ip_expert": 0.9,
        "regulatory_compliance": 0.8,
        "conversion_optimizer": 0.6,
        "storytelling_expert": 0.6,
        "social_media_strategist": 0.5,
        "api_documentation_reviewer": 0.7,
        "sustainability_assessor": 0.7,
        "internationalization_expert": 0.7,
        "crisis_communication": 0.8,
        
        # Special agents (highest complexity)
        "coordinator": 1.0,
        "final_evaluator": 0.9,
    }
    
    TEMPLATES = {
        "methodology_expert": {
            "name": "Methodology Expert",
            "icon": "🔬",
            "instructions": """You are an expert in research methodology with extensive experience in experimental design and scientific methods.
Evaluate the methodology used in this document:
- Validity and appropriateness of methods chosen
- Rigor and controls in place
- Reproducibility of procedures
- Consistency between methods and results
- Potential methodological limitations

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "data_analyst": {
            "name": "Data Analyst",
            "icon": "📊",
            "instructions": """You are a data analysis expert specializing in statistical methods and data interpretation.
Evaluate data-related aspects:
- Correctness of statistical analyses
- Appropriateness of visualizations
- Data presentation quality
- Interpretation validity
- Potential data issues or biases

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "technical_expert": {
            "name": "Technical Expert",
            "icon": "⚙️",
            "instructions": """You are a technical expert with deep knowledge of implementation details and technical accuracy.
Evaluate technical aspects:
- Technical accuracy and correctness
- Implementation feasibility
- Technology choices and architecture
- Performance considerations
- Scalability and maintainability
- Best practices adherence

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "legal_expert": {
            "name": "Legal Expert",
            "icon": "⚖️",
            "instructions": """You are a legal expert specializing in document review and compliance.
Evaluate legal aspects:
- Legal compliance and regulatory adherence
- Contract terms clarity and fairness
- Potential legal risks or liabilities
- Rights and obligations clarity
- Legal language appropriateness
- Missing legal provisions

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "business_analyst": {
            "name": "Business Analyst",
            "icon": "💼",
            "instructions": """You are a business analyst with expertise in business strategy and viability assessment.
Evaluate business aspects:
- Business model viability
- Market analysis quality
- Competitive positioning
- Value proposition clarity
- Revenue/cost assumptions
- Strategic alignment
- Implementation feasibility

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "financial_analyst": {
            "name": "Financial Analyst",
            "icon": "💰",
            "instructions": """You are a financial analyst specializing in financial planning and analysis.
Evaluate financial aspects:
- Financial projections accuracy
- Budget appropriateness
- Cost-benefit analysis quality
- Financial assumptions validity
- ROI calculations
- Risk assessment
- Financial sustainability

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "content_strategist": {
            "name": "Content Strategist",
            "icon": "🎯",
            "instructions": """You are a content strategist with expertise in messaging and audience engagement.
Evaluate content strategy:
- Message clarity and effectiveness
- Audience targeting appropriateness
- Content structure and flow
- Persuasiveness and impact
- Call-to-action effectiveness
- Brand alignment
- Content gaps or opportunities

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "style_editor": {
            "name": "Style Editor",
            "icon": "✍️",
            "instructions": """You are a professional editor specializing in writing quality and style.
Evaluate writing quality:
- Clarity and readability
- Grammar and syntax
- Tone consistency
- Writing style appropriateness
- Sentence structure variety
- Word choice precision
- Overall polish and professionalism

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "fact_checker": {
            "name": "Fact Checker",
            "icon": "🔍",
            "instructions": """You are a fact-checker specializing in accuracy verification and source validation.
Evaluate factual accuracy:
- Claims substantiation
- Source credibility
- Citation completeness
- Statistical accuracy
- Potential misinformation
- Missing references
- Verifiability of statements

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "ethics_reviewer": {
            "name": "Ethics Reviewer",
            "icon": "🛡️",
            "instructions": """You are an ethics expert specializing in ethical implications and compliance.
Evaluate ethical aspects:
- Ethical compliance
- Potential ethical concerns
- Bias or discrimination issues
- Privacy considerations
- Transparency and disclosure
- Stakeholder impact
- Social responsibility

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "security_analyst": {
            "name": "Security Analyst",
            "icon": "🔒",
            "instructions": """You are a security analyst specializing in security assessment and risk analysis.
Evaluate security aspects:
- Security vulnerabilities
- Data protection measures
- Access control appropriateness
- Compliance with security standards
- Incident response preparedness
- Security best practices
- Potential threats

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "ux_expert": {
            "name": "UX Expert",
            "icon": "👥",
            "instructions": """You are a UX expert specializing in user experience and usability.
Evaluate user experience:
- Usability and ease of use
- User journey clarity
- Accessibility considerations
- User needs alignment
- Pain points identification
- Interaction design quality
- User satisfaction potential

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "seo_specialist": {
            "name": "SEO Specialist",
            "icon": "🔎",
            "instructions": """You are an SEO specialist with expertise in search optimization.
Evaluate SEO aspects:
- Keyword usage effectiveness
- Content discoverability
- Meta information quality
- Internal/external linking
- Search intent alignment
- Technical SEO considerations
- Optimization opportunities

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "accessibility_expert": {
            "name": "Accessibility Expert",
            "icon": "♿",
            "instructions": """You are an accessibility expert specializing in inclusive design.
Evaluate accessibility:
- Accessibility compliance (WCAG, ADA)
- Inclusive language usage
- Content accessibility
- Alternative formats availability
- Assistive technology compatibility
- Barrier identification
- Improvement opportunities

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "subject_matter_expert": {
            "name": "Subject Matter Expert",
            "icon": "🎓",
            "instructions": """You are a subject matter expert with deep domain knowledge and web search capabilities.
Evaluate domain-specific aspects:
- Technical accuracy in the domain
- Current best practices adherence (verify with latest sources if needed)
- Industry standards compliance
- Domain terminology usage
- State-of-the-art awareness (use web search for recent developments)
- Domain-specific concerns
- Expert-level insights
- Verify claims against current research/industry data

When evaluating technical content or recent developments, use web search to:
• Verify technical claims
• Check latest industry standards
• Find recent research/publications
• Validate best practices
• Confirm compliance requirements

Provide detailed analysis IN ENGLISH with specific recommendations and sources.""",
            "use_web_search": True
        },
        
        "logic_checker": {
            "name": "Logic Checker",
            "icon": "🧩",
            "instructions": """You are a logic expert specializing in argumentation and reasoning analysis.
Evaluate logical aspects:
- Argument structure and validity
- Logical consistency
- Reasoning soundness
- Premise-conclusion relationships
- Fallacy identification
- Counter-arguments consideration
- Overall coherence

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "impact_assessor": {
            "name": "Impact Assessor",
            "icon": "💡",
            "instructions": """You are an impact assessment expert evaluating significance and potential effects.
Evaluate impact potential:
- Significance and importance
- Potential reach and influence
- Short-term vs long-term impacts
- Stakeholder effects
- Unintended consequences
- Success metrics
- Value creation potential

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "competitor_analyst": {
            "name": "Competitor Analyst",
            "icon": "🏆",
            "instructions": """You are a competitive intelligence analyst specializing in market positioning.
Evaluate competitive aspects:
- Competitive landscape understanding
- Differentiation clarity
- Competitive advantages
- Market positioning
- Benchmarking insights
- Competitive threats
- Strategic opportunities

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "risk_assessor": {
            "name": "Risk Assessor",
            "icon": "⚠️",
            "instructions": """You are a risk management expert specializing in risk identification and mitigation.
Evaluate risks:
- Risk identification completeness
- Risk severity assessment
- Mitigation strategies
- Contingency planning
- Assumption validation
- Limitation acknowledgment
- Risk monitoring approach

Provide detailed analysis IN ENGLISH with specific recommendations."""
        },
        
        "innovation_evaluator": {
            "name": "Innovation Evaluator",
            "icon": "🚀",
            "instructions": """You are an innovation expert evaluating novelty and creative value.
Evaluate innovation:
- Novelty and originality
- Creative approach
- Innovation type (incremental/radical)
- Differentiation from existing solutions
- Innovation feasibility
- Adoption potential
- Future-readiness

Provide detailed analysis with specific recommendations."""
        },
        
        "data_validator": {
            "name": "Data Validator",
            "icon": "🔢",
            "instructions": """You are a data validation expert with Python programming capabilities.
Your task is to verify numerical accuracy, calculations, and data consistency in the document:
1. Identify all numerical data, calculations, percentages, and statistics
2. Verify mathematical accuracy (additions, percentages, ratios, growth rates)
3. Check consistency between tables, charts, and text
4. Validate data logic (e.g., parts should sum to whole, trends should be consistent)
5. For any suspicious numbers, explain what to verify
6. If Python calculations would help, provide the code to run

For each numerical claim, assess:
- Calculation correctness
- Data consistency
- Logical coherence
- Potential errors or discrepancies

If you find errors, provide:
- Description of the error
- Correct value (if calculable)
- Python code to verify (if applicable)

Provide detailed analysis with specific findings and recommendations."""
        },
        
        "plagiarism_detector": {
            "name": "Plagiarism Detector",
            "icon": "🔗",
            "instructions": """You are a plagiarism detection specialist focused on originality and proper attribution.
Evaluate content originality:
- Identify passages that may need citation
- Check for proper attribution of ideas
- Assess paraphrasing quality
- Identify potential duplicate content patterns
- Evaluate quotation usage and attribution
- Check for self-plagiarism indicators
- Review reference completeness

Flag any concerning patterns:
- Uncited claims that should have sources
- Suspiciously generic or templated language
- Inconsistent writing style suggesting multiple sources
- Missing attributions for specific concepts

Provide detailed analysis with specific examples and recommendations."""
        },
        
        "readability_analyst": {
            "name": "Readability Analyst",
            "icon": "📖",
            "instructions": """You are a readability expert specializing in text complexity and audience appropriateness.
Analyze readability:
- Sentence complexity and length
- Vocabulary sophistication
- Paragraph structure
- Flow and transitions
- Jargon usage and explanation
- Target audience alignment
- Reading level estimation (e.g., grade level, professional level)

Assess comprehension factors:
- Clarity of main points
- Logical organization
- Supporting examples effectiveness
- Technical term accessibility
- Overall cognitive load

Provide specific recommendations to improve readability for the intended audience."""
        },
        
        "citation_validator": {
            "name": "Citation Validator",
            "icon": "📚",
            "instructions": """You are a citation and reference validation expert.
Evaluate citations and references:
- Citation format consistency (APA, MLA, Chicago, IEEE, etc.)
- Reference completeness (all required elements present)
- Citation-reference matching (all citations have references, no orphans)
- Currency of sources (appropriate publication dates)
- Source credibility and authority
- Citation density appropriateness
- DOI/URL functionality indicators
- Author names consistency

Check for common issues:
- Missing citations for key claims
- Broken or incomplete references
- Inconsistent citation styles
- Over-reliance on limited sources
- Outdated references for recent topics

Provide detailed analysis with specific examples of issues and corrections."""
        },
        
        "consistency_checker": {
            "name": "Consistency Checker",
            "icon": "✓",
            "instructions": """You are a consistency validation expert focusing on internal coherence.
Check consistency across the document:
- Terminology usage (same concepts named consistently)
- Numerical data (figures match across sections)
- Dates and timelines
- Names and titles
- Formatting and structure
- Acronym definitions and usage
- Units of measurement
- Currency and conversions

Identify inconsistencies:
- Contradictory statements
- Conflicting data points
- Variable terminology for same concept
- Formatting irregularities
- Acronym inconsistencies
- Tense shifts

Provide detailed analysis with specific locations and recommendations for standardization."""
        },
        
        "visual_designer": {
            "name": "Visual Design Reviewer",
            "icon": "🎨",
            "instructions": """You are a visual design expert evaluating document presentation quality.
Assess visual design elements:
- Layout and spacing effectiveness
- Typography choices (fonts, sizes, hierarchy)
- Color usage and contrast
- White space utilization
- Visual hierarchy and flow
- Charts and graphs design quality
- Image quality and relevance
- Table formatting and readability

Evaluate presentation impact:
- Professional appearance
- Visual consistency
- Attention direction
- Information density
- Aesthetic appeal
- Brand alignment (if applicable)

Provide specific recommendations for visual improvements with examples."""
        },
        
        "translation_quality": {
            "name": "Translation Quality Assessor",
            "icon": "🌍",
            "instructions": """You are a translation quality expert evaluating multilingual content.
Assess translation quality:
- Accuracy of meaning transfer
- Natural language flow in target language
- Cultural adaptation appropriateness
- Idiom and expression handling
- Technical term translation
- Consistency in terminology
- Register and tone preservation

Identify translation issues:
- Literal translations that lose meaning
- Cultural references requiring adaptation
- Mistranslated technical terms
- Grammar or syntax errors
- Awkward phrasing
- Missing context

Provide detailed analysis with specific examples and improvement suggestions."""
        },
        
        "cultural_sensitivity": {
            "name": "Cultural Sensitivity Reviewer",
            "icon": "🌏",
            "instructions": """You are a cultural sensitivity expert evaluating inclusive and appropriate content.
Evaluate cultural appropriateness:
- Inclusive language usage
- Cultural stereotypes or biases
- Representation diversity
- Religious sensitivity
- Gender inclusivity
- Geographic/regional awareness
- Generational considerations
- Disability awareness

Identify potential concerns:
- Exclusionary language
- Cultural insensitivity
- Unconscious bias
- Stereotypical representations
- Problematic assumptions
- Missing diverse perspectives

Provide constructive feedback with specific examples and alternative approaches."""
        },
        
        "time_series_analyst": {
            "name": "Time Series Analyst",
            "icon": "📈",
            "instructions": """You are a time series analysis expert specializing in temporal data evaluation.
Analyze temporal data:
- Trend identification and validation
- Seasonality patterns
- Data point consistency over time
- Growth rate calculations
- Forecasting reasonableness
- Historical comparisons
- Temporal logic (cause-effect timing)

Validate time-based claims:
- Year-over-year calculations
- Compound growth rates
- Projection methodology
- Historical data accuracy
- Trend interpretation
- Temporal causality

Provide detailed analysis with calculations and recommendations for temporal data presentation."""
        },
        
        "chart_analyzer": {
            "name": "Chart & Visualization Analyzer",
            "icon": "📊",
            "instructions": """You are a data visualization expert specializing in chart and graph quality.
Evaluate visualizations:
- Chart type appropriateness for data
- Data representation accuracy
- Scale and axis design
- Legend clarity
- Color scheme effectiveness
- Labels and annotations
- Data-ink ratio (Tufte principle)
- Misleading visualization detection

Assess each chart/graph for:
- Correct data representation
- Clear communication of insights
- Visual integrity (no distortion)
- Accessibility (color blindness safe)
- Professional appearance
- Appropriate complexity

Identify issues:
- Misleading scales or axes
- Chart junk (unnecessary elements)
- Poor color choices
- Unclear legends
- Missing labels
- Data distortion

Provide specific recommendations for improving each visualization."""
        },
        
        "web_researcher": {
            "name": "Web Researcher",
            "icon": "🌐",
            "instructions": """You are a Web Research Specialist with real-time internet access.
Your task is to verify factual claims, statistics, and information using web search.

WHAT TO VERIFY:
1. **Factual Claims**: Any statements presented as facts
2. **Statistics & Data**: Numbers, percentages, growth rates, market data, financial figures
3. **Citations**: Verify that cited sources exist and are accurate
4. **Current Information**: Check if information is up-to-date for 2025
5. **Technical Claims**: Verify technical specifications, product features, methodologies
6. **Market Data**: Industry trends, company information, market sizes
7. **Historical Facts**: Dates, events, milestones mentioned

VERIFICATION PROCESS:
1. Use web search actively to find current, authoritative sources
2. Cross-reference information across multiple sources
3. Check publication dates to ensure information is current
4. Verify numbers and statistics against official sources
5. Identify outdated or incorrect information

OUTPUT FORMAT:
For each claim verified:
- **Claim**: [Quote from document]
- **Status**: ✅ VERIFIED / ⚠️ PARTIALLY VERIFIED / ❓ UNVERIFIED / ❌ FALSE
- **Finding**: [What you found from web search]
- **Sources**: [List URLs found]
- **Recommendation**: [If outdated/incorrect, provide current data]

IMPORTANT:
- Actually USE the web search tool - don't rely only on training data
- Provide specific URLs as evidence
- If information is outdated, suggest current data with sources
- Focus on verifiable, factual claims (not opinions)
- Be thorough but prioritize the most important claims

Provide a comprehensive fact-checking report with all sources cited."""
        },
        
        "fact_checker": {
            "name": "Fact Checker",
            "icon": "✓",
            "instructions": """You are a Fact-Checking Expert with web search capabilities.
Your mission is to verify the accuracy of all factual information in the document.

VERIFICATION TARGETS:
1. **Numbers & Statistics**
   - Financial data and projections
   - Market sizes and growth rates
   - Research findings and percentages
   - Technical specifications

2. **Claims & Statements**
   - Company information and achievements
   - Historical facts and timelines
   - Product features and capabilities
   - Industry trends and forecasts

3. **Sources & Citations**
   - Verify cited sources exist
   - Check if citations match the actual content
   - Assess source credibility

ASSESSMENT SCALE:
✅ **VERIFIED**: Claim matches reliable, current sources (provide URLs)
⚠️ **PARTIALLY VERIFIED**: Claim is mostly accurate but has minor discrepancies (explain)
❓ **UNVERIFIED**: Cannot find supporting sources (note this)
❌ **FALSE**: Claim contradicts reliable sources (provide correction with URLs)

PROCESS:
1. Identify all verifiable claims in the document
2. Search the web for each claim using authoritative sources
3. Compare document statements with found information
4. Note any discrepancies or outdated data
5. Provide corrections with sources when needed

OUTPUT:
Provide a structured report with:
- **Summary**: Overall accuracy assessment
- **Verified Claims**: List with sources
- **Issues Found**: Claims that are questionable/false
- **Corrections Needed**: Specific recommendations with current data
- **Source Quality**: Assessment of cited sources
- **Confidence Score**: Your confidence in the document's factual accuracy (0-100%)

Always provide URLs for your sources!"""
        },
        
        # ========== NEW 20 AGENTS (TIER 2 & 3) ==========
        
        # TIER 3: Academic/Research Specialists
        "peer_review_simulator": {
            "name": "Peer Review Simulator",
            "icon": "🎓",
            "instructions": """You are a senior academic peer reviewer simulating formal academic peer review process.
Conduct rigorous peer review:
- Novelty and contribution to field
- Methodological rigor and validity
- Literature contextualization
- Results interpretation soundness
- Limitations acknowledgment
- Reproducibility potential
- Academic writing quality
- Suitability for publication

Provide detailed critique with:
- Major concerns (acceptance blockers)
- Minor concerns (revisions needed)
- Questions for authors
- Recommendation (Accept/Minor Revisions/Major Revisions/Reject)

Use formal academic tone and be constructively critical."""
        },
        
        "academic_researcher": {
            "name": "Academic Researcher",
            "icon": "🔬",
            "instructions": """You are an academic researcher with access to academic databases and web search.
Your role is to perform deep academic research to verify and enhance document claims with scholarly sources.

RESEARCH APPROACH:
1. Identify claims requiring academic verification
2. Use Semantic Scholar API to find relevant papers
3. Use web search for recent developments
4. Cross-reference multiple sources
5. Cite all sources with proper attribution

EVALUATE:
- Academic literature alignment
- Recent research developments
- Methodology comparisons with literature
- Citation relevance and recency
- Gap identification in current knowledge
- Conflicting evidence in literature
- Research trends and emerging topics

For each significant claim, provide:
• Supporting/contradicting academic sources
• Paper titles, authors, year, citations
• DOI/arXiv links when available
• Key findings from sources
• Research gaps identified
• Suggested additional references

Use academic rigor and cite extensively. Prioritize peer-reviewed sources.""",
            "use_academic_search": True,
            "use_web_search": True
        },
        
        "literature_review_expert": {
            "name": "Literature Review Expert",
            "icon": "📖",
            "instructions": """You are a literature review specialist evaluating research contextualization.
Assess literature review quality:
- Coverage completeness (key papers included?)
- Citation currency (recent publications?)
- Synthesis quality (not just listing)
- Gap identification clarity
- Theoretical framework strength
- Literature organization logic
- Critical analysis depth
- Research positioning effectiveness

Identify:
- Missing seminal works
- Outdated citations needing update
- Gaps in coverage
- Weak synthesis areas
- Citation balance issues

Provide specific recommendations for strengthening literature foundation."""
        },
        
        "grant_proposal_reviewer": {
            "name": "Grant Proposal Reviewer",
            "icon": "💵",
            "instructions": """You are a grant review expert specializing in funding proposal evaluation.
Evaluate grant proposal quality:
- Problem significance and urgency
- Innovation and originality
- Methodology feasibility
- Budget justification and realism
- Team qualifications and track record
- Timeline appropriateness
- Impact potential and measurability
- Sustainability and scalability
- Alignment with funder priorities

Assess each criterion with scores and provide:
- Strengths that make it competitive
- Weaknesses that reduce funding chances
- Specific improvements for higher scores
- Competitive positioning advice

Provide frank assessment of funding likelihood."""
        },
        
        "abstract_optimizer": {
            "name": "Abstract Optimizer",
            "icon": "📝",
            "instructions": """You are an abstract optimization specialist focused on maximizing impact.
Evaluate abstract effectiveness:
- Hook strength (first sentence impact)
- Problem statement clarity
- Contribution clarity and prominence
- Methods summary appropriateness
- Results/findings highlight
- Implications statement strength
- Keyword optimization
- Length appropriateness (usually 150-250 words)
- Standalone comprehensibility

Provide rewrite suggestions:
- Alternative openings for stronger hook
- Clearer contribution statements
- More impactful results framing
- Keyword integration improvements

Focus on making abstract compelling for skim-readers."""
        },
        
        # TIER 2: Business/Strategy Agents
        "market_intelligence": {
            "name": "Market Intelligence Analyst",
            "icon": "📈",
            "instructions": """You are a market intelligence analyst specializing in competitive analysis and trends.
Analyze market intelligence:
- Market size and growth accuracy
- Competitive landscape completeness
- Market trends currency and validity
- Competitor positioning assessment
- Market segmentation appropriateness
- Entry barriers identification
- Market dynamics understanding
- Data sources credibility

Evaluate competitive analysis:
- Competitor identification completeness
- Competitive advantages clarity
- Differentiation strength
- Competitive threats assessment
- Market positioning strategy

Provide data-driven recommendations for strengthening market analysis."""
        },
        
        "pitch_deck_critic": {
            "name": "Pitch Deck Critic",
            "icon": "🎤",
            "instructions": """You are an investor pitch deck expert who has reviewed thousands of presentations.
Evaluate pitch effectiveness:
- Opening hook strength
- Problem-solution clarity
- Value proposition impact
- Market opportunity sizing
- Business model clarity
- Traction/validation evidence
- Financial projections realism
- Team credibility presentation
- Ask/use of funds clarity
- Visual design and flow
- Story narrative strength
- Call-to-action power

Assess from investor perspective:
- Investment thesis clarity
- Risk mitigation demonstration
- Growth potential evidence
- Exit strategy visibility
- Competitive advantages proof

Provide specific slide-by-slide recommendations for stronger investor appeal."""
        },
        
        "strategic_alignment": {
            "name": "Strategic Alignment Checker",
            "icon": "🎯",
            "instructions": """You are a strategy alignment expert ensuring consistency between goals and actions.
Verify strategic alignment:
- Vision-mission-goals consistency
- Objectives-tactics alignment
- Resources-priorities matching
- KPIs-goals correspondence
- Timeline-ambition realism
- Budget-strategy alignment
- Team-requirements fit
- Risk mitigation-threats matching

Identify misalignments:
- Goals without supporting actions
- Actions without clear objectives
- Resource allocation inconsistencies
- Timeline conflicts
- Priority contradictions
- Metric-goal mismatches

Provide recommendations for stronger strategic coherence."""
        },
        
        "stakeholder_analyst": {
            "name": "Stakeholder Analyst",
            "icon": "👥",
            "instructions": """You are a stakeholder analysis expert evaluating impact on all parties.
Analyze stakeholder considerations:
- Stakeholder identification completeness
- Interest and power mapping
- Impact assessment thoroughness
- Engagement strategy appropriateness
- Communication plan adequacy
- Resistance anticipation
- Buy-in strategy effectiveness
- Conflict resolution planning

Evaluate for each stakeholder group:
- Needs and concerns addressed?
- Benefits clearly communicated?
- Risks acknowledged?
- Engagement approach suitable?

Identify overlooked stakeholders and provide engagement recommendations."""
        },
        
        # TIER 3: Legal/Compliance Specialists
        "gdpr_compliance": {
            "name": "GDPR Compliance Officer",
            "icon": "🔐",
            "instructions": """You are a GDPR/privacy compliance specialist.
Evaluate GDPR compliance:
- Personal data handling transparency
- Legal basis for processing clarity
- Consent mechanism appropriateness
- Data minimization principle adherence
- Purpose limitation compliance
- Data subject rights acknowledgment
- Security measures adequacy
- Data breach procedures
- International transfer compliance
- Privacy by design implementation
- Cookie consent compliance

Identify compliance gaps:
- Missing privacy disclosures
- Inadequate consent mechanisms
- Excessive data collection
- Missing subject rights information
- Insufficient security measures
- Non-compliant third-party sharing

Provide specific recommendations for GDPR compliance."""
        },
        
        "contract_clause_analyzer": {
            "name": "Contract Clause Analyzer",
            "icon": "📜",
            "instructions": """You are a contract law specialist analyzing contractual provisions.
Analyze contract clauses:
- Obligation clarity and completeness
- Rights and remedies balance
- Liability limitations appropriateness
- Termination provisions fairness
- Dispute resolution mechanisms
- Force majeure adequacy
- Intellectual property terms
- Confidentiality provisions
- Indemnification scope
- Warranty limitations
- Amendment procedures

Flag problematic clauses:
- One-sided or unfair terms
- Ambiguous language
- Conflicting provisions
- Missing protections
- Unreasonable obligations
- Inadequate remedies

Provide clause-by-clause recommendations for balanced contract."""
        },
        
        "ip_expert": {
            "name": "Intellectual Property Expert",
            "icon": "©️",
            "instructions": """You are an intellectual property specialist.
Evaluate IP aspects:
- Patent potential and strategy
- Trademark protection adequacy
- Copyright considerations
- Trade secret protection
- IP ownership clarity
- Licensing terms appropriateness
- Infringement risk assessment
- Prior art consideration
- Freedom to operate analysis
- IP portfolio strategy

Identify IP issues:
- Unprotected innovations
- Ownership ambiguities
- Infringement risks
- Inadequate confidentiality
- Weak IP strategy
- Missing IP disclosures

Provide recommendations for robust IP protection strategy."""
        },
        
        "regulatory_compliance": {
            "name": "Regulatory Compliance Checker",
            "icon": "📋",
            "instructions": """You are a regulatory compliance expert for industry-specific regulations.
Assess regulatory compliance:
- Applicable regulations identification
- Compliance requirements coverage
- Industry standards adherence
- Certification needs
- Reporting obligations
- Safety requirements
- Environmental compliance
- Quality standards
- Licensing requirements
- Audit trail adequacy

Evaluate for specific sectors:
- Healthcare: HIPAA, FDA, clinical trial regs
- Finance: SOX, FINRA, anti-money laundering
- Food: FDA, USDA, food safety regs
- Tech: Data protection, export controls
- Manufacturing: OSHA, EPA, quality standards

Identify compliance gaps and provide sector-specific recommendations."""
        },
        
        # TIER 3: Marketing/Communication Specialists
        "brand_voice": {
            "name": "Brand Voice Analyst",
            "icon": "🗣️",
            "instructions": """You are a brand voice and messaging consistency expert.
Evaluate brand voice:
- Tone consistency throughout
- Personality alignment with brand
- Language style appropriateness
- Voice characteristics clarity
- Messaging consistency
- Brand values reflection
- Target audience alignment
- Emotional resonance
- Differentiation from competitors

Assess voice dimensions:
- Formal vs. casual
- Technical vs. accessible
- Serious vs. playful
- Authoritative vs. collaborative
- Traditional vs. innovative

Identify voice inconsistencies and provide guidelines for unified brand voice."""
        },
        
        "conversion_optimizer": {
            "name": "Conversion Optimizer",
            "icon": "💹",
            "instructions": """You are a conversion rate optimization specialist.
Evaluate conversion elements:
- Call-to-action clarity and strength
- Value proposition visibility
- Friction points identification
- Trust signals presence
- Urgency/scarcity tactics
- Form complexity and length
- Button placement and wording
- Social proof integration
- Risk reversal elements
- Objection handling
- Path to conversion clarity

Apply CRO best practices:
- Above-the-fold CTA presence
- Benefit-focused copy
- Minimal required fields
- Progress indicators
- Mobile optimization
- Loading speed impact

Provide A/B test suggestions and conversion lift recommendations."""
        },
        
        "storytelling_expert": {
            "name": "Storytelling Expert",
            "icon": "📚",
            "instructions": """You are a narrative and storytelling specialist.
Evaluate storytelling elements:
- Narrative arc strength
- Character/protagonist clarity
- Conflict/tension presence
- Stakes establishment
- Emotional engagement
- Story structure effectiveness
- Pacing and momentum
- Climax and resolution
- Authenticity and credibility
- Relatability factors

Assess story components:
- Opening hook impact
- Setup clarity
- Rising action build
- Turning points effectiveness
- Resolution satisfaction
- Message/moral integration

Provide recommendations for more compelling narrative."""
        },
        
        "social_media_strategist": {
            "name": "Social Media Strategist",
            "icon": "📱",
            "instructions": """You are a social media strategy and content optimization expert.
Evaluate social media readiness:
- Platform-specific optimization
- Shareability factors
- Engagement potential
- Hashtag strategy
- Visual content integration
- Length appropriateness per platform
- Timing and frequency considerations
- Community building elements
- Influencer collaboration potential
- Trending topic alignment
- Cross-platform consistency

Assess by platform:
- LinkedIn: Professional tone, thought leadership
- Twitter: Conciseness, conversation starters
- Instagram: Visual appeal, story-worthy
- Facebook: Community focus, longer content
- TikTok: Entertainment, trends

Provide platform-specific optimization recommendations."""
        },
        
        # TIER 3: Technical/Specialized Agents
        "api_documentation_reviewer": {
            "name": "API Documentation Reviewer",
            "icon": "🔌",
            "instructions": """You are an API documentation specialist.
Evaluate API documentation:
- Endpoint documentation completeness
- Request/response examples clarity
- Authentication/authorization coverage
- Error handling documentation
- Rate limiting explanation
- Versioning strategy clarity
- Code samples quality and variety
- SDK documentation
- Getting started guide effectiveness
- API reference organization
- Interactive documentation (e.g., Swagger)

Assess technical accuracy:
- Parameter descriptions completeness
- Data type specifications
- Required vs. optional fields clarity
- Status code coverage
- Edge case documentation

Provide recommendations for developer-friendly API docs."""
        },
        
        "sustainability_assessor": {
            "name": "Sustainability Assessor",
            "icon": "🌱",
            "instructions": """You are a sustainability and environmental impact expert.
Evaluate sustainability aspects:
- Environmental impact assessment
- Carbon footprint consideration
- Resource efficiency
- Circular economy principles
- Waste reduction strategies
- Sustainable materials usage
- Energy efficiency measures
- Water conservation
- Biodiversity impact
- Social sustainability
- Economic sustainability
- Long-term viability

Assess ESG alignment:
- Environmental commitments
- Social responsibility
- Governance practices
- Reporting transparency
- Stakeholder engagement

Provide recommendations for stronger sustainability profile."""
        },
        
        "internationalization_expert": {
            "name": "Internationalization Expert",
            "icon": "🌍",
            "instructions": """You are an internationalization (i18n) and localization specialist.
Evaluate global readiness:
- Cultural sensitivity and appropriateness
- Language localization considerations
- Regional adaptations needed
- Currency and unit handling
- Date/time format flexibility
- Legal and regulatory variations
- Payment method diversity
- Local market understanding
- Translation quality (if present)
- Idiom and expression appropriateness
- Visual element cultural fit
- Color symbolism awareness

Identify internationalization issues:
- Culturally insensitive content
- Region-specific assumptions
- Hard-coded text or formats
- Non-scalable localization
- Missing market-specific considerations

Provide recommendations for successful global expansion."""
        },
        
        "crisis_communication": {
            "name": "Crisis Communication Specialist",
            "icon": "🚨",
            "instructions": """You are a crisis communication expert.
Evaluate crisis readiness:
- Risk scenarios identification
- Crisis response protocols
- Communication chain clarity
- Stakeholder communication plans
- Message consistency strategy
- Timing and speed considerations
- Spokesperson designation
- Media relations approach
- Social media monitoring
- Transparency and honesty balance
- Reputation protection measures
- Recovery and rebuilding plans

Assess communication elements:
- Key messages clarity
- Tone appropriateness
- Empathy demonstration
- Accountability acknowledgment
- Action steps communication
- Follow-up commitments

Provide recommendations for effective crisis communication preparedness."""
        }
    }
    
    @classmethod
    def get_template(cls, agent_type: str) -> Optional[Dict[str, str]]:
        """Get agent template by type."""
        return cls.TEMPLATES.get(agent_type)
    
    @classmethod
    def get_all_agent_types(cls) -> List[str]:
        """Get list of all available agent types."""
        return list(cls.TEMPLATES.keys())

class DocumentScorer:
    """Scores document quality based on reviews."""
    
    def __init__(self, config: Config, output_language: str = "English"):
        self.config = config
        self.output_language = output_language
        self.client = AsyncOpenAI(api_key=config.api_key) if config.api_key else None
    
    async def score_document(self, reviews: Dict[str, str], iteration: int) -> DocumentScore:
        """
        Analyze all reviews and produce a comprehensive quality score.
        """
        if not self.client:
            logger.warning("No client, using default score")
            return self._default_score(iteration)
        
        try:
            # Compile all reviews
            reviews_text = "\n\n".join([
                f"=== {agent_name.upper()} ===\n{content}"
                for agent_name, content in reviews.items()
            ])
            
            prompt = f"""You are a document quality assessment expert. Analyze all the reviews below and provide a comprehensive quality score.

Reviews from expert agents:

{reviews_text}

Based on these reviews, provide a JSON assessment with:
- overall_score: float 0-100 (quality score)
- dimension_scores: dict with scores for each reviewed dimension (e.g., "clarity": 75, "accuracy": 80)
- critical_issues: int (number of CRITICAL problems that must be fixed)
- moderate_issues: int (number of moderate problems)
- minor_issues: int (number of minor improvements suggested)
- strengths: array of strings (top 3-5 strengths)
- weaknesses: array of strings (top 3-5 weaknesses)

Score interpretation:
- 90-100: Excellent, publication ready
- 75-89: Good, minor improvements needed
- 60-74: Fair, moderate improvements needed  
- 40-59: Poor, major revision required
- 0-39: Unacceptable, complete rewrite needed

Return ONLY valid JSON."""

            # Try with response_format first (for GPT-4 compatibility)
            try:
                response = await self.client.chat.completions.create(
                    model=self.config.model_powerful,
                    messages=[
                        {"role": "system", "content": "You are a document quality scorer. Output valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1.0,
                    response_format={"type": "json_object"},
                    max_completion_tokens=2000
                )
            except Exception as e:
                # Fallback without response_format (for GPT-5 or other models)
                logger.debug(f"response_format not supported, trying without: {e}")
                response = await self.client.chat.completions.create(
                    model=self.config.model_powerful,
                    messages=[
                        {"role": "system", "content": "You are a document quality scorer. You MUST output ONLY valid JSON, no additional text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1.0,
                    max_completion_tokens=2000
                )
            
            content = response.choices[0].message.content
            
            logger.debug(f"Raw scoring response: {content[:200] if content else 'None'}...")
            
            if not content or not content.strip():
                logger.warning("Empty response from scoring API, using default score")
                return self._default_score(iteration)
            
            # Try to extract JSON if wrapped in text
            content = content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            result = json.loads(content)
            
            score = DocumentScore(
                overall_score=float(result.get("overall_score", 50.0)),
                dimension_scores=result.get("dimension_scores", {}),
                critical_issues=int(result.get("critical_issues", 0)),
                moderate_issues=int(result.get("moderate_issues", 0)),
                minor_issues=int(result.get("minor_issues", 0)),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                iteration=iteration
            )
            
            logger.info(f"Document scored: {score.overall_score:.1f}/100 "
                       f"(Critical: {score.critical_issues}, Moderate: {score.moderate_issues})")
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring document: {e}")
            return self._default_score(iteration)
    
    def _default_score(self, iteration: int) -> DocumentScore:
        """Fallback score when scoring fails."""
        return DocumentScore(
            overall_score=50.0,
            dimension_scores={},
            critical_issues=0,
            moderate_issues=0,
            minor_issues=0,
            strengths=["Could not assess"],
            weaknesses=["Could not assess"],
            iteration=iteration
        )

@dataclass
class ImprovementRequest:
    """Request for additional information or files."""
    request_type: str  # "information", "file_upload", "clarification"
    question: str  # What is needed
    reason: str  # Why it's needed
    file_types: Optional[List[str]] = None  # Expected file types if file_upload
    optional: bool = False  # Whether user can skip
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.request_type,
            "question": self.question,
            "reason": self.reason,
            "file_types": self.file_types,
            "optional": self.optional
        }

class DocumentRefiner:
    """Applies improvements to document based on agent feedback."""
    
    def __init__(self, config: Config, output_language: str = "English", interactive: bool = True):
        self.config = config
        self.output_language = output_language
        self.interactive = interactive
        self.client = AsyncOpenAI(api_key=config.api_key) if config.api_key else None
        self.supplementary_data: Dict[str, Any] = {}  # Store user-provided data
    
    async def identify_missing_information(self, document_text: str, reviews: Dict[str, str]) -> List[ImprovementRequest]:
        """
        Analyze reviews to identify missing information or data that user could provide.
        """
        if not self.client or not self.interactive:
            return []
        
        try:
            feedback = self._extract_actionable_feedback(reviews)
            
            prompt = f"""You are an intelligent document improvement assistant. Analyze the feedback below and identify what information or files the user could provide to improve the document.

DOCUMENT EXCERPT (first 2000 chars):
{document_text[:2000]}

EXPERT FEEDBACK:
{feedback[:3000]}

Based on the feedback, identify specific requests for:
1. **Missing Information**: Facts, data, explanations that user knows but document lacks
2. **Missing Files**: External files that could help (Excel data, reference PDFs, images, etc.)
3. **Clarifications**: Unclear points where user input would help

For each request, provide:
- type: "information", "file_upload", or "clarification"
- question: Clear question to ask user
- reason: Why this would improve the document
- file_types: (only for file_upload) array like ["xlsx", "csv", "pdf"]
- optional: true/false (is this critical or optional?)

Return JSON with array of requests (max 5 most important):
{{
    "requests": [
        {{
            "type": "information",
            "question": "What was the actual revenue in Q3 2023?",
            "reason": "Data Validator found calculation error, need correct figure",
            "optional": false
        }},
        {{
            "type": "file_upload",
            "question": "Can you provide the Excel file with financial projections?",
            "reason": "To verify all calculations and ensure data consistency",
            "file_types": ["xlsx", "csv"],
            "optional": true
        }}
    ]
}}

If NO additional information is needed, return {{"requests": []}}

Return ONLY valid JSON in {self.output_language}."""

            response = await self.client.chat.completions.create(
                model=self.config.model_standard,
                messages=[
                    {"role": "system", "content": "You are a document improvement assistant. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                response_format={"type": "json_object"},
                max_completion_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            requests = []
            
            for req_data in result.get("requests", [])[:5]:  # Max 5 requests
                request = ImprovementRequest(
                    request_type=req_data.get("type", "information"),
                    question=req_data.get("question", ""),
                    reason=req_data.get("reason", ""),
                    file_types=req_data.get("file_types"),
                    optional=req_data.get("optional", True)
                )
                requests.append(request)
            
            return requests
            
        except Exception as e:
            logger.error(f"Error identifying missing information: {e}")
            return []
    
    def _handle_file_upload(self, file_path: str) -> str:
        """
        Process uploaded file and extract relevant content.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return f"File not found: {file_path}"
        
        try:
            extension = file_path.suffix.lower()
            
            # Excel files
            if extension in ['.xlsx', '.xls', '.csv']:
                return self._extract_from_excel(file_path)
            
            # PDF files
            elif extension == '.pdf':
                from main import FileManager
                fm = FileManager(self.config.output_dir)
                return fm.extract_text_from_pdf(str(file_path))
            
            # Text files
            elif extension in ['.txt', '.md', '.json']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Word files
            elif extension in ['.docx', '.doc']:
                return self._extract_from_word(file_path)
            
            else:
                logger.warning(f"Unsupported file type: {extension}")
                return f"Unsupported file type: {extension}"
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return f"Error processing file: {e}"
    
    def _extract_from_excel(self, file_path: Path) -> str:
        """Extract data from Excel/CSV file."""
        try:
            import pandas as pd
            
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
                
                if isinstance(df, dict):  # Multiple sheets
                    result = []
                    for sheet_name, sheet_df in df.items():
                        result.append(f"\n=== Sheet: {sheet_name} ===\n")
                        result.append(sheet_df.to_string())
                    return '\n'.join(result)
                else:
                    df = pd.read_excel(file_path)
            
            return df.to_string()
            
        except ImportError:
            logger.warning("pandas not installed, cannot read Excel files")
            return "Error: pandas library not available for Excel processing"
        except Exception as e:
            logger.error(f"Error reading Excel: {e}")
            return f"Error reading Excel: {e}"
    
    def _extract_from_word(self, file_path: Path) -> str:
        """Extract text from Word document."""
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            logger.warning("python-docx not installed, cannot read Word files")
            return "Error: python-docx library not available"
        except Exception as e:
            logger.error(f"Error reading Word: {e}")
            return f"Error reading Word: {e}"
    
    async def _collect_user_input(self, requests: List[ImprovementRequest]) -> Dict[str, Any]:
        """
        Interactively collect information or files from user.
        """
        collected_data = {}
        
        if not requests:
            return collected_data
        
        print("\n" + "="*80)
        print("🤔 RICHIESTE DI INFORMAZIONI AGGIUNTIVE")
        print("="*80)
        print("\nPer migliorare ulteriormente il documento, ho bisogno di alcune informazioni:")
        print()
        
        for i, request in enumerate(requests, 1):
            optional_marker = "(Opzionale)" if request.optional else "(Richiesto)"
            print(f"\n{i}. {optional_marker}")
            print(f"   Domanda: {request.question}")
            print(f"   Motivo: {request.reason}")
            
            if request.request_type == "file_upload":
                print(f"   Tipo file: {', '.join(request.file_types) if request.file_types else 'qualsiasi'}")
                print(f"   Inserisci il path del file (o INVIO per saltare):")
                user_input = input("   > ").strip()
                
                if user_input:
                    content = self._handle_file_upload(user_input)
                    collected_data[f"file_{i}"] = {
                        "question": request.question,
                        "content": content,
                        "file_path": user_input
                    }
                    print(f"   ✅ File caricato e processato!")
                elif not request.optional:
                    print(f"   ⚠️  File richiesto ma non fornito")
                    
            else:  # information or clarification
                print(f"   La tua risposta (o INVIO per saltare):")
                user_input = input("   > ").strip()
                
                if user_input:
                    collected_data[f"info_{i}"] = {
                        "question": request.question,
                        "answer": user_input
                    }
                    print(f"   ✅ Informazione ricevuta!")
                elif not request.optional:
                    print(f"   ⚠️  Informazione richiesta ma non fornita")
        
        print("\n" + "="*80)
        
        return collected_data
    
    async def refine_document(self, document_text: str, reviews: Dict[str, str], 
                             iteration: int) -> Tuple[str, List[str]]:
        """
        Apply improvements to document based on all agent reviews.
        If interactive mode, may ask user for additional information/files.
        Returns: (improved_document, list_of_improvements_applied)
        """
        if not self.client:
            logger.warning("No client, returning original document")
            return document_text, []
        
        try:
            # Step 1: Identify what additional information might be helpful
            if self.interactive and iteration == 1:  # Only ask on first iteration
                logger.info("Analyzing if additional information could help...")
                requests = await self.identify_missing_information(document_text, reviews)
                
                if requests:
                    logger.info(f"Found {len(requests)} potential improvements through user input")
                    user_data = await self._collect_user_input(requests)
                    self.supplementary_data.update(user_data)
            
            # Compile feedback focused on actionable improvements
            feedback = self._extract_actionable_feedback(reviews)
            
            # Add supplementary data to context if available
            supplementary_context = ""
            if self.supplementary_data:
                supplementary_context = "\n\nADDITIONAL INFORMATION PROVIDED BY USER:\n"
                for key, data in self.supplementary_data.items():
                    if 'file' in key:
                        supplementary_context += f"\n{data['question']}\nFile content:\n{data['content'][:1000]}\n"
                    else:
                        supplementary_context += f"\n{data['question']}\nAnswer: {data['answer']}\n"
            
            prompt = f"""You are an expert document editor. Your task is to improve the following document based on expert reviews.

ORIGINAL DOCUMENT:
{document_text}

EXPERT FEEDBACK AND IMPROVEMENT SUGGESTIONS:
{feedback}{supplementary_context}

Your task:
1. Apply the suggested improvements to the document
2. Fix identified errors (calculations, grammar, clarity, etc.)
3. Enhance weak areas mentioned by reviewers
4. Maintain the document's original purpose and core message
5. Keep the same language as the original

Provide your response as JSON with:
- improved_document: string (the complete improved document text)
- improvements_applied: array of strings (list of specific improvements you made)

**IMPORTANT**: Write in {self.output_language} language.

Return ONLY valid JSON."""

            response = await self.client.chat.completions.create(
                model=self.config.model_powerful,
                messages=[
                    {"role": "system", "content": f"You are an expert document editor. Output valid JSON only. Write in {self.output_language}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                response_format={"type": "json_object"},
                max_completion_tokens=self.config.max_output_tokens
            )
            
            result = json.loads(response.choices[0].message.content)
            
            improved_doc = result.get("improved_document", document_text)
            improvements = result.get("improvements_applied", [])
            
            logger.info(f"Document refined - {len(improvements)} improvements applied")
            for i, improvement in enumerate(improvements[:5], 1):
                logger.info(f"  {i}. {improvement}")
            
            return improved_doc, improvements
            
        except Exception as e:
            logger.error(f"Error refining document: {e}")
            return document_text, ["Error: Could not apply improvements"]
    
    def _extract_actionable_feedback(self, reviews: Dict[str, str]) -> str:
        """Extract actionable improvement suggestions from reviews."""
        feedback_parts = []
        
        for agent_name, review in reviews.items():
            # Extract recommendation sections and specific critiques
            feedback_parts.append(f"\n=== {agent_name.upper().replace('_', ' ')} FEEDBACK ===")
            
            # Try to extract recommendation sections
            if "recommendation" in review.lower() or "suggest" in review.lower():
                lines = review.split('\n')
                in_recommendations = False
                recommendations = []
                
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['recommendation', 'suggest', 'should', 'improve']):
                        in_recommendations = True
                    
                    if in_recommendations and line.strip():
                        recommendations.append(line.strip())
                        
                        # Stop after getting several recommendations
                        if len(recommendations) > 10:
                            break
                
                if recommendations:
                    feedback_parts.append('\n'.join(recommendations[:10]))
                else:
                    # Use full review if can't extract recommendations
                    feedback_parts.append(review[:1000])
            else:
                feedback_parts.append(review[:1000])
        
        return '\n\n'.join(feedback_parts)

class DynamicAgentFactory:
    """Factory that creates agents dynamically based on document type."""
    
    def __init__(self, config: Config, document_type: DocumentType, output_language: str = "English", enable_python_tools: bool = False, deep_review: bool = False):
        self.config = config
        self.document_type = document_type
        self.output_language = output_language
        self.enable_python_tools = enable_python_tools
        self.deep_review = deep_review  # Enable Tier 3 specialists
        self.template_library = AgentTemplateLibrary()
    
    def _determine_model(self, agent_type: str) -> str:
        """
        Determine appropriate model based on agent type and document complexity.
        Uses AGENT_COMPLEXITY scores (like paper system).
        """
        # Get agent complexity from template library (0.0-1.0)
        agent_complexity = AgentTemplateLibrary.AGENT_COMPLEXITY.get(agent_type, 0.7)
        
        # Document complexity (0.0-1.0)
        doc_complexity = self.document_type.complexity
        
        # Calculate final score (inspired by paper system)
        # Weight: 40% document, 60% agent task
        final_score = (doc_complexity * 0.4) + (agent_complexity * 0.6)
        
        # Model selection thresholds (adjusted for cost optimization)
        # Usa gpt-5 solo per task veramente complessi
        if final_score >= 0.80:
            # High complexity: gpt-5 (solo per i più complessi)
            model = self.config.model_powerful
        elif final_score >= 0.60:
            # Medium complexity: gpt-5-mini (per la maggioranza)
            model = self.config.model_standard
        else:
            # Low complexity: gpt-5-nano (per task semplici)
            model = self.config.model_basic
        
        logger.debug(f"Agent '{agent_type}': complexity={agent_complexity:.2f}, doc={doc_complexity:.2f}, final={final_score:.2f} → {model}")
        return model
    
    def create_agent(self, agent_type: str) -> Optional[Agent]:
        """Create a single agent of the specified type."""
        template = self.template_library.get_template(agent_type)
        if not template:
            logger.warning(f"Unknown agent type: {agent_type}")
            return None
        
        model = self._determine_model(agent_type)
        
        # Special handling for web research agents
        if agent_type in ["web_researcher", "fact_checker"]:
            if not WEB_RESEARCH_AVAILABLE:
                logger.warning(f"Web research not available, skipping {agent_type}")
                return None
            
            # Add language instruction
            language_instruction = f"\n\n**IMPORTANT**: Provide your entire review in {self.output_language} language."
            instructions = template["instructions"] + language_instruction
            
            agent = Agent(
                name=template["name"].replace(" ", "_"),
                instructions=instructions,
                model=model,
                temperature=1.0,
                max_output_tokens=self.config.max_output_tokens,
                use_caching=self.config.use_prompt_caching
            )
            
            # Mark as web research agent
            agent.use_web_search = True
            agent.use_tools = False
            
            logger.info(f"Created agent '{template['name']}' with WEB SEARCH capability")
            return agent
        
        # Special handling for data_validator with tools
        if agent_type == "data_validator" and self.enable_python_tools and AGENT_TOOLS_AVAILABLE:
            instructions = create_data_validator_instructions_with_tools()
            language_instruction = f"\n\n**IMPORTANT**: Provide your entire review in {self.output_language} language."
            instructions = instructions + language_instruction
            use_tools = True
            logger.info(f"Created agent '{template['name']}' with Python execution tools")
        else:
            # Add language instruction and end marker
            language_instruction = f"\n\n**IMPORTANT**: Provide your entire review in {self.output_language} language."
            instructions = template["instructions"] + language_instruction + f'\n\nEnd your review with: "REVIEW COMPLETED - {template["name"]}"'
            use_tools = False
        
        agent = Agent(
            name=template["name"].replace(" ", "_"),
            instructions=instructions,
            model=model,
            temperature=1.0,
            max_output_tokens=self.config.max_output_tokens,
            use_caching=self.config.use_prompt_caching
        )
        
        # Mark agent for tool usage
        agent.use_tools = use_tools
        agent.use_web_search = False
        
        logger.info(f"Created agent '{template['name']}' using model '{model}'" + 
                   (" with tools" if use_tools else ""))
        return agent
    
    def create_coordinator_agent(self) -> Agent:
        """Create coordinator agent for synthesis."""
        return Agent(
            name="Review_Coordinator",
            instructions=f"""You are the coordinator for a comprehensive review of a {self.document_type.category} document.
You have received reviews from multiple expert reviewers. Your task is to:
1. Review all feedback provided by the experts
2. Identify consensus points and disagreements
3. Synthesize feedback into a structured overall assessment
4. Balance criticisms and strengths for fair evaluation
5. Produce clear final recommendations with rationales
6. Highlight priorities for any improvements

Create a comprehensive, balanced summary of all reviewer feedback.

Your assessment should include:
- Executive summary of document's strengths and weaknesses
- Key findings from each reviewer
- Overall quality assessment
- Critical issues requiring attention
- Recommendations for improvement
- Final evaluation

**IMPORTANT**: Provide your entire assessment in {self.output_language} language.

End with: "COORDINATOR ASSESSMENT COMPLETED" """,
            model=self.config.model_powerful,
            temperature=1.0,
            max_output_tokens=self.config.max_output_tokens,
            use_caching=self.config.use_prompt_caching
        )
    
    def create_final_evaluator_agent(self) -> Agent:
        """Create final evaluator for overall judgment."""
        return Agent(
            name="Final_Evaluator",
            instructions=f"""You are a senior evaluator providing final judgment on a {self.document_type.category} document.
Based on all reviews and the coordinator's assessment, provide:
1. Overall quality rating (Excellent/Good/Fair/Poor)
2. Readiness assessment (Ready/Needs Minor Revisions/Needs Major Revisions/Not Ready)
3. Key strengths (top 3-5)
4. Key weaknesses (top 3-5)
5. Priority improvements needed
6. Final recommendation with clear justification

Use professional language and provide actionable guidance.

**IMPORTANT**: Provide your entire evaluation in {self.output_language} language.

End with: "FINAL EVALUATION COMPLETED" """,
            model=self.config.model_powerful,
            temperature=1.0,
            max_output_tokens=self.config.max_output_tokens,
            use_caching=self.config.use_prompt_caching
        )
    
    def create_all_agents(self) -> Dict[str, Agent]:
        """
        Create all agents needed for this document type using 3-tier system.
        
        TIER 1: Core agents (always active)
        TIER 2: Document-specific agents (from classifier suggestions)
        TIER 3: Deep-dive specialists (only if --deep-review flag)
        """
        agents = {}
        
        # TIER 1: Always include core agents (essential for any review)
        tier1_core = ["style_editor", "consistency_checker", "fact_checker", "logic_checker", "technical_expert"]
        logger.info(f"[TIER 1] Creating {len(tier1_core)} core agents (always active)")
        
        for agent_type in tier1_core:
            agent = self.create_agent(agent_type)
            if agent:
                agents[agent_type] = agent
        
        # TIER 2: Create document-specific agents from classifier suggestions
        tier2_agents = [a for a in self.document_type.suggested_agents 
                        if a not in tier1_core and AgentTemplateLibrary.AGENT_TIERS.get(a, 2) == 2]
        logger.info(f"[TIER 2] Creating {len(tier2_agents)} document-specific agents")
        
        for agent_type in tier2_agents:
            agent = self.create_agent(agent_type)
            if agent:
                agents[agent_type] = agent
        
        # TIER 3: Create deep-dive specialists (only if deep_review=True)
        if self.deep_review:
            tier3_agents = [a for a in self.document_type.suggested_agents 
                            if AgentTemplateLibrary.AGENT_TIERS.get(a, 2) == 3]
            logger.info(f"[TIER 3] Creating {len(tier3_agents)} deep-dive specialists (--deep-review active)")
            
            for agent_type in tier3_agents:
                agent = self.create_agent(agent_type)
                if agent:
                    agents[agent_type] = agent
        else:
            tier3_count = len([a for a in self.document_type.suggested_agents 
                              if AgentTemplateLibrary.AGENT_TIERS.get(a, 2) == 3])
            if tier3_count > 0:
                logger.info(f"[TIER 3] Skipping {tier3_count} deep-dive specialists (use --deep-review to enable)")
        
        # Always create coordinator and evaluator
        agents["coordinator"] = self.create_coordinator_agent()
        agents["final_evaluator"] = self.create_final_evaluator_agent()
        
        logger.info(f"✅ Created {len(agents)} total agents for document review (Tier 1: {len([a for a in agents if AgentTemplateLibrary.AGENT_TIERS.get(a, 0) == 1])}, Tier 2: {len([a for a in agents if AgentTemplateLibrary.AGENT_TIERS.get(a, 0) == 2])}, Tier 3: {len([a for a in agents if AgentTemplateLibrary.AGENT_TIERS.get(a, 0) == 3])})")
        return agents

class GenericReviewOrchestrator:
    """Main orchestrator for generic document review."""
    
    def __init__(self, config: Config, output_language: str = "English", 
                 enable_python_tools: bool = False, reference_context: str = "",
                 enable_web_research: bool = None, disable_web_research: bool = False,
                 deep_review: bool = False):
        self.config = config
        self.output_language = output_language
        self.enable_python_tools = enable_python_tools
        self.reference_context = reference_context
        self.deep_review = deep_review  # Enable Tier 3 specialists
        self.file_manager = FileManager(config.output_dir)
        self.classifier = DocumentClassifier(config, enable_web_research, disable_web_research)
        self.document_type: Optional[DocumentType] = None
        self.agents: Dict[str, Agent] = {}
    
    async def execute_review_process(self, document_text: str, document_title: str = "Untitled Document") -> Dict[str, Any]:
        """Execute the full review process."""
        try:
            logger.info("=" * 60)
            logger.info("GENERIC DOCUMENT REVIEW SYSTEM")
            logger.info("=" * 60)
            
            # Step 1: Classify document
            logger.info("\n[STEP 1] Classifying document...")
            self.document_type = await self.classifier.classify_document(document_text)
            self.file_manager.save_json(self.document_type.to_dict(), "document_classification.json")
            
            # Step 2: Create appropriate agents
            logger.info(f"\n[STEP 2] Creating specialized review agents...")
            logger.info(f"Output language: {self.output_language}")
            if self.enable_python_tools:
                logger.info(f"Python tools enabled for data validation")
            agent_factory = DynamicAgentFactory(
                self.config, 
                self.document_type, 
                self.output_language,
                enable_python_tools=self.enable_python_tools,
                deep_review=self.deep_review
            )
            self.agents = agent_factory.create_all_agents()
            
            # Step 3: Prepare review message
            logger.info(f"\n[STEP 3] Preparing document for review...")
            review_message = self._prepare_review_message(document_title, document_text)
            
            # Step 4: Execute reviews in parallel
            logger.info(f"\n[STEP 4] Executing {len(self.agents) - 2} expert reviews in parallel...")
            reviews = await self._execute_parallel_reviews(review_message)
            
            # Step 5: Run coordinator
            logger.info(f"\n[STEP 5] Synthesizing reviews (Coordinator)...")
            coordinator_review = await self._execute_coordinator(reviews)
            reviews["coordinator"] = coordinator_review
            
            # Step 6: Run final evaluator
            logger.info(f"\n[STEP 6] Generating final evaluation...")
            final_evaluation = await self._execute_final_evaluator(reviews)
            
            # Step 7: Compile results
            logger.info(f"\n[STEP 7] Compiling results and generating reports...")
            final_results = self._compile_results(document_title, reviews, final_evaluation)
            
            # Step 8: Generate reports
            self._generate_reports(final_results)
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ REVIEW PROCESS COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
            return final_results
            
        except Exception as e:
            logger.error(f"Critical error in review process: {e}", exc_info=True)
            raise
    
    def _prepare_review_message(self, title: str, document_text: str) -> str:
        """Prepare the message for reviewers."""
        message_parts = []
        
        # Add reference context if available
        if self.reference_context:
            message_parts.append(self.reference_context)
            message_parts.append("\n" + "="*80 + "\n")
        
        # Add document info
        message_parts.append(f"""Document to Review:

Title: {title}
Type: {self.document_type.category} ({self.document_type.subcategory})
Complexity: {self.document_type.complexity:.2f}
Key Characteristics: {', '.join(self.document_type.characteristics)}

Please conduct a comprehensive review of this document from your area of expertise.
""")
        
        if self.reference_context:
            message_parts.append("""
When reviewing, consider:
- How well it matches reference templates/examples (if provided)
- Compliance with guidelines (if provided)
- Comparison to successful examples (if provided)
- Adherence to style guides (if provided)
- Accuracy against reference data (if provided)
""")
        
        message_parts.append(f"""
Document Content:

{document_text}
""")
        
        return ''.join(message_parts)
    
    def _execute_agent_with_optional_tools(self, agent: Agent, message: str) -> str:
        """Execute agent, using tools, academic search, or web search if enabled."""
        # Check if agent uses academic search (Semantic Scholar + Web)
        if hasattr(agent, 'use_academic_search') and agent.use_academic_search:
            logger.info(f"🔬 Executing {agent.name} with ACADEMIC SEARCH")
            
            research_results = []
            
            # 1. Try Semantic Scholar for academic papers
            if SEMANTIC_SCHOLAR_AVAILABLE:
                try:
                    # Extract key terms from message (first 200 chars as query)
                    query = message[:200] if len(message) > 200 else message
                    # Remove common phrases to get clean keywords
                    query = query.replace("Review the following", "").replace("Analyze", "").strip()
                    
                    academic_result = execute_academic_research(agent.name, query, limit=10)
                    
                    if not academic_result.startswith("⚠️"):
                        research_results.append(academic_result)
                        logger.info(f"✅ Semantic Scholar search completed for {agent.name}")
                    else:
                        logger.warning(f"Semantic Scholar search yielded no results")
                except Exception as e:
                    logger.error(f"Semantic Scholar search failed: {e}")
            else:
                logger.warning("Semantic Scholar not available")
            
            # 2. Also try web search for recent developments
            if hasattr(agent, 'use_web_search') and agent.use_web_search and WEB_RESEARCH_AVAILABLE:
                try:
                    import concurrent.futures
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            execute_web_research_agent,
                            api_key=self.config.api_key,
                            model=agent.model,
                            message=f"Find recent research and developments: {message[:300]}",
                            agent_type="researcher"
                        )
                        
                        try:
                            web_result = future.result(timeout=60)
                            research_results.append("\n\n## Recent Web Research\n\n" + web_result)
                            logger.info(f"✅ Web search also completed for {agent.name}")
                        except concurrent.futures.TimeoutError:
                            logger.warning(f"Web search timed out for {agent.name}")
                            future.cancel()
                        except Exception as e:
                            logger.warning(f"Web search failed: {e}")
                            
                except Exception as e:
                    logger.warning(f"Web research component failed: {e}")
            
            # 3. Combine results and let agent analyze
            if research_results:
                combined_research = "\n\n---\n\n".join(research_results)
                combined_message = f"{message}\n\n---\n\n# Research Data\n\n{combined_research}"
                return agent.run(combined_message)
            else:
                logger.warning(f"No research data found for {agent.name}, using standard execution")
                return agent.run(message)
        
        # Check if agent uses web search (Responses API)
        elif hasattr(agent, 'use_web_search') and agent.use_web_search and WEB_RESEARCH_AVAILABLE:
            logger.info(f"🌐 Executing {agent.name} with WEB SEARCH")
            
            # Try OpenAI Responses API first
            try:
                # Execute with timeout to prevent hanging (90 seconds max)
                import concurrent.futures
                
                # Create executor for timeout
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        execute_web_research_agent,
                        api_key=self.config.api_key,
                        model=agent.model,
                        message=f"{agent.instructions}\n\n{message}",
                        agent_type="researcher"
                    )
                    
                    # Wait with timeout (90 seconds for web research)
                    try:
                        result = future.result(timeout=90)
                        logger.info(f"✅ {agent.name} OpenAI web search completed successfully")
                        return result
                    except concurrent.futures.TimeoutError:
                        logger.warning(f"⏱️ {agent.name} OpenAI web search timed out after 90s")
                        future.cancel()
                        # Will try Tavily fallback below
                        raise TimeoutError("OpenAI Responses API timeout")
                        
            except Exception as e:
                logger.warning(f"OpenAI web search failed: {e}")
                
                # Try Tavily as fallback
                if TAVILY_AVAILABLE:
                    logger.info(f"🔄 Trying Tavily fallback for {agent.name}")
                    try:
                        # Extract query from message (first 500 chars for context)
                        query = message[:500] + "..." if len(message) > 500 else message
                        tavily_result = execute_tavily_research(agent.name, query)
                        
                        if not tavily_result.startswith("⚠️"):
                            # Tavily succeeded - now let agent analyze the results
                            combined_message = f"{message}\n\n---\n\n{tavily_result}"
                            return agent.run(combined_message)
                        else:
                            logger.warning(f"Tavily also failed: {tavily_result}")
                    except Exception as tavily_error:
                        logger.error(f"Tavily fallback failed: {tavily_error}")
                
                # All web search methods failed - fallback to standard execution
                logger.info(f"All web search methods failed - falling back to standard execution for {agent.name}")
                return agent.run(message)
        
        # Check if agent has Python tools enabled
        elif hasattr(agent, 'use_tools') and agent.use_tools and AGENT_TOOLS_AVAILABLE:
            logger.info(f"🔧 Executing {agent.name} with Python tools")
            from openai import OpenAI
            client = OpenAI(api_key=self.config.api_key)
            
            messages = [
                {"role": "system", "content": agent.instructions},
                {"role": "user", "content": message}
            ]
            
            # Use tool-enabled execution
            result = execute_agent_with_tools(
                client=client,
                model=agent.model,
                messages=messages,
                max_tool_iterations=10
            )
            return result
        else:
            # Standard execution
            return agent.run(message)
    
    async def _execute_parallel_reviews(self, message: str) -> Dict[str, str]:
        """Execute all review agents in parallel."""
        review_agents = {k: v for k, v in self.agents.items() 
                        if k not in ["coordinator", "final_evaluator"]}
        
        tasks = []
        agent_names = []
        
        for name, agent in review_agents.items():
            agent_names.append(name)
            loop = asyncio.get_running_loop()
            tasks.append(loop.run_in_executor(None, self._execute_agent_with_optional_tools, agent, message))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        reviews = {}
        for name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                logger.error(f"Error in agent {name}: {result}")
                reviews[name] = f"Error during review: {result}"
            else:
                reviews[name] = result
                self.file_manager.save_review(name, result)
        
        return reviews
    
    async def _execute_coordinator(self, reviews: Dict[str, str]) -> str:
        """Execute coordinator synthesis."""
        coordinator = self.agents.get("coordinator")
        if not coordinator:
            return "Coordinator not available"
        
        reviews_text = "\n\n".join([
            f"=== {name.upper().replace('_', ' ')} REVIEW ===\n{content}"
            for name, content in reviews.items()
            if name != "coordinator"
        ])
        
        message = f"""Here are all the expert reviews for the document:

{reviews_text}

Please provide your comprehensive coordinator assessment based on all these reviews."""
        
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, coordinator.run, message)
            self.file_manager.save_review("coordinator", result)
            return result
        except Exception as e:
            logger.error(f"Error in coordinator: {e}")
            return f"Error in coordinator assessment: {str(e)}"
    
    async def _execute_final_evaluator(self, reviews: Dict[str, str]) -> str:
        """Execute final evaluator."""
        evaluator = self.agents.get("final_evaluator")
        if not evaluator:
            return "Final evaluator not available"
        
        reviews_text = "\n\n".join([
            f"=== {name.upper().replace('_', ' ')} REVIEW ===\n{content}"
            for name, content in reviews.items()
        ])
        
        message = f"""Here are all reviews including the coordinator's assessment:

{reviews_text}

Please provide your final evaluation and recommendation."""
        
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, evaluator.run, message)
            self.file_manager.save_review("final_evaluator", result)
            return result
        except Exception as e:
            logger.error(f"Error in final evaluator: {e}")
            return f"Error in final evaluation: {str(e)}"
    
    def _compile_results(self, title: str, reviews: Dict[str, str], 
                        final_evaluation: str) -> Dict[str, Any]:
        """Compile all results."""
        return {
            "document_info": {
                "title": title,
                "type": self.document_type.to_dict(),
                "length": len(reviews.get(list(reviews.keys())[0], "")),  # Approximate
                "review_date": datetime.now().isoformat()
            },
            "reviews": reviews,
            "final_evaluation": final_evaluation,
            "metadata": {
                "num_reviewers": len([r for r in reviews.keys() if r not in ["coordinator"]]),
                "models_used": {
                    "powerful": self.config.model_powerful,
                    "standard": self.config.model_standard,
                    "basic": self.config.model_basic
                }
            }
        }
    
    def _generate_reports(self, results: Dict[str, Any]) -> None:
        """Generate comprehensive reports."""
        # Remove timestamp for Web UI compatibility - files in unique timestamped folder already
        
        # JSON Report
        self.file_manager.save_json(results, "review_results.json")
        
        # Markdown Report
        markdown_report = self._generate_markdown_report(results)
        self.file_manager.save_text(markdown_report, "review_report.md")
        
        # HTML Dashboard
        html_dashboard = self._generate_html_dashboard(results)
        self.file_manager.save_text(html_dashboard, "dashboard.html")
        
        logger.info(f"Reports generated in: {self.config.output_dir}")
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown report."""
        doc_info = results["document_info"]
        reviews = results["reviews"]
        final_eval = results["final_evaluation"]
        doc_type = doc_info["type"]
        
        report = f"""# Document Review Report

**Generated:** {doc_info['review_date']}

## Document Information

**Title:** {doc_info['title']}

**Type:** {doc_type['category']} - {doc_type['subcategory']}

**Complexity:** {doc_type['complexity']:.2f} (Confidence: {doc_type['confidence']:.2f})

**Key Characteristics:** {', '.join(doc_type['characteristics'])}

**Reviewers:** {results['metadata']['num_reviewers']} expert reviewers

## Final Evaluation

{final_eval}

## Coordinator Assessment

{reviews.get('coordinator', 'Not available')}

## Detailed Expert Reviews

"""
        
        # Add each review
        for agent_type, review_content in reviews.items():
            if agent_type not in ["coordinator"]:
                title = agent_type.replace('_', ' ').title()
                report += f"### {title}\n\n{review_content}\n\n---\n\n"
        
        return report
    
    def _generate_html_dashboard(self, results: Dict[str, Any]) -> str:
        """Generate HTML dashboard."""
        doc_info = results["document_info"]
        reviews = results["reviews"]
        final_eval = results["final_evaluation"]
        doc_type = doc_info["type"]
        
        def esc(text: str) -> str:
            import html
            return html.escape(str(text))
        
        # Determine evaluation class based on keywords
        eval_class = "bg-gray-100"
        eval_icon = "📋"
        eval_lower = final_eval.lower()
        if "excellent" in eval_lower or "ready" in eval_lower:
            eval_class = "bg-green-100 border-green-300"
            eval_icon = "✅"
        elif "good" in eval_lower or "minor revisions" in eval_lower:
            eval_class = "bg-blue-100 border-blue-300"
            eval_icon = "🔧"
        elif "fair" in eval_lower or "major revisions" in eval_lower:
            eval_class = "bg-yellow-100 border-yellow-300"
            eval_icon = "⚠️"
        elif "poor" in eval_lower or "not ready" in eval_lower:
            eval_class = "bg-red-100 border-red-300"
            eval_icon = "❌"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Review - {esc(doc_info['title'])}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .review-card {{ transition: all 0.3s ease; }}
        .review-card:hover {{ transform: translateY(-2px); box-shadow: 0 12px 24px rgba(0,0,0,0.1); }}
    </style>
</head>
<body class="bg-gray-50">
    <div class="gradient-bg text-white">
        <div class="container mx-auto px-6 py-12">
            <h1 class="text-4xl font-bold mb-2">📋 Document Review Dashboard</h1>
            <p class="text-purple-100">Generic Document Review System - Powered by AI</p>
        </div>
    </div>
    
    <div class="container mx-auto px-6 py-8 max-w-7xl">
        <!-- Document Info -->
        <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 class="text-2xl font-semibold mb-6">📄 Document Information</h2>
            <div class="grid md:grid-cols-2 gap-6">
                <div>
                    <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Title</h3>
                    <p class="text-lg font-medium text-gray-900">{esc(doc_info['title'])}</p>
                </div>
                <div>
                    <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Type</h3>
                    <p class="text-lg text-gray-700">{esc(doc_type['category'])} - {esc(doc_type['subcategory'])}</p>
                </div>
                <div>
                    <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Complexity</h3>
                    <p class="text-lg text-gray-700">{doc_type['complexity']:.2f} / 1.0</p>
                </div>
                <div>
                    <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Review Date</h3>
                    <p class="text-lg text-gray-700">{esc(doc_info['review_date'])}</p>
                </div>
            </div>
            <div class="mt-6">
                <h3 class="text-sm font-medium text-gray-500 uppercase mb-2">Key Characteristics</h3>
                <div class="flex flex-wrap gap-2">
                    {' '.join([f'<span class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">{esc(char)}</span>' for char in doc_type['characteristics']])}
                </div>
            </div>
        </div>
        
        <!-- Final Evaluation -->
        <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 class="text-2xl font-semibold mb-6 flex items-center">
                <span class="text-2xl mr-3">{eval_icon}</span>
                Final Evaluation
            </h2>
            <div class="{eval_class} border-2 rounded-lg p-6">
                <pre class="whitespace-pre-wrap text-sm leading-relaxed">{esc(final_eval)}</pre>
            </div>
        </div>
        
        <!-- Stats -->
        <div class="grid md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow-lg p-6 text-center">
                <div class="text-3xl font-bold text-purple-600">{results['metadata']['num_reviewers']}</div>
                <div class="text-gray-600 mt-2">Expert Reviewers</div>
            </div>
            <div class="bg-white rounded-lg shadow-lg p-6 text-center">
                <div class="text-3xl font-bold text-purple-600">{doc_type['confidence']:.0%}</div>
                <div class="text-gray-600 mt-2">Classification Confidence</div>
            </div>
            <div class="bg-white rounded-lg shadow-lg p-6 text-center">
                <div class="text-3xl font-bold text-purple-600">{len(doc_type['suggested_agents'])}</div>
                <div class="text-gray-600 mt-2">Analysis Dimensions</div>
            </div>
        </div>
        
        <!-- Coordinator Assessment -->
        <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 class="text-2xl font-semibold mb-6 flex items-center">
                <span class="text-2xl mr-3">🎯</span>
                Coordinator Assessment
            </h2>
            <div class="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
                <pre class="whitespace-pre-wrap text-sm leading-relaxed text-gray-800">{esc(reviews.get('coordinator', 'Not available'))}</pre>
            </div>
        </div>
        
        <!-- Detailed Reviews -->
        <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 class="text-2xl font-semibold mb-6">📋 Detailed Expert Reviews</h2>
            <div class="space-y-6">"""
        
        # Add each review
        for agent_type, review_content in reviews.items():
            if agent_type != "coordinator":
                template = AgentTemplateLibrary.get_template(agent_type)
                if template:
                    icon = template['icon']
                    name = template['name']
                else:
                    icon = "📝"
                    name = agent_type.replace('_', ' ').title()
                
                html += f"""
                <div class="review-card border-2 border-gray-200 rounded-lg p-6">
                    <h3 class="text-xl font-semibold mb-4 flex items-center">
                        <span class="text-2xl mr-3">{icon}</span>
                        {name}
                    </h3>
                    <pre class="whitespace-pre-wrap text-sm leading-relaxed text-gray-800">{esc(review_content)}</pre>
                </div>"""
        
        html += """
            </div>
        </div>
    </div>
</body>
</html>"""
        
        return html

class IterativeReviewOrchestrator:
    """Orchestrator for iterative document improvement through agent feedback."""
    
    def __init__(self, config: Config, output_language: str = "English", 
                 max_iterations: int = 3, target_score: float = 85.0, interactive: bool = False,
                 enable_python_tools: bool = False, reference_context: str = "",
                 enable_web_research: bool = None, disable_web_research: bool = False,
                 deep_review: bool = False):
        self.config = config
        self.output_language = output_language
        self.max_iterations = max_iterations
        self.target_score = target_score
        self.deep_review = deep_review  # Enable Tier 3 specialists
        self.interactive = interactive
        self.enable_python_tools = enable_python_tools
        self.reference_context = reference_context
        self.file_manager = FileManager(config.output_dir)
        self.base_orchestrator = GenericReviewOrchestrator(
            config, output_language, 
            enable_python_tools=enable_python_tools,
            reference_context=reference_context,
            enable_web_research=enable_web_research,
            disable_web_research=disable_web_research,
            deep_review=deep_review
        )
        self.scorer = DocumentScorer(config, output_language)
        self.refiner = DocumentRefiner(config, output_language, interactive)
        self.iteration_history: List[IterationResult] = []
    
    async def execute_iterative_review(self, document_text: str, 
                                      document_title: str = "Untitled Document") -> Dict[str, Any]:
        """
        Execute iterative review process with automatic document improvement.
        """
        try:
            logger.info("=" * 80)
            logger.info("ITERATIVE DOCUMENT REVIEW & IMPROVEMENT SYSTEM")
            logger.info("=" * 80)
            logger.info(f"Max iterations: {self.max_iterations}")
            logger.info(f"Target quality score: {self.target_score}/100")
            logger.info(f"Output language: {self.output_language}")
            logger.info("=" * 80)
            
            current_document = document_text
            current_title = document_title
            best_score = None
            best_iteration = None
            
            # Iteration loop
            for iteration in range(1, self.max_iterations + 1):
                logger.info(f"\n{'='*80}")
                logger.info(f"ITERATION {iteration}/{self.max_iterations}")
                logger.info(f"{'='*80}")
                
                # Step 1: Review current document version
                logger.info(f"\n[ITERATION {iteration} - STEP 1] Reviewing document...")
                review_results = await self.base_orchestrator.execute_review_process(
                    current_document, 
                    f"{current_title} (Iteration {iteration})"
                )
                
                reviews = review_results["reviews"]
                
                # Step 2: Score the document
                logger.info(f"\n[ITERATION {iteration} - STEP 2] Scoring document quality...")
                score = await self.scorer.score_document(reviews, iteration)
                
                logger.info(f"\n📊 Quality Score: {score.overall_score:.1f}/100")
                logger.info(f"   Critical issues: {score.critical_issues}")
                logger.info(f"   Moderate issues: {score.moderate_issues}")
                logger.info(f"   Minor issues: {score.minor_issues}")
                
                # Store iteration result
                iteration_result = IterationResult(
                    iteration_number=iteration,
                    document_version=current_document,
                    reviews=reviews,
                    score=score,
                    improvements_applied=[],
                    timestamp=datetime.now().isoformat()
                )
                self.iteration_history.append(iteration_result)
                
                # Track best version
                if best_score is None or score.is_better_than(best_score):
                    best_score = score
                    best_iteration = iteration
                    logger.info(f"   ⭐ New best version!")
                
                # Check stopping conditions
                if score.overall_score >= self.target_score and score.critical_issues == 0:
                    logger.info(f"\n✅ TARGET REACHED! Score {score.overall_score:.1f} >= {self.target_score}")
                    logger.info(f"   Document quality is excellent. Stopping iteration.")
                    break
                
                # Don't refine if this is the last iteration
                if iteration >= self.max_iterations:
                    logger.info(f"\n⚠️  Maximum iterations reached ({self.max_iterations})")
                    break
                
                # Step 3: Apply improvements for next iteration
                logger.info(f"\n[ITERATION {iteration} - STEP 3] Applying improvements...")
                logger.info("   Extracting actionable feedback from reviews...")
                logger.info("   Generating improved document version...")
                
                improved_doc, improvements = await self.refiner.refine_document(
                    current_document, reviews, iteration
                )
                
                # Update iteration result with improvements
                iteration_result.improvements_applied = improvements
                
                logger.info(f"\n✏️  Improvements Applied ({len(improvements)}):")
                for i, improvement in enumerate(improvements[:10], 1):
                    logger.info(f"   {i}. {improvement[:100]}...")
                
                # Prepare for next iteration
                current_document = improved_doc
                
                # Save intermediate version
                self.file_manager.save_text(
                    improved_doc, 
                    f"document_iteration_{iteration+1}_improved.txt"
                )
            
            # Generate final results
            logger.info(f"\n{'='*80}")
            logger.info("ITERATIVE REVIEW COMPLETED")
            logger.info(f"{'='*80}")
            logger.info(f"Total iterations: {len(self.iteration_history)}")
            logger.info(f"Best iteration: {best_iteration}")
            logger.info(f"Best score: {best_score.overall_score:.1f}/100")
            logger.info(f"Improvement: {best_score.overall_score - self.iteration_history[0].score.overall_score:+.1f} points")
            
            # Compile final results
            final_results = self._compile_iterative_results(document_title)
            
            # Generate reports
            self._generate_iterative_reports(final_results)
            
            return final_results
            
        except Exception as e:
            logger.error(f"Critical error in iterative review: {e}", exc_info=True)
            raise
    
    def _compile_iterative_results(self, title: str) -> Dict[str, Any]:
        """Compile all iteration results."""
        if not self.iteration_history:
            return {}
        
        best_iteration = max(self.iteration_history, 
                           key=lambda x: (x.score.overall_score, -x.score.critical_issues))
        
        return {
            "document_title": title,
            "total_iterations": len(self.iteration_history),
            "max_iterations_allowed": self.max_iterations,
            "target_score": self.target_score,
            "output_language": self.output_language,
            "iterations": [it.to_dict() for it in self.iteration_history],
            "best_iteration": {
                "iteration_number": best_iteration.iteration_number,
                "score": best_iteration.score.to_dict(),
                "document_length": len(best_iteration.document_version)
            },
            "improvement_summary": {
                "initial_score": self.iteration_history[0].score.overall_score,
                "final_score": self.iteration_history[-1].score.overall_score,
                "best_score": best_iteration.score.overall_score,
                "score_improvement": best_iteration.score.overall_score - self.iteration_history[0].score.overall_score,
                "critical_issues_resolved": self.iteration_history[0].score.critical_issues - best_iteration.score.critical_issues,
                "total_improvements_applied": sum(len(it.improvements_applied) for it in self.iteration_history)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_iterative_reports(self, results: Dict[str, Any]) -> None:
        """Generate comprehensive reports for iterative process."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. JSON Report with full data
        self.file_manager.save_json(results, f"iterative_results_{timestamp}.json")
        
        # 2. Markdown comparison report
        markdown_report = self._generate_comparison_report(results)
        self.file_manager.save_text(markdown_report, f"iterative_comparison_{timestamp}.md")
        
        # 3. HTML dashboard
        html_dashboard = self._generate_iterative_dashboard(results)
        self.file_manager.save_text(html_dashboard, f"iterative_dashboard_{timestamp}.html")
        
        # 4. Save best version
        best_iter_num = results["best_iteration"]["iteration_number"]
        best_iteration = self.iteration_history[best_iter_num - 1]
        self.file_manager.save_text(
            best_iteration.document_version,
            f"document_best_version_iter{best_iter_num}.txt"
        )
        
        logger.info(f"\n📁 Reports generated in: {self.config.output_dir}")
    
    def _generate_comparison_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown comparison report."""
        report = f"""# Iterative Document Review Report

**Document:** {results['document_title']}  
**Generated:** {results['timestamp']}  
**Language:** {results['output_language']}

## Process Summary

- **Total Iterations:** {results['total_iterations']}/{results['max_iterations_allowed']}
- **Target Score:** {results['target_score']}/100
- **Best Iteration:** #{results['best_iteration']['iteration_number']}

## Quality Improvement

| Metric | Initial | Final | Best | Change |
|--------|---------|-------|------|--------|
| **Overall Score** | {results['improvement_summary']['initial_score']:.1f} | {results['improvement_summary']['final_score']:.1f} | {results['improvement_summary']['best_score']:.1f} | **{results['improvement_summary']['score_improvement']:+.1f}** |
| **Critical Issues** | {self.iteration_history[0].score.critical_issues} | {self.iteration_history[-1].score.critical_issues} | {results['best_iteration']['score']['critical_issues']} | **{-results['improvement_summary']['critical_issues_resolved']}** |
| **Moderate Issues** | {self.iteration_history[0].score.moderate_issues} | {self.iteration_history[-1].score.moderate_issues} | {results['best_iteration']['score']['moderate_issues']} | - |
| **Total Improvements** | - | - | - | **{results['improvement_summary']['total_improvements_applied']}** |

"""
        
        # Add iteration details
        report += "\n## Iteration Details\n\n"
        
        for iteration in self.iteration_history:
            report += f"### Iteration {iteration.iteration_number}\n\n"
            report += f"**Quality Score:** {iteration.score.overall_score:.1f}/100\n\n"
            
            if iteration.score.strengths:
                report += "**Strengths:**\n"
                for strength in iteration.score.strengths:
                    report += f"- {strength}\n"
                report += "\n"
            
            if iteration.score.weaknesses:
                report += "**Weaknesses:**\n"
                for weakness in iteration.score.weaknesses:
                    report += f"- {weakness}\n"
                report += "\n"
            
            if iteration.improvements_applied:
                report += f"**Improvements Applied ({len(iteration.improvements_applied)}):**\n"
                for i, improvement in enumerate(iteration.improvements_applied[:15], 1):
                    report += f"{i}. {improvement}\n"
                report += "\n"
            
            report += "---\n\n"
        
        return report
    
    def _generate_iterative_dashboard(self, results: Dict[str, Any]) -> str:
        """Generate HTML dashboard for iterative process."""
        def esc(text: str) -> str:
            import html
            return html.escape(str(text))
        
        improvement = results['improvement_summary']['score_improvement']
        improvement_class = "text-green-600" if improvement > 0 else "text-red-600"
        improvement_icon = "↗️" if improvement > 0 else "↘️"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iterative Review - {esc(results['document_title'])}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-50">
    <div class="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <div class="container mx-auto px-6 py-12">
            <h1 class="text-4xl font-bold mb-2">🔄 Iterative Document Review</h1>
            <p class="text-purple-100">{esc(results['document_title'])}</p>
        </div>
    </div>
    
    <div class="container mx-auto px-6 py-8 max-w-7xl">
        <!-- Summary Cards -->
        <div class="grid md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow-lg p-6">
                <div class="text-gray-500 text-sm mb-2">Total Iterations</div>
                <div class="text-3xl font-bold text-purple-600">{results['total_iterations']}</div>
            </div>
            <div class="bg-white rounded-lg shadow-lg p-6">
                <div class="text-gray-500 text-sm mb-2">Best Score</div>
                <div class="text-3xl font-bold text-green-600">{results['improvement_summary']['best_score']:.1f}</div>
            </div>
            <div class="bg-white rounded-lg shadow-lg p-6">
                <div class="text-gray-500 text-sm mb-2">Improvement {improvement_icon}</div>
                <div class="text-3xl font-bold {improvement_class}">{improvement:+.1f}</div>
            </div>
            <div class="bg-white rounded-lg shadow-lg p-6">
                <div class="text-gray-500 text-sm mb-2">Issues Resolved</div>
                <div class="text-3xl font-bold text-blue-600">{results['improvement_summary']['critical_issues_resolved']}</div>
            </div>
        </div>
        
        <!-- Chart -->
        <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 class="text-2xl font-semibold mb-6">Quality Score Evolution</h2>
            <canvas id="scoreChart" height="100"></canvas>
        </div>
        
        <!-- Iterations Table -->
        <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 class="text-2xl font-semibold mb-6">Iteration History</h2>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-100">
                        <tr>
                            <th class="px-4 py-3 text-left">Iteration</th>
                            <th class="px-4 py-3 text-left">Score</th>
                            <th class="px-4 py-3 text-left">Critical</th>
                            <th class="px-4 py-3 text-left">Moderate</th>
                            <th class="px-4 py-3 text-left">Minor</th>
                            <th class="px-4 py-3 text-left">Improvements</th>
                        </tr>
                    </thead>
                    <tbody>"""
        
        for iteration in self.iteration_history:
            is_best = iteration.iteration_number == results['best_iteration']['iteration_number']
            row_class = "bg-green-50 font-semibold" if is_best else ""
            
            html += f"""
                        <tr class="{row_class}">
                            <td class="px-4 py-3 border-t">#{iteration.iteration_number} {'⭐' if is_best else ''}</td>
                            <td class="px-4 py-3 border-t">{iteration.score.overall_score:.1f}</td>
                            <td class="px-4 py-3 border-t">{iteration.score.critical_issues}</td>
                            <td class="px-4 py-3 border-t">{iteration.score.moderate_issues}</td>
                            <td class="px-4 py-3 border-t">{iteration.score.minor_issues}</td>
                            <td class="px-4 py-3 border-t">{len(iteration.improvements_applied)}</td>
                        </tr>"""
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('scoreChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: [""" + ", ".join([f"'Iteration {i.iteration_number}'" for i in self.iteration_history]) + """],
                datasets: [{
                    label: 'Quality Score',
                    data: [""" + ", ".join([str(i.score.overall_score) for i in self.iteration_history]) + """],
                    borderColor: 'rgb(147, 51, 234)',
                    backgroundColor: 'rgba(147, 51, 234, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: { display: true, text: 'Score (0-100)' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    </script>
</body>
</html>"""
        
        return html

async def _handle_batch_processing(args, config, reference_manager, tracker):
    """Handle batch processing of multiple documents."""
    if not MULTI_DOC_AVAILABLE:
        logger.error("Multi-document processing not available. Install required dependencies.")
        return 1
    
    # Determine input source
    input_path = args.batch_dir or args.batch_zip
    
    logger.info(f"\n📚 BATCH PROCESSING MODE")
    logger.info(f"   Input: {input_path}")
    logger.info(f"   Parallel: {'Yes' if args.parallel else 'No'}")
    if args.parallel:
        logger.info(f"   Max concurrent: {args.max_concurrent}")
    
    # Initialize processor
    processor = MultiDocumentProcessor(output_base_dir=config.output_dir)
    
    # Discover documents
    try:
        documents = processor.discover_documents(input_path, recursive=True)
        logger.info(f"   Discovered: {len(documents)} documents")
    except Exception as e:
        logger.error(f"Error discovering documents: {e}")
        return 1
    
    if not documents:
        logger.error("No supported documents found")
        return 1
    
    # Create review function with all options
    async def review_function(document_text, document_title, output_directory):
        """Review function for batch processing."""
        # Update config for this document
        doc_config = Config.from_yaml(args.config)
        doc_config.output_dir = output_directory
        
        # Detect language if needed
        output_language = args.output_language
        if not output_language:
            classifier = DocumentClassifier(doc_config)
            doc_type = await classifier.classify_document(document_text)
            output_language = doc_type.detected_language
        
        # Choose orchestrator based on mode
        if args.iterative:
            orchestrator = IterativeReviewOrchestrator(
                doc_config,
                output_language=output_language,
                max_iterations=args.max_iterations,
                target_score=args.target_score,
                interactive=False,  # Disable interactive in batch mode
                enable_python_tools=getattr(args, 'enable_python_tools', False),
                enable_web_research=getattr(args, 'enable_web_research', None),
                disable_web_research=getattr(args, 'disable_web_research', False),
                deep_review=getattr(args, 'deep_review', False)
            )
            result = await orchestrator.execute_iterative_review(document_text, document_title)
        else:
            orchestrator = GenericReviewOrchestrator(
                doc_config,
                output_language=output_language,
                enable_python_tools=getattr(args, 'enable_python_tools', False),
                enable_web_research=getattr(args, 'enable_web_research', None),
                disable_web_research=getattr(args, 'disable_web_research', False),
                deep_review=getattr(args, 'deep_review', False)
            )
            result = await orchestrator.execute_review_process(document_text, document_title)
        
        # Save to database if enabled
        if tracker and result:
            await _save_to_database(tracker, result, doc_config, args)
        
        return result
    
    # Process batch
    batch_result = await processor.process_batch(
        documents,
        review_function,
        parallel=args.parallel,
        max_concurrent=args.max_concurrent
    )
    
    # Generate comparison report
    if batch_result.successful > 1:
        analyzer = CrossDocumentAnalyzer()
        comparison = analyzer.compare_documents(batch_result.results)
        report_path = Path(batch_result.output_directory) / "comparison_report.md"
        analyzer.generate_comparison_report(comparison, str(report_path))
        logger.info(f"   Comparison report: {report_path}")
    
    # Cleanup
    processor.cleanup_temp()
    
    logger.info(f"\n✅ Batch processing complete!")
    logger.info(f"   Total: {batch_result.total_documents}")
    logger.info(f"   Successful: {batch_result.successful}")
    logger.info(f"   Failed: {batch_result.failed}")
    logger.info(f"   Time: {batch_result.processing_time:.1f}s")
    logger.info(f"   Output: {batch_result.output_directory}")
    
    return 0 if batch_result.failed == 0 else 1


async def _handle_resume(args, config, tracker):
    """Handle resuming from a checkpoint."""
    if not tracker:
        logger.error("Resume requires database tracking. Don't use --no-database")
        return 1
    
    logger.info(f"\n💾 RESUME MODE")
    logger.info(f"   Checkpoint: {args.resume}")
    
    # Load checkpoint
    checkpoint_data = tracker.load_checkpoint(args.resume)
    
    if not checkpoint_data:
        logger.error(f"Checkpoint not found or invalid: {args.resume}")
        logger.info("\nAvailable checkpoints:")
        checkpoints = tracker.list_checkpoints()
        if checkpoints:
            for cp in checkpoints[:5]:
                logger.info(f"  - {cp['checkpoint_id']}: {cp['document_title']} (iter {cp['current_iteration']})")
        else:
            logger.info("  No checkpoints available")
        return 1
    
    logger.info(f"   Document: {checkpoint_data['document_title']}")
    logger.info(f"   Iteration: {checkpoint_data['current_iteration']}")
    logger.info(f"   Phase: {checkpoint_data['current_phase']}")
    
    # TODO: Implement actual resume logic
    logger.warning("Resume functionality is partially implemented - continuing with fresh review")
    
    # For now, just start fresh review with same document
    # Full implementation would restore state and continue
    
    return 0


async def _save_to_database(tracker, result, config, args):
    """Save review result to database."""
    try:
        # Extract score from result
        final_score = result.get('final_score') or result.get('score', 0)
        
        # Create version record
        version = DocumentVersion(
            version_id=f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            document_hash=tracker.compute_document_hash(str(result)),
            document_title=result.get('title', 'Untitled'),
            project_name=args.project,
            review_date=datetime.now().isoformat(),
            score=final_score,
            iteration_number=result.get('iterations', 1),
            file_path=args.document_path or "batch",
            output_directory=config.output_dir,
            review_mode="iterative" if args.iterative else "standard",
            language=args.output_language or "auto-detected",
            improvements_applied=len(result.get('improvements', [])),
            critical_issues=result.get('critical_issues', 0),
            moderate_issues=result.get('moderate_issues', 0),
            minor_issues=result.get('minor_issues', 0),
            agent_count=len(result.get('reviews', [])),
            metadata=json.dumps({
                'target_score': args.target_score if args.iterative else None,
                'interactive': args.interactive,
                'with_references': bool(args.references)
            })
        )
        
        tracker.save_version(version)
        logger.debug(f"Saved to database: {version.version_id}")
        
    except Exception as e:
        logger.warning(f"Failed to save to database: {e}")


def _open_file_dialogs():
    """
    Open GUI dialogs to select documents interactively.
    Returns dict with selected paths or None if user cancels.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except ImportError:
        print("⚠️ GUI dialogs not available (tkinter not installed)")
        return None
    
    # Create hidden root window
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    print("\n" + "="*70)
    print("📂 DOCUMENT SELECTION - Interactive Mode")
    print("="*70)
    print("\nA file dialog window will open to select your document.")
    print("Press ENTER to continue or type 'skip' to use command-line arguments...")
    
    user_input = input("> ").strip().lower()
    if user_input == 'skip':
        root.destroy()
        return None
    
    # Select main document
    print("\n📄 Select the main document to review...")
    main_doc = filedialog.askopenfilename(
        title="Select Document to Review",
        filetypes=[
            ("All Documents", "*.pdf *.txt *.md *.docx *.doc"),
            ("PDF Files", "*.pdf"),
            ("Text Files", "*.txt *.md"),
            ("Word Documents", "*.docx *.doc"),
            ("All Files", "*.*")
        ]
    )
    
    if not main_doc:
        print("❌ No document selected. Exiting...")
        root.destroy()
        return None
    
    print(f"✅ Selected: {Path(main_doc).name}")
    
    # Ask for reference documents
    print("\n" + "-"*70)
    print("📚 Do you want to add reference documents?")
    print("   (templates, guidelines, examples, data, etc.)")
    print("\nPress ENTER to skip, or type 'yes' to select references...")
    
    user_input = input("> ").strip().lower()
    
    references = []
    reference_type = "example"
    
    if user_input in ['yes', 'y', 'si', 'sì']:
        print("\n📋 What type of reference documents are these?")
        print("  1. Template (document structure to follow)")
        print("  2. Guideline (rules and requirements)")
        print("  3. Example (sample documents)")
        print("  4. Data (supporting data/statistics)")
        print("  5. Style Guide (formatting/style rules)")
        print("\nEnter number [1-5] or press ENTER for 'Example':")
        
        ref_type_input = input("> ").strip()
        ref_types = {
            '1': 'template',
            '2': 'guideline',
            '3': 'example',
            '4': 'data',
            '5': 'style_guide'
        }
        reference_type = ref_types.get(ref_type_input, 'example')
        
        print(f"\n📂 Select reference documents (you can select multiple files)...")
        print("   Hold Cmd (Mac) or Ctrl (Windows/Linux) to select multiple files")
        
        ref_files = filedialog.askopenfilenames(
            title=f"Select Reference Documents ({reference_type})",
            filetypes=[
                ("All Documents", "*.pdf *.txt *.md *.docx *.doc *.xlsx *.xls"),
                ("PDF Files", "*.pdf"),
                ("Text Files", "*.txt *.md"),
                ("Word Documents", "*.docx *.doc"),
                ("Excel Files", "*.xlsx *.xls"),
                ("All Files", "*.*")
            ]
        )
        
        if ref_files:
            references = list(ref_files)
            print(f"✅ Selected {len(references)} reference document(s):")
            for ref in references:
                print(f"   - {Path(ref).name}")
        else:
            print("   No references selected.")
    
    # Ask for batch directory
    print("\n" + "-"*70)
    print("📁 Do you want to process a directory of documents (batch mode)?")
    print("   This will process all documents in a folder instead of a single file.")
    print("\nPress ENTER to skip, or type 'yes' to select a directory...")
    
    user_input = input("> ").strip().lower()
    
    batch_dir = None
    if user_input in ['yes', 'y', 'si', 'sì']:
        print("\n📂 Select directory containing documents...")
        batch_dir = filedialog.askdirectory(
            title="Select Directory with Documents to Review"
        )
        if batch_dir:
            print(f"✅ Selected directory: {Path(batch_dir).name}")
            main_doc = None  # Override single document with batch
        else:
            print("   No directory selected.")
    
    root.destroy()
    
    print("\n" + "="*70)
    print("✅ File selection complete!")
    print("="*70 + "\n")
    
    return {
        'document_path': main_doc,
        'references': references,
        'reference_type': reference_type,
        'batch_dir': batch_dir
    }


def main():
    """Main function for generic document review."""
    import argparse
    
    # Check if running without arguments - open GUI
    import sys
    open_gui = len(sys.argv) == 1  # No arguments provided
    
    selected_files = None
    if open_gui:
        selected_files = _open_file_dialogs()
        if selected_files is None and len(sys.argv) == 1:
            # User skipped or cancelled, and no command-line args
            print("No files selected. Exiting...")
            return 1
    
    parser = argparse.ArgumentParser(
        description="Generic Document Review System v3.0 - Enterprise-grade document analysis"
    )
    
    # Document input (mutually exclusive groups)
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument("document_path", nargs='?', help="Path to single document to review")
    input_group.add_argument("--batch-dir", help="Directory with multiple documents to review")
    input_group.add_argument("--batch-zip", help="ZIP file with multiple documents to review")
    input_group.add_argument("--resume", help="Resume from checkpoint ID")
    
    # Basic options
    parser.add_argument("--title", help="Document title (optional)")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--output-dir", help="Override output directory")
    parser.add_argument("--output-language", help="Language for review output (e.g., Italian, English, Spanish)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    # Iterative mode options
    parser.add_argument("--iterative", action="store_true", 
                       help="Enable iterative improvement mode (agents propose changes, document is improved, repeat)")
    parser.add_argument("--max-iterations", type=int, default=3,
                       help="Maximum number of iterations (default: 3)")
    parser.add_argument("--target-score", type=float, default=85.0,
                       help="Target quality score to achieve (0-100, default: 85.0)")
    parser.add_argument("--interactive", action="store_true",
                       help="Enable interactive mode (system may ask for additional information or files)")
    parser.add_argument("--deep-review", action="store_true",
                       help="Enable deep review with Tier 3 specialists (20+ additional ultra-specialized agents)")
    
    # Reference documents (context)
    parser.add_argument("--reference", dest="references", action="append",
                       help="Reference document/directory/ZIP (can be used multiple times)")
    parser.add_argument("--reference-type", default="example",
                       choices=["template", "guideline", "example", "data", "style_guide"],
                       help="Type of reference documents (default: example)")
    parser.add_argument("--reference-max-chars", type=int, default=50000,
                       help="Max characters from references to include (default: 50000)")
    
    # Batch processing options
    parser.add_argument("--parallel", action="store_true",
                       help="Process documents in parallel (batch mode only)")
    parser.add_argument("--max-concurrent", type=int, default=3,
                       help="Max concurrent processes in parallel mode (default: 3)")
    
    # Project organization
    parser.add_argument("--project", help="Project name for organizing related reviews")
    
    # Database & tracking
    parser.add_argument("--db-path", default="document_reviews.db",
                       help="Path to database file (default: document_reviews.db)")
    parser.add_argument("--no-database", action="store_true",
                       help="Disable database tracking")
    
    # Progress & notifications
    parser.add_argument("--no-progress", action="store_true",
                       help="Disable progress bars")
    parser.add_argument("--no-notifications", action="store_true",
                       help="Disable system notifications")
    
    # Agent tools
    parser.add_argument("--enable-python-tools", action="store_true",
                       help="Enable real Python execution for data validator (requires agent_tools)")
    parser.add_argument("--tools-for-all", action="store_true",
                       help="Enable tools for all agents (not just data validator)")
    parser.add_argument("--enable-web-research", action="store_true",
                       help="Force enable web search agents (automatic by default for documents with verifiable claims)")
    parser.add_argument("--disable-web-research", action="store_true",
                       help="Disable automatic web research agent selection")
    
    args = parser.parse_args()
    
    # Override args with GUI-selected files if available
    if selected_files:
        if selected_files['batch_dir']:
            args.batch_dir = selected_files['batch_dir']
            args.document_path = None
        elif selected_files['document_path']:
            args.document_path = selected_files['document_path']
        
        if selected_files['references']:
            args.references = selected_files['references']
            args.reference_type = selected_files['reference_type']
        
        # Enable interactive mode by default when using GUI
        if not args.iterative:
            print("\n💡 GUI Mode: Would you like to enable iterative improvement?")
            print("   (The system will improve the document through multiple iterations)")
            print("\nType 'yes' to enable, or press ENTER to skip:")
            user_input = input("> ").strip().lower()
            if user_input in ['yes', 'y', 'si', 'sì']:
                args.iterative = True
                args.interactive = True
                print("✅ Iterative mode enabled with interactive feedback")
                
                # Ask for max iterations
                print("\nHow many iterations? (default: 3, press ENTER to use default):")
                iter_input = input("> ").strip()
                if iter_input.isdigit():
                    args.max_iterations = int(iter_input)
                    print(f"✅ Max iterations set to: {args.max_iterations}")
        
        # Always enable Python tools in GUI mode
        if not args.enable_python_tools:
            args.enable_python_tools = True
            print("\n✅ Python tools enabled for advanced data validation")
    
    # Setup logging
    global logger
    logger = setup_logging(args.log_level)
    
    try:
        # Load configuration
        config = Config.from_yaml(args.config)
        if args.output_dir:
            config.output_dir = args.output_dir
        config.validate()
        
        # System health check
        health = system_health_check(config)
        logger.info(f"System health: {health}")
        
        # Initialize database tracker if enabled
        tracker = None
        if DATABASE_TRACKING_AVAILABLE and not args.no_database:
            tracker = DocumentTracker(args.db_path)
            logger.info(f"Database tracking enabled: {args.db_path}")
        
        # Initialize reference context if provided
        reference_manager = None
        if REFERENCE_CONTEXT_AVAILABLE and args.references:
            reference_manager = ReferenceContextManager()
            for ref_path in args.references:
                loaded = reference_manager.load_references(
                    ref_path,
                    document_type=args.reference_type,
                    description=f"{args.reference_type.capitalize()} reference"
                )
                logger.info(f"Loaded {loaded} reference documents from {ref_path}")
            
            if reference_manager.references:
                summary = reference_manager.get_summary()
                logger.info(f"Total references: {summary['total_references']}")
        
        # Check for batch processing mode
        if args.batch_dir or args.batch_zip:
            return asyncio.run(_handle_batch_processing(args, config, reference_manager, tracker))
        
        # Check for resume mode
        if args.resume:
            return asyncio.run(_handle_resume(args, config, tracker))
        
        # Single document mode
        if not args.document_path:
            parser.error("document_path is required unless using --batch-dir, --batch-zip, or --resume")
        
        # Read document
        file_manager = FileManager(config.output_dir)
        if args.document_path.lower().endswith(".pdf"):
            document_text = file_manager.extract_text_from_pdf(args.document_path)
        else:
            document_text = file_manager.read_paper(args.document_path)
        
        if not document_text:
            logger.error("Failed to read document")
            return 1
        
        # Get title
        title = args.title or Path(args.document_path).stem
        
        # Create unique output directory with document name + timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length and replace spaces
        unique_output_dir = f"{config.output_dir}/{safe_title}_{timestamp}"
        
        # Update config with unique directory
        config.output_dir = unique_output_dir
        Path(unique_output_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Document loaded: {title}")
        logger.info(f"Length: {len(document_text):,} characters")
        logger.info(f"Output directory: {unique_output_dir}")
        
        # Determine output language
        output_language = args.output_language
        
        if not output_language:
            # Quick classification to detect language
            logger.info("\nDetecting document language...")
            classifier = DocumentClassifier(config)
            doc_type = asyncio.run(classifier.classify_document(document_text))
            detected_lang = doc_type.detected_language
            lang_confidence = doc_type.language_confidence
            
            logger.info(f"Detected language: {detected_lang} (confidence: {lang_confidence:.0%})")
            
            # Ask user for output language
            print(f"\n{'='*60}")
            print(f"Document language detected: {detected_lang}")
            print(f"{'='*60}")
            print("\nIn which language would you like the reviews?")
            print("Opzioni comuni / Common options:")
            print("  - Italian (Italiano)")
            print("  - English (Inglese)")
            print("  - Spanish (Español)")
            print("  - French (Français)")
            print("  - German (Deutsch)")
            print(f"\nPress ENTER to use detected language ({detected_lang}), or type your preferred language:")
            
            user_input = input("> ").strip()
            output_language = user_input if user_input else detected_lang
            
            logger.info(f"Output language set to: {output_language}")
        
        # Initialize progress tracking if enabled
        progress_orchestrator = None
        if PROGRESS_TRACKING_AVAILABLE and not args.no_progress:
            mode = "iterative" if args.iterative else "standard"
            if args.interactive:
                mode = "interactive"
            
            progress_orchestrator = ReviewProgressOrchestrator(
                document_title=title,
                mode=mode,
                max_iterations=args.max_iterations if args.iterative else 1,
                enable_notifications=not args.no_notifications
            )
            progress_orchestrator.start()
        
        # Get reference context if available
        reference_context = ""
        if reference_manager:
            reference_context = reference_manager.get_context_for_review(
                max_total_chars=args.reference_max_chars
            )
            if reference_context:
                logger.info(f"📋 Using {len(reference_manager.references)} reference documents as context")
        
        try:
            # Choose review mode
            if args.iterative:
                # Iterative mode: improve document through multiple iterations
                logger.info(f"\n🔄 ITERATIVE MODE ENABLED")
                logger.info(f"   Max iterations: {args.max_iterations}")
                logger.info(f"   Target score: {args.target_score}/100")
                if args.interactive:
                    logger.info(f"   💬 Interactive mode: ON (may request additional info)")
                if reference_context:
                    logger.info(f"   📋 Reference context: {len(reference_context)} chars")
                
                orchestrator = IterativeReviewOrchestrator(
                    config, 
                    output_language=output_language,
                    max_iterations=args.max_iterations,
                    target_score=args.target_score,
                    interactive=args.interactive,
                    enable_python_tools=args.enable_python_tools,
                    reference_context=reference_context,
                    enable_web_research=args.enable_web_research if args.enable_web_research else None,
                    disable_web_research=args.disable_web_research,
                    deep_review=args.deep_review
                )
                
                results = asyncio.run(orchestrator.execute_iterative_review(document_text, title))
                
                # Complete progress
                if progress_orchestrator:
                    final_score = results.get('best_iteration', {}).get('score', {}).get('overall_score', 0)
                    progress_orchestrator.complete(final_score)
                
                logger.info(f"\n✅ Iterative review completed successfully!")
                logger.info(f"📈 Quality improvement: {results['improvement_summary']['score_improvement']:+.1f} points")
                logger.info(f"⭐ Best iteration: #{results['best_iteration']['iteration_number']}")
                logger.info(f"📁 Results saved in: {config.output_dir}")
                logger.info(f"\n💡 Open iterative_dashboard_*.html to see evolution!")
            else:
                # Standard mode: single review
                orchestrator = GenericReviewOrchestrator(
                    config, 
                    output_language=output_language,
                    enable_python_tools=args.enable_python_tools,
                    reference_context=reference_context,
                    enable_web_research=args.enable_web_research if args.enable_web_research else None,
                    disable_web_research=args.disable_web_research,
                    deep_review=args.deep_review
                )
                
                results = asyncio.run(orchestrator.execute_review_process(document_text, title))
                
                # Complete progress
                if progress_orchestrator:
                    final_score = results.get('final_score', 0)
                    progress_orchestrator.complete(final_score)
                
                logger.info(f"\n✅ Review completed successfully!")
                logger.info(f"Results saved in: {config.output_dir}")
                logger.info(f"\n💡 Tip: Use --iterative for automatic document improvement!")
            
            # Save to database if enabled
            if tracker:
                asyncio.run(_save_to_database(tracker, results, config, args))
                logger.info(f"💾 Saved to database: {args.db_path}")
            
            return 0
            
        except Exception as e:
            if progress_orchestrator:
                progress_orchestrator.notify_error(str(e))
            raise
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

