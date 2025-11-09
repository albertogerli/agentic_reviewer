"""
FastAPI Backend - Fixed & Complete Version
Includes ALL features from Gradio version
"""

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Initialize app
app = FastAPI(title="Agentic Reviewer API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")

manager = ConnectionManager()

# Models
class ReviewConfig(BaseModel):
    output_language: str = ""
    enable_iterative: bool = False
    max_iterations: int = 3
    target_score: float = 85.0
    enable_python_tools: bool = False
    enable_interactive: bool = False
    enable_deep_review: bool = False
    reference_type: str = "example"

# Endpoints
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Agentic Reviewer API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    try:
        config_path = Path(__file__).parent.parent / "config.yaml"
        return {
            "status": "healthy",
            "config_exists": config_path.exists(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/review/upload")
async def upload_document(
    file: UploadFile = File(...),
    config: Optional[str] = Form(None),
    reference_files: Optional[List[UploadFile]] = File(None)
):
    """Upload document with optional reference files"""
    try:
        # Parse config
        review_config = ReviewConfig()
        if config:
            config_dict = json.loads(config)
            review_config = ReviewConfig(**config_dict)
        
        # Save main file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Save reference files
        reference_paths = []
        if reference_files:
            ref_dir = upload_dir / "references"
            ref_dir.mkdir(exist_ok=True)
            for ref_file in reference_files:
                ref_path = ref_dir / ref_file.filename
                with open(ref_path, "wb") as f:
                    content = await ref_file.read()
                    f.write(content)
                reference_paths.append(str(ref_path))
        
        # Generate review ID
        review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Start background processing
        asyncio.create_task(
            process_review(review_id, str(file_path), review_config, reference_paths)
        )
        
        return {
            "status": "started",
            "message": "Review started",
            "review_id": review_id,
            "config": review_config.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def process_review(
    review_id: str,
    file_path: str,
    config: ReviewConfig,
    reference_paths: List[str]
):
    """Background task for document review"""
    try:
        await manager.broadcast({
            "type": "progress",
            "review_id": review_id,
            "progress": 0,
            "status": "Starting review..."
        })
        
        # Import here to avoid startup issues
        from main import Config as AppConfig
        from generic_reviewer import (
            GenericReviewOrchestrator,
            IterativeReviewOrchestrator,
            DocumentClassifier
        )
        
        await manager.broadcast({
            "type": "progress",
            "review_id": review_id,
            "progress": 10,
            "status": "Loading configuration..."
        })
        
        # Load app config FROM YAML! (FIX critico!)
        config_path = Path(__file__).parent.parent / "config.yaml"
        app_config = AppConfig.from_yaml(str(config_path))
        
        # Debug: verifica API key caricata
        if app_config.api_key and app_config.api_key != "LA_TUA_API_KEY_QUI":
            logger.info(f"✅ API key loaded: {app_config.api_key[:20]}...")
        else:
            logger.error(f"❌ API key NOT configured! Check {config_path}")
            raise ValueError("API key not configured in config.yaml")
        
        # Extract text
        await manager.broadcast({
            "type": "progress",
            "review_id": review_id,
            "progress": 20,
            "status": "Extracting document text..."
        })
        
        # Extract document text based on file type
        if file_path.endswith('.pdf'):
            try:
                import PyPDF2
                document_text = ""
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        document_text += page.extract_text() + "\n"
            except Exception as e:
                logger.error(f"PDF extraction failed: {e}")
                raise HTTPException(status_code=500, detail=f"Cannot read PDF: {e}")
        elif file_path.endswith(('.docx', '.doc')):
            try:
                from docx import Document
                doc = Document(file_path)
                document_text = '\n'.join([para.text for para in doc.paragraphs])
            except Exception as e:
                logger.error(f"DOCX extraction failed: {e}")
                # Fallback to text reading
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    document_text = f.read()
        else:
            # Text files
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            document_text = None
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        document_text = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if document_text is None:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    document_text = f.read()
        
        title = Path(file_path).stem
        
        # Classify document
        await manager.broadcast({
            "type": "progress",
            "review_id": review_id,
            "progress": 30,
            "status": "📋 Analyzing document type..."
        })
        
        classifier = DocumentClassifier(app_config)
        doc_type = classifier.classify_document(document_text)
        agent_list = doc_type.suggested_agents if hasattr(doc_type, 'suggested_agents') else []
        
        # Send document classification info
        doc_type_name = getattr(doc_type, 'type', 'Unknown')
        doc_category = getattr(doc_type, 'category', '')
        
        await manager.broadcast({
            "type": "progress",
            "review_id": review_id,
            "progress": 32,
            "status": f"📄 Document classified: {doc_type_name}" + (f" ({doc_category})" if doc_category else "")
        })
        
        await manager.broadcast({
            "type": "agents_selected",
            "review_id": review_id,
            "agents": agent_list,
            "total_agents": len(agent_list),
            "document_type": doc_type_name
        })
        
        # Create output dir using SAME timestamp as review_id
        timestamp = review_id.replace("review_", "")
        output_dir = Path("outputs") / f"{title}_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        app_config.output_dir = str(output_dir)
        
        logger.info(f"📁 Output directory: {output_dir}")
        logger.info(f"🔗 Review ID: {review_id}")
        logger.info(f"✅ Timestamps MATCH!")
        
        # Create progress callback for live updates
        async def progress_callback(progress: int, status: str):
            """Send progress updates via WebSocket with agent details"""
            # Parse structured status format
            agent_info = None
            display_status = status  # Default human-readable status
            
            # Format: AGENT_ANALYZING|icon|name|count or AGENT_COMPLETED|icon|name|count
            if status.startswith("AGENT_"):
                parts = status.split("|")
                if len(parts) == 4:
                    action = parts[0]  # AGENT_ANALYZING or AGENT_COMPLETED
                    icon = parts[1]
                    name = parts[2]
                    count = parts[3]
                    
                    # Determine status
                    if action == "AGENT_ANALYZING":
                        agent_status = "analyzing"
                        display_status = f"{icon} {name} analyzing... ({count} completed)"
                    elif action == "AGENT_COMPLETED":
                        agent_status = "completed"
                        display_status = f"✅ {icon} {name} completed ({count})"
                    else:
                        agent_status = "pending"
                        display_status = status
                    
                    agent_info = {
                        'icon': icon,
                        'name': name,
                        'status': agent_status
                    }
                    
                    logger.info(f"📡 Agent update: {icon} {name} - {agent_status} ({count})")
            
            message = {
                "type": "progress",
                "review_id": review_id,
                "progress": progress,
                "status": display_status
            }
            
            if agent_info:
                message["agent"] = agent_info
                logger.info(f"📤 WebSocket: {agent_info}")
            
            await manager.broadcast(message)
        
        # Choose orchestrator and execute review
        if config.enable_iterative:
            logger.info(f"🔄 Starting ITERATIVE review (max_iterations={config.max_iterations}, target_score={config.target_score})")
            
            orchestrator = IterativeReviewOrchestrator(
                app_config,
                output_language=config.output_language or "en",
                max_iterations=config.max_iterations,
                target_score=config.target_score,
                interactive=config.enable_interactive,
                enable_python_tools=config.enable_python_tools,
                deep_review=config.enable_deep_review,
                progress_callback=progress_callback  # ✅ Live updates!
            )
            
            # Execute with asyncio.run since it's a coroutine!
            logger.info(f"📝 Calling orchestrator.execute_iterative_review...")
            
            try:
                # CRITICAL FIX: Just await since we're already in async context!
                results = await orchestrator.execute_iterative_review(document_text, title)
                
                logger.info(f"✅ Iterative review completed!")
                logger.info(f"   Iterations performed: {results.get('iterations_performed', 'N/A')}")
            except Exception as e:
                logger.error(f"❌ ERROR in execute_iterative_review: {e}", exc_info=True)
                raise
        else:
            logger.info(f"🚀 Starting STANDARD review (deep_review={config.enable_deep_review})")
            
            orchestrator = GenericReviewOrchestrator(
                app_config,
                output_language=config.output_language or "en",
                enable_python_tools=config.enable_python_tools,
                deep_review=config.enable_deep_review,
                progress_callback=progress_callback  # ✅ Live updates!
            )
            
            # Execute with asyncio.run since it's a coroutine!
            logger.info(f"📝 Calling orchestrator.execute_review_process...")
            logger.info(f"   Document length: {len(document_text)} chars")
            logger.info(f"   Title: {title}")
            logger.info(f"   Output dir: {app_config.output_dir}")
            
            try:
                # Send detailed progress updates
                await manager.broadcast({
                    "type": "progress",
                    "review_id": review_id,
                    "progress": 35,
                    "status": "🛡️ Deploying AI agents (Tier 1, 2, 3)..."
                })
                
                # CRITICAL FIX: Just await since we're already in async context!
                results = await orchestrator.execute_review_process(document_text, title)
                
                logger.info(f"✅ Review process completed!")
                logger.info(f"   Results type: {type(results)}")
                if isinstance(results, dict):
                    agent_count = len(results.get('agent_reviews', {}))
                    logger.info(f"   Agent reviews: {agent_count}")
                    logger.info(f"   Output dir: {results.get('output_dir', 'N/A')}")
                    
                    # Send completion info
                    await manager.broadcast({
                        "type": "progress",
                        "review_id": review_id,
                        "progress": 95,
                        "status": f"✅ {agent_count} agents completed analysis!"
                    })
            except Exception as e:
                logger.error(f"❌ ERROR in execute_review_process: {e}", exc_info=True)
                raise
        
        await manager.broadcast({
            "type": "complete",
            "review_id": review_id,
            "progress": 100,
            "status": "Complete!",
            "output_dir": str(output_dir)
        })
        
    except Exception as e:
        logger.error(f"Review failed: {e}", exc_info=True)
        await manager.broadcast({
            "type": "error",
            "review_id": review_id,
            "error": str(e)
        })

@app.get("/api/review/{review_id}/results")
async def get_results(review_id: str):
    """Get review results"""
    try:
        outputs_dir = Path("outputs")
        
        # Find matching directory - match by timestamp!
        matching_dirs = []
        if outputs_dir.exists():
            # Extract timestamp from review_id (e.g., "20251109_084202" from "review_20251109_084202")
            timestamp = review_id.replace('review_', '')
            logger.info(f"Looking for directory with timestamp: {timestamp}")
            
            for d in outputs_dir.iterdir():
                if d.is_dir() and timestamp in d.name:
                    logger.info(f"Found matching directory: {d.name}")
                    matching_dirs.append(d)
        
        if not matching_dirs:
            logger.error(f"No output directory found for review_id: {review_id}")
            raise HTTPException(status_code=404, detail=f"Review not found: {review_id}")
        
        # Use the most recent if multiple
        output_dir = max(matching_dirs, key=lambda p: p.stat().st_mtime)
        logger.info(f"Found output directory: {output_dir}")
        
        results_path = output_dir / "review_results.json"
        
        if not results_path.exists():
            logger.error(f"Results file not found: {results_path}")
            # List what files DO exist
            existing_files = list(output_dir.glob("*"))
            logger.error(f"Files in directory: {[f.name for f in existing_files]}")
            raise HTTPException(status_code=404, detail="Results not generated yet")
        
        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        logger.info(f"✅ Returning results with {len(results.get('agent_reviews', {}))} agent reviews")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/{review_id}/apply-changes")
async def apply_changes(review_id: str, changes: List[dict]):
    """Apply accepted changes to document and generate revised version"""
    try:
        outputs_dir = Path("outputs")
        timestamp = review_id.replace('review_', '')
        matching_dirs = [d for d in outputs_dir.iterdir() if d.is_dir() and timestamp in d.name]
        
        if not matching_dirs:
            raise HTTPException(status_code=404, detail="Review not found")
        
        output_dir = matching_dirs[0]
        
        # Load original results to get document text
        results_path = output_dir / "review_results.json"
        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Get document text (prioritize from results, fallback to reading file)
        document_text = results.get('document_text', '')
        if not document_text:
            # Try to reload from original file
            logger.warning("No document_text in results, cannot apply changes")
            raise HTTPException(status_code=400, detail="Original document text not available")
        
        # Apply only accepted changes
        accepted_changes = [c for c in changes if c.get('status') == 'accepted']
        logger.info(f"✏️ Applying {len(accepted_changes)} accepted changes")
        
        revised_text = document_text
        
        # Sort changes by position (if we had position data) - for now, apply in order
        # Note: This is a simple implementation. For production, you'd want more sophisticated
        # text manipulation with position tracking
        for change in accepted_changes:
            change_type = change.get('type')
            old_text = change.get('old_text', '')
            new_text = change.get('new_text', '')
            
            if change_type == 'delete' and old_text in revised_text:
                revised_text = revised_text.replace(old_text, '', 1)
            elif change_type == 'insert':
                # For insert, we'd need position data. For now, append
                revised_text += f"\n\n{new_text}"
            elif change_type == 'replace' and old_text in revised_text:
                revised_text = revised_text.replace(old_text, new_text, 1)
        
        # Save revised document
        revised_path = output_dir / "revised_document.txt"
        with open(revised_path, 'w', encoding='utf-8') as f:
            f.write(revised_text)
        
        # Generate change summary
        summary = {
            'total_changes': len(changes),
            'accepted': len(accepted_changes),
            'rejected': len([c for c in changes if c.get('status') == 'rejected']),
            'pending': len([c for c in changes if c.get('status') == 'pending']),
            'revised_file': str(revised_path),
            'character_diff': len(revised_text) - len(document_text)
        }
        
        # Save summary
        summary_path = output_dir / "revision_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"✅ Revised document saved: {revised_path}")
        
        return {
            'success': True,
            'summary': summary,
            'revised_text_preview': revised_text[:500] + '...' if len(revised_text) > 500 else revised_text
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying changes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/review/{review_id}/download/{file_type}")
async def download_file(review_id: str, file_type: str):
    """Download files"""
    try:
        outputs_dir = Path("outputs")
        
        # Match by timestamp (same as get_results)
        timestamp = review_id.replace('review_', '')
        matching_dirs = [d for d in outputs_dir.iterdir() if d.is_dir() and timestamp in d.name]
        
        if not matching_dirs:
            raise HTTPException(status_code=404, detail="Review not found")
        
        output_dir = matching_dirs[0]
        
        file_map = {
            "md": "review_report.md",
            "json": "review_results.json",
            "html": "dashboard.html"
        }
        
        if file_type not in file_map:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        file_path = output_dir / file_map[file_type]
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=file_map[file_type],
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/analytics/history")
async def get_review_history(days: int = 30, limit: int = 100):
    """Get review history for the last N days"""
    try:
        outputs_dir = Path("outputs")
        if not outputs_dir.exists():
            return {"reviews": []}
        
        history = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Scan all output directories
        for output_dir in sorted(outputs_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if not output_dir.is_dir():
                continue
            
            # Check if directory is recent enough
            dir_mtime = datetime.fromtimestamp(output_dir.stat().st_mtime)
            if dir_mtime < cutoff_date:
                continue
            
            # Load results.json
            results_path = output_dir / "review_results.json"
            if not results_path.exists():
                continue
            
            try:
                with open(results_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                # Extract key info
                doc_info = results.get('document_info', {})
                metadata = results.get('metadata', {})
                
                # Calculate score from issues if available
                structured_issues = results.get('structured_issues', [])
                score = 100
                if structured_issues:
                    critical = sum(1 for i in structured_issues if i.get('severity') == 'critical')
                    high = sum(1 for i in structured_issues if i.get('severity') == 'high')
                    medium = sum(1 for i in structured_issues if i.get('severity') == 'medium')
                    low = sum(1 for i in structured_issues if i.get('severity') == 'low')
                    
                    # Simple scoring: deduct points
                    score = max(0, 100 - (critical * 20) - (high * 10) - (medium * 5) - (low * 2))
                
                history.append({
                    'id': output_dir.name,
                    'title': doc_info.get('title', 'Untitled'),
                    'type': doc_info.get('type', {}).get('type', 'unknown'),
                    'category': doc_info.get('type', {}).get('category', 'unknown'),
                    'date': doc_info.get('review_date', dir_mtime.isoformat()),
                    'score': score,
                    'total_issues': len(structured_issues),
                    'total_changes': metadata.get('total_changes', 0),
                    'total_agents': metadata.get('total_agents', 0),
                    'output_dir': str(output_dir)
                })
                
                if len(history) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error loading {results_path}: {e}")
                continue
        
        logger.info(f"📊 Retrieved {len(history)} reviews from last {days} days")
        return {"reviews": history, "total": len(history)}
        
    except Exception as e:
        logger.error(f"Error getting history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/trends")
async def get_score_trends(project: str = None, days: int = 30):
    """Get score trends over time"""
    try:
        history_data = await get_review_history(days=days, limit=1000)
        reviews = history_data['reviews']
        
        # Filter by project if specified
        if project:
            reviews = [r for r in reviews if project.lower() in r['title'].lower()]
        
        # Group by date
        daily_scores = {}
        for review in reviews:
            date_str = review['date'][:10]  # YYYY-MM-DD
            if date_str not in daily_scores:
                daily_scores[date_str] = {'scores': [], 'count': 0}
            daily_scores[date_str]['scores'].append(review['score'])
            daily_scores[date_str]['count'] += 1
        
        # Calculate daily averages
        trends = []
        for date_str in sorted(daily_scores.keys()):
            data = daily_scores[date_str]
            avg_score = sum(data['scores']) / len(data['scores'])
            trends.append({
                'date': date_str,
                'avg_score': round(avg_score, 1),
                'count': data['count'],
                'min_score': min(data['scores']),
                'max_score': max(data['scores'])
            })
        
        logger.info(f"📈 Generated trends for {len(trends)} days")
        return {"trends": trends, "total_reviews": len(reviews)}
        
    except Exception as e:
        logger.error(f"Error getting trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/comparison")
async def compare_documents(doc1_id: str, doc2_id: str):
    """Compare two document versions"""
    try:
        outputs_dir = Path("outputs")
        
        # Load both documents
        docs = {}
        for doc_id, key in [(doc1_id, 'doc1'), (doc2_id, 'doc2')]:
            matching_dirs = [d for d in outputs_dir.iterdir() if d.is_dir() and doc_id in d.name]
            if not matching_dirs:
                raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
            
            results_path = matching_dirs[0] / "review_results.json"
            with open(results_path, 'r', encoding='utf-8') as f:
                docs[key] = json.load(f)
        
        # Calculate comparison metrics
        doc1_issues = docs['doc1'].get('structured_issues', [])
        doc2_issues = docs['doc2'].get('structured_issues', [])
        
        comparison = {
            'doc1': {
                'id': doc1_id,
                'title': docs['doc1'].get('document_info', {}).get('title', 'Doc 1'),
                'date': docs['doc1'].get('document_info', {}).get('review_date', ''),
                'total_issues': len(doc1_issues),
                'critical': sum(1 for i in doc1_issues if i.get('severity') == 'critical'),
                'high': sum(1 for i in doc1_issues if i.get('severity') == 'high'),
                'medium': sum(1 for i in doc1_issues if i.get('severity') == 'medium'),
                'low': sum(1 for i in doc1_issues if i.get('severity') == 'low'),
            },
            'doc2': {
                'id': doc2_id,
                'title': docs['doc2'].get('document_info', {}).get('title', 'Doc 2'),
                'date': docs['doc2'].get('document_info', {}).get('review_date', ''),
                'total_issues': len(doc2_issues),
                'critical': sum(1 for i in doc2_issues if i.get('severity') == 'critical'),
                'high': sum(1 for i in doc2_issues if i.get('severity') == 'high'),
                'medium': sum(1 for i in doc2_issues if i.get('severity') == 'medium'),
                'low': sum(1 for i in doc2_issues if i.get('severity') == 'low'),
            },
            'delta': {
                'total_issues': len(doc2_issues) - len(doc1_issues),
                'critical': sum(1 for i in doc2_issues if i.get('severity') == 'critical') - 
                           sum(1 for i in doc1_issues if i.get('severity') == 'critical'),
                'high': sum(1 for i in doc2_issues if i.get('severity') == 'high') - 
                       sum(1 for i in doc1_issues if i.get('severity') == 'high'),
                'medium': sum(1 for i in doc2_issues if i.get('severity') == 'medium') - 
                         sum(1 for i in doc1_issues if i.get('severity') == 'medium'),
                'low': sum(1 for i in doc2_issues if i.get('severity') == 'low') - 
                      sum(1 for i in doc1_issues if i.get('severity') == 'low'),
            },
            'improvement_percentage': 0
        }
        
        # Calculate improvement percentage
        if len(doc1_issues) > 0:
            improvement = ((len(doc1_issues) - len(doc2_issues)) / len(doc1_issues)) * 100
            comparison['improvement_percentage'] = round(improvement, 1)
        
        logger.info(f"🔄 Compared {doc1_id} vs {doc2_id}")
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/agents-performance")
async def get_agents_performance(days: int = 30):
    """Get agent performance analytics"""
    try:
        history_data = await get_review_history(days=days, limit=1000)
        reviews = history_data['reviews']
        
        # Aggregate agent stats
        agent_stats = {}
        
        for review in reviews:
            # Load full results to get agent reviews
            output_dir = Path(review['output_dir'])
            results_path = output_dir / "review_results.json"
            
            try:
                with open(results_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                agent_reviews = results.get('agent_reviews', {})
                structured_issues = results.get('structured_issues', [])
                
                for agent_name in agent_reviews.keys():
                    if agent_name in ['coordinator', 'final_evaluator']:
                        continue
                    
                    if agent_name not in agent_stats:
                        agent_stats[agent_name] = {
                            'name': agent_name.replace('_', ' ').title(),
                            'total_reviews': 0,
                            'total_issues_found': 0,
                            'critical_issues': 0,
                            'high_issues': 0,
                            'avg_issues_per_review': 0
                        }
                    
                    # Count issues found by this agent
                    agent_issues = [i for i in structured_issues if i.get('agent') == agent_name]
                    
                    agent_stats[agent_name]['total_reviews'] += 1
                    agent_stats[agent_name]['total_issues_found'] += len(agent_issues)
                    agent_stats[agent_name]['critical_issues'] += sum(1 for i in agent_issues if i.get('severity') == 'critical')
                    agent_stats[agent_name]['high_issues'] += sum(1 for i in agent_issues if i.get('severity') == 'high')
                    
            except Exception as e:
                logger.error(f"Error processing {results_path}: {e}")
                continue
        
        # Calculate averages
        for agent_name, stats in agent_stats.items():
            if stats['total_reviews'] > 0:
                stats['avg_issues_per_review'] = round(stats['total_issues_found'] / stats['total_reviews'], 1)
        
        # Sort by total issues found
        sorted_agents = sorted(agent_stats.values(), key=lambda x: x['total_issues_found'], reverse=True)
        
        logger.info(f"🤖 Generated performance stats for {len(sorted_agents)} agents")
        return {"agents": sorted_agents, "total_reviews": len(reviews)}
        
    except Exception as e:
        logger.error(f"Error getting agent performance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Run
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Backend...")
    print("📡 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

