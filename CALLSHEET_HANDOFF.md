# CallSheet — Project Handoff
### Agentic Cinema: The Blockbuster Hackathon (Devpost) · Parallel track
Deadline: **September 9, 2026, 2:00 PM PDT** · Prizes per track: $7,500 / $4,500 / $3,000
Hackathon: https://agentic-cinema.devpost.com/ · Resources (GCP credits): https://agentic-cinema.devpost.com/resources

---

---
## STATUS — updated Aug 23, 2026 (evening)
- [x] Devpost registration submitted, track: **Parallel**
- [x] Parallel account created (org: CallSheet), API key in `.env` and **verified working** (HTTP 200; live Search test returned 10 results incl. Fort Rodd Hill / Fisgard Lighthouse — the exact location our test script needs. Good omen.)
- [x] Project folder ready: handoff, sample script, `.env` (key never committed/printed)
- [x] Cursor/Claude Code has read this handoff
- [ ] **Google Cloud $100 credits — form submitted, WAITING for approval (1–5 business days).** Blocks Vertex AI/Agent Builder work; nothing else is blocked.
- [ ] GitHub repo not created yet (do on build day 1, .gitignore + .cursorignore BEFORE first commit)

### While waiting for GCP credits (can start any time)
Frontend shell, data contracts, and the Research Agent can be built **now** — the Research Agent needs only the Parallel key, which works. Only Gemini/Agent Builder calls wait for credits. If credits are slow, prototype agents on the free-tier Gemini API key and swap endpoints later (architecture unchanged).
---

## One-liner
**CallSheet turns a script into a shoot.** A multi-agent system on Gemini reads a screenplay (or even a rough synopsis) and autonomously produces the full pre-production package: scene breakdown, researched real-world locations, storyboard, shooting schedule with call sheets, and an AI-previsualized opening scene — so an indie filmmaker walks onto day one prepared like a studio production.

## Why this wins
- Squarely inside the brief's own examples: script processing, storyboarding, production data management. It is a **tool for filmmakers**, not an AI-generated film.
- Real multi-step autonomy: one input triggers a chain of agents that plan, research the live web, generate, and assemble — not a chat UI.
- The Parallel integration is **load-bearing**, not decorative: the Research Agent cannot do its job without it.
- Judges score "genuine problem-space understanding" — the ReelLocal repo (github.com/SteveEleven/content-rescue-studio) is the proof-of-lineage: same builder, same script→production-pack philosophy, one level up.

## Hackathon requirements → how we meet them
| Requirement | Our answer |
|---|---|
| Functional agent on Gemini / Google Cloud Agent Builder | Multi-agent pipeline built with Google's Agent Development Kit (ADK) / Agent Builder, Gemini as the model, deployed on Cloud Run |
| Multi-step autonomous tasks | One "Break down my script" action fires 5 agents in sequence/parallel with no human in the loop until the pack is ready |
| Media & entertainment workflow | Pre-production: breakdown, location scouting, storyboarding, scheduling, previz |
| Partner integration that RUNS in code | Parallel's Search/Task API (or MCP server) called by the Research Agent at runtime for every location + logistics query |
| Hosted project URL | Cloud Run URL (frontend + API together) |
| 3-min demo video, public, English | Script drafted below; produce with the same screen-capture + HeyGen avatar pipeline used for ReelLocal |
| Public repo + OSS license | New GitHub repo `callsheet`, MIT license, README with run instructions clearly showing Google Cloud + Parallel usage |
| Devpost form + track selection | Register, select **Parallel** track |

## Eligibility note
BC, Canada is eligible (Quebec is excluded). Solo entry is fine.

---

## Architecture

```
                       ┌────────────────────────────────────────────┐
 Script / synopsis ──▶ │ ORCHESTRATOR (ADK root agent, Gemini)      │
                       └──┬─────────┬───────────┬─────────┬─────────┘
                          ▼         ▼           ▼         ▼
                   Breakdown   Research     Storyboard  Scheduler
                   Agent       Agent        Agent       Agent
                   (Gemini)    (Gemini +    (Gemini     (Gemini)
                               PARALLEL     image gen /
                               API/MCP)     Imagen)
                          │         │           │         │
                          └─────────┴─────┬─────┴─────────┘
                                          ▼
                                   Assembler Agent
                                   → Production Pack (JSON)
                                   → PDF call sheets
                                   → (stretch) HeyGen previz clip
```

