#!/usr/bin/env python3
"""
VPR System Backend Runner
Run this file to start the FastAPI server
"""

import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    print("🚀 Starting VPR System Backend...")
    print(f"📍 Server will run on: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )