#!/usr/bin/env python3
"""
run_api.py - Main entry point to start the Stock Trader API server.

This script starts the FastAPI server with proper path configuration
for the new directory structure.

Usage:
    python run_api.py

The API will be available at http://127.0.0.1:8001
Open frontend/index.html in your browser to use the dashboard.
"""

import sys
from pathlib import Path

# Add src directory to Python path so imports work correctly
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

if __name__ == "__main__":
    import uvicorn
    from api import app
    
    print("\n" + "="*70)
    print("🚀 Penny Buzz Stock Trader API")
    print("="*70)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"API Server: http://127.0.0.1:8001")
    print(f"Frontend: Open {PROJECT_ROOT / 'frontend' / 'index.html'} in browser")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=False
    )