- **Breakdown Agent** — parses screenplay into scenes: slugline, INT/EXT, day/night, characters, props, wardrobe, vehicles, estimated page-eighths, mood keywords.
- **Research Agent** — for each unique location requirement, calls **Parallel** to find 2–3 real candidate locations near the user's city: name, address, why it fits, permit/contact info if findable, typical fee range, with source URLs. Also researches logistics (sunset time for the shoot dates, gear rental houses nearby).
- **Storyboard Agent** — generates 1 frame per key scene beat (Imagen on Vertex AI; fallback: styled text-card frames so the demo never breaks).
- **Scheduler Agent** — groups scenes by location/cast into shoot days, applies day/night constraints, outputs a shooting schedule and per-day call sheets (crew call, scene list, cast, location, weather note from Research Agent).
- **Assembler** — merges everything into the Production Pack contract below, renders call sheets to PDF.
- **Previz (stretch, differentiator)** — pipe scene 1's action lines + a narration script into HeyGen to render a 20–30s previz/pitch clip. Demo gold; build only after core works.

### Frontend
Reuse the ReelLocal formula (it worked): Vite + React, one intake screen (paste script / choose sample), a progress screen with live agent-by-agent status ("Breaking down 14 scenes… Researching lighthouse locations…"), and a results screen with tabs: **Breakdown · Locations · Storyboard · Schedule · Call sheets**. Copy/export buttons. Embedded demo pack as fallback so the demo can never break. Same Higgsfield-style dark design system — it demos beautifully.

### Google Cloud pieces (credits: $100)
- Vertex AI: Gemini 2.x for all agents, Imagen for storyboard frames
- Agent Builder / ADK for orchestration (required by rules — make it visible in code and README)
- Cloud Run: host frontend + API (public URL for judging)
- Keep everything in one small service; $100 is plenty at this scale.

### Parallel integration (mandatory, runtime)
- Sign up at parallel.ai for API key; check their MCP server docs.
- The Research Agent calls Parallel for every location/logistics query and stores `source_urls` in the pack — the UI shows "Researched via Parallel" with citations. This makes the integration visibly load-bearing in the demo video.

---

## Data contracts (define first, exactly like ReelLocal — this is what made the weekend build fast)

```jsonc
// POST /api/breakdown  → ProductionPack
{
  "title": "string",
  "logline": "string",
  "scenes": [{
    "number": 1, "slugline": "EXT. LIGHTHOUSE - DUSK", "int_ext": "EXT",
    "day_night": "DUSK", "location_key": "lighthouse", "page_eighths": 6,
    "characters": ["MARA", "DEL"], "props": ["lantern", "rope"],
    "summary": "string", "mood": ["windswept", "tense"]
  }],
  "locations": [{
    "key": "lighthouse", "needed_for_scenes": [1,4],
    "candidates": [{
      "name": "Fisgard Lighthouse", "address": "string", "distance_km": 12,
      "why_it_fits": "string", "permit_contact": "string|null",
      "est_fee": "string|null", "source_urls": ["https://..."]   // ← Parallel results
    }]
  }],
  "storyboard": [{ "scene": 1, "beat": "string", "image_url": "string|null", "caption": "string" }],
  "schedule": [{
    "day": 1, "date_hint": "string", "location_key": "lighthouse",
    "scenes": [1,4], "cast": ["MARA","DEL"], "crew_call": "16:30",
    "wrap_est": "21:30", "notes": "golden hour 19:42, sunset 20:10 (researched)"
  }],
  "call_sheets": [{ "day": 1, "pdf_url": "string|null", "text": "string" }],
  "production_notes": "string"
}
```

Rules learned from ReelLocal that apply verbatim: force JSON out of every agent, validate with a `normalizePack()`-style function, embed a complete demo pack as fallback, generous timeouts + hedged retry, never show a broken state.

---

## Test fixture
`sample_script.md` in this folder — an original 3-page short, **"The Last Ferry"** (two characters, four locations around Victoria BC: ferry terminal, lighthouse, diner, apartment). Small enough to demo fast, rich enough to exercise every agent. Also prepare a "messy input" fixture (a one-paragraph synopsis) to show it works without a formatted screenplay.

---

## Build timeline (17 days, deliberately front-loaded)

