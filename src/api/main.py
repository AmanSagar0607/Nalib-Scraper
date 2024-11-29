from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.database.mongo_client import MongoDBClient
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

# Load environment variables
load_dotenv()

app = FastAPI(title="Nailib Sample API", description="API for accessing IB Math AI SL samples")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB client
db_client = MongoDBClient(
    uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
    db_name=os.getenv("DB_NAME", "nailib_samples"),
    collection_name=os.getenv("COLLECTION_NAME", "samples")
)

# Setup static and template directories
static_dir = os.path.join(project_root, "static")
templates_dir = os.path.join(project_root, "templates")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page showing sample statistics and search interface."""
    try:
        stats = db_client.get_stats()
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "stats": stats}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/samples", response_model=List[Dict[str, Any]])
async def get_samples(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None
):
    """Get paginated list of samples with optional search."""
    try:
        query = {}
        if search:
            query = {"$text": {"$search": search}}
            
        samples = db_client.get_samples(
            query=query,
            skip=skip,
            limit=limit
        )
        
        return samples
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/samples/{sample_id}")
async def get_sample(sample_id: str):
    """Get a specific sample by ID."""
    try:
        sample = db_client.get_sample_by_id(sample_id)
        if not sample:
            raise HTTPException(status_code=404, detail="Sample not found")
        return sample
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get collection statistics."""
    try:
        stats = db_client.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_samples(
    query: str,
    skip: int = 0,
    limit: int = 10
):
    """Search samples using text search."""
    try:
        search_query = {
            "$text": {"$search": query}
        }
        samples = db_client.get_samples(search_query, skip, limit)
        return samples
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)