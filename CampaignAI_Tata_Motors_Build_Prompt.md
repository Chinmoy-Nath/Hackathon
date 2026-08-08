# MASTER BUILD PROMPT — CampaignAI for Tata Motors

> Copy this entire document as the system/task prompt to Claude Code (or your coding agent of choice). It is written to be self-sufficient — an agent with no other context should be able to scaffold the full working prototype from this alone.

---

## 0. ROLE

You are a senior full-stack engineer and AI systems architect. Build a working prototype of **CampaignAI** — a multi-agent AI marketing campaign platform — scoped specifically to **Tata Motors' car portfolio**. This is a 2-day hackathon deliverable: prioritize a working, demoable end-to-end flow over completeness. Do not build anything not listed in this spec. Do not silently add scope (no real OAuth, no real email/social sends, no ML training pipelines).

---

## 1. DOMAIN SCOPE (hard constraint — do not deviate)

All customer, segment, and content data is about **Tata Motors car buyers/prospects**, not generic retail.

**Powertrain axis (3):** `EV`, `Petrol`, `Hybrid`
**Tier axis (3):** `Mid-range`, `Premium`, `Luxury`

This gives **9 fixed segment archetypes**. Map real Tata models into these cells (used consistently across synthetic data, prompts, and UI copy):

| | Mid-range | Premium | Luxury |
|---|---|---|---|
| **EV** | Tiago EV | Nexon EV | Curvv EV / Nexon EV Max |
| **Petrol** | Tiago / Tigor | Punch / Altroz | Harrier / Safari (petrol trims) |
| **Hybrid** | — (use Punch iCNG-equivalent stand-in if needed) | Nexon Hybrid concept | Harrier / Safari Hybrid concept |

> Note: Tata's real hybrid/luxury lineup is limited — for the prototype it's acceptable to label these as "concept trims" since this is illustrative, not a real product claim. Keep any such stand-ins clearly internal (never surface fabricated real-world claims to an end user outside the demo).

Each segment must carry **persona-relevant messaging angles**, e.g.:
- EV segments → range confidence, charging infra, running-cost savings, sustainability
- Petrol mid-range → value, reliability, low maintenance, first-car buyer
- Petrol/Hybrid premium → performance, features, family safety (Harrier/Safari = ADAS, 5-star GNCAP)
- Luxury tier → exclusivity, craftsmanship, status, personalized ownership experience

---

## 2. TECH STACK

- **Frontend:** React (Vite), Tailwind CSS, Recharts (charts), React Router. Match the visual language of the provided screenshots: light neutral background, rounded cards, soft shadows, sidebar nav (Dashboard, Campaign builder, Segments, AI content, Channels, Analytics, Settings), minimal color accents (blue/green/amber status pills).
- **Backend:** FastAPI (Python 3.11+), Pydantic v2 for schemas, SQLite (or Postgres if time allows) via SQLAlchemy for persistence.
- **Agent orchestration:** LangGraph for the multi-agent state machine; LangChain only where it reduces boilerplate (prompt templates, output parsers) — don't over-engineer with LangChain abstractions where a direct Anthropic API call is simpler.
- **LLM:** Claude (Anthropic API) via `anthropic` Python SDK, model `claude-sonnet-4-6`. Use **structured output** (JSON mode via explicit "respond only in JSON" system prompts + Pydantic validation) for all agent outputs — never parse freeform text in the app layer.
- **Synthetic data:** `Faker` (Python) for customer generation; a seeded script so demo data is reproducible.
- **Task/mock scheduling:** in-memory/DB job records with `status: pending/sent/scheduled` — no real cron, no real delivery. A background asyncio task can flip status after a delay to simulate "sending" live during the demo.
- **No auth needed** for the hackathon (skip login flows) unless time remains.

---

## 3. SYSTEM ARCHITECTURE — MULTI-AGENT PIPELINE (LangGraph)

Build a LangGraph state graph with this exact flow:

```
[Segmentation Agent] → [Content Generation Agent] → [Compliance Agent] → [Orchestration/Dispatch Agent] → [Performance Simulator]
                                                            │
                                                    (fail → back to Content Gen with reason)
```

