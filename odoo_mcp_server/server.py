#!/usr/bin/env python3
import os
import sys
import asyncio
import logging
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .odoo_client import OdooClient
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OdooMCPServer:
    def __init__(self):
        self.server = Server("odoo-mcp-server")
        self.odoo_client = None
        self.connection_params = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="odoo_connect",
                    description="Connect to Odoo instance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "Odoo server URL"},
                            "database": {"type": "string", "description": "Database name"},
                            "username": {"type": "string", "description": "Username"},
                            "password": {"type": "string", "description": "Password"}
                        },
                        "required": ["url", "database", "username", "password"]
                    }
                ),
                Tool(
                    name="odoo_search",
                    description="Search records in Odoo model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "Odoo model name"},
                            "domain": {"type": "array", "description": "Search domain"},
                            "fields": {"type": "array", "description": "Fields to retrieve"},
                            "limit": {"type": "integer", "description": "Maximum records"}
                        },
                        "required": ["model"]
                    }
                ),
                Tool(
                    name="odoo_create",
                    description="Create new record in Odoo",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "Odoo model name"},
                            "values": {"type": "object", "description": "Record values"}
                        },
                        "required": ["model", "values"]
                    }
                ),
                Tool(
                    name="odoo_write",
                    description="Update existing records in Odoo",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "Odoo model name"},
                            "ids": {"type": "array", "description": "Record IDs to update"},
                            "values": {"type": "object", "description": "Values to update"}
                        },
                        "required": ["model", "ids", "values"]
                    }
                ),
                Tool(
                    name="odoo_unlink",
                    description="Delete records from Odoo",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "Odoo model name"},
                            "ids": {"type": "array", "description": "Record IDs to delete"}
                        },
                        "required": ["model", "ids"]
                    }
                ),
                Tool(
                    name="odoo_call",
                    description="Call method on Odoo model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "Odoo model name"},
                            "method": {"type": "string", "description": "Method name"},
                            "args": {"type": "array", "description": "Method arguments"},
                            "kwargs": {"type": "object", "description": "Method keyword arguments"}
                        },
                        "required": ["model", "method"]
                    }
                ),
                Tool(
                    name="odoo_get_models",
                    description="Get list of available Odoo models",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter": {"type": "string", "description": "Filter models by name pattern"}
                        }
                    }
                ),
                Tool(
                    name="odoo_get_fields",
                    description="Get fields information for an Odoo model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "Odoo model name"}
                        },
                        "required": ["model"]
                    }
                ),
                Tool(
                    name="odoo_count",
                    description="Count records in Odoo model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "Odoo model name"},
                            "domain": {"type": "array", "description": "Search domain"}
                        },
                        "required": ["model"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "odoo_connect":
                    return await self._handle_connect(arguments)
                elif name == "odoo_search":
                    return await self._handle_search(arguments)
                elif name == "odoo_create":
                    return await self._handle_create(arguments)
                elif name == "odoo_write":
                    return await self._handle_write(arguments)
                elif name == "odoo_unlink":
                    return await self._handle_unlink(arguments)
                elif name == "odoo_call":
                    return await self._handle_call(arguments)
                elif name == "odoo_get_models":
                    return await self._handle_get_models(arguments)
                elif name == "odoo_get_fields":
                    return await self._handle_get_fields(arguments)
                elif name == "odoo_count":
                    return await self._handle_count(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error handling tool {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _handle_connect(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle Odoo connection"""
        try:
            # Use provided args or fallback to environment variables
            url = args.get("url") or os.getenv("ODOO_URL")
            database = args.get("database") or os.getenv("ODOO_DATABASE")
            username = args.get("username") or os.getenv("ODOO_USERNAME")
            password = args.get("password") or os.getenv("ODOO_PASSWORD")
            
            if not all([url, database, username, password]):
                return [TextContent(type="text", text="Missing connection parameters. Provide url, database, username, password or set environment variables.")]
            
            self.odoo_client = OdooClient(
                url=url,
                database=database,
                username=username,
                password=password
            )
            await self.odoo_client.connect()
            
            # Store connection params for reconnection
            self.connection_params = {
                "url": url,
                "database": database,
                "username": username,
                "password": password
            }
            
            return [TextContent(type="text", text=f"Successfully connected to Odoo at {url} (database: {database})")]
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return [TextContent(type="text", text=f"Connection failed: {str(e)}")]
    
    async def _handle_search(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle record search"""
        if not self.odoo_client:
            return [TextContent(type="text", text="Not connected to Odoo. Use odoo_connect first.")]
        
        try:
            result = await self.odoo_client.search_read(
                model=args["model"],
                domain=args.get("domain", []),
                fields=args.get("fields", []),
                limit=args.get("limit", 100)
            )
            return [TextContent(type="text", text=f"Found {len(result)} records: {result}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Search failed: {str(e)}")]
    
    async def _handle_create(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle record creation"""
        if not self.odoo_client:
            return [TextContent(type="text", text="Not connected to Odoo. Use odoo_connect first.")]
        
        try:
            record_id = await self.odoo_client.create(
                model=args["model"],
                values=args["values"]
            )
            return [TextContent(type="text", text=f"Created record with ID: {record_id}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Create failed: {str(e)}")]
    
    async def _handle_write(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle record update"""
        if not self.odoo_client:
            return [TextContent(type="text", text="Not connected to Odoo. Use odoo_connect first.")]
        
        try:
            result = await self.odoo_client.write(
                model=args["model"],
                ids=args["ids"],
                values=args["values"]
            )
            return [TextContent(type="text", text=f"Updated {len(args['ids'])} records: {result}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Update failed: {str(e)}")]
    
    async def _handle_unlink(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle record deletion"""
        if not self.odoo_client:
            return [TextContent(type="text", text="Not connected to Odoo. Use odoo_connect first.")]
        
        try:
            result = await self.odoo_client.unlink(
                model=args["model"],
                ids=args["ids"]
            )
            return [TextContent(type="text", text=f"Deleted {len(args['ids'])} records: {result}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Delete failed: {str(e)}")]
    
    async def _handle_call(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle method call"""
        if not self.odoo_client:
            return [TextContent(type="text", text="Not connected to Odoo. Use odoo_connect first.")]
        
        try:
            result = await self.odoo_client.call_method(
                model=args["model"],
                method=args["method"],
                args=args.get("args", []),
                kwargs=args.get("kwargs", {})
            )
            return [TextContent(type="text", text=f"Method result: {result}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Method call failed: {str(e)}")]
    
    async def _handle_get_models(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle get models request"""
        if not self.odoo_client:
            return [TextContent(type="text", text="Not connected to Odoo. Use odoo_connect first.")]
        
        try:
            models = await self.odoo_client.get_models(args.get("filter"))
            return [TextContent(type="text", text=f"Available models: {json.dumps(models, indent=2)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Get models failed: {str(e)}")]
    
    async def _handle_get_fields(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle get fields request"""
        if not self.odoo_client:
            return [TextContent(type="text", text="Not connected to Odoo. Use odoo_connect first.")]
        
        try:
            fields = await self.odoo_client.get_fields(args["model"])
            return [TextContent(type="text", text=f"Fields for {args['model']}: {json.dumps(fields, indent=2)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Get fields failed: {str(e)}")]
    
    async def _handle_count(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle count records request"""
        if not self.odoo_client:
            return [TextContent(type="text", text="Not connected to Odoo. Use odoo_connect first.")]
        
        try:
            count = await self.odoo_client.count(
                model=args["model"],
                domain=args.get("domain", [])
            )
            return [TextContent(type="text", text=f"Record count for {args['model']}: {count}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Count failed: {str(e)}")]

async def main():
    """Main entry point for the MCP server"""
    server_instance = OdooMCPServer()
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())