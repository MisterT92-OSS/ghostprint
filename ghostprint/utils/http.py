"""
GhostPrint - Async HTTP Utilities
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional


class AsyncHTTPClient:
    """Async HTTP client for concurrent requests"""
    
    def __init__(self, max_connections: int = 100, timeout: int = 10):
        self.max_connections = max_connections
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=10,
            enable_cleanup_closed=True,
            force_close=True,
        )
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        await self.open()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def open(self):
        """Initialize session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'GhostPrint/0.1.0 OSINT Tool'
                }
            )
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Perform GET request"""
        if not self.session:
            await self.open()
        return await self.session.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Perform POST request"""
        if not self.session:
            await self.open()
        return await self.session.post(url, **kwargs)
    
    async def fetch_all(self, urls: List[str], **kwargs) -> List:
        """Fetch multiple URLs concurrently"""
        if not self.session:
            await self.open()
        
        tasks = [self._fetch(url, **kwargs) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _fetch(self, url: str, **kwargs) -> Dict:
        """Fetch single URL with error handling"""
        try:
            async with self.session.get(url, **kwargs) as response:
                return {
                    'url': url,
                    'status': response.status,
                    'headers': dict(response.headers),
                    'text': await response.text()
                }
        except Exception as e:
            return {
                'url': url,
                'error': str(e)
            }


def run_async(coroutine):
    """Helper to run async code from sync context"""
    return asyncio.run(coroutine)