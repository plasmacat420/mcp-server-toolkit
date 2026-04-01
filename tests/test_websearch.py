"""Tests for the web_search tool (httpx mocked with respx)."""

import respx
from httpx import Response

from mcp_toolkit.tools.websearch import _DDG_URL, web_search


@respx.mock
async def test_web_search_returns_results():
    """web_search parses RelatedTopics and returns the expected shape."""
    payload = {
        "RelatedTopics": [
            {
                "Text": "Python - A programming language",
                "FirstURL": "https://example.com/python",
            },
            {
                "Text": "FastMCP - An MCP framework",
                "FirstURL": "https://example.com/fastmcp",
            },
        ]
    }
    respx.get(_DDG_URL).mock(return_value=Response(200, json=payload))

    result = await web_search("python", max_results=5)

    assert "error" not in result
    assert result["query"] == "python"
    assert result["count"] == 2
    assert result["results"][0]["title"] == "Python"
    assert result["results"][0]["url"] == "https://example.com/python"
    assert "programming language" in result["results"][0]["snippet"]


@respx.mock
async def test_web_search_respects_max_results():
    """web_search caps results at max_results."""
    payload = {
        "RelatedTopics": [
            {"Text": f"Result {i} - snippet {i}", "FirstURL": f"https://x.com/{i}"}
            for i in range(10)
        ]
    }
    respx.get(_DDG_URL).mock(return_value=Response(200, json=payload))

    result = await web_search("test", max_results=3)

    assert result["count"] == 3
    assert len(result["results"]) == 3


@respx.mock
async def test_web_search_skips_topic_groups():
    """web_search ignores nested topic group entries (no Text key)."""
    payload = {
        "RelatedTopics": [
            {"Topics": [{"Text": "nested", "FirstURL": "https://x.com"}]},
            {"Text": "Direct result - snippet", "FirstURL": "https://y.com"},
        ]
    }
    respx.get(_DDG_URL).mock(return_value=Response(200, json=payload))

    result = await web_search("test", max_results=5)

    assert result["count"] == 1
    assert result["results"][0]["url"] == "https://y.com"


@respx.mock
async def test_web_search_http_error_returns_error():
    """web_search returns an error dict on HTTP failure."""
    respx.get(_DDG_URL).mock(return_value=Response(500))

    result = await web_search("fail")

    assert "error" in result