### Shared state object (`CampaignState`, Pydantic model)
```python
class CampaignState(BaseModel):
    campaign_id: str
    brief: str                      # e.g. "Win back at-risk EV-premium customers with a charging-offer nudge"
    target_segment_ids: list[str]   # e.g. ["ev_premium", "petrol_midrange"]
    goal: str                       # e.g. "re-engagement", "new-launch", "loyalty"
    audience: list[CustomerProfile] # resolved customers after segmentation
    generated_content: dict[str, ChannelContent]  # keyed by channel: email/social/push/sms
    compliance_result: ComplianceResult | None
    dispatch_result: DispatchResult | None
    status: Literal["draft","generating","pending_review","scheduled","live","completed"]
```

### 3.1 Segmentation Agent (rule-based — NOT an LLM call)
Pure Python rule engine, not an LLM agent (keep it deterministic and fast for the demo). Input: full synthetic customer table. Output: customers bucketed into the 9 fixed segments **plus** 3 cross-cutting behavioral tags layered on top (to match your "High-value loyalists / At-risk churners / New social followers" screen pattern):

```python
def compute_behavioral_tag(customer) -> str:
    if customer.days_since_last_purchase > 90 and customer.historical_purchase_freq >= 2:
        return "at_risk_churner"
    if customer.avg_order_value > 3_000_00 and customer.purchase_count_per_year >= 2:  # INR paise or just use INR int
        return "high_value_loyalist"
    if customer.days_since_signup < 30 and customer.social_engagement_score > 0.6:
        return "new_social_follower"
    return "standard"
```
Final segment = `f"{powertrain}_{tier}"` (e.g. `ev_luxury`) **crossed with** behavioral tag for targeting logic. Store both on the customer record. The Segments screen shows the **behavioral tag view** (3 cards, matching your screenshot); the Campaign Builder's Audience step lets users filter by **powertrain × tier × behavioral tag**.

### 3.2 Content Generation Agent (LLM — this is the centerpiece agent)
LangGraph node that calls Claude with a **per-channel structured prompt**. Generate all 4 channels in parallel (async gather): Email, Social, Push, SMS (SMS can be a stretch/disabled toggle, matching your Channels screen showing "SMS Disabled").

**System prompt for this agent** (use verbatim, adapt segment/brief at runtime):

```
You are the Content Generation Agent for CampaignAI, an AI marketing system for Tata Motors.
You write channel-native marketing copy for Tata Motors car campaigns. You are never generic —
every piece of copy must reflect the specific powertrain (EV/Petrol/Hybrid), tier (Mid-range/
Premium/Luxury), and behavioral context (e.g. at-risk churner, loyalist, new follower) of the
target segment.

BRAND VOICE: Confident, warm, India-first, never overhyped. Avoid superlatives not backed by
real Tata Motors positioning (safety ratings, EV range, ADAS features). No fabricated stats.

HARD CONSTRAINTS:
- Email: subject line ≤ 60 chars, body ≤ 120 words, must include one clear CTA, must include a
  {unsubscribe_footer} placeholder token verbatim (do not write real unsubscribe text yourself).
- Social: caption ≤ 280 chars, include 2-3 relevant hashtags, no emoji spam (max 2 emoji).
- Push: ≤ 90 characters total including emoji, urgent/scannable tone, must include a clear action.
- SMS (if enabled): ≤ 160 characters, must include {opt_out_footer} placeholder token verbatim.
- Never claim specific numeric offers/discounts unless provided explicitly in the campaign brief
  input — if no discount is specified, use benefit-led messaging instead (e.g. "book a test drive"
  not "20% off" if no discount was given).
- Personalization tokens allowed: {first_name}, {model_name}, {nearest_dealer}, {last_purchase_date}.

OUTPUT FORMAT: Respond ONLY with valid JSON matching this schema, no preamble, no markdown fences:
{
  "email": {"subject": str, "body": str},
  "social": {"caption": str, "hashtags": [str]},
  "push": {"text": str},
  "sms": {"text": str} | null
}

INPUT CONTEXT (provided at runtime):
- campaign_brief: free-text goal from the marketer
- segment: {powertrain, tier, behavioral_tag, segment_size, key_traits}
- model_context: relevant Tata model name(s) and 2-3 real positioning facts to draw from
```

