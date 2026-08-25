import os
import json
from dotenv import load_dotenv
from google import genai
from services.parallel_service import ParallelSearchService

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

class CallSheetAgent:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be configured in .env.")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.parallel = ParallelSearchService()

    def parse_script_and_locations(self, script_text: str) -> dict:
        prompt = f"""
        You are an expert Hollywood Assistant Director (1st AD).
        Analyze the following scene text and extract key production requirements in valid JSON format:
        {{
            "scenes": ["Scene numbers and titles"],
            "primary_location": "EXACTLY ONE location - the single most important shooting location. Give a specific, searchable place name including city and province/state (e.g. \"Fisgard Lighthouse, Fort Rodd Hill, Colwood BC\"). Never a list, never a generic description like \"coastal town\".",
            "all_locations": ["Every distinct shooting location found, as searchable place names"],
            "primary_city": "The city, town or municipality containing primary_location, with province/state and country (e.g. \"Colwood, British Columbia, Canada\"). This is used to find the nearest hospital, so give the municipality - never the landmark name.",
            "characters": ["Cast members needed"],
            "time_of_day": "DAY / NIGHT / GOLDEN HOUR",
            "special_equipment": ["VFX, Crane, Drone, Pyro, etc."]
        }}

        SCRIPT TEXT:
        {script_text}
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)

    def generate_call_sheet(self, script_text: str, shooting_date: str = "Tomorrow") -> dict:
        breakdown = self.parse_script_and_locations(script_text)
        location_target = breakdown.get("primary_location", "Local Studio")
        city_target = breakdown.get("primary_city") or location_target

        raw_search_results = self.parallel.search_location_intel(location_target, city=city_target)
        grounded_context = self.parallel.format_search_context(raw_search_results)
        sources = self.parallel.extract_sources(raw_search_results)

        synthesis_prompt = f"""
        You are a seasoned Production Coordinator.
        Generate a professional, fully realized Call Sheet based on the script breakdown and live location intelligence.

        SHOOT DATE: {shooting_date}
        SCRIPT BREAKDOWN:
        {json.dumps(breakdown, indent=2)}

        LIVE GROUNDED RESEARCH (FROM PARALLEL SEARCH API):
        {grounded_context}

        Produce a structured call sheet with:
        1. **Production Header & General Call Time**
        2. **Location & Parking Details** (Include verified addresses and notes from research)
        3. **Hospital & Emergency Information** (Must reflect real hospital data found in research)
        4. **Scene Schedule & Cast Call Times**
        5. **Special Department Notes** (Permits, Sound, Safety precautions)
        6. **Grounding Traceability**: List URLs and sources provided by Parallel.

        ABSOLUTE RULES - these override every other instruction:
        - Use ONLY facts that appear in the LIVE GROUNDED RESEARCH block above. That block is your
          only permitted source of real-world information.
        - If a required detail is NOT in the research - an address, a hospital, a permit authority,
          a phone number - you MUST write exactly this and nothing else for that field:
          "NOT FOUND IN LIVE RESEARCH - VERIFY BEFORE SHOOT DAY"
        - NEVER supply a fact from your own training knowledge. Never write "based on general
          knowledge", "typically", "is likely", or name a place the research did not name.
        - A hospital address you invented could kill someone. An honest gap is always correct;
          a plausible guess is always wrong. When in doubt, declare the gap.
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=synthesis_prompt
        )

        return {
            "breakdown": breakdown,
            "grounded_context": grounded_context,
            "sources": sources,
            "location_target": location_target,
            "call_sheet_markdown": response.text
        }
