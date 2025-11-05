#!/usr/bin/env python3
"""
Regenerate HTML dashboard from existing review files
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import the ReviewDashboard class from main
sys.path.insert(0, str(Path(__file__).parent))
from main import ReviewDashboard, FileManager

def load_reviews(output_dir: str) -> dict:
    """Load all review files from the output directory."""
    reviews = {}
    output_path = Path(output_dir)
    
    # Map file names to review keys
    review_files = {
        "methodology": "review_methodology.txt",
        "results": "review_results.txt",
        "literature": "review_literature.txt",
        "structure": "review_structure.txt",
        "impact": "review_impact.txt",
        "contradiction": "review_contradiction.txt",
        "ethics": "review_ethics.txt",
        "ai_origin": "review_ai_origin.txt",
        "hallucination": "review_hallucination.txt",
        "coordinator": "review_coordinator.txt",
        "editor": "review_editor.txt",
        "author_editor_summary": "review_author_editor_summary.txt",
    }
    
    for key, filename in review_files.items():
        filepath = output_path / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reviews[key] = f.read()
                print(f"✓ Loaded: {filename}")
            except Exception as e:
                print(f"✗ Error loading {filename}: {e}")
        else:
            print(f"⚠ Not found: {filename}")
    
    return reviews

def load_paper_info(output_dir: str) -> dict:
    """Load paper information from JSON file."""
    paper_info_path = Path(output_dir) / "paper_info.json"
    
    if paper_info_path.exists():
        try:
            with open(paper_info_path, 'r', encoding='utf-8') as f:
                paper_info = json.load(f)
            print(f"✓ Loaded: paper_info.json")
            return paper_info
        except Exception as e:
            print(f"✗ Error loading paper_info.json: {e}")
            return {}
    else:
        print(f"⚠ Not found: paper_info.json")
        return {}

def main():
    output_dir = "output_paper_review"
    
    print("=" * 60)
    print("Dashboard Regeneration Tool")
    print("=" * 60)
    print()
    
    # Load paper info
    print("Loading paper information...")
    paper_info = load_paper_info(output_dir)
    print()
    
    # Load reviews
    print("Loading review files...")
    reviews = load_reviews(output_dir)
    print()
    
    if not reviews:
        print("❌ No review files found. Cannot generate dashboard.")
        return 1
    
    # Get editor decision
    editor_decision = reviews.pop("editor", "Editorial decision not available")
    
    # Create results structure
    results = {
        "paper_info": paper_info,
        "reviews": reviews,
        "editor_decision": editor_decision,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "models_used": {
                "powerful": "gpt-5",
                "standard": "gpt-5-mini",
                "basic": "gpt-5-nano"
            },
            "num_reviewers": len([r for r in reviews.keys() if r not in ["coordinator", "author_editor_summary"]])
        }
    }
    
    print(f"Reviews loaded: {len(reviews)}")
    print(f"Number of expert reviewers: {results['config']['num_reviewers']}")
    print()
    
    # Generate dashboard
    print("Generating HTML dashboard...")
    try:
        dashboard = ReviewDashboard()
        html = dashboard.generate_html_dashboard(results)
        
        # Save dashboard
        file_manager = FileManager(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dashboard_{timestamp}.html"
        
        if file_manager.save_text(html, filename):
            print(f"✅ Dashboard generated successfully: {output_dir}/{filename}")
            return 0
        else:
            print(f"❌ Failed to save dashboard")
            return 1
            
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

