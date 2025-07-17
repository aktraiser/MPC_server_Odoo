#!/usr/bin/env python3
"""
Main entry point for the Odoo MCP Server package
"""
import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())