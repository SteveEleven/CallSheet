import streamlit as st
from services.gemini_service import CallSheetAgent

st.set_page_config(page_title="CallSheet AI | Agentic Cinema", layout="wide", page_icon="🎬")

st.title("🎬 CallSheet: Web-Grounded Production Agent")
st.caption("Powered by Gemini 3.1 Pro & Parallel Search API Grounding")

with st.sidebar:
    st.header("⚙️ Configuration")
    shoot_date = st.date_input("Shooting Date")
    st.markdown("---")
    st.markdown("**Active Integrations:**")
    st.success("✅ Parallel Search API (Runtime Grounding)")
    st.success("✅ Google Gemini 3.1 Pro (Orchestration)")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Input Scene or Script")
    sample_script = """SCENE 4. EXT. FISGARD LIGHTHOUSE - DUSK
Marcus (40s, drenched) scrambles up the rocky shore towards the beacon tower.
Sirens echo in the distance. The wind is howling at 30 knots.
He reaches into his jacket and pulls out the encrypted hard drive."""

    script_input = st.text_area("Paste Screenplay / Scene Description", value=sample_script, height=280)
    generate_btn = st.button("Generate Grounded Call Sheet", type="primary", use_container_width=True)

if generate_btn:
    if not script_input.strip():
        st.error("Please enter a scene description or script.")
    else:
        with st.spinner("AD Agent analyzing script & querying Parallel for location data..."):
            try:
                agent = CallSheetAgent()
                result = agent.generate_call_sheet(script_input, shooting_date=str(shoot_date))

                with col2:
                    st.subheader("2. Generated Call Sheet")
                    st.markdown(result["call_sheet_markdown"])

                with st.expander("🔍 View Runtime Grounding Pipeline (Parallel API Output & Breakdown)"):
                    st.json(result["breakdown"])
                    st.markdown("#### Parallel Search Data Extracted at Runtime:")
                    st.text(result["grounded_context"])

            except Exception as e:
                st.error(f"Error during agent execution: {str(e)}")
