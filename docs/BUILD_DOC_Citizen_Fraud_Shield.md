# Build Doc: Citizen Fraud Shield
## AI-Powered Digital Arrest Scam Detection & Citizen Protection

**Hackathon:** ET AI Hackathon 2026
**Problem Statement:** #6 — AI for Digital Public Safety: Defeating Counterfeiting, Fraud & Digital Arrest Scams
**Team Size:** 2
**Version:** 2.0 (consolidated build doc)

---

## 1. Problem Statement

Digital arrest scams defrauded Indian citizens of over ₹1,776 crore in the first nine months of 2024. Fraudsters impersonating CBI/ED/Customs/Police trap victims in multi-day psychological hostage situations over video calls, using spoofed numbers, scripted intimidation, and fake government portals. Law enforcement lacks a way to detect these scams **at the point of contact** — before money moves, not after a complaint is filed weeks later.

**Core insight:** These scams follow highly repeatable script patterns, call structures, and psychological pressure tactics. That repeatability is exploitable by AI.

---

## 2. Product Vision

A two-part system that (1) detects an active digital arrest / fraud scam in near real-time from a call transcript, message, or screenshot, and (2) gives the citizen an instant, trustworthy verdict and next steps — through a simple chat interface, no installation required.

**One-line pitch:** *"Paste what you heard or saw. Know in 5 seconds if it's a scam — before you lose your money."*

---

## 3. Goals & Non-Goals

