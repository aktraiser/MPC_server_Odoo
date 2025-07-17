#!/usr/bin/env python3
"""
HTTP API server for Odoo MCP functionality
Provides REST endpoints for Odoo operations instead of stdio communication
"""
import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from .odoo_client import OdooClient
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Odoo MCP HTTP API Server", version="0.2.0")

# Global Odoo client instance
odoo_client: Optional[OdooClient] = None
connection_params: Optional[Dict[str, str]] = None

# Pydantic models for request/response validation
class ConnectionRequest(BaseModel):
    url: str = Field(..., description="Odoo server URL")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class SearchRequest(BaseModel):
    model: str = Field(..., description="Odoo model name")
    domain: List[List[Any]] = Field(default=[], description="Search domain")
    fields: List[str] = Field(default=[], description="Fields to retrieve")
    limit: int = Field(default=100, description="Maximum records")

class CreateRequest(BaseModel):
    model: str = Field(..., description="Odoo model name")
    values: Dict[str, Any] = Field(..., description="Record values")

class WriteRequest(BaseModel):
    model: str = Field(..., description="Odoo model name")
    ids: List[int] = Field(..., description="Record IDs to update")
    values: Dict[str, Any] = Field(..., description="Values to update")

class UnlinkRequest(BaseModel):
    model: str = Field(..., description="Odoo model name")
    ids: List[int] = Field(..., description="Record IDs to delete")

class CallMethodRequest(BaseModel):
    model: str = Field(..., description="Odoo model name")
    method: str = Field(..., description="Method name")
    args: List[Any] = Field(default=[], description="Method arguments")
    kwargs: Dict[str, Any] = Field(default={}, description="Method keyword arguments")

class GetModelsRequest(BaseModel):
    filter: Optional[str] = Field(default=None, description="Filter models by name pattern")

class GetFieldsRequest(BaseModel):
    model: str = Field(..., description="Odoo model name")

class CountRequest(BaseModel):
    model: str = Field(..., description="Odoo model name")
    domain: List[List[Any]] = Field(default=[], description="Search domain")

# Helper function to check connection
def check_connection():
    """Check if connected to Odoo"""
    if not odoo_client:
        raise HTTPException(status_code=400, detail="Not connected to Odoo. Use /connect endpoint first.")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Odoo MCP HTTP API Server",
        "version": "0.2.0",
        "connected": odoo_client is not None,
        "endpoints": [
            "/connect",
            "/search",
            "/create",
            "/write",
            "/unlink",
            "/call",
            "/models",
            "/fields",
            "/count"
        ]
    }

@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "connected": odoo_client is not None
    }

@app.post("/connect")
async def connect(request: ConnectionRequest):
    """Connect to Odoo instance"""
    global odoo_client, connection_params
    
    try:
        # Use provided args or fallback to environment variables
        url = request.url or os.getenv("ODOO_URL")
        database = request.database or os.getenv("ODOO_DATABASE")
        username = request.username or os.getenv("ODOO_USERNAME")
        password = request.password or os.getenv("ODOO_PASSWORD")
        
        if not all([url, database, username, password]):
            raise HTTPException(
                status_code=400,
                detail="Missing connection parameters. Provide url, database, username, password or set environment variables."
            )
        
        odoo_client = OdooClient(
            url=url,
            database=database,
            username=username,
            password=password
        )
        await odoo_client.connect()
        
        # Store connection params for reconnection
        connection_params = {
            "url": url,
            "database": database,
            "username": username,
            "password": password
        }
        
        return {
            "status": "success",
            "message": f"Successfully connected to Odoo at {url} (database: {database})"
        }
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")

@app.post("/search")
async def search(request: SearchRequest):
    """Search records in Odoo model"""
    check_connection()
    
    try:
        result = await odoo_client.search_read(
            model=request.model,
            domain=request.domain,
            fields=request.fields,
            limit=request.limit
        )
        return {
            "status": "success",
            "count": len(result),
            "records": result
        }
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/create")
async def create(request: CreateRequest):
    """Create new record in Odoo"""
    check_connection()
    
    try:
        record_id = await odoo_client.create(
            model=request.model,
            values=request.values
        )
        return {
            "status": "success",
            "id": record_id,
            "message": f"Created record with ID: {record_id}"
        }
    except Exception as e:
        logger.error(f"Create error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Create failed: {str(e)}")

@app.post("/write")
async def write(request: WriteRequest):
    """Update existing records in Odoo"""
    check_connection()
    
    try:
        result = await odoo_client.write(
            model=request.model,
            ids=request.ids,
            values=request.values
        )
        return {
            "status": "success",
            "updated": len(request.ids),
            "result": result,
            "message": f"Updated {len(request.ids)} records"
        }
    except Exception as e:
        logger.error(f"Write error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@app.post("/unlink")
async def unlink(request: UnlinkRequest):
    """Delete records from Odoo"""
    check_connection()
    
    try:
        result = await odoo_client.unlink(
            model=request.model,
            ids=request.ids
        )
        return {
            "status": "success",
            "deleted": len(request.ids),
            "result": result,
            "message": f"Deleted {len(request.ids)} records"
        }
    except Exception as e:
        logger.error(f"Unlink error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@app.post("/call")
async def call_method(request: CallMethodRequest):
    """Call method on Odoo model"""
    check_connection()
    
    try:
        result = await odoo_client.call_method(
            model=request.model,
            method=request.method,
            args=request.args,
            kwargs=request.kwargs
        )
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Call error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Method call failed: {str(e)}")

@app.post("/models")
async def get_models(request: GetModelsRequest):
    """Get list of available Odoo models"""
    check_connection()
    
    try:
        models = await odoo_client.get_models(request.filter)
        return {
            "status": "success",
            "count": len(models),
            "models": models
        }
    except Exception as e:
        logger.error(f"Get models error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get models failed: {str(e)}")

@app.post("/fields")
async def get_fields(request: GetFieldsRequest):
    """Get fields information for an Odoo model"""
    check_connection()
    
    try:
        fields = await odoo_client.get_fields(request.model)
        return {
            "status": "success",
            "model": request.model,
            "fields": fields
        }
    except Exception as e:
        logger.error(f"Get fields error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get fields failed: {str(e)}")

@app.post("/count")
async def count(request: CountRequest):
    """Count records in Odoo model"""
    check_connection()
    
    try:
        count = await odoo_client.count(
            model=request.model,
            domain=request.domain
        )
        return {
            "status": "success",
            "model": request.model,
            "count": count
        }
    except Exception as e:
        logger.error(f"Count error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Count failed: {str(e)}")

def run_http_server():
    """Run the HTTP server"""
    port = int(os.getenv("PORT", "8000"))
    host = "0.0.0.0"
    
    logger.info(f"Starting Odoo MCP HTTP API Server on {host}:{port}")
    logger.info("Available endpoints:")
    logger.info("  POST /connect - Connect to Odoo")
    logger.info("  POST /search - Search records")
    logger.info("  POST /create - Create records")
    logger.info("  POST /write - Update records")
    logger.info("  POST /unlink - Delete records")
    logger.info("  POST /call - Call Odoo methods")
    logger.info("  POST /models - List available models")
    logger.info("  POST /fields - Get model fields")
    logger.info("  POST /count - Count records")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_http_server()