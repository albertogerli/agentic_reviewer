"""
Gamma API Integration for Presentation Generation
Creates professional slide decks from document review results.
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GammaConfig:
    """Configuration for Gamma API."""
    api_key: str
    theme_id: Optional[str] = "Oasis"  # Default theme
    num_cards: int = 12
    format: str = "presentation"
    export_as: str = "pdf"  # or "pptx"
    

class GammaPresentationGenerator:
    """
    Generate professional presentations using Gamma API from review results.
    """
    
    BASE_URL = "https://public-api.gamma.app/v1.0"
    
    def __init__(self, api_key: str):
        """
        Initialize Gamma integration.
        
        Args:
            api_key: Gamma API key (get from gamma.app/settings/api)
        """
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-KEY": api_key
        }
        
    def format_review_for_gamma(self, review_results: Dict[str, Any]) -> str:
        """
        Format review results into structured text for Gamma.
        Creates a narrative structure optimized for presentation slides.
        
        Args:
            review_results: Complete review results dictionary
            
        Returns:
            Formatted text with slide breaks
        """
        # Extract key information
        doc_info = review_results.get('document_info', {})
        doc_title = doc_info.get('title', 'Document Review')
        doc_type = doc_info.get('type', 'Document')
        
        final_eval = review_results.get('final_evaluation', 'No evaluation available.')
        
        # Extract issues and suggestions
        structured_issues = review_results.get('structured_issues', [])
        issues_by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for issue in structured_issues:
            severity = issue.get('severity', 'low')
            issues_by_severity[severity].append(issue)
        
        # Count total issues
        total_issues = len(structured_issues)
        critical_count = len(issues_by_severity['critical'])
        high_count = len(issues_by_severity['high'])
        
        # Extract agent reviews summary
        agent_reviews = review_results.get('agent_reviews', {})
        num_agents = len(agent_reviews)
        
        # Build structured presentation content
        content_parts = []
        
        # Slide 1: Title
        content_parts.append(f"""# {doc_title}
AI-Powered Document Review & Analysis
Comprehensive assessment by {num_agents} specialized AI agents""")
        
        # Slide 2: Executive Summary
        content_parts.append(f"""# Executive Summary
## Document Type: {doc_type}
## Total Issues Found: {total_issues}
* Critical: {critical_count}
* High Priority: {high_count}
* Medium Priority: {len(issues_by_severity['medium'])}
* Low Priority: {len(issues_by_severity['low'])}

{final_eval[:500] if len(final_eval) > 500 else final_eval}""")
        
        # Slide 3: Risk Heatmap
        risk_heatmap = review_results.get('risk_heatmap', {})
        if risk_heatmap:
            heatmap_content = "# Risk Assessment by Category\n"
            sorted_risks = sorted(risk_heatmap.items(), key=lambda x: x[1], reverse=True)[:8]
            for category, score in sorted_risks:
                bar = "█" * int(score / 10)
                heatmap_content += f"* {category.replace('_', ' ').title()}: {bar} ({score:.0f})\n"
            content_parts.append(heatmap_content)
        
        # Slide 4-5: Critical Issues
        if critical_count > 0:
            critical_content = "# Critical Issues Identified\n"
            for i, issue in enumerate(issues_by_severity['critical'][:5], 1):
                critical_content += f"""## {i}. {issue.get('title', 'Issue')}