Wrap this in a LangChain `PromptTemplate` + Anthropic structured call; validate the returned JSON against a Pydantic `ChannelContent` model; on validation failure, retry once with an error-correction follow-up message before failing the node.

Expose a `regenerate` variant (same node, re-invoked) and an `edit manually` path (frontend-only override, written straight to state, bypassing the agent) — this matches your **Campaign Builder screen's "Accept & continue / Regenerate / Edit manually"** buttons.

### 3.3 Compliance Agent (rule-based, not LLM — deterministic and demo-safe)
Runs before any content can move to `scheduled`. Checks, per customer in the resolved audience:
1. `consent_email` / `consent_sms` flags on the customer record (GDPR/consent proxy) — filters out non-consented customers per channel rather than blocking the whole campaign.
2. Injects the real unsubscribe/opt-out text into `{unsubscribe_footer}` / `{opt_out_footer}` tokens (CAN-SPAM requirement) at dispatch time, not generation time.
3. Flags (does not silently drop) any content that still contains an unresolved `{token}` after personalization — surfaces as a warning in the Review step.

Output: `ComplianceResult{passed: bool, excluded_count: int, warnings: list[str]}`. Surface this plainly in the Review step of Campaign Builder — this is a genuine differentiator to call out to judges ("every send is gated by a compliance agent, not a UI checkbox").

### 3.4 Orchestration / Dispatch Agent (mocked channel adapters)
Not an LLM call — a thin adapter layer with one interface, one mock implementation per channel:
```python
class ChannelAdapter(Protocol):
    async def send(self, content: ChannelContent, audience: list[CustomerProfile]) -> DispatchResult: ...

class MockEmailAdapter: ...   # returns fake message IDs, simulated delivery count
class MockSocialAdapter: ...  # returns fake post ID + "reached" count
class MockPushAdapter: ...    # returns fake scheduled timestamp
```
Design this layer so a real `SendGridEmailAdapter` / `MetaGraphSocialAdapter` / `FCMPushAdapter` could be dropped in later without touching agent code — mention this explicitly in your demo as the production extension point. Persist dispatch records so the Channels screen ("4,210 sent", "3,041 reached", "Scheduled 2pm") has something real to read from.

### 3.5 Performance Simulator (feeds Analytics + Dashboard)
Not a "real" agent — a synthetic engagement generator that runs after dispatch:
- Per segment, apply a believable base engagement rate **with segment-flavored variance** (e.g. EV segments respond better to sustainability-angled content; luxury tier has lower open rate but higher conversion value; at-risk churners have a low but non-zero recovery rate).
- Emit events over a simulated time window (can be pre-computed, not truly real-time, but presented as if streaming — e.g. poll every few seconds on the frontend to animate the dashboard numbers ticking up).
- Also compute and store a fixed **"before AI" baseline** (hardcoded average, e.g. 6.1%) to drive the "Before AI vs With AI campaigns" comparison card on the Analytics screen.

---

## 4. DATA MODEL

```python
class CustomerProfile(BaseModel):
    id: str
    first_name: str
    powertrain: Literal["EV","Petrol","Hybrid"]
    tier: Literal["Mid-range","Premium","Luxury"]
    model_interest: str                 # e.g. "Nexon EV Max"
    behavioral_tag: Literal["high_value_loyalist","at_risk_churner","new_social_follower","standard"]
    avg_order_value: int                # INR, synthetic
    purchases_last_year: int
    days_since_last_purchase: int
    social_engagement_score: float      # 0-1
    consent_email: bool
    consent_sms: bool
    app_user: bool
    nearest_dealer: str

class ChannelContent(BaseModel):
    email: EmailContent | None
    social: SocialContent | None
    push: PushContent | None
    sms: SMSContent | None
    status_by_channel: dict[str, Literal["generated","pending","disabled"]]

class Campaign(BaseModel):
    id: str
    name: str
    brief: str
    goal: str
    target_segments: list[str]
    content: ChannelContent
    compliance: ComplianceResult
    status: Literal["draft","scheduled","live","completed"]
    channel_stats: dict[str, ChannelStats]  # sent/reached/scheduled counts

class MetricsSnapshot(BaseModel):
    campaign_id: str
    engagement_rate: float
    conversions: int
    email_open_rate: float
    ctr: float
    conversion_rate: float
    avg_order_value: int
    revenue_attributed: int
    channel_conversions: dict[str, int]  # for the bar chart
```

