"""
GhostPrint - Web Search Module
Search using free APIs that don't require keys
"""
import asyncio
import aiohttp
import re
from typing import Dict, List, Optional
from urllib.parse import quote_plus


class WebSearchInvestigator:
    """Search for mentions using free APIs and scraping"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = None

    async def _init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/html',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            )

    async def _search_github(self, query: str) -> List[Dict]:
        """Search GitHub users (API sans auth, rate limitée)"""
        results = []
        try:
            url = f"https://api.github.com/search/users?q={quote_plus(query)}&per_page=10"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for user in data.get('items', []):
                        results.append({
                            'url': user.get('html_url', ''),
                            'title': f"GitHub: {user.get('login', '')}",
                            'snippet': f"Type: {user.get('type', 'User')}",
                            'engine': 'github',
                            'avatar': user.get('avatar_url', ''),
                        })
                elif self.verbose:
                    print(f"[GitHub] Status: {resp.status}")
        except Exception as e:
            if self.verbose:
                print(f"[GitHub] Error: {e}")
        return results

    async def _search_reddit(self, query: str) -> List[Dict]:
        """Search Reddit posts (JSON endpoint sans auth)"""
        results = []
        try:
            url = f"https://www.reddit.com/search.json?q={quote_plus(query)}&limit=10"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    posts = data.get('data', {}).get('children', [])
                    for post in posts:
                        post_data = post.get('data', {})
                        results.append({
                            'url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'title': f"Reddit: {post_data.get('title', '')[:100]}",
                            'snippet': post_data.get('selftext', '')[:200],
                            'engine': 'reddit',
                            'subreddit': post_data.get('subreddit', ''),
                        })
                elif self.verbose:
                    print(f"[Reddit] Status: {resp.status}")
        except Exception as e:
            if self.verbose:
                print(f"[Reddit] Error: {e}")
        return results

    async def _search_wikipedia(self, query: str) -> List[Dict]:
        """Search Wikipedia (API REST officielle, sans auth)"""
        results = []
        try:
            # Search API
            search_url = f"https://en.wikipedia.org/w/rest.php/v1/search/title?q={quote_plus(query)}&limit=10"
            async with self.session.get(search_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for page in data.get('pages', []):
                        results.append({
                            'url': f"https://en.wikipedia.org/wiki/{page.get('key', '')}",
                            'title': f"Wikipedia: {page.get('title', '')}",
                            'snippet': page.get('description', ''),
                            'engine': 'wikipedia',
                        })
                elif self.verbose:
                    print(f"[Wikipedia] Status: {resp.status}")
        except Exception as e:
            if self.verbose:
                print(f"[Wikipedia] Error: {e}")
        return results

    async def _search_nominatim(self, query: str) -> List[Dict]:
        """Search locations (OpenStreetMap Nominatim, sans auth)"""
        results = []
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={quote_plus(query)}&format=json&limit=5"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for place in data:
                        results.append({
                            'url': f"https://www.openstreetmap.org/?mlat={place.get('lat')}&mlon={place.get('lon')}",
                            'title': f"Location: {place.get('display_name', '')[:80]}",
                            'snippet': f"Type: {place.get('type', 'unknown')}",
                            'engine': 'openstreetmap',
                        })
                elif self.verbose:
                    print(f"[Nominatim] Status: {resp.status}")
        except Exception as e:
            if self.verbose:
                print(f"[Nominatim] Error: {e}")
        return results

    async def _search_newsapi(self, query: str) -> List[Dict]:
        """Search news via HackerNews Algolia (API sans auth)"""
        results = []
        try:
            url = f"https://hn.algolia.com/api/v1/search?q={quote_plus(query)}&tags=story&hitsPerPage=10"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for hit in data.get('hits', []):
                        results.append({
                            'url': hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                            'title': f"HN: {hit.get('title', '')[:100]}",
                            'snippet': f"Points: {hit.get('points', 0)}, Comments: {hit.get('num_comments', 0)}",
                            'engine': 'hackernews',
                            'author': hit.get('author', ''),
                        })
                elif self.verbose:
                    print(f"[HackerNews] Status: {resp.status}")
        except Exception as e:
            if self.verbose:
                print(f"[HackerNews] Error: {e}")
        return results

    async def _search_quotes(self, query: str) -> List[Dict]:
        """Search quotes via Quotable API (sans auth)"""
        results = []
        try:
            url = f"https://api.quotable.io/quotes?author={quote_plus(query)}&limit=5"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for quote in data.get('results', []):
                        results.append({
                            'url': f"https://quotable.io/quotes/{quote.get('_id', '')}",
                            'title': f"Quote by {quote.get('author', '')}",
                            'snippet': quote.get('content', '')[:200],
                            'engine': 'quotable',
                            'tags': ', '.join(quote.get('tags', [])),
                        })
                elif self.verbose:
                    print(f"[Quotable] Status: {resp.status}")
        except Exception as e:
            if self.verbose:
                print(f"[Quotable] Error: {e}")
        return results

    async def _search_duckduckgo_instant(self, query: str) -> List[Dict]:
        """DuckDuckGo Instant Answer API (sans auth)"""
        results = []
        try:
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    # DDG returns JSONP-like format
                    import json
                    try:
                        data = json.loads(text)
                        for topic in data.get('RelatedTopics', [])[:5]:
                            if 'FirstURL' in topic:
                                results.append({
                                    'url': topic.get('FirstURL', ''),
                                    'title': topic.get('Text', '')[:80],
                                    'snippet': topic.get('Result', '')[:200],
                                    'engine': 'duckduckgo',
                                })
                    except:
                        pass
                elif self.verbose:
                    print(f"[DDG] Status: {resp.status}")
        except Exception as e:
            if self.verbose:
                print(f"[DDG] Error: {e}")
        return results

    async def _search_gitlab(self, query: str) -> List[Dict]:
        """Search GitLab users (API sans auth)"""
        results = []
        try:
            url = f"https://gitlab.com/api/v4/users?search={quote_plus(query)}&per_page=10"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for user in data:
                        results.append({
                            'url': user.get('web_url', ''),
                            'title': f"GitLab: {user.get('username', '')}",
                            'snippet': user.get('name', ''),
                            'engine': 'gitlab',
                        })
                elif self.verbose:
                    print(f"[GitLab] Status: {resp.status}")
        except Exception as e:
            if self.verbose:
                print(f"[GitLab] Error: {e}")
        return results

    def investigate(self, query: str, query_type: str = 'username') -> Dict:
        """
        Search across multiple free sources
        """
        async def run_search():
            await self._init_session()

            tasks = []

            if query_type == 'username':
                # Pour username, chercher sur les réseaux dev
                tasks.append(('github', self._search_github(query)))
                tasks.append(('gitlab', self._search_gitlab(query)))
                tasks.append(('reddit', self._search_reddit(query)))
                tasks.append(('hackernews', self._search_newsapi(query)))
                tasks.append(('wikipedia', self._search_wikipedia(query)))
            elif query_type == 'email':
                # Pour email, chercher les profils associés
                local_part = query.split('@')[0]
                tasks.append(('github', self._search_github(local_part)))
                tasks.append(('reddit', self._search_reddit(local_part)))
                tasks.append(('wikipedia', self._search_wikipedia(local_part)))
            else:
                # Recherche générale
                tasks.append(('wikipedia', self._search_wikipedia(query)))
                tasks.append(('duckduckgo', self._search_duckduckgo_instant(query)))
                tasks.append(('hackernews', self._search_newsapi(query)))
                tasks.append(('reddit', self._search_reddit(query)))

            # Exécuter toutes les recherches en parallèle
            results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)

            all_results = []
            engines_working = []
            engines_failed = []

            for (source_name, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    engines_failed.append(source_name)
                    continue
                if result:
                    all_results.extend(result)
                    engines_working.append(source_name)

            # Supprimer les doublons par URL
            seen_urls = set()
            unique_results = []
            for r in all_results:
                url = r.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(r)

            if self.session:
                await self.session.close()

            return {
                'query': query,
                'query_type': query_type,
                'engines_working': engines_working,
                'engines_failed': engines_failed,
                'total_results': len(unique_results),
                'results': unique_results[:20],
            }

        return asyncio.run(run_search())


if __name__ == '__main__':
    import sys

    test_query = sys.argv[1] if len(sys.argv) > 1 else 'torvalds'
    test_type = sys.argv[2] if len(sys.argv) > 2 else 'username'

    print(f"\n{'='*60}")
    print(f"Web Search: {test_query} ({test_type})")
    print(f"{'='*60}")

    investigator = WebSearchInvestigator(verbose=True)
    results = investigator.investigate(test_query, test_type)

    print(f"\nSources utilisées: {', '.join(results.get('engines_working', []))}")
    print(f"Sources échouées: {', '.join(results.get('engines_failed', []))}")
    print(f"Résultats trouvés: {results.get('total_results', 0)}")
    print(f"\n{'-'*60}")

    for i, result in enumerate(results.get('results', [])[:10], 1):
        print(f"\n{i}. [{result.get('engine', '?')}] {result.get('title', 'N/A')[:60]}")
        print(f"   URL: {result.get('url', 'N/A')[:70]}")
        snippet = result.get('snippet', '')
        if snippet:
            print(f"   {snippet[:100]}...")

    print(f"\n{'='*60}")
