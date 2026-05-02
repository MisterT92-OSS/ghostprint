"""
GhostPrint - Data Breach Intelligence
Multi-source breach database queries
"""
import asyncio
import aiohttp
import hashlib
from typing import Dict, List, Optional


class BreachInvestigator:
    """Query multiple breach databases"""
    
    BREACH_SOURCES = {
        'haveibeenpwned': {
            'url': 'https://haveibeenpwned.com/api/v3/breachedaccount/{}',
            'auth_required': True,
        },
        'dehashed': {
            'url': 'https://api.dehashed.com/search',
            'auth_required': True,
        },
        'leaklookup': {
            'url': 'https://leak-lookup.com/api/search',
            'auth_required': True,
        }
    }
    
    def __init__(self, hibp_api_key: Optional[str] = None,
                 dehashed_email: Optional[str] = None,
                 dehashed_api_key: Optional[str] = None,
                 leaklookup_api_key: Optional[str] = None,
                 verbose: bool = False):
        self.hibp_api_key = hibp_api_key
        self.dehashed_email = dehashed_email
        self.dehashed_api_key = dehashed_api_key
        self.leaklookup_api_key = leaklookup_api_key
        self.verbose = verbose
        self.session = None
    
    async def _init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GhostPrint-Breach/0.2.0'},
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    async def check_haveibeenpwned(self, email: str) -> Dict:
        """Check HaveIBeenPwned for email breaches"""
        if not self.hibp_api_key:
            return {'status': 'no_api_key', 'breaches': []}
        
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {
                'hibp-api-key': self.hibp_api_key,
                'User-Agent': 'GhostPrint-OSINT'
            }
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        'status': 'found',
                        'breach_count': len(data),
                        'breaches': [
                            {
                                'name': b.get('Name'),
                                'title': b.get('Title'),
                                'domain': b.get('Domain'),
                                'breach_date': b.get('BreachDate'),
                                'added_date': b.get('AddedDate'),
                                'description': b.get('Description'),
                                'data_classes': b.get('DataClasses', []),
                                'is_verified': b.get('IsVerified'),
                                'is_fabricated': b.get('IsFabricated'),
                                'is_sensitive': b.get('IsSensitive'),
                                'is_retired': b.get('IsRetired'),
                                'is_spam_list': b.get('IsSpamList'),
                            }
                            for b in data
                        ]
                    }
                elif resp.status == 404:
                    return {'status': 'not_found', 'breaches': []}
                else:
                    return {'status': f'error_{resp.status}', 'breaches': []}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'breaches': []}
    
    async def check_dehashed(self, query: str, type_: str = 'email') -> Dict:
        """Query Dehashed database"""
        if not self.dehashed_email or not self.dehashed_api_key:
            return {'status': 'no_api_key', 'entries': []}
        
        try:
            url = "https://api.dehashed.com/search"
            params = {'query': f"{type_}:{query}"}
            auth = aiohttp.BasicAuth(self.dehashed_email, self.dehashed_api_key)
            
            async with self.session.get(url, auth=auth, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        'status': 'success',
                        'total': data.get('total', 0),
                        'entries': data.get('entries', [])
                    }
                return {'status': f'error_{resp.status}', 'entries': []}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'entries': []}
    
    async def check_leaklookup(self, query: str, type_: str = 'email') -> Dict:
        """Query LeakLookup database"""
        if not self.leaklookup_api_key:
            return {'status': 'no_api_key', 'leaks': []}
        
        try:
            url = "https://leak-lookup.com/api/search"
            data = {
                'key': self.leaklookup_api_key,
                'type': type_,
                'query': query
            }
            async with self.session.post(url, data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return {
                        'status': 'success',
                        'leaks': result.get('message', [])
                    }
                return {'status': f'error_{resp.status}', 'leaks': []}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'leaks': []}
    
    async def check_public_pastes(self, email: str) -> List[Dict]:
        """Check for email in public pastes"""
        pastes = []
        
        # Pastebin search (limited)
        try:
            url = "https://psbdmp.ws/api/v3/search/{}".format(email.split('@')[0])
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for paste in data.get('data', []):
                        pastes.append({
                            'source': 'psbdmp',
                            'id': paste.get('id'),
                            'title': paste.get('title'),
                            'date': paste.get('time')
                        })
        except:
            pass
        
        return pastes
    
    def investigate(self, email: str) -> Dict:
        """Full breach investigation"""
        
        async def run():
            await self._init_session()
            
            results = {
                'email': email,
                'hibp': {},
                'dehashed': {},
                'leaklookup': {},
                'pastes': []
            }
            
            # Run all checks concurrently
            tasks = [
                self.check_haveibeenpwned(email),
                self.check_dehashed(email),
                self.check_leaklookup(email),
                self.check_public_pastes(email)
            ]
            
            hibp, dehashed, leaklookup, pastes = await asyncio.gather(*tasks)
            
            results['hibp'] = hibp
            results['dehashed'] = dehashed
            results['leaklookup'] = leaklookup
            results['pastes'] = pastes
            results['total_breaches'] = (
                len(hibp.get('breaches', [])) +
                dehashed.get('total', 0) +
                len(leaklookup.get('leaks', []))
            )
            
            if self.session:
                await self.session.close()
            
            return results
        
        return asyncio.run(run())
    
    def check_password_strength(self, password: str) -> Dict:
        """Check password strength and commonality"""
        # Calculate NTLM hash for checking
        ntlm_hash = hashlib.new('md4', password.encode('utf-16le')).hexdigest().upper()
        
        result = {
            'password_length': len(password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digits': any(c.isdigit() for c in password),
            'has_special': any(not c.isalnum() for c in password),
            'ntlm_hash': ntlm_hash,
            'strength': 'weak'
        }
        
        # Simple strength calculation
        score = 0
        if len(password) >= 8: score += 1
        if len(password) >= 12: score += 1
        if result['has_uppercase']: score += 1
        if result['has_lowercase']: score += 1
        if result['has_digits']: score += 1
        if result['has_special']: score += 1
        
        if score >= 6: result['strength'] = 'strong'
        elif score >= 4: result['strength'] = 'medium'
        
        return result