**Synthetic data generation script** (`seed_data.py`): generate ~300-500 customers distributed across the 9 segments (skew realistically — more mid-range than luxury), with Faker names, plausible order values in INR matching real Tata price bands (Tiago ~₹6-9L, Nexon ~₹8-16L, Harrier/Safari ~₹15-27L), and randomized but bounded consent/engagement fields. Seed the RNG for reproducibility (`Faker.seed(42)`).

---

## 5. API CONTRACT (FastAPI)

```
GET  /api/segments                     → 9 segment summaries + 3 behavioral-tag cards (counts, sample traits, engagement stats)
GET  /api/customers?segment=&tag=      → filtered customer list

POST /api/campaigns                    → create draft campaign {name, brief, goal, target_segments}
POST /api/campaigns/{id}/generate      → runs Content Generation Agent → returns ChannelContent
POST /api/campaigns/{id}/regenerate    → re-runs generation for one channel or all
PATCH /api/campaigns/{id}/content      → manual edit override
POST /api/campaigns/{id}/compliance    → runs Compliance Agent → returns ComplianceResult
POST /api/campaigns/{id}/schedule      → sets status=scheduled, stores send time
POST /api/campaigns/{id}/dispatch      → runs Orchestration Agent (mocked send) → DispatchResult
GET  /api/campaigns                    → list (for Dashboard "Active campaigns")
GET  /api/campaigns/{id}                → full detail

GET  /api/channels/overview            → per-channel sent/reached/scheduled totals (Channels screen)
GET  /api/channels/routing-rules       → segment → channel default mapping (Channels screen bottom card)

GET  /api/analytics/{campaign_id}      → MetricsSnapshot (Analytics screen)
GET  /api/analytics/{campaign_id}/stream  → SSE or polling endpoint that ticks metrics upward post-dispatch, simulating real-time

GET  /api/dashboard/summary            → engagement rate, conversions, campaigns live, avg time-to-launch (Dashboard screen top cards)
```

Wrap the LangGraph pipeline invocation behind `/generate`, `/compliance`, `/dispatch` as **separate, independently callable steps** (not one mega-endpoint) — this is what lets the Campaign Builder wizard show real step-by-step progress and lets you demo each agent individually if asked.

---

## 6. FRONTEND — SCREEN SPECS (match provided screenshots exactly)

Sidebar (persistent, all screens): `CampaignAI / Retail Marketing Suite` header → nav items: Dashboard, Campaign builder, Segments, AI content, Channels, Analytics → Settings pinned bottom.

### 6.1 Dashboard
Top row, 4 stat cards: **Engagement rate** (18.4%, +4.2% vs last month), **Conversions** (2,841, +12%), **Campaigns live** (3, "2 scheduled"), **Avg. time-to-launch** (41 min, "↓68% with AI"). Below: **Active campaigns** list (name, status pill Live/Scheduled/Draft, progress bar) + **Channel performance today** (Email/Social/Push/SMS with progress bars). Pull all numbers from `/api/dashboard/summary`.

### 6.2 Segments
3 cards: **High-value loyalists**, **At-risk churners**, **New social followers** — each with customer count, trait pills (derived from the rule engine's thresholds, e.g. "Avg. order > ₹3,000" → adapt to Tata price scale, e.g. "6+ purchases/yr" → adapt to "Repeat buyer / referral", since Tata cars aren't repeat-purchase-per-year — **reframe traits to make sense for automotive**: e.g. "Owns 2+ Tata vehicles", "Service loyalty 3+ yrs", "Test-drive booked, no purchase 90+ days", "First purchase < 90 days, high app engagement"), and two progress-bar metrics each (e.g. email open rate, service-booking rate, referral rate — adapt "repeat purchase" metric to something automotive-sane, like "Service renewal rate" or "Referral rate").

