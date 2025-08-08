import xmlrpc.client
import asyncio
import ssl
from typing import Any, Dict, List, Optional
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class OdooClient:
    """Async Odoo XML-RPC client for MCP server"""
    
    def __init__(self, url: str, database: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.database = database
        self.username = username
        self.password = password
        self.uid = None
        self.common = None
        self.models = None
        self._setup_ssl_context()
    
    def _setup_ssl_context(self):
        """Setup SSL context for secure connections"""
        self.ssl_context = ssl.create_default_context()
        # For development/testing, you might want to disable SSL verification
        # self.ssl_context.check_hostname = False
        # self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def connect(self):
        """Establish connection to Odoo server"""
        try:
            # Setup XML-RPC connections
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            
            # Authenticate
            self.uid = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.common.authenticate,
                self.database, self.username, self.password, {}
            )
            
            if not self.uid:
                raise Exception("Authentication failed")
            
            logger.info(f"Connected to Odoo as user ID: {self.uid}")
            
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise
    
    async def search_read(self, model: str, domain: List = None, fields: List = None, limit: int = 100) -> List[Dict]:
        """Search and read records from Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        domain = domain or []
        fields = fields or []
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, 'search_read',
                [domain],
                {'fields': fields, 'limit': limit}
            )
            return result
        except Exception as e:
            logger.error(f"Search read error: {str(e)}")
            raise
    
    async def create(self, model: str, values: Dict) -> int:
        """Create new record in Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        try:
            record_id = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, 'create',
                [values]
            )
            return record_id
        except Exception as e:
            logger.error(f"Create error: {str(e)}")
            raise
    
    async def write(self, model: str, ids: List[int], values: Dict) -> bool:
        """Update existing records in Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, 'write',
                [ids, values]
            )
            return result
        except Exception as e:
            logger.error(f"Write error: {str(e)}")
            raise
    
    async def unlink(self, model: str, ids: List[int]) -> bool:
        """Delete records from Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, 'unlink',
                [ids]
            )
            return result
        except Exception as e:
            logger.error(f"Unlink error: {str(e)}")
            raise
    
    async def call_method(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """Call custom method on Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        args = args or []
        kwargs = kwargs or {}
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, method,
                args, kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Method call error: {str(e)}")
            raise
    
    async def search(self, model: str, domain: List = None, limit: int = 100) -> List[int]:
        """Search for record IDs in Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        domain = domain or []
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, 'search',
                [domain],
                {'limit': limit}
            )
            return result
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise
    
    async def read(self, model: str, ids: List[int], fields: List = None) -> List[Dict]:
        """Read specific records from Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        fields = fields or []
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, 'read',
                [ids],
                {'fields': fields}
            )
            return result
        except Exception as e:
            logger.error(f"Read error: {str(e)}")
            raise
    
    async def get_models(self, filter_pattern: str = None) -> List[Dict]:
        """Get list of available Odoo models"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        try:
            # Get all models
            models = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                'ir.model', 'search_read',
                [[]],
                {'fields': ['model', 'name', 'info']}
            )
            
            # Filter if pattern provided
            if filter_pattern:
                models = [m for m in models if filter_pattern.lower() in m['model'].lower()]
            
            return models
        except Exception as e:
            logger.error(f"Get models error: {str(e)}")
            raise
    
    async def get_fields(self, model: str) -> Dict:
        """Get fields information for an Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        try:
            fields = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, 'fields_get',
                [],
                {}
            )
            return fields
        except Exception as e:
            logger.error(f"Get fields error: {str(e)}")
            raise
    
    async def count(self, model: str, domain: List = None) -> int:
        """Count records in Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated")
        
        domain = domain or []
        
        try:
            count = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, 'search_count',
                [domain]
            )
            return count
        except Exception as e:
            logger.error(f"Count error: {str(e)}")
            raise

    async def read_group(
        self,
        model: str,
        domain: List = None,
        fields: List[str] = None,
        groupby: List[str] = None,
        limit: int = 100,
        orderby: Optional[str] = None,
        lazy: bool = True,
    ) -> List[Dict[str, Any]]:
        """Aggregate records using Odoo read_group

        Parameters mirror Odoo's read_group:
        - domain: search domain
        - fields: list of fields with optional aggregate specs (e.g. "expected_revenue:sum")
        - groupby: list of fields to group by (e.g. ["stage_id"]) 
        - limit/orderby/lazy: passthrough options
        """
        if not self.uid:
            raise Exception("Not authenticated")

        domain = domain or []
        fields = fields or []
        groupby = groupby or []

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.models.execute_kw,
                self.database, self.uid, self.password,
                model, 'read_group',
                [domain, fields, groupby],
                {k: v for k, v in {
                    'limit': limit,
                    'orderby': orderby,
                    'lazy': lazy,
                }.items() if v is not None}
            )
            return result
        except Exception as e:
            logger.error(f"Read group error: {str(e)}")
            raise