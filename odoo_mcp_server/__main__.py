#!/usr/bin/env python3
"""
Main entry point for the Odoo MCP Server package
"""
import os
import asyncio
from .main import main
from .http_server import run_http_server

if __name__ == "__main__":
    # Check if we're running on Render or similar platform
    if os.getenv("RENDER") or os.getenv("PORT"):
        # Run HTTP server wrapper for cloud deployment
        run_http_server()
    else:
        # Run normal MCP server for local/direct usage
        asyncio.run(main())