### 6.3 Campaign Builder (6-step wizard)
Steps: **Audience → Goal → AI content → Channels → Schedule → Review**. This is your main demo screen.
- Audience step: pick powertrain × tier × behavioral tag (checkboxes/pills), shows resolved customer count live.
- Goal step: campaign brief textbox + goal type dropdown (re-engagement, new-launch, loyalty, test-drive push).
- AI content step: shows generated Email subject/body preview, Social post variant, Push notification — exactly like your screenshot — with **Accept & continue / Regenerate / Edit manually** buttons.
- Channels step: toggle which channels are active for this send.
- Schedule step: date/time picker (mocked — just stores the value).
- Review step: compliance check summary (pass/excluded count/warnings) + final "Launch campaign" button that triggers `/dispatch`.

### 6.4 AI Content Studio
Standalone content generation view (not tied to a specific campaign wizard flow) — campaign brief textbox at top + **Generate all** button, 4 channel cards below (Email/Social/Push/SMS) each showing generated preview + status pill (`Generated`/`Pending`). This is useful as a **quick single-screen demo of the Content Generation Agent** in isolation, separate from the full wizard — keep both, they serve different demo purposes (one shows the agent, one shows the full orchestration).

### 6.5 Channels
Top: delivery overview cards per channel with live counts (Email sent, Social reached, Push scheduled time, SMS disabled state). Bottom: **Segment → channel routing rules** table (behavioral tag → default channel pills) — this is your rule-based orchestration logic made visible, e.g. High-value loyalists → Email + Push; At-risk churners → Email + SMS; New social followers → Social + Push. Adapt these defaults sensibly for auto (e.g. luxury tier customers skew Email + Push over SMS).

### 6.6 Analytics
Top: **Before AI (avg. engagement) → With AI campaigns** comparison card (6.1% → 18.4% ↑). Below: **Conversions by channel** bar chart (Email/Social/Push/SMS) + **Key metrics** list (Email open rate, CTR, conversion rate, avg order value in ₹, revenue attributed in ₹L/₹Cr — Tata car ticket sizes mean revenue-attributed should read in lakhs/crores, not the retail-apparel-scale numbers in the reference screenshot).

---

## 7. DEMO NARRATIVE (what this build must support live)

1. Show **Segments** — 9 rule-based Tata segments + 3 behavioral overlays, real synthetic numbers.
2. Go to **Campaign Builder** — pick "EV Luxury, at-risk churners" → write brief → watch **AI content step generate live** (this is the money shot — the LLM call happening on stage).
3. Switch audience to "Petrol Mid-range, new social followers" → regenerate → show visibly different tone/CTA/channel mix.
4. Show **Review step** — compliance agent excluding non-consented customers, injecting unsubscribe footer.
5. Launch → **Channels** screen shows mock dispatch numbers appear.
6. **Analytics/Dashboard** — before/after AI comparison, time-to-launch metric (~41 min or faster, contrasted with "days" manually).

---

## 8. WHAT NOT TO BUILD (explicit exclusions for time management)

- No real email/social/SMS API integrations — mock adapters only, clearly labeled in code comments as swap-in points.
- No user auth/login.
- No real ML clustering — segmentation is deterministic rules.
- No training/fine-tuning — all Claude calls are prompted, not fine-tuned.
- No payment/checkout flows.
- Keep SMS as a "disabled/coming soon" channel per the screenshot rather than building it out, unless time remains after core flow works end-to-end.

---

## 9. BUILD ORDER (so the agent building this doesn't thrash)

1. Data models + synthetic data seed script → verify data looks right in isolation.
2. FastAPI backend: segments endpoint + customers endpoint (no LLM yet) → test with curl/Postman.
3. LangGraph pipeline: Segmentation (already done in step 1-2) → Content Generation Agent (single channel first, e.g. email only) → verify one real Claude call end-to-end → then expand to all 4 channels in parallel.
4. Compliance Agent + Orchestration mock adapters → Dispatch endpoint.
5. Performance Simulator + Analytics/Dashboard endpoints.
6. React frontend: Dashboard → Segments → Campaign Builder wizard (this is the largest UI effort — build last of the screens but first in priority) → AI Content Studio → Channels → Analytics.
7. Wire frontend to backend, remove all mock/hardcoded frontend data, verify live end-to-end demo path.
8. Polish: loading states, error states, status pill colors, number formatting (₹ lakhs/crores).
