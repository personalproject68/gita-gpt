# GitaGPT - Decisions

## Status Legend
- 💡 Idea - Raw, needs deliberation
- 📋 Planned - Deliberated, ready to build
- 🔄 In Progress - Currently building
- ✅ Done - Shipped
- ❌ Dropped - Rejected (see Dropped table)

---

## Active

| ID | Problem | Feature | Arch | GTM | Status |
|----|---------|---------|------|-----|--------|
| P1 | Users can't find relevant shloka | Semantic search | ChromaDB + Cohere | "Ask any question" | ✅ Done |
| P2 | Users want to browse by mood | Topic menu (5 topics) | curated_topics.json + inline keyboards | "Browse by feeling" | ✅ Done |
| P3 | Users forget the bot exists | Daily shloka push (auto-subscribe) | SQLite subscribers + cron (6 AM IST) | Organic re-engagement | ✅ Done |
| P4 | Users want to share wisdom | Forward-friendly formatting | "गीता GPT 🙏" footer | Organic forwarding | ✅ Done |
| P5 | Spam and abuse risk | Rate limit + keyword filter | SQLite rate tracking + content_filter.py | - | ✅ Done |
| P6 | Users want deeper explanation | "और" follow-up | Next related shloka from search results | - | ✅ Done |
| P11 | Elderly struggle with text input | Voice-to-text | Google STT + Gemini fallback | Telegram voice notes | ✅ Done |
| P12 | Users need word-by-word clarity | Shabdarth (शब्दार्थ) for 56 key shlokas | Pre-generated with [SECTION] parsing | Deeper understanding | ✅ Done |
| P13 | Need visibility into bot usage | /stats admin command | SQLite metrics (DAU, messages, subscribers) | - | ✅ Done |
| P14 | Daily shloka felt repetitive | Expanded daily pool to 30 shlokas | 30 best shlokas across 8 chapters, date-based cycling | Fresh daily content | ✅ Done |
| P15 | Daily shlokas feel random, no retention | गीता यात्रा — sequential 701-shloka journey | journey_position in SQLite, inline "अगला श्लोक →" button | "Complete the entire Gita" | ✅ Done |
| P16 | No curated "greatest hits" discovery path | अमृत श्लोक — 10 iconic shlokas as inline menu | AMRIT_SHLOKAS in config, COMPLETE_LOOKUP + pre-fetched interpretations | /amrit command + text triggers | ✅ Done |

---

## Key Decisions (from Interview 2025-02-07)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Platform | Telegram first | ₹500/mo vs ₹41K/mo. Zero-cost validation. WhatsApp after PMF via Meta API. |
| Code approach | Clean rewrite | Fresh Telegram bot. Reuse only search/AI/data logic from WhatsApp MVP. |
| File structure | Modular from start | routes/, services/, guardrails/ structure. No monolith. |
| Search engine | ChromaDB + Cohere | Keep from MVP. Already working, battle-tested. |
| Voice | Google STT (voice-to-text only) | Already have GOOGLE_API_KEY. Text responses only for v1. |
| Persistence | SQLite | Replace in-memory sessions. Survives restarts. |
| Onboarding | Simple welcome message | No 3-step drip for v1. Add later. |
| Dataset | 100 curated shlokas | Higher quality. Expand based on user queries later. |
| Daily shloka | Auto-subscribe | Soft opt-in on first message. "रोकें" to unsubscribe. |
| Krishna images | Skip for v1 | Need to source. Add later. |
| Monetization | Add after 1 month | Build trust first. Dakshina model when ready. |
| Deployment | Railway | No sleep, built-in cron, simple deploy. |
| Interpretations | Pre-fetched, not live API | Instant responses, zero cost. Gemini only for shabdarth. |

---

## Backlog

| ID | Problem | Notes |
|----|---------|-------|
| P7 | Users want audio responses | TTS for voice-out. Add after voice-in is validated. |
| P8 | Users forget to return | Solved by P3 (daily push). May need more engagement hooks later. |
| P9 | Trust/credibility gap | Commentary citations (Shankaracharya, Ramanujacharya). Post-launch. |
| P10 | Conversation feels transactional | Empathy arc in AI interpretation. Post-launch. |

---

## Dropped

| ID | Problem | Why Dropped |
|----|---------|-------------|
