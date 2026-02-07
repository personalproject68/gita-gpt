# Fix: Slow & Confusing Double-Message Response Flow

## Context
The bot sends TWO messages per question — a fast generic interpretation, then a slow Gemini contextual one seconds later. With duplicate footers, this confuses elderly users. Topics unnecessarily hit Cohere API when curated mappings already exist. No typing indicator while searching.

**Goal**: One contextual message per question. Instant responses for topics/daily/"more".

---

## Changes

### 1. `routes/telegram.py` — Core refactor

**`_process_question()` (line 285)** — Single synchronous message with Gemini:
- Add `send_chat_action(chat_id, 'typing')` before search
- Call `get_contextual_interpretation()` synchronously (not in background thread)
- Fallback to `get_ai_interpretation()` if Gemini fails
- Send ONE message via `format_shloka()`
- Remove `_trigger_contextual_followup()` call

**`_handle_callback()` (line 207)** — Instant topic response:
- Replace `find_relevant_shlokas(topic_label)` (Cohere API) with direct lookup: `CURATED_TOPICS[topic_id]['best_shlokas']` → `SHLOKA_LOOKUP[sid]`
- Use pre-fetched `get_ai_interpretation()` (instant)
- Remove `_trigger_contextual_followup()` call
- Import `CURATED_TOPICS, SHLOKA_LOOKUP` from `models.shloka`

**`_handle_more()` (line 176)** — Simplify:
- Keep Cohere search (needed to find unseen shlokas)
- Use pre-fetched `get_ai_interpretation()` only (no Gemini needed for "more")
- Remove `_trigger_contextual_followup()` call

**Delete functions:**
- `_send_contextual_followup()` (lines 37-45)
- `_trigger_contextual_followup()` (lines 48-55)
- Remove `import threading`
- Remove `format_contextual_followup` from imports

### 2. `services/formatter.py` — Cleanup

- Delete `format_contextual_followup()` (line 115-117) — no longer used

### 3. `run_local.py` — Polling fix

- Line 34: Change `'timeout': 5` → `'timeout': 30`
- Line 38: Change `timeout=10` → `timeout=35` (must exceed polling timeout)

### 4. No changes needed
- `services/ai_interpretation.py` — both functions stay as-is
- `services/search.py` — unchanged
- `models/shloka.py` — unchanged (already has `CURATED_TOPICS`, `SHLOKA_LOOKUP`)

---

## Expected Performance

| Flow | Before | After |
|------|--------|-------|
| Question | 3-5s, 2 messages, no feedback | 3-5s, 1 message, typing indicator |
| Topic | 3-5s, 2 messages (Cohere + Gemini) | <500ms, 1 message (direct lookup) |
| "More" | 3-5s, 2 messages | 1-2s, 1 message (Cohere only, no Gemini) |
| Daily | Instant | No change |

---

## Verification

1. Run `python run_local.py`
2. Send a question like "मुझे गुस्सा आता है" → typing indicator appears → ONE message with contextual Gemini interpretation + shloka + single footer
3. Send `/topic` → tap a topic button → instant response (<1s), no Cohere delay
4. Send "और" → next shloka with pre-fetched interpretation, single message
5. Send `/daily` → still instant
6. Kill Gemini (unset GOOGLE_API_KEY) → question still works with pre-fetched fallback
