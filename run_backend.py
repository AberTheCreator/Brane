#!/usr/bin/env python3
"""
Brane AI Backend Launcher
========================

Sets environment variables and starts the FastAPI backend.
"""

import os
import uvicorn

# Set Redis environment variables
os.environ["REDIS_HOST"] = "redis-19369.c275.us-east-1-4.ec2.redns.redis-cloud.com"
os.environ["REDIS_PORT"] = "19369"
os.environ["REDIS_PASSWORD"] = "********"

if __name__ == "__main__":
    print("🧠 Starting Brane AI Redis Backend...")
    print(f"Redis Host: {os.environ['REDIS_HOST']}")
    print(f"Redis Port: {os.environ['REDIS_PORT']}")
    print("="*50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )