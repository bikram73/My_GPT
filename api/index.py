"""
Vercel serverless function entry point for FastAPI
"""
import sys
from pathlib import Path
from mangum import Mangum

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the FastAPI app
from main import app

# Wrap FastAPI with Mangum for serverless
handler = Mangum(app, lifespan="off")



