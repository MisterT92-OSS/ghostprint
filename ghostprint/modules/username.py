"""
GhostPrint - Username Investigation Module
Enumerate username presence across platforms
"""
import asyncio
import aiohttp
from typing import Dict, List, Optional


class UsernameInvestigator:
    """Investigate usernames across social platforms"""
    
    # Platform configurations
    PLATFORMS = {
        'twitter': {
            'url': 'https://twitter.com/{}',
            'check_url': 'https://api.twitter.com/2/users/by/username/{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'github': {
            'url': 'https://github.com/{}',
            'api_url': 'https://api.github.com/users/{}',
            'method': 'api',
        },
        'instagram': {
            'url': 'https://www.instagram.com/{}/',
            'method': 'status_code',
            'exists_code': 200,
        },
        'reddit': {
            'url': 'https://www.reddit.com/user/{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'linkedin': {
            'url': 'https://www.linkedin.com/in/{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'tiktok': {
            'url': 'https://www.tiktok.com/@{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'youtube': {
            'url': 'https://www.youtube.com/@{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'pinterest': {
            'url': 'https://www.pinterest.com/{}/',
            'method': 'status_code',
            'exists_code': 200,
        },
        'twitch': {
            'url': 'https://www.twitch.tv/{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'spotify': {
            'url': 'https://open.spotify.com/user/{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'medium': {
            'url': 'https://medium.com/@{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'deviantart': {
            'url': 'https://www.deviantart.com/{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'soundcloud': {
            'url': 'https://soundcloud.com/{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'gitlab': {
            'url': 'https://gitlab.com/{}',
            'method': 'status_code',
            'exists_code': 200,
        },
        'stackoverflow': {
            'url': 'https://stackoverflow.com/users/{}',
            'method': 'status_code',
            'exists_code': 200,
        },
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = None
    
    async def _init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GhostPrint/0.1.0'},
                timeout=aiohttp.ClientTimeout(total=10)
            )
    
    async def _check_platform(self, username: str, platform: str, 
                             config: Dict) -> Dict:
        """Check if username exists on a specific platform"""
        result = {
            'platform': platform,
            'exists': False,
            'url': config['url'].format(username),
            'error': None
        }
        
        try:
            if config.get('method') == 'api' and 'api_url' in config:
                # API-based check (like GitHub)
                url = config['api_url'].format(username)
                async with self.session.get(url) as resp:
                    result['exists'] = resp.status == 200
                    if result['exists']:
                        data = await resp.json()
                        result['profile'] = {
                            'name': data.get('name'),
                            'bio': data.get('bio'),
                            'location': data.get('location'),
                            'created_at': data.get('created_at'),
                        }
            else:
                # Status code based check
                async with self.session.get(result['url'], allow_redirects=True) as resp:
                    result['exists'] = resp.status == config.get('exists_code', 200)
                    
        except aiohttp.ClientError as e:
            result['error'] = str(e)
            if self.verbose:
                print(f"Error checking {platform}: {e}")
        
        return result
    
    def investigate(self, username: str, platforms: Optional[List[str]] = None) -> Dict:
        """
        Investigate a username across platforms
        
        Args:
            username: Username to investigate
            platforms: List of platforms to check (None = all)
            
        Returns:
            Dictionary with findings
        """
        # Determine which platforms to check
        if platforms:
            platforms_to_check = {p: self.PLATFORMS[p] for p in platforms 
                                   if p in self.PLATFORMS}
        else:
            platforms_to_check = self.PLATFORMS
        
        results = {
            'username': username,
            'total_platforms': len(platforms_to_check),
            'found_on': [],
            'not_found_on': [],
            'profiles': {},
            'errors': []
        }
        
        async def run_investigation():
            await self._init_session()
            
            # Create tasks for all platforms
            tasks = [
                self._check_platform(username, platform, config)
                for platform, config in platforms_to_check.items()
            ]
            
            # Run all checks concurrently
            platform_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in platform_results:
                if isinstance(result, Exception):
                    results['errors'].append(str(result))
                    continue
                
                platform = result['platform']
                
                if result['exists']:
                    results['found_on'].append(platform)
                    results['profiles'][platform] = {
                        'url': result['url']
                    }
                    if 'profile' in result:
                        results['profiles'][platform].update(result['profile'])
                else:
                    results['not_found_on'].append(platform)
            
            if self.session:
                await self.session.close()
        
        # Run async investigation
        asyncio.run(run_investigation())
        
        return results


if __name__ == '__main__':
    investigator = UsernameInvestigator(verbose=True)
    results = investigator.investigate('torvalds')  # Linus Torvalds
    
    print(f"\nUsername: {results['username']}")
    print(f"Found on: {', '.join(results['found_on'])}")
    print(f"Profiles: {results['profiles']}")