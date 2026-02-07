# GitaGPT - Go-To-Market Strategy

## Target Audience
- Elderly Indians (55+)
- Hindi-speaking
- Religious/spiritual (already interested in Gita)
- Wealthy segment (disposable income, pension, savings)

---

## Platform Strategy: Telegram First (Confirmed)

### Why Telegram First

| Factor | Telegram | WhatsApp (Twilio) |
|--------|----------|-------------------|
| Cost (1000 users) | ~₹500/mo (server only) | ~₹41,000/mo |
| API cost per message | Free | ₹0.42 |
| Setup time | Minutes (@BotFather) | Days (business verification) |
| Rich UI | Inline keyboards, buttons | Text only |
| Voice notes | Native support | Limited |
| Risk to validate | Near zero | ₹41K/mo burn before PMF |

### Platform Roadmap
1. **Now:** Telegram — validate product, iterate fast, near-zero cost
2. **After PMF:** WhatsApp via Meta Business API directly (₹18K/mo) — skip Twilio
3. **Never:** Twilio WhatsApp at scale (unit economics don't work)

### Telegram-Specific Advantages for Elderly Users
- Inline keyboard buttons = no typing numbers
- Native voice message support (critical for P11)
- Group/channel features for community building
- Bot discovery through Telegram search

---

## Primary GTM Channel: Parents' Gita Class

### Why This Works
| Factor | Advantage |
|--------|-----------|
| Warm intro | Parents introduce = instant trust |
| Pre-qualified | Already love Gita, no convincing needed |
| Wealthy | Self-selected affluent segment |
| Captive audience | Meet weekly, can demo live |
| Word of mouth | Elderly love recommending to friends |
| Zero CAC | ₹0 customer acquisition cost |

---

## Parallel GTM Channel: NRI Gifting

### Why This Is High Priority (Not "Long-Term")
- Children abroad gifting spiritual connection to parents back home
- Highest willingness to pay: ₹500/mo without hesitation
- Already on Telegram (NRIs use it more than elderly in India)
- Emotional trigger: guilt about being far from aging parents

### Execution
1. **Landing page** (English): "Gift your parents daily Gita wisdom"
2. **Channels:** Indian diaspora WhatsApp/Telegram groups, Reddit (r/ABCDesis, r/india)
3. **Pricing:** ₹500/mo or ₹5,000/year ("Gita Seva subscription")
4. **What they get:** Parents receive daily personalized shloka + bot access
5. **Onboarding:** NRI signs up → you personally set up bot for their parent

### Projections
| Metric | Conservative | Optimistic |
|--------|--------------|------------|
| NRI subscribers (Month 3) | 5 | 15 |
| Monthly revenue | ₹2,500 | ₹7,500 |
| Cost to serve | ~₹0 (Telegram) | ~₹0 |

---

## Execution Plan

### Phase 1: Soft Launch on Telegram (This Week)

**Step 1: Build & deploy**
- Clean Telegram rewrite with modular structure
- Core features: search, topics, daily push, voice-to-text
- Deploy on Railway
- Test thoroughly before demo

**Step 2: Parents introduce casually**
```
"हमारे बेटे ने एक Telegram सेवा बनाई है।
रोज़ सुबह गीता का श्लोक आता है।
कोई समस्या हो तो पूछो, गीता से जवाब मिलता है।
आवाज़ में बोलो तो भी जवाब मिलता है।"
```

**Step 3: Live demo (5 minutes)**
- Attend one class (or parents show on phone)
- Demo: "मुझे गुस्सा आता है" → show response
- Demo: Send voice note → show transcription + response
- Show daily shloka feature
- "बिल्कुल मुफ्त है, बस Telegram पर भेजना है"
- Help install Telegram if needed (most already have it)

**Step 4: Collect signups**
- Share bot link: t.me/GitaGPTbot — one tap to start
- Or collect numbers, send them the link
- Target: 20-30 signups from first class

### Phase 2: Activation (Week 2-3)

**Daily engagement:**
- 6 AM shloka to all users (elderly wake early)
- Personalized by their most-engaged topic

**Personal follow-up after 7 days:**
```
🙏 नमस्ते आंटी/अंकल,

मैं आशीष, [माता-पिता] का बेटा।

आपको गीता के श्लोक कैसे लग रहे हैं?
कोई सुझाव हो तो ज़रूर बताइएगा।

🙏 राधे राधे
```

### Phase 3: Retention (Week 4+)

**Weekly themed series:**
- 7 days of Karma Yoga
- 7 days of Bhakti
- 7 days on overcoming fear

**Festival specials:**
- Gita Jayanti (special 18-chapter journey)
- Janmashtami (Krishna-focused shlokas)
- Navratri, Diwali (themed content)

**Milestone messages:**
```
🙏 आप 30 दिन से गीता GPT के साथ हैं!
आपने 45 श्लोक पढ़े हैं।
आज का विशेष श्लोक आपके लिए...
```

**Monthly feedback prompt:**
```
आपको गीता GPT कैसा लगा?
1️⃣ बहुत अच्छा
2️⃣ अच्छा
3️⃣ ठीक है
4️⃣ सुधार चाहिए
```

### Phase 4: Monetization (Month 2)

**NOT in v1.** Add after 1 month of trust-building.

After trust is built, introduce seva option:
```
🙏 गीता वर्ग के सभी साथियों को सूचना

अब आप सेवा में योगदान दे सकते हैं।
यह पूरी तरह स्वैच्छिक है।

QR Code स्कैन करें या "सेवा" भेजें।

जो न दे सकें, उनकी शुभकामनाएं भी स्वीकार हैं।
```

### Phase 5: Expand (Month 3+)

**Ask for referrals:**
```
"क्या आपके कोई मित्र और गीता वर्ग जाते हैं?
मैं वहां भी यह सेवा पहुंचाना चाहता हूं।"
```

One class → leads to 3-4 more classes

---

## Projections

### From One Gita Class (30-40 people)

| Metric | Conservative | Optimistic |
|--------|--------------|------------|
| Signups | 20 | 35 |
| Daily active after 1 month | 10 | 20 |
| Donors (Month 2) | 2-3 | 5-7 |
| Monthly revenue (Month 2) | ₹500-1,500 | ₹2,000-5,000 |

### Scaling to 5 Classes + NRI Channel

| Metric | 5 Classes | + NRI |
|--------|-----------|-------|
| Total signups | 100-150 | +10-30 NRI |
| Active users | 50-100 | +10-30 |
| Monthly revenue | ₹3,000-15,000 | +₹2,500-7,500 |
| Monthly cost (Telegram) | ~₹3,600 | ~₹3,600 |

---

## Monetization Model: Dakshina (Month 2 — Not v1)

### Principles
- No sponsorships (feels commercial)
- No mandatory payments
- Pure voluntary seva/dakshina
- Personal relationship > transaction

### Payment Methods
1. **One-time**: UPI QR code (GPay/PhonePe/Paytm)
2. **Monthly**: Razorpay subscription link (optional)
3. **NRI**: Razorpay international (USD/GBP/CAD)

### Trigger Words in Bot
`दान`, `सेवा`, `donate`, `pay`, `योगदान`

---

## Organic Relationship Building

### Philosophy
Genuine seva builds genuine relationships. Never target or manipulate. Let generosity emerge naturally from people who find real value.

### What NOT to Do
- Don't profile users by vulnerability (grief, loneliness) for monetization
- Don't push donation messages to active/emotional users
- Don't track "donor potential" metrics
- Don't differentiate service based on donation status

### What to Do
- Respond personally when someone shares deep emotions
- Offer phone calls to elderly users who seem to want human connection
- Thank every donor equally regardless of amount
- Share project updates with donors (they feel invested)

---

## Cost Structure (Telegram v1)

### Per Message
| Component | Cost |
|-----------|------|
| Telegram Bot API | Free |
| Cohere embedding | ₹0.008 |
| Gemini AI | ₹0.008 |
| Google STT (voice only) | ₹0.05 |
| **Text total** | **₹0.016/msg** |
| **Voice total** | **₹0.066/msg** |

### Monthly (1000 users, 3 msgs/day, 30% voice)
- Server (Railway): ₹0-400
- AI APIs: ₹1,440
- Google STT: ₹1,800
- **Total: ~₹3,600/mo**

### Future: WhatsApp via Meta Business API
Monthly (1000 users): ~₹20,000 — only viable after revenue covers it.

---

## Launch Checklist (This Week)

### Before Demo
- [ ] Telegram bot created via @BotFather
- [ ] Bot works flawlessly in Hindi (text + voice)
- [ ] Daily shloka scheduled at 6 AM IST
- [ ] Deployed on Railway
- [ ] Parents briefed on demo script
- [ ] Bot link ready: t.me/GitaGPTbot

### Demo Script (for parents)
```
1. "देखो, मैं लिखता हूं 'मन शांत नहीं रहता'"
2. [Show response with shloka]
3. "अब आवाज़ में बोलता हूं" [Send voice note]
4. [Show transcription + response]
5. "रोज़ सुबह श्लोक आता है बिना मांगे"
6. "कोई पैसा नहीं लगता"
```

### Printed Cards (Optional)
```
┌─────────────────────────────┐
│  🙏 गीता GPT                │
│                             │
│  रोज़ सुबह गीता का श्लोक      │
│  जीवन के प्रश्नों का उत्तर    │
│  आवाज़ में बोलो, जवाब मिलेगा  │
│                             │
│  Telegram पर खोजें:          │
│  @GitaGPTbot                │
│                             │
│  "hi" भेजें शुरू करने के लिए   │
└─────────────────────────────┘
```
Cost: ₹500 for 100 cards

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Parents feel awkward promoting | Position as "helping beta's seva project" |
| Elderly don't have Telegram | Help install at class (2 min), or family member helps |
| Class organizer objects | Offer to donate portion to class/temple |
| Tech issues embarrass parents | Test thoroughly before demo |
| Voice transcription fails in noisy env | Fallback message + text input always available |
| Telegram adoption too low | Pivot to WhatsApp (Meta API) once revenue allows |

---

## Success Metrics

### Week 1 (Launch)
- [ ] Bot deployed and working on Telegram
- [ ] Voice-to-text working reliably
- [ ] Daily push sending at 6 AM

### Month 1
- [ ] 20+ signups from first class
- [ ] 50% 7-day retention
- [ ] Monthly cost < ₹4,000

### Month 2
- [ ] Monetization (dakshina) added
- [ ] 1-2 donations received
- [ ] Feedback rating > 3.5/5

### Month 3
- [ ] 3+ Gita classes onboarded
- [ ] 100+ active users
- [ ] ₹3,000+ monthly revenue (classes + NRI)

### Month 6
- [ ] 500+ active users
- [ ] Revenue > costs (break-even)
- [ ] NRI channel generating ₹5,000+/mo
- [ ] Consider WhatsApp expansion
