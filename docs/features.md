# GitaGPT - Features (Telegram v1)

## v1 Scope — Ship This Week

Features marked with ✅ are in v1 scope. Features marked with 🔜 are post-launch.

---

## ✅ 1. Content Moderation (Keyword-Only)

No AI moderation tier. Simple keyword filtering optimized for elderly users.

### Blocklist Layers:
| Script | Examples |
|--------|----------|
| Hindi (Devanagari) | साला, कुत्ता, भड़वा |
| Hinglish (Roman) | saala/sala, bc/bhenchod, mc, kutta |
| English | Standard profanity list |

### Keep:
- Rate limiting: 20 messages/hour/user (SQLite-backed)
- Max input: 500 characters
- Input sanitization

### Compassionate Response:
Instead of punitive blocking, redirect with empathy:
```
आपके मन में कुछ कठिन भाव हैं। क्या मैं क्रोध या निराशा पर गीता का मार्गदर्शन दूं?
```

---

## ✅ 2. Topic Menu (5 Topics, Inline Keyboard)

5 topics. First-person framing. Telegram inline keyboard buttons (no typing needed).

### Primary approach: Natural conversation
After greeting, ask:
```
आज आपके मन में क्या चल रहा है? बस बता दीजिए।
```
Let the user describe their feeling naturally → route to semantic search.

### Fallback: Topic menu (inline keyboard)
Show when user:
- Sends `विषय` / `topic` explicitly
- Sends `?` or "pata nahi" / "kuch bhi"
- Sends a message too vague to search

```
विषय चुनें:
[मुझे चिंता/डर लगता है]
[मुझे गुस्सा आता है]
[मुझे समझ नहीं आता क्या करूं]
[मैं बीमार हूं / कोई खो दिया]
[मैं अकेला महसूस करता हूं]
```

| # | Internal Key | Covers |
|---|--------------|--------|
| 1 | chinta | fear, anxiety, peace, meditation |
| 2 | krodh | anger |
| 3 | kartavya | duty, decisions, family conflicts |
| 4 | dukh | illness, death, grief, loss |
| 5 | akela | loneliness, isolation |

---

## ✅ 3. Single Shloka + Deep Interpretation

Show 1 shloka per question. Invest in search accuracy.

### Response Format (Forward-Friendly):
```
📿 गीता 2.47

कर्मण्येवाधिकारस्ते...

[Hindi meaning]

[Deep AI interpretation - 3-4 lines, contextual]

— गीता GPT 🙏
```

### Follow-up:
- `और` = show another related shloka
- Store multiple matches in session, serve next on "और"

### Forward-Friendly Design:
- No bot-specific UI elements in the shloka block
- "गीता GPT 🙏" footer acts as organic branding when forwarded
- Keep `share` command as fallback for wa.me link

---

## ✅ 4. Daily Shloka Push (Auto-Subscribe)

Auto-subscribe on first message. Essential for habit formation.

### Welcome Message (Soft Opt-in):
Part of the simple welcome message:
```
🙏 गीता GPT में स्वागत है!

मैं आपको प्रतिदिन सुबह 6 बजे प्रेरणादायक श्लोक भेजूंगा।

बंद करने के लिए कभी भी "रोकें" भेजें।

आज आपके मन में क्या चल रहा है? बस बता दीजिए।
```

### Unsubscribe Commands:
- `रोकें` / `रुको` / `stop` / `unsubscribe` / `band`

### Personalization:
- Track each user's most-engaged topics (based on queries)
- Rotate daily shlokas by user's top topic
- Fallback: random from curated list for new users

### Technical:
- `/daily-push` POST endpoint (with secret key)
- Railway cron or GitHub Actions at 6:00 AM IST
- Subscribers in SQLite

---

## ✅ 5. Voice-to-Text (P11)

Accept Telegram voice notes, transcribe to text, respond with text.

### How it works:
1. User sends voice note in Telegram
2. Bot downloads the .ogg file via Telegram API
3. Google Speech-to-Text transcribes (Hindi language)
4. Transcription processed as normal text query
5. Response sent as text

### Config:
- Language: `hi-IN` (Hindi)
- Max voice duration: 60 seconds
- Fallback on transcription failure: "मुझे आपकी बात समझ नहीं आई। कृपया टाइप करके भेजें।"

---

## ✅ 6. Simple Welcome Message

Single welcome message on first contact. No drip system for v1.

### On `/start` or `hi`:
```
🙏 गीता GPT में स्वागत है!

जीवन का कोई भी प्रश्न पूछें — गीता से उत्तर मिलेगा।

रोज़ सुबह 6 बजे प्रेरणादायक श्लोक आएगा।
बंद करने के लिए "रोकें" भेजें।

विषय देखने के लिए "विषय" भेजें।
मदद के लिए "मदद" भेजें।
```

---

## 🔜 7. Krishna Images (Post-Launch)

Images for daily shloka push. Makes it feel special.

**Status:** Need to source 5 images matching topic themes.

| Tag | Image Theme |
|-----|-------------|
| chinta | Peaceful/calming Krishna |
| krodh | Calm/composed Krishna |
| kartavya | Krishna teaching Arjuna |
| dukh | Compassionate Krishna |
| akela | Krishna with devotees |

---

## 🔜 8. Onboarding Drip (Post-Launch)

3-message drip instead of single welcome. Reveals features gradually.

**Status:** Deferred. Simple welcome for v1.

---

## 🔜 9. Monetization — Dakshina (Month 2)

Voluntary donation model. UPI QR + Razorpay.

**Status:** Add after 1 month of trust-building.

Trigger words: `दान`, `सेवा`, `donate`, `pay`, `योगदान`

---

## 🔜 10. Voice Output — TTS (Post-Launch)

Reply with audio for users who prefer listening.

**Status:** Depends on P7 cost analysis. Add after voice-in is validated.

---

## Commands (v1)

| Command | Hindi | Action |
|---------|-------|--------|
| `/start`, `hi`, `hello` | `नमस्ते`, `हेलो` | Welcome message |
| `help` | `मदद`, `सहायता` | Show commands |
| `topic` | `विषय` | Show 5 topic categories (inline keyboard) |
| `daily` | `प्रेरणा`, `आज` | Today's shloka (on-demand) |
| `और` | `more` | Show another related shloka |
| `share` | `भेजें` | Shareable link |
| `रोकें` | `stop` | Unsubscribe from daily |

---

## Pre-work Required (v1)

- [ ] Build Hinglish profanity blocklist with spelling variants
- [ ] Update `curated_topics.json` for 5 new topics (chinta, krodh, kartavya, dukh, akela)
- [ ] Set up Telegram bot via @BotFather
- [ ] Create SQLite schema (sessions, messages, subscribers)
- [ ] Implement Google STT integration for voice notes
- [ ] Add "गीता GPT 🙏" footer to shloka response formatter
- [ ] Set up Railway deployment
- [ ] Configure daily push cron (6 AM IST)
