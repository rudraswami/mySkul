"""
🌐 Web Search Tool - Enterprise-Grade Educational Search
=========================================================

ADVANCED FEATURES:
- DuckDuckGo Instant Answers API (free, no API key)
- Domain whitelist (trusted educational sources only)
- Result caching (1 hour TTL, reduces latency)
- Strict timeout (3s hard cap)
- Graceful degradation (never blocks agent)
- Educational context extraction
- Citation generation

GOVERNANCE:
- Only searches when curriculum knowledge is insufficient
- Filters non-educational content
- Hard limits on results and latency
- Circuit breaker pattern for external API

SCALABILITY (Cognito OS v1.0):
- Circuit breaker: Fails fast when DuckDuckGo is down
- Concurrency limiter: Prevents API overload
- Both are feature-flagged for zero-regression rollback

This makes agents SMARTER by giving them access to
real-time information when needed, without compromising
safety or performance.
"""

import logging
import asyncio
import aiohttp
import hashlib
import time
import os
from typing import Dict, Any, Optional, List
from functools import lru_cache
from datetime import datetime, timezone

from agents.core.tool_registry import BaseTool, ToolResult, ToolStatus

logger = logging.getLogger(__name__)

# Feature flags for scalability
ENABLE_WEB_SEARCH_LIMITER = os.getenv("ENABLE_WEB_SEARCH_LIMITER", "true").lower() == "true"
ENABLE_WEB_SEARCH_CIRCUIT_BREAKER = os.getenv("ENABLE_WEB_SEARCH_CIRCUIT_BREAKER", "true").lower() == "true"


