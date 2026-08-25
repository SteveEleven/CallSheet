import os
import requests
from dotenv import load_dotenv

load_dotenv()

PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
PARALLEL_SEARCH_URL = "https://api.parallel.ai/v1/search"


class ParallelSearchService:
    """Live web grounding for CallSheet, powered by the Parallel Search API.

    Every call sheet this app produces is grounded in results fetched from
    Parallel at runtime -- nothing here is cached, mocked, or model-recalled.
    """

    # The three questions a real 1st AD has to answer before a shoot day.
    QUERY_TEMPLATES = [
        ("Location & Access", "{location} exact address parking and physical access notes"),
        ("Nearest Hospital", "nearest emergency hospital near {location} address contact"),
        ("Permits & Jurisdiction", "filming permit and municipal jurisdiction for {location}"),
    ]

    def __init__(self, api_key: str = None):
        self.api_key = api_key or PARALLEL_API_KEY
        if not self.api_key:
            raise ValueError("PARALLEL_API_KEY is not set in environment or .env file.")

    def search_location_intel(self, location_name: str) -> dict:
        # FIXED: Parallel uses x-api-key header, not Bearer token
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        results = {}
        for label, template in self.QUERY_TEMPLATES:
            query = template.format(location=location_name)
            try:
                # FIXED: Parallel v1 uses search_queries list and mode
                payload = {
                    "search_queries": [query],
                    "mode": "turbo",
                }
                response = requests.post(
                    PARALLEL_SEARCH_URL,
                    headers=headers,
                    json=payload,
                    timeout=12,
                )
                if response.status_code == 200:
                    results[query] = response.json()
                else:
                    results[query] = {
                        "error": f"HTTP {response.status_code}",
                        "detail": response.text,
                    }
            except Exception as e:
                results[query] = {"error": str(e)}
            # Keep the human-readable label alongside the raw query.
            if isinstance(results.get(query), dict):
                results[query]["_callsheet_label"] = label

        return results

    def extract_sources(self, search_results: dict) -> list:
        """Flatten Parallel's response into citations the UI can render directly.

        Returns a list of {label, query, title, url, excerpt} dicts, deduplicated
        by URL so the same source is not listed three times.
        """
        sources = []
        seen_urls = set()

        for query, data in search_results.items():
            if not isinstance(data, dict):
                continue
            label = data.get("_callsheet_label", "Research")
            items = data.get("results")
            if not isinstance(items, list):
                continue
            for item in items:
                url = item.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                excerpts = item.get("excerpts", [])
                excerpt = excerpts[0].strip() if excerpts else ""
                sources.append({
                    "label": label,
                    "query": query,
                    "title": item.get("title") or url,
                    "url": url,
                    "excerpt": excerpt[:400],
                })

        return sources

    def format_search_context(self, search_results: dict) -> str:
        context_chunks = []
        for query, data in search_results.items():
            context_chunks.append(f"### Research Query: {query}")
            if "results" in data and isinstance(data["results"], list):
                for item in data["results"]:
                    title = item.get("title", "Source")
                    # FIXED: Parallel returns a list of 'excerpts' instead of 'snippet'
                    excerpts = item.get("excerpts", [])
                    snippet = excerpts[0][:500] if excerpts else ""
                    url = item.get("url", "")
                    context_chunks.append(f"- **{title}** ({url}): {snippet}")
            else:
                context_chunks.append(f"Raw Output: {str(data)}")
            context_chunks.append("\n")
        return "\n".join(context_chunks)
