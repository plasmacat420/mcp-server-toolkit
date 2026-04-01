"""Web search tool powered by the DuckDuckGo free JSON API."""

import httpx

_DDG_URL = "https://api.duckduckgo.com/"
_HEADERS = {"User-Agent": "mcp-toolkit/0.1.0"}


async def web_search(query: str, max_results: int = 5) -> dict:
    """Search the web using DuckDuckGo's free API (no API key required).

    Args:
        query: Search query string.
        max_results: Maximum number of results to return (default 5).

    Returns:
        Dict with keys ``results`` (list of {title, url, snippet}),
        ``query``, and ``count``, or ``{"error": message}`` on failure.
    """
    try:
        async with httpx.AsyncClient(headers=_HEADERS, timeout=10.0) as client:
            response = await client.get(
                _DDG_URL,
                params={
                    "q": query,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1",
                },
            )
            response.raise_for_status()
            data = response.json()

        results: list[dict] = []
        for topic in data.get("RelatedTopics", []):
            if len(results) >= max_results:
                break
            # Skip nested topic groups (they have a "Topics" key, not "Text")
            if "Text" not in topic or "FirstURL" not in topic:
                continue
            text: str = topic["Text"]
            url: str = topic["FirstURL"]
            parts = text.split(" - ", 1)
            title = parts[0] if len(parts) > 1 else text[:60]
            snippet = parts[1] if len(parts) > 1 else text
            results.append({"title": title, "url": url, "snippet": snippet})

        return {"results": results, "query": query, "count": len(results)}
    except Exception as exc:
        return {"error": str(exc)}