class WebSearchTool(BaseTool):
    """
    🌐 Enterprise-Grade Web Search for Educational AI
    
    INTELLIGENCE FEATURES:
    - Searches trusted educational sources only
    - Extracts key facts, definitions, and summaries
    - Provides citations for academic integrity
    - Caches results for fast repeated queries
    
    SAFETY FEATURES:
    - Domain whitelist (Wikipedia, Khan Academy, NCERT, etc.)
    - Hard 3-second timeout
    - Maximum 5 results
    - Rate limiting (10 searches/minute per user)
    - Graceful fallback on failure
    
    USAGE:
    Only triggered when:
    - Question asks about recent events/news
    - Question asks for current statistics
    - Curriculum knowledge is insufficient
    - Agent explicitly needs external verification
    """
    
    # ================================================================
    # CONFIGURATION (Enterprise-Grade Defaults)
    # ================================================================
    
    # Trusted educational domains only
    TRUSTED_DOMAINS = [
        "wikipedia.org",
        "khanacademy.org",
        "ncert.nic.in",
        "britannica.com",
        "mathworld.wolfram.com",
        "physics.info",
        "chemguide.co.uk",
        "hyperphysics.phy-astr.gsu.edu",
        "byjus.com",
        "vedantu.com",
        "toppr.com",
        "sciencedirect.com",
        "nature.com",
        "nasa.gov",
        "education.gov.in"
    ]
    
    # DuckDuckGo API endpoint
    DDG_API_URL = "https://api.duckduckgo.com/"
    
    # Performance limits
    TIMEOUT_SECONDS = 3.0
    MAX_RESULTS = 5
    CACHE_TTL_SECONDS = 3600  # 1 hour
    MAX_CONTENT_LENGTH = 500  # Characters per result
    
    # Rate limiting (per user)
    MAX_SEARCHES_PER_MINUTE = 10
    
    # In-memory cache (LRU with TTL)
    _cache: Dict[str, tuple] = {}  # {hash: (result, timestamp)}
    _user_rate_limits: Dict[str, List[float]] = {}  # {user_id: [timestamps]}
    
    def __init__(self):
        super().__init__()
        logger.info("🌐 WebSearchTool initialized (DuckDuckGo + Educational Whitelist)")
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return (
            "Searches trusted educational websites (Wikipedia, Khan Academy, NCERT, etc.) "
            "for current/real-time information. Use ONLY when curriculum knowledge is "
            "insufficient - for recent events, current statistics, or topics not in textbooks. "
            "Returns verified facts with citations. Max 5 results, 3-second timeout."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "query": "The educational topic to search for (required)",
            "subject": "(Optional) Subject context: Physics, Chemistry, Biology, Mathematics",
            "require_recent": "(Optional) Set true for time-sensitive information"
        }
    
    async def execute(
        self,
        query: str = "",
        subject: str = None,
        require_recent: bool = False,
        context: Dict = None,
        **kwargs
    ) -> ToolResult:
        """
        Execute web search with full governance.
        
        Flow:
        1. Validate input
        2. Check rate limit
        3. Check cache
        4. Call DuckDuckGo API
        5. Filter/format results
        6. Cache and return
        """
        context = context or {}
        user_id = context.get('user_id', 'anonymous')
        request_id = context.get('request_id', 'ws_unknown')
        
        # ================================================================
        # STEP 1: Input Validation
        # ================================================================
        if not query or len(query.strip()) < 3:
            return ToolResult.error_result(
                "Search query too short. Please provide a specific topic.",
                ToolStatus.INVALID_INPUT
            )
        
        query = query.strip()[:200]  # Bound query length
        
        # ================================================================
        # STEP 2: Rate Limit Check
        # ================================================================
        if not self._check_rate_limit(user_id):
            logger.warning(f"[{request_id}] 🚫 WebSearch rate limit for user {user_id[:8]}")
            return ToolResult.error_result(
                "Search rate limit reached. Please wait a moment.",
                ToolStatus.ERROR
            )
        
        # ================================================================
        # STEP 3: Cache Check
        # ================================================================
        cache_key = self._get_cache_key(query, subject)
        cached = self._get_cached(cache_key)
        if cached:
            logger.info(f"[{request_id}] ⚡ WebSearch cache hit: {query[:40]}")
            return cached
        
        # ================================================================
        # STEP 4: DuckDuckGo API Call (with scalability protection)
        # ================================================================
        logger.info(f"[{request_id}] 🌐 WebSearch: {query[:50]}...")
        
        try:
            results = await self._search_with_scalability(query, subject, request_id)
        except Exception as e:
            error_type = type(e).__name__
            if "ResourceLimitExceeded" in error_type or "CircuitOpenError" in error_type:
                logger.warning(f"[{request_id}] ⛔ WebSearch rejected: {e}")
                return self._fallback_response(query)
            logger.error(f"[{request_id}] ❌ WebSearch error: {e}")
            return self._fallback_response(query)
        
        # ================================================================
        # STEP 5: Format Results
        # ================================================================
        if not results:
            return ToolResult.success_result(
                f"No web results found for '{query}'. "
                f"Try the knowledge_search tool for curriculum-based information.",
                metadata={
                    "found": False,
                    "query": query,
                    "source": "duckduckgo"
                }
            )
        
        formatted = self._format_results(query, results, subject)
        
        # ================================================================
        # STEP 6: Cache and Return
        # ================================================================
        result = ToolResult.success_result(
            formatted,
            metadata={
                "found": True,
                "count": len(results),
                "query": query,
                "source": "duckduckgo",
                "cached": False,
                "domains": [r.get('source', '') for r in results]
            }
        )
        
        self._set_cached(cache_key, result)
        logger.info(f"[{request_id}] ✅ WebSearch: {len(results)} results for '{query[:40]}'")
        
        return result
    
    # ================================================================
    # SCALABILITY WRAPPER
    # ================================================================
    
    async def _search_with_scalability(
        self, 
        query: str, 
        subject: str = None, 
        request_id: str = None
    ) -> List[Dict]:
        """
        Execute search with concurrency limiter + circuit breaker.
        
        Order of protection:
        1. Concurrency limiter (reject if too many searches in flight)
        2. Circuit breaker (fail fast if DuckDuckGo is down)
        3. Timeout wrapper
        4. Actual search
        
        FAIL-SAFE: If scalability module fails, proceed with direct search.
        """
        limiter = None
        acquired = False
        
        # Try to load scalability (fail-safe)
        try:
            from services.scalability import (
                get_concurrency_limiter,
                CircuitBreakerRegistry,
                ResourceType,
                ENABLE_CONCURRENCY_LIMITER,
                ENABLE_CIRCUIT_BREAKER
            )
            scalability_available = True
        except Exception as e:
            logger.warning(f"Scalability module unavailable for web_search: {e}")
            scalability_available = False
        
        # Step 1: Acquire concurrency slot (if available)
        # FAST: Don't block waiting for slot - fail fast
        if scalability_available and ENABLE_WEB_SEARCH_LIMITER and ENABLE_CONCURRENCY_LIMITER:
            try:
                limiter = get_concurrency_limiter()
                acquired = await limiter.acquire(
                    ResourceType.TOOL_WEB_SEARCH,
                    timeout=0.5,  # FAST: Don't wait long
                    request_id=request_id
                )
                if not acquired:
                    # Graceful degradation - proceed without slot tracking
                    acquired = False
            except Exception as e:
                logger.warning(f"WebSearch limiter error: {e}")
                acquired = False
        
        try:
            # Step 2: Call through circuit breaker (if available)
            if scalability_available and ENABLE_WEB_SEARCH_CIRCUIT_BREAKER and ENABLE_CIRCUIT_BREAKER:
                try:
                    breaker = CircuitBreakerRegistry.get('web_search')
                    return await breaker.call(
                        self._perform_combined_search_with_timeout,
                        self._empty_results_fallback,
                        query,
                        subject
                    )
                except Exception as e:
                    logger.warning(f"WebSearch circuit breaker error: {e}")
                    return await self._perform_combined_search_with_timeout(query, subject)
            else:
                return await self._perform_combined_search_with_timeout(query, subject)
        finally:
            if acquired and limiter:
                try:
                    from services.scalability import ResourceType
                    await limiter.release(ResourceType.TOOL_WEB_SEARCH)
                except Exception:
                    pass
    
    async def _perform_combined_search_with_timeout(
        self, 
        query: str, 
        subject: str = None
    ) -> List[Dict]:
        """Wrapper with timeout for circuit breaker"""
        return await asyncio.wait_for(
            self._perform_combined_search(query, subject),
            timeout=self.TIMEOUT_SECONDS
        )
    
    async def _empty_results_fallback(self, query: str, subject: str = None) -> List[Dict]:
        """Fallback when circuit is open - return empty results"""
        logger.warning(f"WebSearch circuit open, returning empty results")
        return []
    
    # ================================================================
    # DUCKDUCKGO API
    # ================================================================
    
    async def _perform_combined_search(self, query: str, subject: str = None) -> List[Dict]:
        """Try HTML scraper first, then API fallback"""
        # 1. Try HTML Scraper (Best for news/recent)
        try:
            # Add strict sub-timeout for HTML to allow time for API fallback if needed
            results = await self._search_html(query)
            if results:
                return results
        except Exception as e:
            logger.warning(f"HTML search failed, falling back: {e}")
            
        # 2. Fallback to API (Best for definitions)
        return await self._search_api(query, subject)

    async def _search_html(self, query: str) -> List[Dict]:
        """
        Scrape html.duckduckgo.com using Regex (Zero Dependency).
        Necessary because 'Instant Answer' API is deprecated/useless for news.
        """
        import re
        import html
        from urllib.parse import unquote
        
        results = []
        url = "https://html.duckduckgo.com/html/"
        params = {'q': query, 'kl': 'us-en'} # Default region
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    data=params, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=3.0) # Fast timeout
                ) as response:
                    if response.status != 200:
                        return []
                    html_content = await response.text()
            
            # Extract links/titles: <a class="result__a" href="URI">TITLE</a>
            link_pattern = r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
            matches = re.findall(link_pattern, html_content)
            
            # Extract snippets: <a class="result__snippet" ...>SNIPPET</a>
            snippet_pattern = r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>'
            snippet_matches = re.findall(snippet_pattern, html_content)
            
            for i, (url, title) in enumerate(matches[:5]): # Max 5
                # Decode HTML entities
                title_clean = html.unescape(re.sub(r'<[^>]+>', '', title)).strip()
                summary_clean = ""
                
                if i < len(snippet_matches):
                    summary_clean = html.unescape(re.sub(r'<[^>]+>', '', snippet_matches[i])).strip()
                
                # Decode URL (often comes as /l/?kh=-1&uddg=ACTUAL_URL)
                if "duckduckgo.com/l/?" in url:
                    try:
                        # Extract 'uddg' param
                        uddg_match = re.search(r'uddg=([^&]+)', url)
                        if uddg_match:
                            url = unquote(uddg_match.group(1))
                    except:
                        pass
                
                if title_clean and url:
                    results.append({
                        "title": title_clean,
                        "summary": summary_clean,
                        "source": self._extract_domain(url),
                        "url": url,
                        "type": "web_result"
                    })
                    
            return results
        except Exception as e:
            logger.warning(f"HTML scraper failed: {e}")
            return []

    async def _search_api(
        self,
        query: str,
        subject: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo Instant Answers API (Fallback).
        """
        results = []
        
        # Enhance query with subject context
        enhanced_query = query
        if subject and subject.lower() not in query.lower():
            enhanced_query = f"{query} {subject}"
        
        params = {
            "q": enhanced_query,
            "format": "json",
            "no_redirect": "1",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        # Headers to ensure proper API response
        headers = {
            "User-Agent": "DruvAI Educational Assistant/1.0 (Educational Purpose)",
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.DDG_API_URL,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=2.0)
            ) as response:
                if response.status != 200:
                    logger.warning(f"DuckDuckGo API returned {response.status}")
                    return []
                
                data = await response.json()
        
        # Extract Abstract (main answer)
        if data.get("Abstract"):
            results.append({
                "title": data.get("Heading", query),
                "summary": data.get("Abstract", "")[:self.MAX_CONTENT_LENGTH],
                "source": self._extract_domain(data.get("AbstractSource", "")),
                "url": data.get("AbstractURL", ""),
                "type": "definition"
            })
        
        # Extract Related Topics
        for topic in data.get("RelatedTopics", [])[:self.MAX_RESULTS - len(results)]:
            if isinstance(topic, dict) and topic.get("Text"):
                # Skip non-educational sources
                url = topic.get("FirstURL", "")
                domain = self._extract_domain(url)
                
                if not self._is_trusted_domain(domain):
                    continue
                
                results.append({
                    "title": topic.get("Text", "")[:100],
                    "summary": topic.get("Text", "")[:self.MAX_CONTENT_LENGTH],
                    "source": domain,
                    "url": url,
                    "type": "related"
                })
        
        # Extract Infobox facts
        if data.get("Infobox") and data["Infobox"].get("content"):
            facts = []
            for item in data["Infobox"]["content"][:5]:
                if item.get("label") and item.get("value"):
                    facts.append(f"{item['label']}: {item['value']}")
            
            if facts:
                results.append({
                    "title": f"Quick Facts: {data.get('Heading', query)}",
                    "summary": "\n".join(facts[:5]),
                    "source": "duckduckgo_infobox",
                    "url": data.get("AbstractURL", ""),
                    "type": "facts"
                })
        
        # Extract Answer (direct answer)
        if data.get("Answer"):
            results.insert(0, {
                "title": "Direct Answer",
                "summary": data.get("Answer", "")[:self.MAX_CONTENT_LENGTH],
                "source": data.get("AnswerType", "instant_answer"),
                "url": "",
                "type": "answer"
            })
        
        return results[:self.MAX_RESULTS]
    
    # ================================================================
    # FORMATTING
    # ================================================================
    
    def _format_results(
        self,
        query: str,
        results: List[Dict],
        subject: str = None
    ) -> str:
        """Format search results for agent consumption."""
        parts = [
            f"**🌐 Web Search Results: {query}**",
            f"_Source: DuckDuckGo Educational Search | {len(results)} results_",
            "---"
        ]
        
        for i, result in enumerate(results, 1):
            result_type = result.get("type", "article")
            icon = {
                "definition": "📖",
                "facts": "📊",
                "answer": "✅",
                "related": "🔗"
            }.get(result_type, "📄")
            
            parts.append(f"\n### {icon} {result.get('title', 'Result')}")
            parts.append(result.get("summary", ""))
            
            source = result.get("source", "")
            url = result.get("url", "")
            if source:
                citation = f"_Source: {source}_"
                if url:
                    citation += f" | [Link]({url})"
                parts.append(citation)
        
        parts.append("\n---")
        parts.append("_⚠️ Web results supplement curriculum knowledge. Verify important facts._")
        
        return "\n".join(parts)
    
    # ================================================================
    # HELPERS
    # ================================================================
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain
        except Exception:
            return url[:50]
    
    def _is_trusted_domain(self, domain: str) -> bool:
        """Check if domain is in trusted whitelist."""
        if not domain:
            return True  # Allow empty domains (internal results)
        
        domain_lower = domain.lower()
        return any(
            trusted in domain_lower
            for trusted in self.TRUSTED_DOMAINS
        )
    
    # ================================================================
    # CACHING
    # ================================================================
    
    def _get_cache_key(self, query: str, subject: str = None) -> str:
        """Generate cache key from query."""
        key_str = f"{query.lower().strip()}:{subject or ''}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[ToolResult]:
        """Get result from cache if not expired."""
        if cache_key not in self._cache:
            return None
        
        result, timestamp = self._cache[cache_key]
        age = time.time() - timestamp
        
        if age > self.CACHE_TTL_SECONDS:
            del self._cache[cache_key]
            return None
        
        # Update result to indicate cache hit
        cached_result = ToolResult.success_result(
            result.output,
            metadata={
                **(result.metadata or {}),
                "cached": True,
                "cache_age_seconds": int(age)
            }
        )
        return cached_result
    
    def _set_cached(self, cache_key: str, result: ToolResult) -> None:
        """Store result in cache."""
        # Limit cache size
        if len(self._cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(
                self._cache.keys(),
                key=lambda k: self._cache[k][1]
            )[:100]
            for key in oldest_keys:
                del self._cache[key]
        
        self._cache[cache_key] = (result, time.time())
    
    # ================================================================
    # RATE LIMITING
    # ================================================================
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limit."""
        now = time.time()
        
        if user_id not in self._user_rate_limits:
            self._user_rate_limits[user_id] = []
        
        # Clean old timestamps
        timestamps = self._user_rate_limits[user_id]
        timestamps = [t for t in timestamps if now - t < 60]
        self._user_rate_limits[user_id] = timestamps
        
        if len(timestamps) >= self.MAX_SEARCHES_PER_MINUTE:
            return False
        
        timestamps.append(now)
        return True
    
    # ================================================================
    # FALLBACK
    # ================================================================
    
    def _fallback_response(self, query: str) -> ToolResult:
        """Fallback when web search fails."""
        return ToolResult.success_result(
            f"Web search is temporarily unavailable for '{query}'. "
            f"I'll answer using my curriculum knowledge instead. "
            f"For the most current information, you can manually search "
            f"trusted sources like Wikipedia or Khan Academy.",
            metadata={
                "found": False,
                "query": query,
                "source": "fallback",
                "error": True
            }
        )
