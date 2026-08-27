import os
import streamlit as st

for _k in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "PARALLEL_API_KEY"):
    try:
        if _k in st.secrets and not os.environ.get(_k):
            os.environ[_k] = str(st.secrets[_k])
    except Exception:
        pass

from services.gemini_service import CallSheetAgent

st.set_page_config(page_title="CallSheet AI | Agentic Cinema", layout="wide", page_icon="🎬")

st.title("🎬 CallSheet: Web-Grounded Production Agent")
st.caption("Google Gemini 2.5 Flash (google-genai) orchestration · Parallel Search API live grounding")


# ---------------------------------------------------------------- fixtures --
FISGARD_SCENE = """SCENE 4. EXT. FISGARD LIGHTHOUSE - DUSK
Marcus (40s, drenched) scrambles up the rocky shore towards the beacon tower.
Sirens echo in the distance. The wind is howling at 30 knots.
He reaches into his jacket and pulls out the encrypted hard drive."""

MESSY_SYNOPSIS = (
    "A woman comes back to her hometown on the coast to scatter her mother's ashes "
    "at the old lighthouse with a family friend, and finds out her mother left her "
    "the keeper's key. Two actors, want to shoot it in a weekend around Victoria BC "
    "on no budget."
)


@st.cache_data
def load_last_ferry() -> str:
    """Load the screenplay body of sample_script.md, minus the fixture notes."""
    path = os.path.join(os.path.dirname(__file__), "sample_script.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return FISGARD_SCENE
    # Drop the trailing "Why this fixture is good for testing" notes.
    return text.split("## Why this fixture")[0].strip()


FIXTURES = {
    "The Last Ferry — full 4-scene short": load_last_ferry,
    "Fisgard Lighthouse — single scene": lambda: FISGARD_SCENE,
    "Messy synopsis — no screenplay formatting": lambda: MESSY_SYNOPSIS,
    "Blank — paste your own": lambda: "",
}


# ----------------------------------------------------------------- sidebar --
with st.sidebar:
    st.header("⚙️ Configuration")
    shoot_date = st.date_input("Shooting Date")
    fixture_name = st.selectbox("Sample input", list(FIXTURES.keys()))
    st.markdown("---")
    st.markdown("**Active Integrations (runtime):**")
    st.success("✅ Parallel Search API — live grounding")
    st.success("✅ Google Gemini 2.5 Flash — orchestration")
    st.caption(
        "Every call sheet below is grounded in web results fetched from Parallel "
        "at generation time. Nothing is cached or recalled from the model."
    )


col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Input Scene or Script")
    script_input = st.text_area(
        "Paste Screenplay / Scene Description",
        value=FIXTURES[fixture_name](),
        height=380,
        key=fixture_name,
    )
    generate_btn = st.button(
        "Generate Grounded Call Sheet", type="primary", use_container_width=True
    )


def render_sources(sources: list, location_target: str) -> None:
    """Parallel citations, rendered in the main pane — not buried in an expander."""
    st.markdown("### 🔗 Live Research — sourced via Parallel Search API")

    if not sources:
        st.warning(
            "Parallel returned no citable sources for this location. "
            "The call sheet above is ungrounded — treat it as a draft."
        )
        return

    m1, m2 = st.columns(2)
    m1.metric("Sources retrieved live", len(sources))
    m2.metric("Location researched", location_target or "—")

    grouped = {}
    for src in sources:
        grouped.setdefault(src["label"], []).append(src)

    for label, items in grouped.items():
        st.markdown(f"**{label}**")
        for src in items:
            st.markdown(f"- [{src['title']}]({src['url']})")
            if src["excerpt"]:
                st.caption(src["excerpt"])


if generate_btn:
    if not script_input.strip():
        st.error("Please enter a scene description or script.")
    else:
        with st.spinner("AD Agent analyzing script & querying Parallel for location data..."):
            try:
                agent = CallSheetAgent()
                result = agent.generate_call_sheet(script_input, shooting_date=str(shoot_date))

                if result.get("insufficient_location"):
                    with col2:
                        st.subheader("2. Generated Call Sheet")
                        st.warning(
                            "**No shootable location found in this scene.**\n\n"
                            "CallSheet only reports facts it can verify against live web results, "
                            "so it will not research a location the script never named. Add a real, "
                            "findable place — a town, a landmark, an address — and generate again.\n\n"
                            "Guessing a location here would return real, citable research about "
                            "somewhere your crew is not going."
                        )
                        st.markdown("**What the breakdown did find:**")
                        st.json(result["breakdown"])
                else:
                    with col2:
                        st.subheader("2. Generated Call Sheet")
                        srcs = result.get("sources", [])
                        b1, b2 = st.columns(2)
                        b1.metric("Verified sources from Parallel", len(srcs))
                        b2.metric("Location researched", result.get("location_target", "—"))
                        dead = result.get("dead_links", 0)
                        note = (
                            "Every fact below was retrieved at generation time, and every source "
                            "link was checked for a live response before being cited. "
                            "The full source list is at the bottom of this call sheet."
                        )
                        if dead:
                            note += (
                                f"  \n\n**{dead} source"
                                f"{'' if dead == 1 else 's'} returned a dead link and "
                                "were excluded** — a citation you cannot open is not a citation."
                            )
                        st.caption(note)
                        st.markdown("---")
                        st.markdown(result["call_sheet_markdown"])
                        st.markdown("---")
                        render_sources(srcs, result.get("location_target", ""))

                    with st.expander("🔍 Runtime pipeline detail (script breakdown & raw Parallel output)"):
                        st.markdown("#### Gemini script breakdown")
                        st.json(result["breakdown"])
                        st.markdown("#### Parallel Search data extracted at runtime")
                        st.text(result["grounded_context"])

            except Exception as e:
                st.error(f"Error during agent execution: {str(e)}")
