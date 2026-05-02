"""
GhostPrint - Email Investigation Module
Investigate email addresses for breaches and social profiles
"""
import asyncio
import aiohttp
from typing import Dict, List, Optional
import hashlib
import re
import os


class EmailInvestigator:
    """Investigate email addresses with multiple verification methods"""

    # Pattern for validating email format
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    # MX records for common email providers (simplified check)
    EMAIL_PROVIDERS = {
        'gmail.com': 'Google Gmail',
        'yahoo.com': 'Yahoo Mail',
        'outlook.com': 'Microsoft Outlook',
        'hotmail.com': 'Microsoft Hotmail',
        'live.com': 'Microsoft Live',
        'icloud.com': 'Apple iCloud',
        'protonmail.com': 'ProtonMail',
        'proton.me': 'ProtonMail',
        'aol.com': 'AOL Mail',
        'mail.ru': 'Mail.ru',
        'yandex.ru': 'Yandex Mail',
        'qq.com': 'QQ Mail',
        '163.com': '163 Mail',
        '126.com': '126 Mail',
        'foxmail.com': 'Foxmail',
        'gmx.com': 'GMX Mail',
        'gmx.net': 'GMX Mail',
        'zoho.com': 'Zoho Mail',
        'fastmail.com': 'Fastmail',
    }

    def __init__(self, verbose: bool = False, hibp_api_key: Optional[str] = None):
        self.verbose = verbose
        self.session = None
        self.hibp_api_key = hibp_api_key or os.getenv('HIBP_API_KEY')

        # Sources to check
        self.breach_sources = [
            'haveibeenpwned',
        ]

        self.social_platforms = [
            'github', 'gitlab', 'gravatar'
        ]

    def validate_email(self, email: str) -> Dict:
        """Validate email format and extract components"""
        result = {
            'valid': False,
            'email': email,
            'local_part': None,
            'domain': None,
            'provider': 'Unknown',
            'is_disposable': False,
        }

        if not email:
            return result

        # Check format
        if not self.EMAIL_REGEX.match(email):
            return result

        result['valid'] = True

        # Extract parts
        local_part, domain = email.rsplit('@', 1)
        result['local_part'] = local_part
        result['domain'] = domain.lower()

        # Check provider
        if result['domain'] in self.EMAIL_PROVIDERS:
            result['provider'] = self.EMAIL_PROVIDERS[result['domain']]
        else:
            result['provider'] = f"Custom ({result['domain']})"

        # Check for disposable email patterns
        disposable_patterns = [
            'temp', 'tmp', 'throwaway', 'guerrilla', '10minutemail',
            'mailinator', 'yopmail', 'fake', 'burner'
        ]
        result['is_disposable'] = any(p in result['domain'].lower() for p in disposable_patterns)

        return result

    async def _init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GhostPrint/0.1.0'},
                timeout=aiohttp.ClientTimeout(total=15)
            )

    async def _check_haveibeenpwned(self, email: str) -> Dict:
        """Check HaveIBeenPwned for breaches with better error handling"""
        result = {
            'breaches': [],
            'breach_count': 0,
            'error': None,
            'api_key_required': not bool(self.hibp_api_key)
        }

        if not self.session:
            await self._init_session()

        if not self.hibp_api_key:
            result['error'] = 'HIBP API key not configured. Set HIBP_API_KEY environment variable.'
            return result

        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {
                'User-Agent': 'GhostPrint-OSINT',
                'hibp-api-key': self.hibp_api_key
            }

            async with self.session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result['breaches'] = data
                    result['breach_count'] = len(data)
                elif resp.status == 404:
                    # No breaches found - this is actually good news
                    result['breaches'] = []
                    result['breach_count'] = 0
                elif resp.status == 429:
                    result['error'] = 'Rate limited by HIBP API'
                elif resp.status == 401:
                    result['error'] = 'Invalid HIBP API key'
                else:
                    result['error'] = f'HIBP API returned status {resp.status}'

        except asyncio.TimeoutError:
            result['error'] = 'Timeout connecting to HIBP'
        except aiohttp.ClientError as e:
            result['error'] = f'Network error: {str(e)}'
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'

        return result

    async def _check_gravatar(self, email: str) -> Dict:
        """Check Gravatar for profile picture and info"""
        result = {'exists': False, 'profile': None, 'url': None}

        if not self.session:
            await self._init_session()

        try:
            # Generate MD5 hash of email for Gravatar
            email_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
            url = f"https://en.gravatar.com/{email_hash}.json"

            async with self.session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'entry' in data and len(data['entry']) > 0:
                        entry = data['entry'][0]
                        result['exists'] = True
                        result['url'] = f"https://gravatar.com/{email_hash}"
                        result['profile'] = {
                            'display_name': entry.get('displayName'),
                            'thumbnail': entry.get('thumbnailUrl'),
                            'urls': [u.get('value') for u in entry.get('urls', [])],
                        }
                elif resp.status == 404:
                    result['exists'] = False

        except Exception as e:
            if self.verbose:
                print(f"Error checking Gravatar: {e}")

        return result

    async def _check_github(self, email: str) -> Dict:
        """Check GitHub for users with this email"""
        result = {'exists': False, 'users': []}

        if not self.session:
            await self._init_session()

        try:
            # Search for users by email
            url = f"https://api.github.com/search/users?q={email}+in:email"
            headers = {'Accept': 'application/vnd.github.v3+json'}

            async with self.session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result['exists'] = data.get('total_count', 0) > 0
                    if result['exists']:
                        # Get first 3 users
                        for item in data.get('items', [])[:3]:
                            result['users'].append({
                                'username': item.get('login'),
                                'url': item.get('html_url'),
                                'avatar': item.get('avatar_url'),
                            })
                elif resp.status == 403:
                    result['rate_limited'] = True

        except Exception as e:
            if self.verbose:
                print(f"Error checking GitHub: {e}")

        return result

    async def _check_gitlab(self, email: str) -> Dict:
        """Check GitLab for users with this email"""
        result = {'exists': False, 'users': []}

        if not self.session:
            await self._init_session()

        try:
            # GitLab public API for user search
            url = f"https://gitlab.com/api/v4/users?search={email}"

            async with self.session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        result['exists'] = True
                        for user in data[:3]:
                            result['users'].append({
                                'username': user.get('username'),
                                'url': f"https://gitlab.com/{user.get('username')}",
                                'name': user.get('name'),
                            })

        except Exception as e:
            if self.verbose:
                print(f"Error checking GitLab: {e}")

        return result
    
    def investigate(self, email: str, check_breaches: bool = True,
                   check_social: bool = True) -> Dict:
        """
        Main investigation method

        Args:
            email: Email address to investigate
            check_breaches: Check breach databases
            check_social: Check social platforms

        Returns:
            Dictionary with investigation results
        """
        # Validate email first
        validation = self.validate_email(email)

        results = {
            'email': email,
            'valid': validation['valid'],
            'provider': validation['provider'],
            'is_disposable': validation['is_disposable'],
            'breaches': [],
            'breach_count': 0,
            'social_profiles': {},
            'gravatar': None,
            'status': 'completed',
            'errors': []
        }

        if not validation['valid']:
            results['status'] = 'invalid_email'
            results['errors'].append('Invalid email format')
            return results

        async def run_investigation():
            await self._init_session()

            tasks = []

            if check_breaches:
                tasks.append(('hibp', self._check_haveibeenpwned(email)))

            if check_social:
                tasks.append(('gravatar', self._check_gravatar(email)))
                tasks.append(('github', self._check_github(email)))
                tasks.append(('gitlab', self._check_gitlab(email)))

            # Run all checks concurrently
            check_results = await asyncio.gather(
                *[task[1] for task in tasks],
                return_exceptions=True
            )

            # Process results
            for (source_name, _), result in zip(tasks, check_results):
                if isinstance(result, Exception):
                    results['errors'].append(f"{source_name}: {str(result)}")
                    continue

                if source_name == 'hibp':
                    results['breaches'] = result.get('breaches', [])
                    results['breach_count'] = result.get('breach_count', 0)
                    if result.get('error') and not result.get('api_key_required'):
                        results['errors'].append(f"HIBP: {result['error']}")

                elif source_name == 'gravatar':
                    results['gravatar'] = result

                elif source_name in ('github', 'gitlab'):
                    if result.get('exists'):
                        results['social_profiles'][source_name] = result

            if self.session:
                await self.session.close()

        # Run async investigation
        asyncio.run(run_investigation())

        return results


