# Problem Deliberations

For each problem, document evidence, impact, and whether it's worth solving.

---

## P1: Users can't find relevant shlokas ✅ Done (MVP)

### Evidence
- Test users typed chapter numbers (2.47) — they don't know them
- Users described feelings: "I'm anxious", "my son doesn't listen"
- Keyword search failed for emotional, colloquial queries

### Who experiences this?
- Elderly users unfamiliar with Gita structure
- Young users searching by life situation

### Impact if unsolved
- Core value proposition fails
- Users leave after first failed query

### Ideal state
User describes their situation in natural Hindi → Gets relevant shloka. No Gita knowledge required.

### Status: ✅ Solved in MVP with ChromaDB + Cohere semantic search. Carrying forward to Telegram v1.

---

## P2: Users want to browse by mood ✅ Done (MVP) → 📋 Evolving for Telegram

### Evidence
- Users don't always have a specific question
- "Show me something about peace" type requests
- Browsing behavior observed in testing

### Who experiences this?
- Casual users exploring Gita wisdom
- Users seeking daily inspiration

### Impact if unsolved
- Limited engagement for exploratory users
- Miss opportunity for repeat usage

### Ideal state
User taps a topic button → Gets curated shloka for that mood. No typing needed.

### Status: Evolving from 7 text topics → 5 topics with Telegram inline keyboard buttons.

---

## P3: Users forget the bot exists ✅ Done (MVP) → 📋 Evolving for Telegram

### Evidence
- One-time usage pattern in early testing
- No re-engagement mechanism

### Who experiences this?
- All users after initial interaction

### Impact if unsolved
- Low retention
- Limited viral spread

### Ideal state
Daily touchpoint that brings users back. Auto-subscribe, personalized by engagement history.

### Status: Evolving from random shloka → personalized by user's top topics. Auto-subscribe on first message.

---

## P4: Users want to share wisdom ✅ Done (MVP) → 📋 Evolving for Telegram

### Evidence
- Users screenshot shlokas to share
- WhatsApp forward culture in target demographic
- "How do I send this to my son?" type questions

### Who experiences this?
- Elderly users wanting to share with family

### Impact if unsolved
- Miss viral loop opportunity
- Friction in sharing reduces spread

### Ideal state
Forward-friendly formatting that looks good when forwarded. "गीता GPT 🙏" footer for organic branding.

### Status: Evolving from wa.me links → forward-friendly formatting with branded footer.

---

## P5: Spam and abuse risk ✅ Done (MVP) → 📋 Evolving for Telegram

### Evidence
- Bots are targets for abuse
- API costs per message
- Prompt injection attempts observed

### Who experiences this?
- System (not users)

### Impact if unsolved
- High API costs from spam
- Jailbreak attempts

### Ideal state
Rate limiting + compassionate content filtering. SQLite-backed for persistence.

### Status: Evolving from in-memory → SQLite persistence. Adding Hinglish profanity variants.

---

## P6: Users want deeper explanation ✅ Done (MVP) → 📋 Evolving for Telegram

### Evidence
- "What does this mean for me?" type follow-ups
- Sanskrit shlokas need interpretation
- Context-specific application requested

### Who experiences this?
- Users who find relevant shlokas

### Impact if unsolved
- Shlokas feel generic without personal context

### Ideal state
AI interpretation connecting shloka to user's question. "और" command for next related shloka.

### Status: Evolving from numbered 1/2/3 → "और" command (avoids collision with topic numbers).

---

## P9: Users don't trust an anonymous bot 💡 Backlog

### Evidence
- Elderly users ask "यह किसने बनाया?" (who made this?)
- No pandit endorsement, temple association, or commentary citations
- Target demographic values authority: guru, pandit, established institution

### Who experiences this?
- Elderly users (primary audience) — trust hierarchy matters deeply
- New users evaluating whether to continue using

### Impact if unsolved
- Users dismiss bot as "timepass" or unreliable
- Won't share with friends without credibility signal
- Limits word-of-mouth in Gita class community

### Ideal state
Bot cites specific commentaries (Shankaracharya, Ramanujacharya), has endorsement from a known pandit/teacher, or is associated with a respected institution.

### Status: 💡 Backlog. Address post-launch based on user feedback.

---

## P10: Conversation feels cold and transactional 💡 Backlog

### Evidence
- Bot jumps straight to shloka without acknowledging user's emotion
- Real guru interaction: empathy first → teaching → takeaway
- Users describing grief/anxiety get a formatted shloka block — feels robotic

### Who experiences this?
- Users sharing emotional/vulnerable situations
- First-time users forming impression of the bot

### Impact if unsolved
- Users feel unheard — defeats purpose of spiritual guidance
- Low emotional connection = low retention

### Ideal state
Bot acknowledges emotion first ("यह कठिन समय है"), then offers shloka with personal context, then gives a practical takeaway. Feels like a compassionate teacher, not a search engine.

### Status: 💡 Backlog. Partially addressed by Gemini AI interpretation prompt. Full empathy arc post-launch.

---

## P11: Elderly users struggle with text input 📋 Planned (Telegram v1)

### Evidence
- 55+ users have poor eyesight, small phone screens
- Hindi typing on phone keyboard is difficult (script switching)
- Many elderly prefer voice notes (already habitual)
- Accessibility is not addressed in current design

### Who experiences this?
- Primary audience (55+ elderly users)
- Users with vision impairment or motor difficulties

### Impact if unsolved
- Excludes significant portion of target users
- Creates friction that prevents regular usage
- Limits adoption in the exact demographic being targeted

### Ideal state
Users send voice notes → bot transcribes and responds with text.

### Solution
- Google Speech-to-Text (Hindi: `hi-IN`)
- Telegram native voice message support
- Voice-to-text only for v1 (no TTS response)
- Max 60 seconds, fallback message on failure

### Status: 📋 Planned for Telegram v1. Voice-to-text using Google STT.

---

## Template for New Problems

```markdown
## P[n]: [Problem Title]

### Evidence
- What have you observed?
- What did users say?
- What data supports this?

### Who experiences this?
- Target user segment
- Frequency of occurrence

### Impact if unsolved
- What's the cost of not solving?
- Does it block core value proposition?

### Ideal state
- What would "solved" look like?
```
