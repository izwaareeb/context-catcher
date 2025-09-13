from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.assistant import get_yesterday_recap, get_today_plan, process_command, get_system_status

app = FastAPI(title="Context Catcher API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend) - FIXED PATH
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class CommandRequest(BaseModel):
    command: str

@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Context Catcher"}

@app.get("/status")
async def get_status():
    """Get system status."""
    try:
        return get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/briefing/yesterday")
async def yesterday_briefing():
    """Get yesterday's recap briefing."""
    try:
        return get_yesterday_recap()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/briefing/today")
async def today_briefing():
    """Get today's plan briefing."""
    try:
        return get_today_plan()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/command")
async def execute_command(request: CommandRequest):
    """Process and execute a voice command."""
    try:
        return process_command(request.command)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events")
async def get_events(limit: int = 10, source: str = None):
    """Get recent events."""
    try:
        from backend.organizer import ContextOrganizer
        organizer = ContextOrganizer()
        
        # Get events from database
        cur = organizer.conn.cursor()
        if source:
            cur.execute("SELECT * FROM events WHERE source = ? ORDER BY timestamp DESC LIMIT ?", (source, limit))
        else:
            cur.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
        
        events = cur.fetchall()
        return {"events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/threads")
async def get_threads():
    """Get organized threads."""
    try:
        from backend.organizer import ContextOrganizer
        organizer = ContextOrganizer()
        threads = organizer.get_all_threads()
        return {"threads": threads, "count": len(threads)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Initialize database
    from backend.db import init_db
    init_db()
    
    print("�� Starting Context Catcher Server...")
    print("📱 Frontend: http://localhost:8000")
    print("🔧 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)