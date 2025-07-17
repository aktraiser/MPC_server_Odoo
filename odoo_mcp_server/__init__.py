"""
Odoo MCP Server - Model Context Protocol server for Odoo integration
"""

__version__ = "0.1.0"
__author__ = "Developer"
__email__ = "dev@example.com"

from .main import OdooMCPServer
from .odoo_client import OdooClient

__all__ = ["OdooMCPServer", "OdooClient"]