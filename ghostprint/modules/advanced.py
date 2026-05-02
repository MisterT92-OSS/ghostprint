"""
GhostPrint Advanced - Extended OSINT Sources
Shodan, Censys, Certificate Transparency, etc.
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime


class AdvancedInvestigator:
    """Advanced reconnaissance with multiple external sources"""
    
    def __init__(self, shodan_api_key: Optional[str] = None,
                 censys_api_id: Optional[str] = None,
                 censys_api_secret: Optional[str] = None,
                 verbose: bool = False):
        self.shodan_api_key = shodan_api_key
        self.censys_api_id = censys_api_id
        self.censys_api_secret = censys_api_secret
        self.verbose = verbose
        self.session = None
    
    async def _init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GhostPrint-Advanced/0.2.0'},
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    async def shodan_host_search(self, ip: str) -> Dict:
        """Search IP on Shodan"""
        if not self.shodan_api_key:
            return {'error': 'Shodan API key not configured'}
        
        try:
            url = f"https://api.shodan.io/shodan/host/{ip}?key={self.shodan_api_key}"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {'error': f'Shodan API error: {resp.status}'}
        except Exception as e:
            return {'error': str(e)}
    
    async def censys_search(self, query: str) -> Dict:
        """Search on Censys"""
        if not self.censys_api_id or not self.censys_api_secret:
            return {'error': 'Censys API credentials not configured'}
        
        try:
            url = "https://search.censys.io/api/v2/hosts/search"
            auth = aiohttp.BasicAuth(self.censys_api_id, self.censys_api_secret)
            params = {'q': query, 'per_page': 20}
            
            async with self.session.get(url, auth=auth, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {'error': f'Censys API error: {resp.status}'}
        except Exception as e:
            return {'error': str(e)}
    
    async def certificate_transparency(self, domain: str) -> List[Dict]:
        """Query Certificate Transparency logs via crt.sh"""
        try:
            url = f"https://crt.sh/?q={domain}&output=json"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Parse and deduplicate
                    certs = []
                    seen = set()
                    for cert in data:
                        name = cert.get('name_value', '')
                        if name and name not in seen:
                            seen.add(name)
                            certs.append({
                                'domain': name,
                                'issuer': cert.get('issuer_name'),
                                'not_before': cert.get('not_before'),
                                'not_after': cert.get('not_after'),
                                'entry_timestamp': cert.get('entry_timestamp')
                            })
                    return certs
                return []
        except Exception as e:
            return [{'error': str(e)}]
    
    async def threatcrowd_lookup(self, indicator: str, type_: str = 'domain') -> Dict:
        """Lookup on ThreatCrowd"""
        try:
            url = f"https://www.threatcrowd.org/searchApi/v2/{type_}/report/"
            params = {type_: indicator}
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {'error': f'ThreatCrowd error: {resp.status}'}
        except Exception as e:
            return {'error': str(e)}
    
    async def virustotal_lookup(self, indicator: str, api_key: Optional[str] = None) -> Dict:
        """Lookup on VirusTotal"""
        if not api_key:
            return {'error': 'VirusTotal API key not configured'}
        
        try:
            url = f"https://www.virustotal.com/api/v3/domains/{indicator}"
            headers = {'x-apikey': api_key}
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {'error': f'VT error: {resp.status}'}
        except Exception as e:
            return {'error': str(e)}
    
    async def urlscan_search(self, domain: str) -> Dict:
        """Search URLScan.io for domain scans"""
        try:
            url = "https://urlscan.io/api/v1/search/"
            params = {'q': f'page.domain:{domain}', 'size': 20}
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {'error': f'URLScan error: {resp.status}'}
        except Exception as e:
            return {'error': str(e)}
    
    async def spyse_lookup(self, domain: str, api_key: Optional[str] = None) -> Dict:
        """Lookup on Spyse"""
        if not api_key:
            return {'error': 'Spyse API key not configured'}
        
        try:
            url = f"https://spyse.com/api/data/domain/{domain}"
            headers = {'Authorization': f'Bearer {api_key}'}
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {'error': f'Spyse error: {resp.status}'}
        except Exception as e:
            return {'error': str(e)}
    
    def investigate(self, target: str, target_type: str = 'domain',
                   use_shodan: bool = False,
                   use_censys: bool = False,
                   use_ct: bool = True,
                   use_threat_intel: bool = True) -> Dict:
        """Run advanced investigation"""
        
        async def run():
            await self._init_session()
            results = {
                'target': target,
                'type': target_type,
                'timestamp': datetime.now().isoformat(),
                'shodan': {},
                'censys': {},
                'certificate_transparency': [],
                'threat_intelligence': {},
                'urlscan': {}
            }
            
            # Certificate Transparency
            if use_ct and target_type == 'domain':
                results['certificate_transparency'] = await self.certificate_transparency(target)
            
            # Threat Intelligence
            if use_threat_intel:
                if target_type == 'domain':
                    results['threat_intelligence']['threatcrowd'] = await self.threatcrowd_lookup(target, 'domain')
                elif target_type == 'ip':
                    results['threat_intelligence']['threatcrowd'] = await self.threatcrowd_lookup(target, 'ip')
            
            # URLScan
            if target_type == 'domain':
                results['urlscan'] = await self.urlscan_search(target)
            
            # Shodan (requires API key)
            if use_shodan and target_type == 'ip':
                results['shodan'] = await self.shodan_host_search(target)
            
            # Censys (requires API key)
            if use_censys:
                query = target if target_type == 'ip' else f"services.http.request.host: {target}"
                results['censys'] = await self.censys_search(query)
            
            if self.session:
                await self.session.close()
            
            return results
        
        return asyncio.run(run())