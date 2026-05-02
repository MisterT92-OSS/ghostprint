"""
GhostPrint - Email Investigation Module
Investigate email addresses for breaches and social profiles
"""
import asyncio
import aiohttp
from typing import Dict, List, Optional
import hashlib


class EmailInvestigator:
    """Investigate email addresses"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = None
        
        # Sources to check
        self.breach_sources = [
            'haveibeenpwned',
            # Add more sources here
        ]
        
        self.social_platforms = [
            'twitter', 'github', 'instagram', 'linkedin', 'reddit'
        ]
    
    async def _init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GhostPrint/0.1.0'}
            )
    
    async def _check_haveibeenpwned(self, email: str) -> List[Dict]:
        """Check HaveIBeenPwned for breaches"""
        breaches = []
        
        if not self.session:
            await self._init_session()
        
        try:
            # HIBP API v3 (requires key for full API, using k-anonymity for passwords)
            # For email breaches, we'd need the API key
            # This is a placeholder implementation
            
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {
                'User-Agent': 'GhostPrint-OSINT',
                'hibp-api-key': 'YOUR_API_KEY_HERE'  # User needs to configure this
            }
            
            async with self.session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    breaches = data
                elif resp.status == 404:
                    # No breaches found
                    pass
                    
        except Exception as e:
            if self.verbose:
                print(f"Error checking HIBP: {e}")
        
        return breaches
    
    async def _check_social_platforms(self, email: str) -> Dict[str, bool]:
        """Check email presence on social platforms"""
        results = {}
        
        if not self.session:
            await self._init_session()
        
        # GitHub check (public endpoint)
        try:
            url = f"https://api.github.com/search/users?q={email}+in:email"
            async with self.session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results['github'] = data.get('total_count', 0) > 0
                else:
                    results['github'] = False
        except Exception as e:
            results['github'] = None
            if self.verbose:
                print(f"Error checking GitHub: {e}")
        
        # Add more platforms here...
        
        return results
    
    def investigate(self, email: str, check_breaches: bool = True, 
                   check_social: bool = False) -> Dict:
        """
        Main investigation method
        
        Args:
            email: Email address to investigate
            check_breaches: Check breach databases
            check_social: Check social platforms
            
        Returns:
            Dictionary with investigation results
        """
        results = {
            'email': email,
            'breaches': [],
            'breach_count': 0,
            'social_profiles': {},
            'status': 'completed'
        }
        
        async def run_investigation():
            await self._init_session()
            
            if check_breaches:
                # Run breach checks
                breaches = await self._check_haveibeenpwned(email)
                results['breaches'] = breaches
                results['breach_count'] = len(breaches)
            
            if check_social:
                # Run social checks
                social = await self._check_social_platforms(email)
                results['social_profiles'] = social
            
            if self.session:
                await self.session.close()
        
        # Run async investigation
        asyncio.run(run_investigation())
        
        return results


# For testing
if __name__ == '__main__':
    investigator = EmailInvestigator(verbose=True)
    results = investigator.investigate('test@example.com', check_breaches=True)
    print(results)