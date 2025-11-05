#!/usr/bin/env python3
"""
Semantic Scholar API Integration for Academic Research

Provides free access to academic papers database with:
- Paper search by keywords
- Citation data
- Author information
- Paper recommendations
- Full metadata

API Documentation: https://api.semanticscholar.org/
"""

import os
import logging
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

# Semantic Scholar API endpoint (no auth required!)
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"

@dataclass
class AcademicPaper:
    """Academic paper metadata from Semantic Scholar"""
    paper_id: str
    title: str
    authors: List[str]
    year: Optional[int]
    citation_count: int
    abstract: Optional[str]
    url: Optional[str]
    doi: Optional[str]
    arxiv_id: Optional[str]
    venue: Optional[str]
    fields_of_study: List[str]
    influential_citation_count: int = 0
    
    def __str__(self) -> str:
        """Format paper for display"""
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += " et al."
        
        year_str = f"({self.year})" if self.year else ""
        citations_str = f"[{self.citation_count} citations]"
        
        result = f"{authors_str} {year_str}. {self.title}. {citations_str}"
        
        if self.venue:
            result += f"\n  Published in: {self.venue}"
        if self.doi:
            result += f"\n  DOI: {self.doi}"
        elif self.arxiv_id:
            result += f"\n  arXiv: {self.arxiv_id}"
        if self.url:
            result += f"\n  URL: {self.url}"
        
        return result


