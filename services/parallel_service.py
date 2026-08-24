import os
import requests
from dotenv import load_dotenv

load_dotenv()

PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
PARALLEL_SEARCH_URL = "https://api.parallel.ai/v1/search"

class ParallelSearchService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or PARALLEL_API_KEY
        if not self.api_key:
            raise ValueError("PARALLEL_API_KEY is not set in environment or .env file.")

    def search_location_intel(self, location_name: str) -> dict:
        queries = [
            f"{location_name} exact address parking and physical access notes",
            f"nearest emergency hospital near {location_name} address contact",
            f"filming permit and municipal jurisdiction for {location_name}"
        ]

        # FIXED: Parallel uses x-api-key header, not Bearer token
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        results = {}
        for query in queries:
            try:
                # FIXED: Parallel v1 uses search_queries list and mode
                payload = {
                    "search_queries": [query], 
                    "mode": "turbo"
                }
                response = requests.post(
                    PARALLEL_SEARCH_URL,
                    headers=headers,
                    json=payload,
                    timeout=12
                )
                if response.status_code == 200:
                    results[query] = response.json()
                else:
                    results[query] = {"error": f"HTTP {response.status_code}", "detail": response.text}
            except Exception as e:
                results[query] = {"error": str(e)}

        return results

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