**Location**: {issue.get('location', 'N/A')}
**Problem**: {issue.get('description', 'N/A')[:200]}
**Impact**: High priority - requires immediate attention\n\n"""
            content_parts.append(critical_content)
        
        # Slide 6-7: High Priority Issues
        if high_count > 0:
            high_content = "# High Priority Issues\n"
            for i, issue in enumerate(issues_by_severity['high'][:5], 1):
                high_content += f"""## {i}. {issue.get('title', 'Issue')}
{issue.get('description', 'N/A')[:150]}
**Recommendation**: {issue.get('suggestion', 'N/A')[:150]}\n\n"""
            content_parts.append(high_content)
        
        # Slide 8: Proposed Changes Summary
        proposed_changes = review_results.get('proposed_changes', [])
        if proposed_changes:
            changes_content = "# Proposed Improvements\n"
            changes_content += f"**Total Modifications Suggested**: {len(proposed_changes)}\n\n"
            
            changes_by_type = {}
            for change in proposed_changes:
                change_type = change.get('type', 'other')
                changes_by_type[change_type] = changes_by_type.get(change_type, 0) + 1
            
            for change_type, count in changes_by_type.items():
                changes_content += f"* **{change_type.title()}**: {count} changes\n"
            
            content_parts.append(changes_content)
        
        # Slide 9: Key Strengths
        strengths_content = "# Document Strengths\n"
        strengths_content += "Areas where the document excels:\n\n"
        
        # Extract positive feedback from agent reviews
        positive_keywords = ['excellent', 'strong', 'well', 'good', 'clear', 'effective', 'comprehensive']
        strengths_found = []
        
        for agent_name, review_text in list(agent_reviews.items())[:5]:
            review_lower = review_text.lower()
            for keyword in positive_keywords:
                if keyword in review_lower:
                    # Extract sentence with positive keyword
                    sentences = review_text.split('.')
                    for sent in sentences:
                        if keyword in sent.lower() and len(sent) > 20:
                            strengths_found.append(f"* {sent.strip()[:150]}")
                            break
                    break
            if len(strengths_found) >= 5:
                break
        
        if strengths_found:
            strengths_content += '\n'.join(strengths_found[:5])
        else:
            strengths_content += "* Overall structure and organization\n* Technical accuracy of content\n* Appropriate depth of coverage"
        
        content_parts.append(strengths_content)
        
        # Slide 10: Agent Analysis Overview
        agents_content = f"# Multi-Agent Analysis Process\n"
        agents_content += f"**{num_agents} Specialized AI Agents** analyzed this document:\n\n"
        
        agent_names = list(agent_reviews.keys())[:10]
        for agent_name in agent_names:
            display_name = agent_name.replace('_', ' ').title()
            agents_content += f"* {display_name}\n"
        
        content_parts.append(agents_content)
        
        # Slide 11: Recommendations
        recommendations_content = "# Key Recommendations\n"
        recommendations_content += "Priority actions to improve document quality:\n\n"
        
        # Top recommendations from critical/high issues
        top_suggestions = []
        for issue in (issues_by_severity['critical'] + issues_by_severity['high'])[:6]:
            suggestion = issue.get('suggestion', '')
            if suggestion and len(suggestion) > 20:
                top_suggestions.append(f"* {suggestion[:200]}")
        
        if top_suggestions:
            recommendations_content += '\n'.join(top_suggestions)
        else:
            recommendations_content += "* Address critical issues identified in slides 4-5\n* Review high-priority items in slides 6-7\n* Implement proposed changes from slide 8"
        
        content_parts.append(recommendations_content)
        
        # Slide 12: Next Steps
        next_steps_content = """# Next Steps
## Immediate Actions
1. Review and prioritize critical issues
2. Assign ownership for each issue category
3. Set timeline for implementing changes
4. Schedule follow-up review