class SemanticScholarAPI:
    """Interface to Semantic Scholar API for academic research"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Semantic Scholar API client.
        
        Args:
            api_key: Optional API key for higher rate limits (not required)
        """
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"x-api-key": self.api_key})
        
        # Rate limiting (1 request per second for free tier, 10/sec with API key)
        self.rate_limit_delay = 0.1 if self.api_key else 1.0
        self.last_request_time = 0
        
        logger.info(f"✅ Semantic Scholar API initialized {'with API key' if self.api_key else '(free tier)'}")
    
    def _rate_limit(self):
        """Implement rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def search_papers(
        self,
        query: str,
        limit: int = 10,
        fields: Optional[List[str]] = None,
        year_range: Optional[tuple] = None
    ) -> List[AcademicPaper]:
        """
        Search for academic papers by query.
        
        Args:
            query: Search query (keywords, phrases)
            limit: Maximum number of results (max 100)
            fields: List of fields to retrieve (default: all)
            year_range: Optional tuple (min_year, max_year)
        
        Returns:
            List of AcademicPaper objects
        """
        self._rate_limit()
        
        if fields is None:
            fields = [
                "paperId", "title", "authors", "year", "citationCount",
                "abstract", "url", "externalIds", "venue", "fieldsOfStudy",
                "influentialCitationCount"
            ]
        
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": ",".join(fields)
        }
        
        if year_range:
            params["year"] = f"{year_range[0]}-{year_range[1]}"
        
        try:
            response = self.session.get(
                f"{SEMANTIC_SCHOLAR_API}/paper/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for item in data.get("data", []):
                try:
                    paper = self._parse_paper(item)
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Failed to parse paper: {e}")
                    continue
            
            logger.info(f"📚 Found {len(papers)} papers for query: '{query}'")
            return papers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Semantic Scholar API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching papers: {e}")
            return []
    
    def get_paper_by_id(self, paper_id: str, fields: Optional[List[str]] = None) -> Optional[AcademicPaper]:
        """
        Get paper details by Semantic Scholar ID, DOI, or arXiv ID.
        
        Args:
            paper_id: Paper identifier (S2 ID, DOI, or arXiv ID)
            fields: List of fields to retrieve
        
        Returns:
            AcademicPaper object or None
        """
        self._rate_limit()
        
        if fields is None:
            fields = [
                "paperId", "title", "authors", "year", "citationCount",
                "abstract", "url", "externalIds", "venue", "fieldsOfStudy",
                "influentialCitationCount"
            ]
        
        try:
            response = self.session.get(
                f"{SEMANTIC_SCHOLAR_API}/paper/{paper_id}",
                params={"fields": ",".join(fields)},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return self._parse_paper(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get paper {paper_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting paper: {e}")
            return None
    
    def get_paper_citations(self, paper_id: str, limit: int = 10) -> List[AcademicPaper]:
        """
        Get papers that cite the given paper.
        
        Args:
            paper_id: Paper identifier
            limit: Maximum number of citations to retrieve
        
        Returns:
            List of AcademicPaper objects
        """
        self._rate_limit()
        
        try:
            response = self.session.get(
                f"{SEMANTIC_SCHOLAR_API}/paper/{paper_id}/citations",
                params={"limit": limit, "fields": "paperId,title,authors,year,citationCount"},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for item in data.get("data", []):
                citing_paper = item.get("citingPaper")
                if citing_paper:
                    try:
                        paper = self._parse_paper(citing_paper)
                        papers.append(paper)
                    except Exception:
                        continue
            
            return papers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get citations for {paper_id}: {e}")
            return []
    
    def get_paper_references(self, paper_id: str, limit: int = 10) -> List[AcademicPaper]:
        """
        Get papers referenced by the given paper.
        
        Args:
            paper_id: Paper identifier
            limit: Maximum number of references to retrieve
        
        Returns:
            List of AcademicPaper objects
        """
        self._rate_limit()
        
        try:
            response = self.session.get(
                f"{SEMANTIC_SCHOLAR_API}/paper/{paper_id}/references",
                params={"limit": limit, "fields": "paperId,title,authors,year,citationCount"},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for item in data.get("data", []):
                cited_paper = item.get("citedPaper")
                if cited_paper:
                    try:
                        paper = self._parse_paper(cited_paper)
                        papers.append(paper)
                    except Exception:
                        continue
            
            return papers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get references for {paper_id}: {e}")
            return []
    
    def get_related_papers(self, paper_id: str, limit: int = 10) -> List[AcademicPaper]:
        """
        Get papers related to the given paper.
        
        Args:
            paper_id: Paper identifier
            limit: Maximum number of related papers
        
        Returns:
            List of AcademicPaper objects
        """
        self._rate_limit()
        
        try:
            # Use recommendations endpoint
            response = self.session.get(
                f"{SEMANTIC_SCHOLAR_API}/paper/{paper_id}/related",
                params={"limit": limit},
                timeout=30
            )
            
            if response.status_code == 404:
                # Fallback: search by paper title/keywords
                paper = self.get_paper_by_id(paper_id, fields=["title", "fieldsOfStudy"])
                if paper and paper.title:
                    return self.search_papers(paper.title, limit=limit)
                return []
            
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for item in data.get("data", []):
                try:
                    paper = self._parse_paper(item)
                    papers.append(paper)
                except Exception:
                    continue
            
            return papers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get related papers for {paper_id}: {e}")
            return []
    
    def _parse_paper(self, data: Dict[str, Any]) -> AcademicPaper:
        """Parse paper data from API response"""
        # Extract authors
        authors = []
        for author in data.get("authors", []):
            name = author.get("name")
            if name:
                authors.append(name)
        
        # Extract external IDs
        external_ids = data.get("externalIds", {}) or {}
        doi = external_ids.get("DOI")
        arxiv_id = external_ids.get("ArXiv")
        
        # Build URL
        url = data.get("url")
        if not url and doi:
            url = f"https://doi.org/{doi}"
        elif not url and arxiv_id:
            url = f"https://arxiv.org/abs/{arxiv_id}"
        
        return AcademicPaper(
            paper_id=data.get("paperId", ""),
            title=data.get("title", "Untitled"),
            authors=authors,
            year=data.get("year"),
            citation_count=data.get("citationCount", 0),
            abstract=data.get("abstract"),
            url=url,
            doi=doi,
            arxiv_id=arxiv_id,
            venue=data.get("venue"),
            fields_of_study=data.get("fieldsOfStudy", []) or [],
            influential_citation_count=data.get("influentialCitationCount", 0)
        )


def format_papers_for_agent(papers: List[AcademicPaper], max_papers: int = 10) -> str:
    """
    Format papers for inclusion in agent context.
    
    Args:
        papers: List of AcademicPaper objects
        max_papers: Maximum number of papers to include
    
    Returns:
        Formatted string with paper details
    """
    if not papers:
        return "No relevant academic papers found."
    
    # Sort by citation count (most cited first)
    sorted_papers = sorted(papers, key=lambda p: p.citation_count, reverse=True)[:max_papers]
    
    result = f"## Academic Research Results ({len(sorted_papers)} papers)\n\n"
    
    for i, paper in enumerate(sorted_papers, 1):
        result += f"### [{i}] {paper.title}\n"
        
        # Authors
        authors_str = ", ".join(paper.authors[:5])
        if len(paper.authors) > 5:
            authors_str += " et al."
        result += f"**Authors:** {authors_str}\n"
        
        # Year and citations
        year_str = f" ({paper.year})" if paper.year else ""
        result += f"**Published:** {paper.venue or 'N/A'}{year_str}\n"
        result += f"**Citations:** {paper.citation_count} (Influential: {paper.influential_citation_count})\n"
        
        # Fields of study
        if paper.fields_of_study:
            result += f"**Fields:** {', '.join(paper.fields_of_study[:5])}\n"
        
        # Links
        if paper.doi:
            result += f"**DOI:** [{paper.doi}](https://doi.org/{paper.doi})\n"
        elif paper.arxiv_id:
            result += f"**arXiv:** [{paper.arxiv_id}](https://arxiv.org/abs/{paper.arxiv_id})\n"
        elif paper.url:
            result += f"**URL:** {paper.url}\n"
        
        # Abstract (truncated)
        if paper.abstract:
            abstract = paper.abstract[:300]
            if len(paper.abstract) > 300:
                abstract += "..."
            result += f"**Abstract:** {abstract}\n"
        
        result += "\n"
    
    return result


# Test function
def test_semantic_scholar():
    """Test Semantic Scholar API functionality"""
    print("🧪 Testing Semantic Scholar API...\n")
    
    api = SemanticScholarAPI()
    
    # Test 1: Search papers
    print("📚 Test 1: Searching papers about 'transformers in NLP'...")
    papers = api.search_papers("transformers in NLP", limit=5, year_range=(2020, 2024))
    print(f"Found {len(papers)} papers")
    if papers:
        print(f"\nTop result:\n{papers[0]}\n")
    
    # Test 2: Get paper by DOI
    print("\n📄 Test 2: Getting paper by DOI...")
    bert_paper = api.get_paper_by_id("10.18653/v1/N19-1423")  # BERT paper
    if bert_paper:
        print(f"Found: {bert_paper.title}")
        print(f"Citations: {bert_paper.citation_count}")
    
    # Test 3: Format for agent
    print("\n📝 Test 3: Formatting papers for agent context...")
    formatted = format_papers_for_agent(papers, max_papers=3)
    print(formatted[:500] + "...")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # Run tests
    test_semantic_scholar()

