"""
FastAPI Backend SEMPLIFICATO - Test Version
"""

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import json
from datetime import datetime
from pathlib import Path

# Initialize FastAPI
app = FastAPI(
    title="Agentic Reviewer API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
active_connections: List[WebSocket] = []

# Models
class ReviewConfig(BaseModel):
    output_language: str = ""
    enable_iterative: bool = False
    max_iterations: int = 3
    target_score: float = 85.0
    enable_python_tools: bool = False
    enable_interactive: bool = False
    enable_deep_review: bool = False

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Agentic Reviewer API",
        "version": "2.0.0-simple",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/review/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and start review"""
    try:
        # Save file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "status": "started",
            "message": "Review started (simplified version)",
            "review_id": review_id,
            "output_dir": ""
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected"
        })
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong", "data": data})
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SIMPLIFIED Backend...")
    print("📡 Backend will be at: http://localhost:8000")
    print("📚 Docs at: http://localhost:8000/docs")
    uvicorn.run(
        app,  # Oggetto app direttamente!
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabilitato per evitare problemi
        log_level="info"
    )