**Today (before anything else) — Steve, 15 minutes:**
1. Register on Devpost, select the **Parallel** track.
2. Request the **$100 GCP credits** on the resources page (1–5 business days, while supplies last — this is the only hard deadline today).
3. Create a Parallel account / API key.
4. (Optional) Reserve the GitHub repo name `callsheet`.

**Aug 24–27 — Skeleton that already demos:** repo scaffold (MIT license from day one), frontend shell with sample script + fallback pack, Breakdown Agent working end-to-end on Gemini via ADK. Definition of done: paste script → see scene breakdown in UI.
**Aug 28–31 — The agentic core:** Research Agent with live Parallel calls + citations in UI; Scheduler Agent; orchestrator chaining all agents autonomously with progress events streamed to the UI.
**Sep 1–3 — Visual layer:** Storyboard Agent (Imagen), call-sheet PDFs, deploy to Cloud Run (hosted URL live and stable).
**Sep 4–5 — Stretch + polish:** HeyGen previz clip, design polish, README with run instructions, second test fixture.
**Sep 6–7 — Ship:** record 3-min demo video (script below), Devpost submission text (draft below), submit. **Target: submitted by Sep 7**, two days of buffer before the Sep 9 deadline.

Guardrail from the playbook that won the weekend: one polished workflow beats six half-finished features. Breakdown → Research(Parallel) → Schedule is the must-ship spine; storyboard and previz are polish.

---

## 3-minute demo video — draft script
0:00–0:20 · Hook: "Indie filmmakers spend weeks on pre-production before shooting a single frame. CallSheet does it while you get coffee." Show a script being pasted.
0:20–0:50 · One click. The agent pipeline runs on screen: breakdown → research → storyboard → schedule, each agent reporting in.
0:50–1:30 · The Locations tab: "The script calls for a lighthouse at dusk. CallSheet's research agent used **Parallel** to find three real lighthouses near Victoria, with permit contacts and sources." Click a citation.
1:30–2:10 · Schedule + call sheets: scenes grouped by location and cast, crew calls set to researched golden hour. Open a PDF call sheet.
2:10–2:40 · Previz: "And before you commit a dollar, watch your opening scene." Play the HeyGen previz clip (or storyboard pan if previz not built).
2:40–3:00 · Stack slide: Gemini + Agent Builder on Google Cloud, Parallel for live research, deployed on Cloud Run. "From script to shoot. CallSheet." URL on screen.
Production notes: reuse the ReelLocal video pipeline (Claude drives the app for screen captures, HeyGen avatar for narration, ffmpeg composite). Must be public on YouTube, English.

## Devpost submission text — draft
**Inspiration:** Last month I built a tool that turns a local business's website into a week of video content in two minutes. Filmmakers have the same problem one level up: the gap between a finished script and a plan you can actually shoot is weeks of unglamorous work — breakdowns, location scouting, scheduling. Agents can close that gap.
**What it does:** CallSheet reads a screenplay and autonomously produces the complete pre-production package: scene breakdown, real researched locations with permits and sources (via Parallel), a storyboard, a shooting schedule, printable call sheets, and an AI previz of the opening scene.
**How we built it:** A multi-agent system on Google Cloud — Gemini via Agent Builder/ADK orchestrating five specialized agents, Imagen for storyboard frames, Cloud Run for hosting. Parallel's research API powers every location and logistics query at runtime; every claim in the pack carries its source URL.
**Challenges / Accomplishments / What's next:** fill in during build week (honest notes beat polished fluff).

## Risks & fallbacks
- **GCP credits delayed** → build agents against the plain Gemini API first (free tier), swap to Agent Builder endpoints when credits land; architecture identical.
- **Imagen quota/cost** → styled text-card storyboard frames as automatic fallback.
- **Parallel rate limits** → cache research results per location_key; demo pack embeds pre-fetched results.
- **Agent Builder learning curve** → ADK quickstart first day; if truly blocked, ADK-python with Gemini still satisfies "Gemini + Google Cloud" (verify wording on rules page before relying on this).
- **Scope creep** → the spine is Breakdown → Research → Schedule. Everything else is optional.

## Assets to reuse from ReelLocal
Design system (styles.css tokens), the fallback/normalize pattern in `api.ts`, the progress-screen pattern, the copy/share utilities, the secret hygiene setup (.env + .gitignore + .cursorignore + gitleaks before every push), and the demo-video production pipeline.

## Naming
Working name **CallSheet** (check Devpost for collisions when registering; alternates: ShowRunner, FirstAD, PreProd Pilot, SceneOne).