## Long-term Strategy
* Establish regular review cycles
* Monitor compliance and quality metrics
* Continuous improvement process
* Stakeholder communication plan"""
        
        content_parts.append(next_steps_content)
        
        # Join with slide breaks
        return "\n---\n".join(content_parts)
    
    def create_presentation(
        self,
        review_results: Dict[str, Any],
        config: Optional[GammaConfig] = None,
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Gamma presentation from review results.
        
        Args:
            review_results: Complete review results dictionary
            config: Gamma configuration (uses defaults if None)
            additional_instructions: Additional instructions for Gamma
            
        Returns:
            Response with generation_id and status
        """
        if config is None:
            config = GammaConfig(api_key=self.api_key)
        
        # Format review content
        input_text = self.format_review_for_gamma(review_results)
        
        # Build request payload
        payload = {
            "inputText": input_text,
            "textMode": "preserve",  # Keep our structured text
            "format": config.format,
            "themeId": config.theme_id,
            "numCards": config.num_cards,
            "cardSplit": "inputTextBreaks",  # Use our \n---\n breaks
            "exportAs": config.export_as,
            "textOptions": {
                "amount": "detailed",
                "language": "en"
            },
            "imageOptions": {
                "source": "aiGenerated",
                "model": "imagen-4-pro",
                "style": "professional, modern, clean, business"
            },
            "cardOptions": {
                "dimensions": "16x9",
                "headerFooter": {
                    "topRight": {
                        "type": "text",
                        "value": "AI Document Review"
                    },
                    "bottomRight": {
                        "type": "cardNumber"
                    },
                    "hideFromFirstCard": True
                }
            }
        }
        
        if additional_instructions:
            payload["additionalInstructions"] = additional_instructions
        
        # Make API request
        try:
            logger.info("🎨 Creating Gamma presentation...")
            response = requests.post(
                f"{self.BASE_URL}/generations",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ Presentation generation started: {result.get('generationId')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Gamma API error: {e}")
            raise
    
    def check_status(self, generation_id: str) -> Dict[str, Any]:
        """
        Check the status of a presentation generation.
        
        Args:
            generation_id: ID returned from create_presentation
            
        Returns:
            Status response with URLs when completed
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/generations/{generation_id}",
                headers=self.headers,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Status check error: {e}")
            raise
    
    def wait_for_completion(
        self,
        generation_id: str,
        max_wait: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Wait for presentation generation to complete.
        
        Args:
            generation_id: ID returned from create_presentation
            max_wait: Maximum seconds to wait
            poll_interval: Seconds between status checks
            
        Returns:
            Final status with URLs
        """
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            status = self.check_status(generation_id)
            
            if status.get('status') == 'completed':
                logger.info("✅ Presentation generation completed!")
                return status
            
            elif status.get('status') == 'failed':
                logger.error(f"❌ Presentation generation failed: {status.get('error')}")
                raise Exception(f"Generation failed: {status.get('error')}")
            
            logger.info(f"⏳ Status: {status.get('status')} - waiting...")
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Presentation generation exceeded {max_wait}s timeout")
    
    def download_file(self, url: str, output_path: str) -> str:
        """
        Download PDF/PPTX file from Gamma.
        
        Args:
            url: Download URL from generation result
            output_path: Local path to save file
            
        Returns:
            Path to downloaded file
        """
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"📥 Downloaded presentation: {output_path}")
            return output_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Download error: {e}")
            raise


def create_presentation_from_review(
    review_results: Dict[str, Any],
    gamma_api_key: str,
    output_dir: str,
    theme_id: Optional[str] = None,
    export_format: str = "pdf"
) -> Dict[str, str]:
    """
    Convenience function to create and download presentation.
    
    Args:
        review_results: Complete review results
        gamma_api_key: Gamma API key
        output_dir: Directory to save presentation
        theme_id: Optional theme ID
        export_format: "pdf" or "pptx"
        
    Returns:
        Dictionary with URLs and local paths
    """
    generator = GammaPresentationGenerator(gamma_api_key)
    
    config = GammaConfig(
        api_key=gamma_api_key,
        theme_id=theme_id or "Oasis",
        num_cards=12,
        export_as=export_format
    )
    
    # Create presentation
    result = generator.create_presentation(review_results, config)
    generation_id = result['generationId']
    
    # Wait for completion
    final_status = generator.wait_for_completion(generation_id)
    
    # Extract URLs
    gamma_url = final_status.get('gammaUrl')
    export_url = final_status.get('exportUrl')
    
    # Download file
    local_path = None
    if export_url:
        filename = f"presentation.{export_format}"
        local_path = os.path.join(output_dir, filename)
        generator.download_file(export_url, local_path)
    
    return {
        'generation_id': generation_id,
        'gamma_url': gamma_url,
        'export_url': export_url,
        'local_path': local_path
    }


if __name__ == "__main__":
    # Test with sample review results
    sample_results = {
        "document_info": {
            "title": "Sample Business Proposal",
            "type": "business_proposal"
        },
        "final_evaluation": "Overall strong proposal with minor improvements needed.",
        "structured_issues": [
            {
                "severity": "high",
                "title": "Missing Financial Projections",
                "description": "The proposal lacks detailed financial forecasts.",
                "location": "Section 3",
                "suggestion": "Add 3-year revenue and cost projections"
            }
        ],
        "risk_heatmap": {
            "financial": 75,
            "technical": 45,
            "compliance": 60
        },
        "agent_reviews": {
            "business_analyst": "Strong value proposition...",
            "financial_analyst": "Revenue model needs clarification..."
        }
    }
    
    # Initialize (replace with your API key)
    api_key = os.getenv("GAMMA_API_KEY", "")
    if api_key:
        generator = GammaPresentationGenerator(api_key)
        
        # Format content
        formatted_text = generator.format_review_for_gamma(sample_results)
        print("📄 Formatted content preview:")
        print(formatted_text[:500])
        print("\n...")

