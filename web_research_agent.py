"""
Web Research Agent
Uses OpenAI Responses API with native web_search tool to verify facts and find information online.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    WEB_RESEARCH_AVAILABLE = True
except ImportError:
    WEB_RESEARCH_AVAILABLE = False
    logger.warning("OpenAI not available - web research features disabled")


@dataclass
class WebSearchResult:
    """Result from web search with citations."""
    text: str
    citations: List[str]
    sources_count: int


class WebResearchAgent:
    """
    Agent that uses OpenAI Responses API with native web_search tool.
    Can search the web, verify facts, and provide cited information.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-5"):
        """
        Initialize web research agent.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-5, gpt-5-mini, gpt-5-nano, gpt-4o, etc.)
        """
        if not WEB_RESEARCH_AVAILABLE:
            raise ImportError("OpenAI library required for web research")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model  # Use model as-is, no mapping
        self.conversation_id = None  # For multi-turn conversations
        
        logger.info(f"WebResearchAgent initialized with model {self.model}")
    
    def search(self, query: str, system_prompt: Optional[str] = None) -> WebSearchResult:
        """
        Perform web search and return results with citations.
        
        Args:
            query: Search query or question
            system_prompt: Optional system prompt to guide the search
        
        Returns:
            WebSearchResult with text and citations
        """
        if not system_prompt:
            system_prompt = (
                "You are a research assistant. When using web search, always cite sources "
                "at the end of your response. Be accurate and fact-based."
            )
        
        try:
            logger.info(f"🔍 Web search starting: {query[:100]}...")
            logger.debug(f"Using model: {self.model}")
            
            # Call Responses API with web_search tool
            logger.debug("Calling client.responses.create()...")
            resp = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": system_prompt}]
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": query}]
                    }
                ],
                tools=[{"type": "web_search"}],  # Enable native web search
            )
            
            logger.debug(f"Response received, ID: {resp.id}")
            
            # Store conversation ID for follow-ups
            self.conversation_id = resp.id
            
            # Extract message and citations
            logger.debug(f"Response output type: {type(resp.output)}")
            logger.debug(f"Response output length: {len(resp.output) if resp.output else 0}")
            
            msg = next((o for o in resp.output if getattr(o, "type", None) == "message"), None)
            
            if not msg:
                logger.warning("No message in response output!")
                logger.debug(f"Output items: {[getattr(o, 'type', None) for o in resp.output]}")
            
            text = ""
            urls = []
            
            if msg and msg.content:
                logger.debug(f"Message content length: {len(msg.content)}")
                block = msg.content[0]
                text = getattr(block, "text", "") or getattr(block, "value", "")
                logger.debug(f"Extracted text length: {len(text)}")
                
                # Extract URL citations from annotations
                annotations = getattr(block, "annotations", []) or []
                logger.debug(f"Annotations found: {len(annotations)}")
                urls = [a.url for a in annotations if getattr(a, "type", "") == "url_citation"]
                logger.debug(f"URL citations extracted: {len(urls)}")
            else:
                logger.warning("No content in message!")
            
            result = WebSearchResult(
                text=text,
                citations=urls,
                sources_count=len(urls)
            )
            
            logger.info(f"✅ Web search completed: {result.sources_count} sources found, {len(text)} chars")
            if urls:
                logger.info(f"📚 Sources: {urls[:3]}{'...' if len(urls) > 3 else ''}")
            
            return result
            
        except Exception as e:
            import traceback
            logger.error(f"❌ Web search failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return WebSearchResult(
                text=f"Web search failed: {str(e)}\n\nPlease check that:\n1. Responses API is available for your account\n2. Model {self.model} supports web_search\n3. API key has necessary permissions",
                citations=[],
                sources_count=0
            )
    
    def follow_up(self, query: str) -> WebSearchResult:
        """
        Continue conversation with follow-up query, maintaining context.
        
        Args:
            query: Follow-up question or request
        
        Returns:
            WebSearchResult with text and citations
        """
        if not self.conversation_id:
            logger.warning("No previous conversation, starting new search")
            return self.search(query)
        
        try:
            logger.info(f"Follow-up search: {query[:100]}...")
            
            # Continue conversation using previous_response_id
            resp = self.client.responses.create(
                model=self.model,
                input=query,
                previous_response_id=self.conversation_id,  # Maintains context
                tools=[{"type": "web_search"}],
            )
            
            # Update conversation ID
            self.conversation_id = resp.id
            
            # Extract message and citations
            msg = next((o for o in resp.output if getattr(o, "type", None) == "message"), None)
            
            text = ""
            urls = []
            
            if msg and msg.content:
                block = msg.content[0]
                text = getattr(block, "text", "") or getattr(block, "value", "")
                annotations = getattr(block, "annotations", []) or []
                urls = [a.url for a in annotations if getattr(a, "type", "") == "url_citation"]
            
            result = WebSearchResult(
                text=text,
                citations=urls,
                sources_count=len(urls)
            )
            
            logger.info(f"Follow-up completed: {result.sources_count} sources found")
            
            return result
            
        except Exception as e:
            logger.error(f"Follow-up search failed: {e}")
            return WebSearchResult(
                text=f"Follow-up search failed: {str(e)}",
                citations=[],
                sources_count=0
            )
    
    def verify_claim(self, claim: str, context: str = "") -> Dict[str, Any]:
        """
        Verify a specific claim using web search.
        
        Args:
            claim: Claim to verify
            context: Optional context about the claim
        
        Returns:
            Dict with verification result, confidence, and citations
        """
        system_prompt = (
            "You are a fact-checking expert. Verify claims using web search. "
            "Return your assessment as: VERIFIED, PARTIALLY VERIFIED, UNVERIFIED, or FALSE. "
            "Always provide sources and explain your reasoning."
        )
        
        query = f"Verify this claim: {claim}"
        if context:
            query += f"\n\nContext: {context}"
        
        result = self.search(query, system_prompt)
        
        # Parse verification result
        text_lower = result.text.lower()
        
        if "verified" in text_lower and "partially" not in text_lower and "unverified" not in text_lower:
            status = "VERIFIED"
        elif "partially verified" in text_lower:
            status = "PARTIALLY_VERIFIED"
        elif "false" in text_lower or "incorrect" in text_lower:
            status = "FALSE"
        else:
            status = "UNVERIFIED"
        
        return {
            "claim": claim,
            "status": status,
            "explanation": result.text,
            "citations": result.citations,
            "sources_count": result.sources_count
        }


