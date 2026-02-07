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
| P1 | Users can't find relevant shloka | Semantic search | ChromaDB + Cohere | "Ask any question" | ✅ Done (WhatsApp MVP) |
| P2 | Users want to browse by mood | Topic menu (5 topics) | curated_topics.json + inline keyboards | "Browse by feeling" | 📋 Planned (Telegram) |
| P3 | Users forget the bot exists | Daily shloka push (auto-subscribe) | SQLite subscribers + GitHub Actions cron | 6 AM IST daily | 📋 Planned (Telegram) |
| P4 | Users want to share wisdom | Forward-friendly formatting | "गीता GPT 🙏" footer + wa.me fallback | Organic forwarding | 📋 Planned (Telegram) |
| P5 | Spam and abuse risk | Rate limit + keyword filter | SQLite rate tracking | - | 📋 Planned (Telegram) |
| P6 | Users want deeper explanation | "और" follow-up | Gemini interpretation | - | 📋 Planned (Telegram) |
| P11 | Elderly struggle with text input | Voice-to-text | Google Speech-to-Text | Telegram voice notes | 📋 Planned (Telegram) |

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
| Timeline | This week | Get core Telegram bot working for Gita class demo. |

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
