#!/usr/bin/env python3
"""
Review History Manager
CLI tool for managing document review history, checkpoints, and comparisons.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from document_tracker import DocumentTracker, DocumentVersion
from tabulate import tabulate


class ReviewHistoryCLI:
    """Command-line interface for review history management."""
    
    def __init__(self, db_path: str = "document_reviews.db"):
        self.tracker = DocumentTracker(db_path)
    
    def list_recent(self, limit: int = 10):
        """List recent reviews."""
        versions = self.tracker.get_recent_reviews(limit)
        
        if not versions:
            print("No reviews found in database.")
            return
        
        print(f"\n📊 RECENT REVIEWS (Last {limit})\n")
        print("="*100)
        
        table_data = []
        for v in versions:
            date_str = datetime.fromisoformat(v.review_date).strftime("%Y-%m-%d %H:%M")
            table_data.append([
                v.version_id[:8] + "...",
                v.document_title[:30],
                v.project_name[:20] if v.project_name else "-",
                f"{v.score:.1f}/100",
                v.review_mode,
                date_str
            ])
        
        headers = ["Version ID", "Document", "Project", "Score", "Mode", "Date"]
        print(tabulate(table_data, headers=headers, tablefmt="simple"))
        print()
    
    def list_projects(self):
        """List all projects."""
        projects = self.tracker.get_all_projects()
        
        if not projects:
            print("No projects found in database.")
            return
        
        print(f"\n📁 ALL PROJECTS ({len(projects)})\n")
        print("="*80)
        
        for i, project in enumerate(projects, 1):
            summary = self.tracker.get_project_summary(project)
            if summary:
                print(f"\n{i}. {project}")
                print(f"   Document: {summary.document_title}")
                print(f"   Versions: {summary.total_versions}")
                print(f"   Best Score: {summary.best_score:.1f}/100")
                print(f"   Improvement: +{summary.score_improvement:.1f} points")
                print(f"   Period: {summary.first_review_date[:10]} → {summary.last_review_date[:10]}")
        print()
    
    def show_project(self, project_name: str):
        """Show detailed project history."""
        summary = self.tracker.get_project_summary(project_name)
        
        if not summary:
            print(f"Project '{project_name}' not found.")
            return
        
        print(f"\n📊 PROJECT: {project_name}\n")
        print("="*100)
        print(f"Document: {summary.document_title}")
        print(f"Total Versions: {summary.total_versions}")
        print(f"First Review: {summary.first_review_date}")
        print(f"Last Review: {summary.last_review_date}")
        print(f"Best Score: {summary.best_score:.1f}/100 (version: {summary.best_version_id[:12]})")
        print(f"Total Improvement: +{summary.score_improvement:.1f} points")
        print(f"Total Iterations: {summary.total_iterations}")
        
        # Get all versions
        versions = self.tracker.get_project_history(project_name)
        
        if versions:
            print(f"\n📝 VERSION HISTORY ({len(versions)} versions)\n")
            
            table_data = []
            for v in versions:
                date_str = datetime.fromisoformat(v.review_date).strftime("%Y-%m-%d %H:%M")
                issues = f"C:{v.critical_issues} M:{v.moderate_issues} m:{v.minor_issues}"
                table_data.append([
                    v.version_id[:12] + "...",
                    date_str,
                    f"{v.score:.1f}",
                    issues,
                    v.review_mode,
                    v.iteration_number
                ])
            
            headers = ["Version ID", "Date", "Score", "Issues", "Mode", "Iterations"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        print()
    
    def show_document_history(self, document_hash: str):
        """Show history for a specific document."""
        versions = self.tracker.get_document_history(document_hash)
        
        if not versions:
            print(f"No history found for document hash: {document_hash}")
            return
        
        first_version = versions[-1]
        print(f"\n📄 DOCUMENT HISTORY: {first_version.document_title}\n")
        print("="*100)
        print(f"Document Hash: {document_hash}")
        print(f"Total Versions: {len(versions)}")
        
        if versions[0].project_name:
            print(f"Project: {versions[0].project_name}")
        
        print(f"\n📊 SCORE EVOLUTION\n")
        
        table_data = []
        for i, v in enumerate(reversed(versions), 1):
            date_str = datetime.fromisoformat(v.review_date).strftime("%Y-%m-%d %H:%M")
            
            # Calculate score change
            if i > 1:
                prev_score = versions[-i+1].score
                change = v.score - prev_score
                change_str = f"{change:+.1f}"
            else:
                change_str = "-"
            
            table_data.append([
                i,
                v.version_id[:12] + "...",
                date_str,
                f"{v.score:.1f}/100",
                change_str,
                f"C:{v.critical_issues} M:{v.moderate_issues}",
                v.review_mode
            ])
        
        headers = ["#", "Version ID", "Date", "Score", "Change", "Issues", "Mode"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
    
    def compare_versions(self, version_id_1: str, version_id_2: str):
        """Compare two versions."""
        comparison = self.tracker.compare_versions(version_id_1, version_id_2)
        
        if "error" in comparison:
            print(f"Error: {comparison['error']}")
            return
        
        v1 = comparison["version_1"]
        v2 = comparison["version_2"]
        improvements = comparison["improvements"]
        
        print(f"\n📊 VERSION COMPARISON\n")
        print("="*80)
        print(f"Time Between Reviews: {comparison['time_between']}")
        print()
        
        # Side by side comparison
        table_data = [
            ["Version ID", v1["version_id"][:20], v2["version_id"][:20]],
            ["Date", v1["date"][:19], v2["date"][:19]],
            ["", "", ""],
            ["Score", f"{v1['score']:.1f}/100", f"{v2['score']:.1f}/100"],
            ["", "", ""],
            ["Critical Issues", v1["issues"]["critical"], v2["issues"]["critical"]],
            ["Moderate Issues", v1["issues"]["moderate"], v2["issues"]["moderate"]],
            ["Minor Issues", v1["issues"]["minor"], v2["issues"]["minor"]]
        ]
        
        headers = ["Metric", "Version 1", "Version 2"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        print(f"\n📈 IMPROVEMENTS\n")
        print(f"  Score Change: {improvements['score_change']:+.1f} points")
        print(f"  Critical Issues Resolved: {improvements['critical_resolved']}")
        print(f"  Moderate Issues Resolved: {improvements['moderate_resolved']}")
        print(f"  Minor Issues Resolved: {improvements['minor_resolved']}")
        print()
        
        # Visual score comparison
        if improvements['score_change'] > 0:
            print("  📈 Score improved!")
        elif improvements['score_change'] < 0:
            print("  📉 Score decreased")
        else:
            print("  ➡️  Score unchanged")
        print()
    
    def list_checkpoints(self):
        """List available checkpoints."""
        checkpoints = self.tracker.list_checkpoints()
        
        if not checkpoints:
            print("No resumable checkpoints found.")
            return
        
        print(f"\n💾 AVAILABLE CHECKPOINTS ({len(checkpoints)})\n")
        print("="*100)
        
        table_data = []
        for cp in checkpoints:
            date_str = datetime.fromisoformat(cp["checkpoint_date"]).strftime("%Y-%m-%d %H:%M:%S")
            table_data.append([
                cp["checkpoint_id"][:20] + "...",
                cp["document_title"][:40],
                cp["current_iteration"],
                cp["current_phase"][:30],
                date_str
            ])
        
        headers = ["Checkpoint ID", "Document", "Iteration", "Phase", "Date"]
        print(tabulate(table_data, headers=headers, tablefmt="simple"))
        print()
    
    def export_project(self, project_name: str, output_file: str):
        """Export project data to JSON."""
        versions = self.tracker.get_project_history(project_name)
        
        if not versions:
            print(f"Project '{project_name}' not found.")
            return
        
        summary = self.tracker.get_project_summary(project_name)
        
        export_data = {
            "project_name": project_name,
            "export_date": datetime.now().isoformat(),
            "summary": {
                "document_title": summary.document_title if summary else "",
                "total_versions": len(versions),
                "best_score": max(v.score for v in versions),
                "score_improvement": max(v.score for v in versions) - min(v.score for v in versions),
                "date_range": {
                    "first": versions[-1].review_date if versions else "",
                    "last": versions[0].review_date if versions else ""
                }
            },
            "versions": []
        }
        
        for v in versions:
            export_data["versions"].append({
                "version_id": v.version_id,
                "review_date": v.review_date,
                "score": v.score,
                "iteration_number": v.iteration_number,
                "review_mode": v.review_mode,
                "language": v.language,
                "issues": {
                    "critical": v.critical_issues,
                    "moderate": v.moderate_issues,
                    "minor": v.minor_issues
                },
                "output_directory": v.output_directory
            })
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n✅ Project '{project_name}' exported to: {output_file}")
        print(f"   {len(versions)} versions exported")
        print()
    
    def show_stats(self):
        """Show overall statistics."""
        all_versions = self.tracker.get_recent_reviews(limit=1000)
        projects = self.tracker.get_all_projects()
        
        if not all_versions:
            print("No reviews in database yet.")
            return
        
        print(f"\n📊 OVERALL STATISTICS\n")
        print("="*80)
        print(f"Total Reviews: {len(all_versions)}")
        print(f"Total Projects: {len(projects)}")
        
        # Score statistics
        scores = [v.score for v in all_versions]
        print(f"\nScore Statistics:")
        print(f"  Average Score: {sum(scores)/len(scores):.1f}/100")
        print(f"  Highest Score: {max(scores):.1f}/100")
        print(f"  Lowest Score: {min(scores):.1f}/100")
        
        # Mode statistics
        modes = {}
        for v in all_versions:
            modes[v.review_mode] = modes.get(v.review_mode, 0) + 1
        
        print(f"\nReview Modes:")
        for mode, count in sorted(modes.items(), key=lambda x: x[1], reverse=True):
            print(f"  {mode.capitalize()}: {count} ({count/len(all_versions)*100:.1f}%)")
        
        # Language statistics
        langs = {}
        for v in all_versions:
            langs[v.language] = langs.get(v.language, 0) + 1
        
        print(f"\nLanguages:")
        for lang, count in sorted(langs.items(), key=lambda x: x[1], reverse=True):
            print(f"  {lang}: {count} ({count/len(all_versions)*100:.1f}%)")
        
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Document Review History Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List recent reviews
  python3 review_history.py recent

  # List all projects
  python3 review_history.py projects

  # Show project details
  python3 review_history.py project "My Business Plan"

  # Show document history
  python3 review_history.py document abc123def456

  # Compare two versions
  python3 review_history.py compare version_id_1 version_id_2

  # List checkpoints
  python3 review_history.py checkpoints

  # Export project
  python3 review_history.py export "My Business Plan" output.json

  # Show statistics
  python3 review_history.py stats
        """
    )
    
    parser.add_argument("--db", default="document_reviews.db", 
                       help="Path to database file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Recent reviews
    recent_parser = subparsers.add_parser("recent", help="List recent reviews")
    recent_parser.add_argument("--limit", type=int, default=10, help="Number of reviews to show")
    
    # Projects
    subparsers.add_parser("projects", help="List all projects")
    
    # Project details
    project_parser = subparsers.add_parser("project", help="Show project details")
    project_parser.add_argument("name", help="Project name")
    
    # Document history
    doc_parser = subparsers.add_parser("document", help="Show document history")
    doc_parser.add_argument("hash", help="Document hash")
    
    # Compare versions
    compare_parser = subparsers.add_parser("compare", help="Compare two versions")
    compare_parser.add_argument("version1", help="First version ID")
    compare_parser.add_argument("version2", help="Second version ID")
    
    # Checkpoints
    subparsers.add_parser("checkpoints", help="List available checkpoints")
    
    # Export
    export_parser = subparsers.add_parser("export", help="Export project to JSON")
    export_parser.add_argument("project", help="Project name")
    export_parser.add_argument("output", help="Output JSON file")
    
    # Stats
    subparsers.add_parser("stats", help="Show overall statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = ReviewHistoryCLI(args.db)
    
    try:
        if args.command == "recent":
            cli.list_recent(args.limit)
        elif args.command == "projects":
            cli.list_projects()
        elif args.command == "project":
            cli.show_project(args.name)
        elif args.command == "document":
            cli.show_document_history(args.hash)
        elif args.command == "compare":
            cli.compare_versions(args.version1, args.version2)
        elif args.command == "checkpoints":
            cli.list_checkpoints()
        elif args.command == "export":
            cli.export_project(args.project, args.output)
        elif args.command == "stats":
            cli.show_stats()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

