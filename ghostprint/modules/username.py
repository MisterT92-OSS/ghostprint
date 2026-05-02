"""
GhostPrint - Username Investigation Module
Enumerate username presence across platforms
"""
import asyncio
import aiohttp
import re
from typing import Dict, List, Optional


class UsernameInvestigator:
    """Investigate usernames across social platforms"""

    # Platform configurations with content verification patterns
    PLATFORMS = {
        'github': {
            'url': 'https://github.com/{}',
            'api_url': 'https://api.github.com/users/{}',
            'method': 'api',
            'exists_patterns': [r'"login":', r'"id":', r'"avatar_url":'],
            'not_found_patterns': [r'Not Found', r'404'],
        },
        'gitlab': {
            'url': 'https://gitlab.com/{}',
            'api_url': 'https://gitlab.com/api/v4/users?username={}',
            'method': 'api',
            'exists_patterns': [r'"username":', r'"id":'],
            'not_found_patterns': [],
        },
        'twitter': {
            'url': 'https://nitter.net/{}',
            'method': 'content',
            'exists_patterns': [r'@{}', r'profile-card', r'profile-name', r'profile-bio'],
            'not_found_patterns': [r'Not found', r'could not find', r'404', r'not exist'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'instagram': {
            'url': 'https://www.instagram.com/{}/',
            'method': 'content',
            'exists_patterns': [r'"username":"{}"', r'profile_pic_url', r'biography'],
            'not_found_patterns': [r'Sorry, this page', r'404', r'not found', r'unavailable'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'reddit': {
            'url': 'https://www.reddit.com/user/{}/about.json',
            'method': 'content_json',
            'exists_patterns': [r'"name":', r'"created_utc":'],
            'not_found_patterns': [r'Not Found', r'404', r'{"kind": "t2", "data": {"is_suspended": true}}'],
        },
        'linkedin': {
            'url': 'https://www.linkedin.com/in/{}',
            'method': 'content',
            'exists_patterns': [r'profileName', r'profile-photo', r'experience-section', r'summary'],
            'not_found_patterns': [r'Page not found', r'404', r'does not exist', r'Profil introuvable'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'tiktok': {
            'url': 'https://www.tiktok.com/@{}',
            'method': 'content',
            'exists_patterns': [r'"uniqueId":"{}"', r'user-info-container', r'follow-count'],
            'not_found_patterns': [r'Not found', r'404', r'could not be found', r'does not exist'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'youtube': {
            'url': 'https://www.youtube.com/@{}',
            'method': 'content',
            'exists_patterns': [r'"channelId":', r'subscriber-count', r'channel-name', r'videos-count'],
            'not_found_patterns': [r'Not found', r'404', r'Cette page n', r'does not exist'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'pinterest': {
            'url': 'https://www.pinterest.com/{}/',
            'method': 'content',
            'exists_patterns': [r'"username":"{}"', r'profile-image', r'boards-container'],
            'not_found_patterns': [r'Not found', r'404', r'Oops', r'does not exist'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'twitch': {
            'url': 'https://www.twitch.tv/{}',
            'method': 'content',
            'exists_patterns': [r'"displayName":"{}"', r'channel-header', r'follow-btn', r'viewers-count'],
            'not_found_patterns': [r'not found', r'404', r'unavailable', r'does not exist'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'spotify': {
            'url': 'https://open.spotify.com/user/{}',
            'method': 'content',
            'exists_patterns': [r'"username":"{}"', r'user-profile', r'profile-name'],
            'not_found_patterns': [r'Not found', r'404', r'unavailable', r'does not exist'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'medium': {
            'url': 'https://medium.com/@{}',
            'method': 'content',
            'exists_patterns': [r'authorName', r'profile-info', r'avatar-image'],
            'not_found_patterns': [r'Not found', r'404', r'page unavailable'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'deviantart': {
            'url': 'https://www.deviantart.com/{}',
            'method': 'content',
            'exists_patterns': [r'user-link', r'profile-avatar', r'profile-stats', r'deviant-artist'],
            'not_found_patterns': [r'not found', r'404', r'No user found', r'Fan of'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        },
        'soundcloud': {
            'url': 'https://soundcloud.com/{}',
            'method': 'content',
            'exists_patterns': [r'userAudible', r'profileHeader', r'followButton', r'profileAvatar'],
            'not_found_patterns': [r'not found', r'404', r'could not be found', r'Not Found'],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
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
        """Check if username exists on a specific platform with content verification"""
        result = {
            'platform': platform,
            'exists': False,
            'confidence': 0,
            'url': config['url'].format(username),
            'error': None
        }

        try:
            headers = config.get('headers', {'User-Agent': 'GhostPrint/0.1.0'})

            if config.get('method') == 'api' and 'api_url' in config:
                # API-based check (like GitHub, GitLab)
                url = config['api_url'].format(username)
                async with self.session.get(url, headers=headers) as resp:
                    content = await resp.text()
                    if resp.status == 200:
                        # Verify content matches expected patterns
                        exists_patterns = config.get('exists_patterns', [])
                        if exists_patterns:
                            matches = sum(1 for p in exists_patterns if re.search(p, content, re.IGNORECASE))
                            result['exists'] = matches >= 1
                            result['confidence'] = min(matches / len(exists_patterns) * 100, 100) if exists_patterns else 50
                        else:
                            result['exists'] = True
                            result['confidence'] = 100

                        if result['exists']:
                            try:
                                data = await resp.json()
                                result['profile'] = self._extract_profile_data(data, platform)
                            except:
                                pass
                    else:
                        result['exists'] = False
                        result['confidence'] = 100

            elif config.get('method') == 'content_json':
                # JSON API-based check
                url = config['url'].format(username)
                async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    content = await resp.text()
                    exists_patterns = config.get('exists_patterns', [])
                    not_found_patterns = config.get('not_found_patterns', [])

                    if resp.status == 200:
                        # Check for positive indicators
                        exists_matches = sum(1 for p in exists_patterns if re.search(p, content, re.IGNORECASE))
                        # Check for negative indicators
                        not_found_matches = sum(1 for p in not_found_patterns if re.search(p, content, re.IGNORECASE))

                        if exists_matches > 0 and not_found_matches == 0:
                            result['exists'] = True
                            result['confidence'] = min(exists_matches / len(exists_patterns) * 100, 100) if exists_patterns else 70
                        elif not_found_matches > 0:
                            result['exists'] = False
                            result['confidence'] = min(not_found_matches / len(not_found_patterns) * 100, 100) if not_found_patterns else 70
                        else:
                            result['exists'] = False
                            result['confidence'] = 30
                    else:
                        result['exists'] = False
                        result['confidence'] = 100

            else:
                # Content-based check with pattern matching
                async with self.session.get(result['url'], headers=headers,
                                            allow_redirects=True,
                                            timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    content = await resp.text()
                    exists_patterns = config.get('exists_patterns', [])
                    not_found_patterns = config.get('not_found_patterns', [])

                    # Check for positive indicators
                    exists_matches = sum(1 for p in exists_patterns if re.search(p.format(re.escape(username)), content, re.IGNORECASE))
                    # Check for negative indicators
                    not_found_matches = sum(1 for p in not_found_patterns if re.search(p, content, re.IGNORECASE))

                    if self.verbose:
                        print(f"[{platform}] Status: {resp.status}, Exists patterns: {exists_matches}, Not found: {not_found_matches}")

                    # Decision logic with confidence scoring
                    if resp.status == 200:
                        if exists_matches > 0 and not_found_matches == 0:
                            result['exists'] = True
                            result['confidence'] = min(exists_matches / len(exists_patterns) * 100, 100) if exists_patterns else 70
                        elif not_found_matches > 0:
                            result['exists'] = False
                            result['confidence'] = min(not_found_matches / len(not_found_patterns) * 100, 100) if not_found_patterns else 70
                        elif exists_matches == 0 and not_found_matches == 0:
                            # Ambiguous - page loaded but no clear indicators
                            result['exists'] = False
                            result['confidence'] = 40
                        else:
                            result['exists'] = False
                            result['confidence'] = 60
                    elif resp.status == 404:
                        result['exists'] = False
                        result['confidence'] = 100
                    else:
                        # Other status codes
                        result['exists'] = False
                        result['confidence'] = 70

        except asyncio.TimeoutError:
            result['error'] = 'Timeout'
            result['confidence'] = 0
            if self.verbose:
                print(f"Timeout checking {platform}")
        except aiohttp.ClientError as e:
            result['error'] = str(e)
            result['confidence'] = 0
            if self.verbose:
                print(f"Error checking {platform}: {e}")
        except Exception as e:
            result['error'] = str(e)
            result['confidence'] = 0
            if self.verbose:
                print(f"Unexpected error checking {platform}: {e}")

        return result

    def _extract_profile_data(self, data: Dict, platform: str) -> Dict:
        """Extract common profile fields from platform-specific data"""
        profile = {}

        if platform == 'github':
            profile = {
                'name': data.get('name'),
                'bio': data.get('bio'),
                'location': data.get('location'),
                'company': data.get('company'),
                'blog': data.get('blog'),
                'public_repos': data.get('public_repos'),
                'followers': data.get('followers'),
                'following': data.get('following'),
                'created_at': data.get('created_at'),
            }
        elif platform == 'gitlab':
            if isinstance(data, list) and len(data) > 0:
                user = data[0]
                profile = {
                    'name': user.get('name'),
                    'id': user.get('id'),
                    'avatar_url': user.get('avatar_url'),
                }

        return {k: v for k, v in profile.items() if v is not None}
    
    def investigate(self, username: str, platforms: Optional[List[str]] = None,
                   min_confidence: int = 50) -> Dict:
        """
        Investigate a username across platforms with confidence scoring

        Args:
            username: Username to investigate
            platforms: List of platforms to check (None = all)
            min_confidence: Minimum confidence score (0-100) to consider a result valid

        Returns:
            Dictionary with findings
        """
        # Validate username
        if not username or len(username.strip()) < 2:
            return {
                'username': username,
                'error': 'Invalid username provided',
                'total_platforms': 0,
                'found_on': [],
                'not_found_on': [],
                'profiles': {},
                'uncertain': [],
                'errors': []
            }

        username = username.strip()

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
            'uncertain': [],
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
                confidence = result.get('confidence', 0)

                if result['error']:
                    results['errors'].append(f"{platform}: {result['error']}")

                # Categorize based on confidence
                if result['exists'] and confidence >= min_confidence:
                    results['found_on'].append({
                        'platform': platform,
                        'url': result['url'],
                        'confidence': confidence
                    })
                    results['profiles'][platform] = {
                        'url': result['url'],
                        'confidence': confidence
                    }
                    if 'profile' in result:
                        results['profiles'][platform].update(result['profile'])
                elif not result['exists'] and confidence >= 70:
                    results['not_found_on'].append(platform)
                else:
                    # Uncertain results
                    results['uncertain'].append({
                        'platform': platform,
                        'url': result['url'],
                        'exists': result['exists'],
                        'confidence': confidence
                    })

            if self.session:
                await self.session.close()

        # Run async investigation
        asyncio.run(run_investigation())

        # Sort by confidence
        results['found_on'].sort(key=lambda x: x['confidence'], reverse=True)

        return results


if __name__ == '__main__':
    import sys

    test_username = sys.argv[1] if len(sys.argv) > 1 else 'torvalds'

    investigator = UsernameInvestigator(verbose=True)
    results = investigator.investigate(test_username, min_confidence=50)

    print(f"\n{'='*60}")
    print(f"Username Investigation: {results['username']}")
    print(f"{'='*60}")
    print(f"Platforms checked: {results['total_platforms']}")

    print(f"\n✓ Found on ({len(results['found_on'])}):")
    for found in results['found_on']:
        conf_str = f"({found['confidence']:.0f}%)" if 'confidence' in found else ""
        print(f"  - {found['platform']} {conf_str}")
        print(f"    URL: {found['url']}")

    print(f"\n✗ Not found on ({len(results['not_found_on'])}):")
    for platform in results['not_found_on']:
        print(f"  - {platform}")

    if results['uncertain']:
        print(f"\n? Uncertain ({len(results['uncertain'])}):")
        for item in results['uncertain']:
            print(f"  - {item['platform']} (exists: {item['exists']}, confidence: {item['confidence']:.0f}%)")

    if results['errors']:
        print(f"\n⚠ Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")

    print(f"\n{'='*60}")