# For testing
if __name__ == '__main__':
    import sys

    test_email = sys.argv[1] if len(sys.argv) > 1 else 'test@example.com'

    investigator = EmailInvestigator(verbose=True)
    results = investigator.investigate(test_email, check_breaches=True, check_social=True)

    print(f"\n{'='*60}")
    print(f"Email Investigation: {results['email']}")
    print(f"{'='*60}")
    print(f"Valid: {results['valid']}")
    print(f"Provider: {results['provider']}")
    print(f"Disposable: {results['is_disposable']}")

    print(f"\n✓ Breaches: {results['breach_count']}")
    if results['breaches']:
        for breach in results['breaches'][:5]:  # Show first 5
            print(f"  - {breach.get('Name', 'Unknown')} ({breach.get('BreachDate', 'N/A')})")

    print(f"\n✓ Social Profiles:")
    if results['social_profiles']:
        for platform, data in results['social_profiles'].items():
            print(f"  - {platform}:")
            for user in data.get('users', []):
                print(f"    @{user.get('username')} - {user.get('url', 'N/A')}")
    else:
        print("  No social profiles found")

    if results['gravatar'] and results['gravatar'].get('exists'):
        print(f"\n✓ Gravatar:")
        print(f"  URL: {results['gravatar'].get('url')}")
        profile = results['gravatar'].get('profile', {})
        if profile.get('display_name'):
            print(f"  Name: {profile['display_name']}")

    if results['errors']:
        print(f"\n⚠ Errors:")
        for error in results['errors']:
            print(f"  - {error}")

    print(f"\n{'='*60}")