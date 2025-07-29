#!/usr/bin/env python3
"""
Startup script for GUI-Actor FastAPI server
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Start GUI-Actor FastAPI server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to (default: 8080)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], 
                       help="Log level (default: info)")
    
    args = parser.parse_args()
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("Error: main.py not found in current directory")
        print("Please run this script from the directory containing main.py")
        sys.exit(1)
    
    # Set environment variables
    os.environ.setdefault("MAX_PIXELS", str(3200 * 1800))
    
    print(f"Starting GUI-Actor FastAPI server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Workers: {args.workers}")
    print(f"Log level: {args.log_level}")
    print(f"Auto-reload: {args.reload}")
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,
            log_level=args.log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 