def create_web_researcher_instructions(document_type: str = "document") -> str:
    """
    Get instructions for web researcher agent.
    
    Args:
        document_type: Type of document being reviewed
    
    Returns:
        Instructions string
    """
    return f"""You are a Web Research Specialist reviewing this {document_type}.

Your task is to verify factual claims, statistics, and information using web search.

WHAT TO CHECK:
1. **Factual Claims**: Any statements presented as facts
2. **Statistics & Data**: Numbers, percentages, growth rates, market data
3. **Citations**: Verify that cited sources exist and are accurate
4. **Current Information**: Check if information is up-to-date
5. **Technical Claims**: Verify technical specifications, methodologies

PROCESS:
1. Identify key claims that can be verified
2. Search the web to verify each claim
3. Compare document claims with found sources
4. Rate accuracy: VERIFIED ✅, PARTIALLY VERIFIED ⚠️, UNVERIFIED ❓, FALSE ❌

OUTPUT FORMAT:
For each verified claim:
- **Claim**: [Quote from document]
- **Status**: [VERIFIED/PARTIALLY VERIFIED/UNVERIFIED/FALSE]
- **Finding**: [What you found from web search]
- **Sources**: [List URLs found]

IMPORTANT:
- Use web search actively - don't just rely on your training data
- Provide specific URLs as evidence
- If information is outdated, suggest current data
- Be thorough but focus on the most important claims

Provide a comprehensive fact-checking report with all sources cited."""


def create_fact_checker_instructions(language: str = "English") -> str:
    """
    Get instructions for fact checker agent.
    
    Args:
        language: Output language
    
    Returns:
        Instructions string
    """
    return f"""You are a Fact-Checking Expert with web search capabilities.

Your task is to verify the accuracy of information in the document using online sources.

VERIFICATION PROCESS:
1. **Identify Verifiable Claims**
   - Numbers and statistics
   - Historical facts and dates
   - Technical specifications
   - Market data and trends
   - Research findings

2. **Web Search Verification**
   - Search for authoritative sources
   - Cross-reference multiple sources
   - Check publication dates
   - Verify data accuracy

3. **Assessment**
   ✅ VERIFIED: Claim matches reliable sources
   ⚠️ PARTIALLY VERIFIED: Claim is mostly accurate but has minor issues
   ❓ UNVERIFIED: Cannot find supporting sources
   ❌ FALSE: Claim contradicts reliable sources

4. **Documentation**
   - Always cite your sources (URLs)
   - Explain any discrepancies
   - Suggest corrections when needed

OUTPUT (in {language}):
Provide a detailed fact-checking report with:
- List of verified claims with sources
- List of questionable claims with concerns
- List of false claims with corrections
- Overall accuracy assessment
- Recommendations for improvements

Be thorough and cite all sources!"""


# Integration helper for existing agent system
def execute_web_research_agent(api_key: str, model: str, message: str, 
                               agent_type: str = "researcher") -> str:
    """
    Execute web research agent and return formatted response.
    
    Args:
        api_key: OpenAI API key
        model: Model to use
        message: Agent task/message
        agent_type: "researcher" or "fact_checker"
    
    Returns:
        Formatted response with citations
    """
    if not WEB_RESEARCH_AVAILABLE:
        return "⚠️ Web research not available - OpenAI library required"
    
    try:
        agent = WebResearchAgent(api_key, model)
        result = agent.search(message)
        
        # Format response with citations
        response = result.text
        
        if result.citations:
            response += "\n\n**📚 Sources:**\n"
            for i, url in enumerate(result.citations, 1):
                response += f"{i}. {url}\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Web research agent failed: {e}")
        return f"⚠️ Web research failed: {str(e)}"


# Example usage
if __name__ == "__main__":
    import sys
    
    # Test web research
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        sys.exit(1)
    
    agent = WebResearchAgent(api_key, model="gpt-4o")
    
    # Example 1: General search
    print("=" * 70)
    print("TEST 1: General Web Search")
    print("=" * 70)
    
    result = agent.search(
        "What are the latest trends in LED market in Europe for 2025? Provide 5 key points with sources."
    )
    
    print(result.text)
    if result.citations:
        print("\n📚 Sources:")
        for url in result.citations:
            print(f"  - {url}")
    
    # Example 2: Fact verification
    print("\n" + "=" * 70)
    print("TEST 2: Fact Verification")
    print("=" * 70)
    
    verification = agent.verify_claim(
        "The global LED market is expected to reach $100 billion by 2025",
        "Market research report claim"
    )
    
    print(f"Claim: {verification['claim']}")
    print(f"Status: {verification['status']}")
    print(f"\n{verification['explanation']}")
    if verification['citations']:
        print("\n📚 Sources:")
        for url in verification['citations']:
            print(f"  - {url}")

