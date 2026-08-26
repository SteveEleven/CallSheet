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
            "film_title": "The title of the film exactly as written in the script text (look for a title line, a heading, or a TITLE card). If the text states no title, return exactly UNTITLED. Never invent one.",
            "scenes": ["Scene numbers and titles"],
            "primary_location": "EXACTLY ONE location. If the text names no real, findable place on Earth - it is vague (\"a coastal town\", \"a car\", \"a room\") or fictional (Hogwarts, a Mars colony) - return exactly UNKNOWN. Never guess a real place the text does not name. Otherwise: EXACTLY ONE location - the single most important shooting location. Give a specific, searchable place name including city and province/state (e.g. \"Fisgard Lighthouse, Fort Rodd Hill, Colwood BC\"). Never a list, never a generic description like \"coastal town\".",
            "all_locations": ["Every distinct shooting location found, as searchable place names"],
            "primary_city": "The city, town or municipality the text names, with province/state and country (e.g. \"Victoria, British Columbia, Canada\"). If the text names a real city even when primary_location is UNKNOWN (a vague landmark in a named town), still return that city. Return exactly UNKNOWN only if the text names no real city. Never the landmark name. Never guess a city the text does not name.",
            "primary_region": "The larger metropolitan or regional area the city sits in, ending in the province/state (e.g. \"Greater Victoria, Vancouver Island, British Columbia\"). Small towns often have no hospital of their own, so this wider region is what the hospital search uses.",
            "characters": ["Cast members needed"],
            "time_of_day": "DAY / NIGHT / GOLDEN HOUR",
            "special_equipment": ["VFX, Crane, Drone, Pyro, etc."]
        }}

        SCRIPT TEXT:
        {script_text}
        """

        last_error = None
        for attempt in range(2):
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            try:
                return json.loads(response.text)
            except json.JSONDecodeError as e:
                last_error = e
                continue
        raise ValueError(
            "The script breakdown came back in a format we could not read. "
            "Please try again."
        ) from last_error

    def generate_call_sheet(self, script_text: str, shooting_date: str = "Tomorrow") -> dict:
        breakdown = self.parse_script_and_locations(script_text)
        location_target = (breakdown.get("primary_location") or "").strip()
        city_target = (breakdown.get("primary_city") or "").strip()
        region_target = (breakdown.get("primary_region") or "").strip()

        UNUSABLE = {"", "unknown", "n/a", "none", "tbd", "local studio", "unspecified"}

        def _unusable(value: str) -> bool:
            return value.lower() in UNUSABLE

        # One extra breakdown pass when the model zeros a city that a longer
        # synopsis actually named. Short unnamed lines ("a car") skip this.
        if _unusable(city_target) and len(script_text.strip()) > 60:
            breakdown = self.parse_script_and_locations(script_text)
            location_target = (breakdown.get("primary_location") or "").strip()
            city_target = (breakdown.get("primary_city") or "").strip()
            region_target = (breakdown.get("primary_region") or "").strip()

        # A fictional or unnamed landmark (Hogwarts, "a car") is not shootable
        # unless the text also names a real city. City is the gate: without one,
        # searching would return real sources for a place the crew is not going.
        if _unusable(city_target):
            return {
                "insufficient_location": True,
                "breakdown": breakdown,
                "grounded_context": "",
                "sources": [],
                "location_target": location_target or "UNKNOWN",
                "call_sheet_markdown": "",
            }

        if _unusable(location_target):
            location_target = city_target
        region_target = region_target if not _unusable(region_target) else city_target

        raw_search_results = self.parallel.search_location_intel(
            location_target, city=city_target, region=region_target
        )
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

        SCOPE - read this first. These rules govern REAL-WORLD FACTS ONLY: street addresses,
        hospitals, permit authorities, phone numbers, email addresses, opening hours, access
        restrictions, and the names of real organisations. Those are things you must look up.
        They do NOT govern production planning fields - film title, day number, unit base,
        crew call and cast call times, scene order, department notes, or anything drawn from
        the SCRIPT BREAKDOWN. Those are the coordinator's decisions, not facts about the world.
        Fill those in normally and sensibly:
          * FILM TITLE: use the "film_title" value from the SCRIPT BREAKDOWN verbatim.
            If it is UNTITLED, write UNTITLED. Never invent a title.
          * PRODUCTION COMPANY, DIRECTOR, PRODUCER, 1st AD, and any other named crew member
            or company: write "TBC". These are REAL PEOPLE AND REAL BUSINESSES. Inventing a
            person's name and printing it on a production document is never acceptable, not
            even as a realistic-looking placeholder.
          * DAY #, UNIT BASE, CALL TIMES: propose sensible values for the shoot date given.
          * WEATHER / SUNRISE / SUNSET: write "TBC - check forecast closer to the date".
        Never write "NOT FOUND IN LIVE RESEARCH" against any of those fields. Doing so makes
        the call sheet look broken rather than careful.

        - For REAL-WORLD FACTS: use ONLY what appears in the LIVE GROUNDED RESEARCH block above.
          That block is your only permitted source of real-world information.
        - If such a fact is NOT in the research - an address, a hospital, a permit authority,
          a phone number - you MUST write exactly this and nothing else for that field:
          "NOT FOUND IN LIVE RESEARCH - VERIFY BEFORE SHOOT DAY"
        - NEVER supply a fact from your own training knowledge. Never write "based on general
          knowledge", "typically", "is likely", or name a place the research did not name.
        - A hospital address you invented could kill someone. An honest gap is always correct;
          a plausible guess is always wrong. When in doubt, declare the gap.
        - THE HOSPITAL LINE - SAME-SOURCE RULE: the hospital NAME, its ADDRESS and its PHONE
          must all come from THE SAME single source entry in the research. Never assemble a
          hospital from parts of different sources. If the research names hospital A but the
          only address or phone you can see belongs to hospital B, or you cannot tell which
          hospital an address belongs to, keep the name and write
          "NOT FOUND IN LIVE RESEARCH - VERIFY BEFORE SHOOT DAY" for the address and phone.
          A real address attached to the wrong hospital is more dangerous than no address,
          because it looks verified.
        - THE HOSPITAL LINE: a source saying a hospital "serves" or "covers" a region does NOT
          establish that it is the CLOSEST one. Do not claim "nearest" unless the research states
          proximity or distance. Label the field "ER IDENTIFIED IN RESEARCH", name the source
          domain it came from in brackets, and always end that section with this line verbatim:
          "CONFIRM CLOSEST ER FOR YOUR EXACT LOCATION BEFORE SHOOT DAY - a hospital that serves
          a region is not always the nearest one to your set."
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
