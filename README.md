# 🎬 CallSheet — a web-grounded production agent

**Agentic Cinema Hackathon · Parallel track**

CallSheet turns a screenplay scene into a real, shootable call sheet — with the
location, hospital, and permit details **verified against the live web at
generation time**, not recalled from a model's memory.

Paste a scene. Gemini breaks it down. Parallel Search goes and finds out where
the place actually is, where the nearest ER is, and who issues the film permit.
Gemini writes the call sheet from those real results, and every source is cited
on the page.

---

## Why this matters

A hallucinated hospital address on a call sheet is not a bad demo — it is a
safety incident. Production paperwork is exactly the category of document where
"plausible" is worthless and "verified" is the whole job. That is why the
grounding step here is load-bearing rather than decorative.

---

## Required-technology compliance

| Requirement | How CallSheet meets it | Where in the code |
|---|---|---|
| **Google Cloud AI** | `google-genai` SDK, model `gemini-2.5-flash`, called at runtime on every generation | `services/gemini_service.py` — `genai.Client(...)`, two `generate_content` calls |
| **Parallel track: Parallel Search API at runtime** | Three live `POST https://api.parallel.ai/v1/search` calls per generation, `mode=turbo` | `services/parallel_service.py` — `search_location_intel()` |
| **Open-source license** | MIT | `LICENSE` |

Neither integration is a stub. Remove either one and the app stops producing
output — there is no cached, mocked, or fallback data path.

> **Model note:** this project runs on **`gemini-2.5-flash`**. An early commit
> message mentions Gemini 3.1 Pro; that endpoint was never used in working code
> and the history was left intact rather than rewritten.

---

## How it works

```
Scene text
    │
    ▼
[1] Breakdown Agent — Gemini 2.5 Flash
    Extracts: scenes, primary location, characters, time of day, special equipment
    │
    ▼
[2] Research — Parallel Search API  ◀── live web, at runtime
    Q1  exact address, parking, physical access
    Q2  nearest emergency hospital + contact
    Q3  filming permit + municipal jurisdiction
    │
    ▼
[3] Call Sheet Agent — Gemini 2.5 Flash
    Synthesises breakdown + grounded research into a production call sheet
    │
    ▼
Call sheet + visible source citations
```

The three research questions are the ones a 1st AD has to answer before any
shoot day, which is why they are the ones the agent asks.

---

## Running it locally

```bash
git clone https://github.com/SteveEleven/CallSheet.git
cd CallSheet
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_google_api_key
PARALLEL_API_KEY=your_parallel_api_key
```

Then:

```bash
streamlit run app.py
```

`.env` is gitignored. No key is ever committed, logged, or rendered in the UI.

---

## Sample inputs

Four inputs ship with the app, selectable in the sidebar:

- **The Last Ferry** — an original 4-scene short (`sample_script.md`), written
  for this project. Four locations, three characters, a day/night spread.
- **Fisgard Lighthouse** — a single scene, for a fast demo.
- **Messy synopsis** — unformatted prose, to show the breakdown step working
  without screenplay structure.
- **Blank** — paste your own.

---

## Stack

| Layer | Technology |
|---|---|
| Orchestration | Google Gemini 2.5 Flash via `google-genai` |
| Live grounding | Parallel Search API (v1, turbo mode) |
| UI | Streamlit |
| Language | Python 3.10+ |

---

## Roadmap

- Multi-agent orchestration on Google ADK / Gemini Enterprise Agent Platform
  (the same Gemini calls, restructured as discrete agents — the Parallel path
  does not change)
- Scheduler agent producing structured shoot-day ordering
- PDF call sheet export
- Storyboard / previz generation
- Cloud Run deployment

---

## License

MIT — see [LICENSE](LICENSE).
