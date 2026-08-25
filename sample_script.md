# THE LAST FERRY
*An original short screenplay — test fixture for CallSheet. Written for the Agentic Cinema hackathon; free to use in this project.*

---

FADE IN:

**1. EXT. BRENTWOOD BAY FERRY TERMINAL, CENTRAL SAANICH BC — LATE AFTERNOON**

Rain-slick tarmac. A near-empty holding lane. MARA (30s, sea-worn coat, a cardboard box under one arm) stands at the ticket window as the Mill Bay crossing loads. The AGENT behind the glass shakes his head.

> **AGENT**
> Last one's at six. After that, nothing till Monday.

> **MARA**
> Then I need the six.

She counts out crumpled bills. Short. The Agent looks at her, looks at the box, slides a ticket under the glass anyway.

> **AGENT**
> You didn't get that from me.

**2. INT. VILLAGE DINER, BRENTWOOD BAY — CONTINUOUS**

Steam on the windows. DEL (60s, flannel, hands like rope) sits in the back booth, two coffees already poured. Mara slides in opposite. Sets the box between them.

> **DEL**
> You actually came.

> **MARA**
> You actually called.

Del opens the box an inch. Whatever's inside makes him close it again, slower.

> **DEL**
> Your mother wanted Fisgard. Scattered off the gallery rail, last light, like her father before her.

> **MARA**
> Gate's locked at dusk.

> **DEL**
> Then we should drive fast.

**3. EXT. FISGARD LIGHTHOUSE, FORT RODD HILL NATIONAL HISTORIC SITE, COLWOOD BC — DUSK**

Wind off Esquimalt Harbour. The red-brick tower catches the last orange light. Mara and Del climb the gallery stairs, the box passed between them like something living. At the rail, the strait goes gold.

Del takes off his cap. Mara opens the box.

> **MARA**
> (quiet)
> Okay, Mom. Best seat in the house.

Ash on the wind, out over the water. Neither of them speaks. The lighthouse lamp stutters on above them — one beat of light across their faces.

**4. INT. MARA'S APARTMENT, VICTORIA BC — NIGHT**

Bare walls, packed boxes. Mara enters alone, coat dripping. On the table: the empty cardboard box, and inside it now, a folded note in an old hand and a brass key.

She turns the key over. Stamped on it: **"FISGARD — KEEPER'S DOOR."**

Mara looks toward the window. Far off, faint, the light sweeps the dark.

She doesn't unpack. She picks up her coat.

SMASH CUT TO BLACK.

> **TITLE: THE LAST FERRY**

FADE OUT.

---

## Why this fixture is good for testing
- 4 scenes, 4 **real, named** locations on southern Vancouver Island — Brentwood Bay ferry terminal (BC Ferries, Mill Bay route), a Brentwood Bay diner, Fisgard Lighthouse at Fort Rodd Hill National Historic Site in Colwood, and a Victoria apartment. Every one of them has a verifiable address, a real nearest hospital, and a real permitting authority, so the Research Agent has genuine ground truth to find.
- Fisgard sits on federal Parks Canada land inside an active naval harbour — a genuinely tricky permitting case, and exactly the kind of thing a director would get wrong at midnight.
- The dusk scene runs against posted site closing times, which is a real scheduling constraint the agent should surface.
- 3 characters with overlapping availability → exercises the Scheduler (Del appears in 2 and 3 only).
- Day/night spread (afternoon, continuous, dusk, night) → exercises day/night constraints and the golden-hour research call.
- Props (cardboard box, brass key, ferry ticket), wardrobe, weather (rain) → exercises breakdown extraction.
- The dusk lighthouse scene is the previz/storyboard money shot.

## Second fixture — messy input (paste as plain synopsis)
"A woman takes the last Brentwood Bay ferry home to scatter her mother's ashes at Fisgard Lighthouse with an old family friend, and finds out her mother left her the keeper's key. Two actors, want to shoot it in a weekend around Victoria BC on no budget."