### Goals (MVP — buildable by 2 people in a hackathon window)
- Detect digital arrest / financial fraud scam patterns from **text** (call transcripts, WhatsApp/SMS messages, email)
- Provide a **risk score + verdict + explanation** (which red flags triggered it, which known pattern it matches)
- Provide a **guided next-step flow** (block, report to NCRB 1930/cybercrime.gov.in, don't transfer money, verify via official channel)
- Support **regional language input/output** for at least 2-3 Indian languages
- Ship a working demo: chat interface + backend classifier + a curated scam-pattern knowledge base

### Stretch Goals (only if MVP is fully done early)
- Audio input → Whisper transcription → same pipeline
- A small fraud pattern dashboard (mock "law enforcement view") using the corpus data
- Counterfeit note detection via image upload — only pursue if everything else is rock solid

### Non-Goals (explicitly out of scope)
- Real integration with telecom providers or MHA alert systems (mock/simulate in the demo)
- Real-time live call interception
- Court-admissible evidence packaging
- Multi-agency case management systems

---

## 4. Target Users

| Persona | Need |
|---|---|
| **Citizen (primary — build for this one)** | Just received a scary call/message claiming to be police/CBI/courier/bank — needs an instant verdict |
| **Bank/telecom ops team (secondary, pitch only)** | Could embed this as a widget to flag suspicious customer-reported calls |
| **Law enforcement (tertiary, pitch only)** | Aggregated dashboard of scam patterns reported, for prioritization |

---

## 5. Core Features (MVP Scope)

### 5.1 Scam Pattern Classifier ("Detection Engine")
- Input: pasted text (call transcript / message / email body)
- Output: `{ verdict: SCAM | SUSPICIOUS | LIKELY_SAFE, confidence: 0-100, red_flags: [...], matched_pattern: "...", explanation: "..." }`
- Hybrid detection — two layers working together, not just one LLM call:
  1. **Rule-based layer** (deterministic, fast, catches novel phrasing): impersonation of authority, urgency + isolation language, OTP/payment/verification-transfer requests, fake case numbers/portals, threats of arrest
  2. **RAG-grounded LLM layer**: retrieves the closest matching known patterns from the corpus, then generates a verdict + explanation grounded in those real examples

### 5.2 Citizen Fraud Shield Chat Interface
- Simple conversational UI, mobile-responsive
- Multi-turn: paste text, ask follow-ups ("what do I do now?")
- Verdict delivered in plain language with matched pattern cited, not just a score
- One-click actions: "Report to NCRB (cybercrime.gov.in / 1930)", "Block & Save Evidence checklist"

### 5.3 Regional Language Support
- Auto-detect input language; respond in same language
- MVP languages: Hindi, English + one more (Telugu/Tamil/Kannada based on preference)

### 5.4 Scam Pattern Corpus (RAG knowledge base) — see Section 8, this is the highest-risk component
- Curated dataset of known scam scripts, MHA/RBI/NCRB advisories, real case patterns
- Grounds LLM explanations so the tool cites a matched real pattern, not a generic guess

### 5.5 (Stretch) Fraud Pattern Dashboard
- Simple chart: scam types reported, red-flag frequency, mock geospatial hotspot using sample data
- Shows the "law enforcement" scalability angle without needing real integration

### 5.6 Emerging Campaign Detection (predictive layer — this is what makes the platform *predictive*, not just reactive)
- **Why this exists:** the problem statement explicitly asks for "predictive threat neutralisation," not just per-message detection. A citizen pasting one transcript and getting a verdict is still reactive at the individual level. This feature turns every citizen interaction, **across all users**, into a sensor for the aggregate system.
- **Critical design point — this is cross-user, not per-session.** One person's message means nothing on its own. The signal only exists in aggregate: if 6 *different* citizens submit similar scripts within a short window, that's a live campaign. The clustering query must look across the entire shared submission log, not scope to a session or user ID. Do not architect this as per-user history — it defeats the purpose.
- **How it works:** every classified transcript is logged (anonymized — no PII, no user-identifying data beyond a random non-reversible submission ID) along with its embedding (already computed for RAG), scam type, red flags, and a timestamp, into a **persistent, shared store** — see storage note below. A similarity check runs against all recent submissions in a time window, regardless of which user submitted them.
- **Storage:** a second ChromaDB collection (`campaign_submissions`), persisted to disk (not in-memory) — reuses the same embedding pipeline as RAG, and Chroma's similarity search does the clustering natively. On-disk persistence matters here specifically because the log has to survive across many separate requests from many different users/sessions over the course of the demo, not just live within one running process by luck.
- **Trigger logic:** if N similar transcripts (same fake agency name, same script structure, high embedding similarity) appear across submissions within a short window, the system flags an **active emerging campaign** — a scam operation scaling right now, before most of its victims have been hit.
- **Output:** a small "trending campaigns" panel — e.g. *"6 similar 'fake customs officer' scripts detected from different reporters in the last 2 hours"* — surfaced to the citizen-facing UI and framed in the pitch as the law-enforcement-facing view.
- **This is the direct answer to "how is this predictive"** — individually the system reacts to an incoming message; collectively, clustering signals across many citizens lets it surface a scaling campaign before hundreds more victims are hit. Frame this explicitly in the pitch narrative (Section 11).
- **Scope note:** this uses infrastructure you're already building (embeddings from RAG) — it's a second Chroma collection + a clustering query, not a new subsystem. Treat as MVP, not stretch, given how directly it answers the problem statement.
- **Demo simulation note:** since you'll be the only ones testing before judging, seed the collection yourself with several slightly-varied transcripts (different phrasing, same underlying scam) submitted as if from different users, to demonstrate the cross-user clustering behavior convincingly live.

---

## 6. System Architecture

```
┌─────────────────┐      ┌──────────────────────┐      ┌───────────────────┐
│   Web Chat UI    │─────▶│   FastAPI Backend      │─────▶│  LLM                │
│ (React+Tailwind  │◀─────│  (classification +     │◀─────│  gpt-5.4-mini       │
│  or Streamlit)   │      │   RAG orchestration)    │      │  (OpenAI API)       │
└─────────────────┘      └──────────┬────────────┘      └───────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
        ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────────┐
        │  Rule-based          │ │  RAG retrieval        │ │  Campaign log +          │
        │  detection            │ │  Embeddings + vector  │ │  clustering              │
        │  Regex + keyword      │ │  search               │ │  (predictive layer)      │
        │  flags                │ │                        │ │                          │
        └───────────────────┘ └─────────┬─────────┘ └───────────────────────┘
                                          ▼
                              ┌───────────────────────┐
                              │  Scam corpus            │
                              │  scam_corpus.json in    │
                              │  ChromaDB               │
                              └───────────────────────┘
```

The **campaign log + clustering** component reuses the same embeddings computed for RAG — every classified transcript, from any user, is logged anonymized with its embedding into a persistent, shared ChromaDB collection, and a similarity check against recent submissions **across all users** in the same time window flags an emerging campaign. This is the piece that makes the platform predictive at the aggregate level, not just reactive per-message. See Section 5.6.

### Component Table

| Layer | Tool | Notes |
|---|---|---|
| **LLM inference** | **OpenAI `gpt-5.4-mini`** — budgeted to ~1.25M tokens/day (~50% of your 2.5M mini-tier daily quota), roughly 650-800 requests/day at ~1.5-2K tokens each | Strong enough for classification + RAG-grounded explanation. Never default any code path to the 250K/day big-model quota (gpt-5, gpt-4o, etc.) — keep that as manual emergency reserve only |
| **Embeddings (RAG)** | `sentence-transformers` (`all-MiniLM-L6-v2`) — runs locally, no API | Free, fast, good enough for a 50-80 entry corpus |
| **Vector store** | **ChromaDB** (local, in-memory or on-disk) | Free, zero setup, pure Python |
| **Backend** | **FastAPI** + Python | Fast to build, great docs |
| **Frontend** | **React + Tailwind**, or **Streamlit/Gradio** for speed | Recommended: start with Streamlit/Gradio calling `classifier.py` directly — skip the separate API layer unless you have time left over |
| **Language detection/translation** | `langdetect` (free) + let the LLM handle translation directly via prompt (simplest, avoids a separate translation API) | Avoids paid translation dependency |
| **Speech-to-text (stretch)** | OpenAI Whisper (open-source, local) or `faster-whisper` | Free, no API key, fine for short clips |
| **Hosting (demo)** | Run locally on the presenting laptop — safest for a live demo. Vercel/Render free tiers as backup if you want a shareable link | No cost, no key required, avoids live-demo network risk |

> **Honesty note for judges:** this build uses `gpt-5.4-mini` via a personal OpenAI quota — not a free-tier or open-source model. Don't claim "100% free" if asked about cost. Lead the pitch with detection-before-money-moves and RAG-grounded, explainable verdicts instead.

---

## 7. Project Structure

```
citizen-fraud-shield/
├── backend/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── config.py                # env vars, model config, token budget settings
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── detection/
│   │   ├── rules.py              # deterministic red-flag regex/keyword engine
│   │   ├── classifier.py         # orchestrates rules + RAG + LLM verdict
│   │   └── prompts.py            # prompt templates for verdict + explanation
│   │
│   ├── rag/
│   │   ├── embed.py              # sentence-transformers embedding logic
│   │   ├── vectorstore.py        # ChromaDB init + query
│   │   └── ingest.py             # one-time script: load scam_corpus.json into Chroma
│   │
│   ├── intelligence/
│   │   ├── campaign_log.py       # writes anonymized submissions (any user) to a persistent, shared ChromaDB collection
│   │   └── clustering.py         # queries across ALL users' recent submissions — flags emerging campaigns
│   │
│   ├── llm/
│   │   └── openai_client.py      # gpt-5.4-mini wrapper + token-usage logging
│   │
│   ├── language/
│   │   └── translate.py          # langdetect + LLM-based translation for regional lang
│   │
│   ├── data/
│   │   └── scam_corpus.json      # curated scam pattern entries (see Section 8)
│   │
│   └── api/
│       └── routes.py             # POST /analyze, POST /followup, GET /health
│
├── frontend/                     # React+Tailwind (or collapse into a single app.py — see note)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── VerdictCard.jsx   # shows SCAM/SUSPICIOUS/SAFE + red flags + matched pattern
│   │   │   ├── ActionButtons.jsx # "Report to NCRB", "Block & Save Evidence"
│   │   │   └── LanguageToggle.jsx
│   │   └── api/client.js         # calls backend /analyze
│   ├── package.json
│   └── tailwind.config.js
│
├── dashboard/
│   ├── pattern_stats.py          # simple charts on scam_corpus.json (stretch)
│   └── trending_campaigns.py     # renders the emerging-campaign panel (MVP — see Section 5.6)
│
├── docs/
│   ├── BUILD_DOC_Citizen_Fraud_Shield.md   # this file
│   ├── architecture_diagram.png
│   └── demo_script.md
│
└── README.md
```

**Fastest-path alternative:** if backend/frontend integration eats time, collapse `frontend/` into a single `app.py` using **Streamlit or Gradio** that calls `detection/classifier.py` directly — no separate API layer needed. Recommended starting point for a 2-person team; only split into FastAPI+React if there's time left over.

---

## 8. Scam Corpus Strategy (highest-risk component — read this carefully)

**The risk:** a small, mostly hand-written `scam_corpus.json` is easy for a judge to dismiss as "you just made this up." This directly threatens your RAG-grounded explanation pitch if not handled deliberately.

**Mitigations to actually implement, not just mention:**

1. **Grow past 50 entries with real-source majority.** Pull from public sources: NCRB advisory pages, PIB press releases, RBI reports, news coverage of actual cases (search and paraphrase — never copy text verbatim). Target 60-80 entries where most are sourced, not synthetic.
2. **Write 3-4 phrasing variants per scam type**, not just one canonical script per type. Judges testing edge cases will paste something slightly different — variant coverage matters more than raw entry count.
3. **Rule-based layer must not depend on RAG matching.** Keyword/regex red flags should catch novel phrasing even with a weak RAG match — this makes "small corpus" a limitation on explanation richness, not detection accuracy.
4. **Disclose the limitation proactively in the pitch**, before a judge asks: *"Our corpus is a seed set for this demo — in production this would ingest NCRB's live complaint database continuously. The architecture doesn't change, only data volume does."* Naming it first reads as rigor, not weakness.
5. **Prepare one test case deliberately outside the corpus** and show it still gets flagged correctly via the rule layer + general LLM reasoning. This is the single best live defusal of the "you just made this up" objection.

### Corpus entry structure

```json
{
  "id": "scam_001",
  "type": "digital_arrest_cbi",
  "title": "CBI Digital Arrest — Fake Case Number",
  "script_summary": "Caller claims to be a CBI inspector investigating the victim for money laundering tied to a parcel/SIM card in their name. Victim is told to stay on video call continuously, not disconnect or tell family, and is shown a fake arrest warrant with a case number. Victim is asked to transfer funds to a 'RBI verification/safe account' to prove innocence, with promise of refund after clearance.",
  "red_flags": [
    "impersonation of central investigation agency",
    "insists victim stay on video call, isolates from family",
    "fake case number / arrest warrant document",
    "demands money transfer for 'verification'",
    "creates false urgency / fear of real arrest"
  ],
  "source": "MHA advisory, Oct 2024 / PIB press release",
  "is_synthetic": false
}
```

**Field notes:**
- `script_summary` → gets embedded and searched (the actual RAG lookup)
- `red_flags` → pulled directly into the LLM's explanation output
- `type` → groups entries for the stretch dashboard
- `source` / `is_synthetic` → protects you if a judge asks "is this data real?" — answer honestly

**Scam categories to cover:** digital arrest (CBI/ED/Customs/Police variants), courier/parcel scams, fake KYC update calls, loan app harassment, fake job offers, sextortion-adjacent threats.

---

## 9. Success Metrics (Aligned to Judging Criteria)

| Judging Criterion | Weight | How this build addresses it |
|---|---|---|
| **Innovation** | 25% | Point-of-contact detection (before money moves) vs. reactive complaint-based systems; RAG-grounded explanations, not a black-box score; **individual citizen queries feed a predictive campaign-clustering layer, directly answering the brief's "predictive threat neutralisation" ask** |
| **Business Impact** | 25% | Directly targets the ₹1,776 crore/9-month fraud category; low-infra deployability; emerging-campaign alerts give law enforcement a lead-time advantage, not just after-the-fact case data |
| **Technical Excellence** | 20% | Hybrid detection (deterministic rules + LLM reasoning + RAG grounding) — more robust and explainable than a single black-box classifier |
| **Scalability** | 15% | Multi-language by design, stateless backend, minimal infra requirements |
| **User Experience** | 15% | Plain-language verdicts, guided next steps, regional language support, fast response |

Also prepare to speak to the official Evaluation Focus areas: detection precision/recall, **false positive rate (must be very low** — a citizen dismissed as "safe" when it's a real scam is the worst failure mode), and auditability of the verdict trail.

---

## 10. 2-Person Task Split

**Person A — Backend / AI / Detection Logic**

| Phase | Task | Files |
|---|---|---|
| Hour 0–2 | Set up OpenAI API key, test `gpt-5.4-mini`, wire up token-usage logging | `llm/openai_client.py` |
| Hour 2–5 | Build rule-based red-flag engine | `detection/rules.py` |
| Hour 5–9 | Build RAG pipeline: embed corpus, Chroma setup, retrieval-augmented prompt for verdict + explanation | `rag/embed.py`, `rag/vectorstore.py`, `detection/classifier.py`, `detection/prompts.py` |
| Hour 9–11 | Wire up `/analyze` and `/followup` endpoints, test with sample transcripts | `api/routes.py`, `main.py` |
| Hour 11–12.5 | Build campaign log + similarity clustering on top of existing embeddings; wire a `/trending` endpoint | `intelligence/campaign_log.py`, `intelligence/clustering.py` |
| Buffer | Tune false-positive rate on safe messages (courier, real bank alerts) — highest-leverage tuning work | `detection/rules.py` |

**Person B — Data / Frontend / Language / Pitch**

| Phase | Task | Files |
|---|---|---|
| Hour 0–3 | Compile `scam_corpus.json` per Section 8 strategy | `data/scam_corpus.json` |
| Hour 3–4 | Write 5-8 realistic demo transcripts + 1 deliberately-outside-corpus edge case | `docs/demo_script.md` |
| Hour 4–8 | Build chat UI (Streamlit/Gradio first, or React if time allows) | `frontend/` or `app.py` |
| Hour 8–10 | Add language detect + toggle, wire LLM translation for Hindi + one more | `language/translate.py` |
| Hour 10–11.5 | Build the trending-campaigns panel UI (consumes `/trending` from Person A) | `dashboard/trending_campaigns.py` |
| Hour 11.5–12 | Architecture diagram, pitch deck, demo video script | `docs/`, deck |

**Shared — last 3-4 hours**
- Integration testing end-to-end with demo transcripts
- Fix false positives/negatives together — highest-leverage joint work
- Record demo video
- Rehearse pitch live on the actual presenting laptop

---

## 11. Demo Script

1. Paste a realistic "CBI digital arrest" transcript → instant SCAM verdict with red flags highlighted and explanation citing the matched known pattern
2. Paste a legitimate courier delivery message → LIKELY_SAFE verdict, demonstrating low false-positive behavior
3. Ask a follow-up in Hindi ("mujhe ab kya karna chahiye?") → response in Hindi with NCRB reporting guidance
4. Paste the deliberately outside-corpus edge case → still correctly flagged, demonstrating the system isn't overfit to its own dataset
5. **Paste 3-4 pre-seeded similar "fake customs officer" transcripts in quick succession, then show the trending-campaigns panel light up** — *"6 similar scripts detected in the last 2 hours"* — this is the moment that directly demonstrates the predictive layer, not just per-message detection. Say explicitly: *"Every citizen interaction is a sensor. Individually we react to a message. Collectively, we're seeing a campaign scale in real time — that's the predictive piece the problem statement asks for."*
6. (If further stretch built) Show the broader pattern dashboard as the full "law enforcement view"

---

## 12. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Corpus looks thin / self-authored | Section 8 strategy: real-source majority, phrasing variants, proactive disclosure, outside-corpus test case |
| Daily token quota exhausted mid-demo | Request counter/logger with a soft ceiling; cache repeated test-transcript results during dev; never default any path to the big-model quota; keep a couple of mocked responses ready as last-resort UI fallback |
| LLM hallucinating a wrong verdict | Rule-layer acts as a floor/override; always show *why* (cited red flags), never just a number |
| False positive on a real, safe message during live judging | Deliberately tune and test against common safe-message patterns (courier, bank alerts, OTP for legitimate logins) before demo day |
| Scope creep (attempting counterfeit detection too) | Treat as stretch-only; MVP text-based fraud detection must be rock solid first |

---

## 13. Deliverables Checklist

- [ ] Working Prototype (chat interface + backend, demoable live)
- [ ] Architecture Diagram (Section 6)
- [ ] Presentation Deck (lead with the ₹1,776 crore stat + honest cost framing)
- [ ] Demo Video (Section 11 script)