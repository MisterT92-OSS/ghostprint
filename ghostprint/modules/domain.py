"""
GhostPrint - Domain Investigation Module
Reconnaissance: subdomains, DNS, WHOIS, technologies
"""
import asyncio
import aiohttp
import dns.resolver
import whois
from typing import Dict, List, Optional
from datetime import datetime


class DomainInvestigator:
    """Investigate domains for OSINT"""
    
    # Common subdomains to check
    SUBDOMAIN_WORDLIST = [
        'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
        'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'ns3', 'm', 'imap',
        'test', 'ns', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news',
        'vpn', 'ns4', 'email', 'webmaster', 'api', 'support', 'mobile', 'dns',
        'shop', 'www1', 'chat', 'app', 'portal', 'demo', 'home', 'wiki',
        'store', 'panel', 'cdn', 'media', 'static', 'assets', 'img', 'images'
    ]
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = None
    
    async def _init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GhostPrint/0.1.0'},
                timeout=aiohttp.ClientTimeout(total=5)
            )
    
    def _check_whois(self, domain: str) -> Dict:
        """Perform WHOIS lookup"""
        result = {
            'registrar': None,
            'creation_date': None,
            'expiration_date': None,
            'name_servers': [],
            'status': None,
            'error': None
        }
        
        try:
            w = whois.whois(domain)
            result['registrar'] = w.registrar
            result['creation_date'] = str(w.creation_date)
            result['expiration_date'] = str(w.expiration_date)
            result['name_servers'] = w.name_servers if isinstance(w.name_servers, list) else [w.name_servers]
            result['status'] = w.status
        except Exception as e:
            result['error'] = str(e)
            if self.verbose:
                print(f"WHOIS error: {e}")
        
        return result
    
    def _check_dns(self, domain: str) -> Dict:
        """Check DNS records"""
        records = {
            'A': [],
            'AAAA': [],
            'MX': [],
            'NS': [],
            'TXT': [],
            'CNAME': [],
            'error': None
        }
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
        
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                records[rtype] = [str(rdata) for rdata in answers]
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NXDOMAIN:
                records['error'] = f"Domain {domain} does not exist"
            except Exception as e:
                if self.verbose:
                    print(f"DNS {rtype} error: {e}")
        
        return records
    
    async def _check_subdomain(self, domain: str, subdomain: str) -> Optional[str]:
        """Check if a subdomain exists"""
        full_domain = f"{subdomain}.{domain}"
        
        try:
            # Try DNS resolution first
            answers = dns.resolver.resolve(full_domain, 'A')
            if answers:
                return full_domain
        except:
            pass
        
        # Try HTTP check as fallback
        try:
            url = f"http://{full_domain}"
            async with self.session.get(url, allow_redirects=True) as resp:
                if resp.status < 400:
                    return full_domain
        except:
            pass
        
        return None
    
    async def _enumerate_subdomains(self, domain: str) -> List[str]:
        """Enumerate common subdomains"""
        await self._init_session()
        
        tasks = [
            self._check_subdomain(domain, sub)
            for sub in self.SUBDOMAIN_WORDLIST
        ]
        
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]
    
    def investigate(self, domain: str, enumerate_subdomains: bool = True,
                   check_dns: bool = True, check_whois: bool = True,
                   detect_tech: bool = False) -> Dict:
        """
        Main investigation method
        
        Args:
            domain: Domain to investigate
            enumerate_subdomains: Find subdomains
            check_dns: Check DNS records
            check_whois: Perform WHOIS lookup
            detect_tech: Detect technologies (requires additional requests)
            
        Returns:
            Dictionary with investigation results
        """
        results = {
            'domain': domain,
            'subdomains': [],
            'dns': {},
            'whois': {},
            'technologies': [],
            'status': 'completed'
        }
        
        # WHOIS lookup
        if check_whois:
            results['whois'] = self._check_whois(domain)
        
        # DNS records
        if check_dns:
            results['dns'] = self._check_dns(domain)
        
        # Subdomain enumeration
        if enumerate_subdomains:
            async def run_subdomain_enum():
                await self._init_session()
                subs = await self._enumerate_subdomains(domain)
                results['subdomains'] = subs
                if self.session:
                    await self.session.close()
            
            asyncio.run(run_subdomain_enum())
        
        return results


if __name__ == '__main__':
    investigator = DomainInvestigator(verbose=True)
    results = investigator.investigate('github.com')
    
    print(f"\nDomain: {results['domain']}")
    print(f"Subdomains found: {len(results['subdomains'])}")
    print(f"WHOIS: {results['whois']}")
    print(f"DNS: {results['dns']}")