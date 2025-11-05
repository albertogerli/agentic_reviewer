"""
Document Tracking System
Provides persistent storage for document reviews, version history, and project tracking.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentVersion:
    """Represents a single version of a document."""
    version_id: str
    document_hash: str
    document_title: str
    project_name: Optional[str]
    review_date: str
    score: float
    iteration_number: int
    file_path: str
    output_directory: str
    review_mode: str  # "standard", "iterative", "interactive"
    language: str
    improvements_applied: int
    critical_issues: int
    moderate_issues: int
    minor_issues: int
    agent_count: int
    metadata: str  # JSON string


@dataclass
class ProjectSummary:
    """Summary of all versions of a document in a project."""
    project_name: str
    document_title: str
    total_versions: int
    first_review_date: str
    last_review_date: str
    best_score: float
    best_version_id: str
    score_improvement: float
    total_iterations: int


class DocumentTracker:
    """
    Manages persistent storage of document reviews and enables:
    - Version tracking across multiple reviews
    - Project-based organization
    - Historical comparison
    - Progress tracking
    """
    
    def __init__(self, db_path: str = "document_reviews.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main table for document versions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_versions (
                version_id TEXT PRIMARY KEY,
                document_hash TEXT NOT NULL,
                document_title TEXT NOT NULL,
                project_name TEXT,
                review_date TEXT NOT NULL,
                score REAL NOT NULL,
                iteration_number INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                output_directory TEXT NOT NULL,
                review_mode TEXT NOT NULL,
                language TEXT NOT NULL,
                improvements_applied INTEGER DEFAULT 0,
                critical_issues INTEGER DEFAULT 0,
                moderate_issues INTEGER DEFAULT 0,
                minor_issues INTEGER DEFAULT 0,
                agent_count INTEGER DEFAULT 0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for checkpoints (pause/resume)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                document_hash TEXT NOT NULL,
                document_title TEXT NOT NULL,
                checkpoint_date TEXT NOT NULL,
                current_iteration INTEGER NOT NULL,
                current_phase TEXT NOT NULL,
                state_data TEXT NOT NULL,
                can_resume INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for tracking active sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_sessions (
                session_id TEXT PRIMARY KEY,
                document_hash TEXT NOT NULL,
                document_title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                status TEXT NOT NULL,
                progress_percent REAL DEFAULT 0,
                current_phase TEXT,
                output_directory TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_document_hash 
            ON document_versions(document_hash)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_project_name 
            ON document_versions(project_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_review_date 
            ON document_versions(review_date)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    def compute_document_hash(self, content: str) -> str:
        """Compute SHA-256 hash of document content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def save_version(self, version: DocumentVersion) -> bool:
        """Save a document version to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO document_versions (
                    version_id, document_hash, document_title, project_name,
                    review_date, score, iteration_number, file_path,
                    output_directory, review_mode, language, improvements_applied,
                    critical_issues, moderate_issues, minor_issues, agent_count, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version.version_id,
                version.document_hash,
                version.document_title,
                version.project_name,
                version.review_date,
                version.score,
                version.iteration_number,
                version.file_path,
                version.output_directory,
                version.review_mode,
                version.language,
                version.improvements_applied,
                version.critical_issues,
                version.moderate_issues,
                version.minor_issues,
                version.agent_count,
                version.metadata
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved version {version.version_id} to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving version to database: {e}")
            return False
    
    def get_document_history(self, document_hash: str) -> List[DocumentVersion]:
        """Get all versions of a document by its hash."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version_id, document_hash, document_title, project_name,
                   review_date, score, iteration_number, file_path,
                   output_directory, review_mode, language, improvements_applied,
                   critical_issues, moderate_issues, minor_issues, agent_count, metadata
            FROM document_versions
            WHERE document_hash = ?
            ORDER BY review_date DESC
        """, (document_hash,))
        
        versions = []
        for row in cursor.fetchall():
            version = DocumentVersion(*row)
            versions.append(version)
        
        conn.close()
        return versions
    
    def get_project_history(self, project_name: str) -> List[DocumentVersion]:
        """Get all versions in a project."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version_id, document_hash, document_title, project_name,
                   review_date, score, iteration_number, file_path,
                   output_directory, review_mode, language, improvements_applied,
                   critical_issues, moderate_issues, minor_issues, agent_count, metadata
            FROM document_versions
            WHERE project_name = ?
            ORDER BY review_date DESC
        """, (project_name,))
        
        versions = []
        for row in cursor.fetchall():
            version = DocumentVersion(*row)
            versions.append(version)
        
        conn.close()
        return versions
    
    def get_project_summary(self, project_name: str) -> Optional[ProjectSummary]:
        """Get summary statistics for a project."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                project_name,
                document_title,
                COUNT(*) as total_versions,
                MIN(review_date) as first_review_date,
                MAX(review_date) as last_review_date,
                MAX(score) as best_score,
                SUM(iteration_number) as total_iterations
            FROM document_versions
            WHERE project_name = ?
            GROUP BY project_name, document_title
        """, (project_name,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        # Get best version ID
        cursor.execute("""
            SELECT version_id, score
            FROM document_versions
            WHERE project_name = ?
            ORDER BY score DESC
            LIMIT 1
        """, (project_name,))
        
        best_row = cursor.fetchone()
        best_version_id = best_row[0] if best_row else ""
        
        # Get first score for improvement calculation
        cursor.execute("""
            SELECT score
            FROM document_versions
            WHERE project_name = ?
            ORDER BY review_date ASC
            LIMIT 1
        """, (project_name,))
        
        first_score = cursor.fetchone()[0]
        
        conn.close()
        
        summary = ProjectSummary(
            project_name=row[0],
            document_title=row[1],
            total_versions=row[2],
            first_review_date=row[3],
            last_review_date=row[4],
            best_score=row[5],
            best_version_id=best_version_id,
            score_improvement=row[5] - first_score,
            total_iterations=row[6]
        )
        
        return summary
    
    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict[str, Any]:
        """Compare two versions of a document."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        versions = []
        for vid in [version_id_1, version_id_2]:
            cursor.execute("""
                SELECT version_id, document_hash, document_title, project_name,
                       review_date, score, iteration_number, file_path,
                       output_directory, review_mode, language, improvements_applied,
                       critical_issues, moderate_issues, minor_issues, agent_count, metadata
                FROM document_versions
                WHERE version_id = ?
            """, (vid,))
            
            row = cursor.fetchone()
            if row:
                versions.append(DocumentVersion(*row))
        
        conn.close()
        
        if len(versions) != 2:
            return {"error": "Could not find both versions"}
        
        v1, v2 = versions
        
        comparison = {
            "version_1": {
                "version_id": v1.version_id,
                "date": v1.review_date,
                "score": v1.score,
                "issues": {
                    "critical": v1.critical_issues,
                    "moderate": v1.moderate_issues,
                    "minor": v1.minor_issues
                }
            },
            "version_2": {
                "version_id": v2.version_id,
                "date": v2.review_date,
                "score": v2.score,
                "issues": {
                    "critical": v2.critical_issues,
                    "moderate": v2.moderate_issues,
                    "minor": v2.minor_issues
                }
            },
            "improvements": {
                "score_change": v2.score - v1.score,
                "critical_resolved": v1.critical_issues - v2.critical_issues,
                "moderate_resolved": v1.moderate_issues - v2.moderate_issues,
                "minor_resolved": v1.minor_issues - v2.minor_issues
            },
            "time_between": self._calculate_time_diff(v1.review_date, v2.review_date)
        }
        
        return comparison
    
    def _calculate_time_diff(self, date1: str, date2: str) -> str:
        """Calculate human-readable time difference."""
        try:
            dt1 = datetime.fromisoformat(date1)
            dt2 = datetime.fromisoformat(date2)
            diff = abs((dt2 - dt1).total_seconds())
            
            if diff < 3600:
                return f"{int(diff/60)} minutes"
            elif diff < 86400:
                return f"{int(diff/3600)} hours"
            else:
                return f"{int(diff/86400)} days"
        except:
            return "unknown"
    
    def save_checkpoint(self, checkpoint_id: str, document_hash: str, 
                       document_title: str, current_iteration: int,
                       current_phase: str, state_data: Dict[str, Any]) -> bool:
        """Save checkpoint for pause/resume."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO checkpoints (
                    checkpoint_id, document_hash, document_title, checkpoint_date,
                    current_iteration, current_phase, state_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                checkpoint_id,
                document_hash,
                document_title,
                datetime.now().isoformat(),
                current_iteration,
                current_phase,
                json.dumps(state_data)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Checkpoint saved: {checkpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
            return False
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint for resume."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT document_hash, document_title, checkpoint_date,
                   current_iteration, current_phase, state_data, can_resume
            FROM checkpoints
            WHERE checkpoint_id = ?
        """, (checkpoint_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        if row[6] == 0:  # can_resume = 0
            logger.warning(f"Checkpoint {checkpoint_id} cannot be resumed")
            return None
        
        return {
            "document_hash": row[0],
            "document_title": row[1],
            "checkpoint_date": row[2],
            "current_iteration": row[3],
            "current_phase": row[4],
            "state_data": json.loads(row[5])
        }
    
    def list_checkpoints(self, document_hash: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available checkpoints."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if document_hash:
            cursor.execute("""
                SELECT checkpoint_id, document_title, checkpoint_date,
                       current_iteration, current_phase, can_resume
                FROM checkpoints
                WHERE document_hash = ? AND can_resume = 1
                ORDER BY checkpoint_date DESC
            """, (document_hash,))
        else:
            cursor.execute("""
                SELECT checkpoint_id, document_title, checkpoint_date,
                       current_iteration, current_phase, can_resume
                FROM checkpoints
                WHERE can_resume = 1
                ORDER BY checkpoint_date DESC
            """)
        
        checkpoints = []
        for row in cursor.fetchall():
            checkpoints.append({
                "checkpoint_id": row[0],
                "document_title": row[1],
                "checkpoint_date": row[2],
                "current_iteration": row[3],
                "current_phase": row[4]
            })
        
        conn.close()
        return checkpoints
    
    def invalidate_checkpoint(self, checkpoint_id: str):
        """Mark checkpoint as no longer resumable."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE checkpoints SET can_resume = 0 WHERE checkpoint_id = ?
        """, (checkpoint_id,))
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str, document_hash: str,
                      document_title: str, output_directory: str) -> bool:
        """Create active session tracking."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO active_sessions (
                    session_id, document_hash, document_title, start_time,
                    status, output_directory
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                document_hash,
                document_title,
                datetime.now().isoformat(),
                "running",
                output_directory
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return False
    
    def update_session(self, session_id: str, progress: float, 
                      current_phase: str, status: str = "running"):
        """Update session progress."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE active_sessions 
            SET progress_percent = ?, current_phase = ?, status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (progress, current_phase, status, session_id))
        
        conn.commit()
        conn.close()
    
    def get_all_projects(self) -> List[str]:
        """Get list of all project names."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT project_name 
            FROM document_versions 
            WHERE project_name IS NOT NULL
            ORDER BY project_name
        """)
        
        projects = [row[0] for row in cursor.fetchall()]
        conn.close()
        return projects
    
    def get_recent_reviews(self, limit: int = 10) -> List[DocumentVersion]:
        """Get most recent reviews across all documents."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version_id, document_hash, document_title, project_name,
                   review_date, score, iteration_number, file_path,
                   output_directory, review_mode, language, improvements_applied,
                   critical_issues, moderate_issues, minor_issues, agent_count, metadata
            FROM document_versions
            ORDER BY review_date DESC
            LIMIT ?
        """, (limit,))
        
        versions = []
        for row in cursor.fetchall():
            versions.append(DocumentVersion(*row))
        
        conn.close()
        return versions

