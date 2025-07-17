#!/usr/bin/env python3
"""
HTTP wrapper for MCP server to enable deployment on platforms like Render
"""
import os
import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Odoo MCP Server", version="0.1.0")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Odoo MCP Server",
        "version": "0.1.0",
        "message": "This is an MCP server for Odoo integration. Use MCP client to connect."
    }

@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "healthy"}

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    MCP endpoint - Note: This is a placeholder.
    Real MCP communication happens via stdio, not HTTP.
    This server keeps the container running on Render.
    """
    return JSONResponse(
        status_code=501,
        content={
            "error": "Not Implemented",
            "message": "MCP servers communicate via stdio, not HTTP. Use an MCP client to connect."
        }
    )

def run_http_server():
    """Run the HTTP server"""
    port = int(os.getenv("PORT", "8000"))
    host = "0.0.0.0"
    
    logger.info(f"Starting HTTP server on {host}:{port}")
    logger.info("Note: This is a wrapper to keep the container running on Render.")
    logger.info("MCP communication happens via stdio when connected through an MCP client.")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_http_server()