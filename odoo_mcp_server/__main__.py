#!/usr/bin/env python3
"""
Main entry point for the Odoo MCP Server package
"""
from .http_server import run_http_server

if __name__ == "__main__":
    # Always run HTTP server for API access
    run_http_server()