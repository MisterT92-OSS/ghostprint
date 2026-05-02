"""
GhostPrint - Social Media Intelligence (SOCMINT)
Extended social media enumeration and analysis
"""
import asyncio
import aiohttp
import re
from typing import Dict, List, Optional
from datetime import datetime


class SocialMediaInvestigator:
    """Advanced social media OSINT"""
    
    # Extended platform list (50+ platforms)
    PLATFORMS = {
        # Major platforms
        'facebook': 'https://www.facebook.com/{}',
        'twitter': 'https://twitter.com/{}',
        'instagram': 'https://www.instagram.com/{}/',
        'linkedin': 'https://www.linkedin.com/in/{}',
        'youtube': 'https://www.youtube.com/@{}',
        'tiktok': 'https://www.tiktok.com/@{}',
        'reddit': 'https://www.reddit.com/user/{}',
        'pinterest': 'https://www.pinterest.com/{}/',
        'tumblr': 'https://{}.tumblr.com',
        'flickr': 'https://www.flickr.com/photos/{}',
        
        # Professional
        'github': 'https://github.com/{}',
        'gitlab': 'https://gitlab.com/{}',
        'bitbucket': 'https://bitbucket.org/{}/',
        'stackoverflow': 'https://stackoverflow.com/users/{}',
        'devto': 'https://dev.to/{}',
        'medium': 'https://medium.com/@{}',
        'hashnode': 'https://hashnode.com/@{}',
        'keybase': 'https://keybase.io/{}',
        
        # Gaming
        'steam': 'https://steamcommunity.com/id/{}',
        'twitch': 'https://www.twitch.tv/{}',
        'discord': 'https://discord.com/users/{}',  # Limited
        'xbox': 'https://xboxgamertag.com/search/{}',
        'playstation': 'https://my.playstation.com/profile/{}',
        
        # Audio/Video
        'spotify': 'https://open.spotify.com/user/{}',
        'soundcloud': 'https://soundcloud.com/{}',
        'bandcamp': 'https://{}.bandcamp.com',
        'mixcloud': 'https://www.mixcloud.com/{}',
        'vimeo': 'https://vimeo.com/{}',
        'dailymotion': 'https://www.dailymotion.com/{}',
        
        # Art/Creative
        'deviantart': 'https://www.deviantart.com/{}',
        'artstation': 'https://www.artstation.com/{}',
        'behance': 'https://www.behance.net/{}',
        'dribbble': 'https://dribbble.com/{}',
        '500px': 'https://500px.com/{}',
        
        # Forums/Community
        'quora': 'https://www.quora.com/profile/{}',
        'goodreads': 'https://www.goodreads.com/{}',
        'tripadvisor': 'https://www.tripadvisor.com/members/{}',
        'strava': 'https://www.strava.com/athletes/{}',
        'untappd': 'https://untappd.com/user/{}',
        
        # Shopping
        'ebay': 'https://www.ebay.com/usr/{}',
        'etsy': 'https://www.etsy.com/shop/{}',
        'amazon': 'https://www.amazon.com/gp/profile/amzn1.account.{}',  # Limited
        
        # Other
        'aboutme': 'https://about.me/{}',
        'gravatar': 'https://en.gravatar.com/{}',
        'lastfm': 'https://www.last.fm/user/{}',
        'myspace': 'https://myspace.com/{}',
        'snapchat': 'https://www.snapchat.com/add/{}',
        'telegram': 'https://t.me/{}',
        'whatsapp': 'https://wa.me/{}',  # Requires number
        'signal': 'https://signal.group/{}',  # Limited
        
        # Regional
        'weibo': 'https://weibo.com/{}',
        'vk': 'https://vk.com/{}',
        'ok': 'https://ok.ru/{}',
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = None
    
    async def _init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'Mozilla/5.0 (compatible; GhostPrint/0.2.0)'},
                timeout=aiohttp.ClientTimeout(total=10)
            )
    
    async def check_platform(self, username: str, platform: str, url_template: str) -> Dict:
        """Check single platform"""
        result = {
            'platform': platform,
            'exists': False,
            'url': url_template.format(username),
            'profile_data': {}
        }
        
        try:
            async with self.session.get(result['url'], allow_redirects=True) as resp:
                result['status_code'] = resp.status
                
                if resp.status == 200:
                    # Check for common "not found" indicators
                    text = await resp.text()
                    
                    # Platform-specific checks
                    not_found_indicators = {
                        'github': ['Not Found', '404'],
                        'twitter': ['page doesn\'t exist', 'Page non trouvée'],
                        'instagram': ['Page Not Found', 'page not found'],
                        'facebook': ['Content Unavailable'],
                        'reddit': ['Sorry, nobody on Reddit goes by that name'],
                        'linkedin': ['This page doesn\'t exist'],
                    }
                    
                    indicators = not_found_indicators.get(platform, [])
                    if not any(indicator in text for indicator in indicators):
                        result['exists'] = True
                        
                        # Try to extract profile data
                        result['profile_data'] = self._extract_profile_data(text, platform)
        
        except Exception as e:
            result['error'] = str(e)
            if self.verbose:
                print(f"Error checking {platform}: {e}")
        
        return result
    
    def _extract_profile_data(self, html: str, platform: str) -> Dict:
        """Extract profile data from HTML"""
        data = {}
        
        try:
            if platform == 'github':
                # Extract name
                name_match = re.search(r'<span class="p-name vcard-fullname d-block overflow-hidden" itemprop="name">([^<]+)', html)
                if name_match:
                    data['name'] = name_match.group(1).strip()
                
                # Extract bio
                bio_match = re.search(r'<div class="p-note user-profile-bio mb-3 js-user-profile-bio f4">([^<]+)', html)
                if bio_match:
                    data['bio'] = bio_match.group(1).strip()
                
                # Extract location
                loc_match = re.search(r'<span class="p-label"[^>]*>([^<]+)', html)
                if loc_match:
                    data['location'] = loc_match.group(1).strip()
                
                # Extract company
                company_match = re.search(r'<span class="p-org"[^>]*>([^<]+)', html)
                if company_match:
                    data['company'] = company_match.group(1).strip()
                
                # Extract public repos/followers
                repos_match = re.search(r'<span class="Counter"[^>]*>([^<]+).*Public', html)
                if repos_match:
                    data['public_repos'] = repos_match.group(1).strip()
                
                followers_match = re.search(r'<span class="text-bold color-fg-default">([^<]+)</span>\s*followers', html)
                if followers_match:
                    data['followers'] = followers_match.group(1).strip()
            
            elif platform == 'twitter':
                # Extract display name
                name_match = re.search(r'<title>([^)]+) \(@[^)]+\)', html)
                if name_match:
                    data['name'] = name_match.group(1)
                
                # Extract bio from meta
                bio_match = re.search(r'<meta name="description" content="([^"]+)', html)
                if bio_match:
                    data['bio'] = bio_match.group(1)
            
            elif platform == 'reddit':
                # Extract karma
                karma_match = re.search(r'([\d,]+)\s+karma', html)
                if karma_match:
                    data['karma'] = karma_match.group(1)
                
                # Extract account age
                age_match = re.search(r'(\w+\s+\d{1,2},\s+\d{4})', html)
                if age_match:
                    data['account_created'] = age_match.group(1)
        
        except Exception as e:
            if self.verbose:
                print(f"Error extracting data from {platform}: {e}")
        
        return data
    
    async def analyze_profile_picture(self, image_url: str) -> Dict:
        """Analyze profile picture (placeholder for image analysis)"""
        return {
            'url': image_url,
            'note': 'Image analysis requires additional libraries (PIL, exif)'
        }
    
    def investigate(self, username: str, platforms: Optional[List[str]] = None) -> Dict:
        """Full social media investigation"""
        
        # Select platforms
        if platforms:
            platforms_to_check = {p: self.PLATFORMS[p] for p in platforms if p in self.PLATFORMS}
        else:
            platforms_to_check = self.PLATFORMS
        
        results = {
            'username': username,
            'total_platforms': len(platforms_to_check),
            'found_on': [],
            'not_found_on': [],
            'profiles': {},
            'potential_others': [],
            'analysis': {}
        }
        
        async def run():
            await self._init_session()
            
            # Check all platforms concurrently
            tasks = [
                self.check_platform(username, platform, url)
                for platform, url in platforms_to_check.items()
            ]
            
            platform_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in platform_results:
                if isinstance(result, Exception):
                    continue
                
                platform = result['platform']
                
                if result['exists']:
                    results['found_on'].append(platform)
                    results['profiles'][platform] = {
                        'url': result['url'],
                        'profile_data': result.get('profile_data', {})
                    }
                else:
                    results['not_found_on'].append(platform)
            
            # Generate analysis
            results['analysis'] = self._analyze_results(results)
            
            if self.session:
                await self.session.close()
            
            return results
        
        return asyncio.run(run())
    
    def _analyze_results(self, results: Dict) -> Dict:
        """Analyze findings for patterns"""
        analysis = {
            'total_found': len(results['found_on']),
            'presence_score': len(results['found_on']) / results['total_platforms'],
            'platform_categories': {},
            'recommendations': []
        }
        
        # Categorize findings
        categories = {
            'professional': ['github', 'gitlab', 'linkedin', 'stackoverflow', 'devto'],
            'social': ['facebook', 'twitter', 'instagram', 'tiktok', 'reddit'],
            'creative': ['deviantart', 'artstation', 'behance', 'dribbble', '500px'],
            'gaming': ['steam', 'twitch', 'xbox', 'playstation'],
            'audio': ['spotify', 'soundcloud', 'bandcamp', 'mixcloud'],
            'regional': ['weibo', 'vk', 'ok']
        }
        
        for cat, platforms in categories.items():
            found = [p for p in platforms if p in results['found_on']]
            if found:
                analysis['platform_categories'][cat] = found
        
        # Recommendations
        if 'github' in results['found_on']:
            analysis['recommendations'].append('Check GitHub repos for email/domain leaks')
        
        if 'twitter' in results['found_on']:
            analysis['recommendations'].append('Analyze Twitter history for location/timezone data')
        
        if len(results['found_on']) > 10:
            analysis['recommendations'].append('High digital footprint - consider checking for credential reuse')
        
        return analysis