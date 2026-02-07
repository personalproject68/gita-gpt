# Product Ledger Methodology

A lightweight, markdown-based system for shipping small products with full traceability from customer insight to shipped code.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Problem with Existing Approaches](#2-the-problem-with-existing-approaches)
3. [What is Product Ledger](#3-what-is-product-ledger)
4. [How It's Different](#4-how-its-different-from-existing-frameworks)
5. [The Structure](#5-the-structure)
6. [Why It Works](#6-why-it-works)
7. [Where It Fails](#7-where-it-fails--limitations)
8. [When to Use vs Skip](#8-when-to-use-vs-when-to-skip)
9. [Workflow](#9-workflow-how-to-use-it)
10. [Template](#10-template)
11. [Real Example: GitaGPT](#11-real-example-gitagpt)
12. [Anti-Patterns](#12-anti-patterns-common-mistakes)
13. [Variations and Extensions](#13-variations-and-extensions)

---

## 1. Executive Summary

### What is Product Ledger?

Product Ledger is a methodology for shipping small products that uses:
- **One decision table** (`DECISIONS.md`) as both inbox and verdict
- **Four mandatory supporting files** as the deliberation layer
- **ID-based linking** for full traceability

### Who is it for?

- Solo makers shipping multiple small products
- Small teams (2-3 people) moving fast
- Anyone who finds PRDs too heavy but needs more structure than a README

### One-line value proposition

**Every idea enters raw, passes through forced deliberation, and exits as an accepted feature or a documented rejection.**

---

## 2. The Problem with Existing Approaches

### PRDs are too heavy

Product Requirement Documents assume:
- Dedicated product managers
- Formal review cycles
- Stakeholder sign-offs

For a solo maker shipping a WhatsApp bot in a week, a 10-page PRD is absurd.

### Agile/Scrum assumes teams

Sprint planning, standups, retrospectives, story points — these rituals exist to coordinate multiple people. A solo maker doing daily standups with themselves is cargo-culting process.

### Documentation fragments across tools

In a typical startup:
- Tasks live in Jira
- Specs live in Confluence
- Designs live in Figma
- Architecture lives in Google Docs
- Code lives in GitHub

Finding "why did we build this feature?" requires archaeology across 5 tools.

### Solo makers keep everything in their head

The opposite extreme: no documentation at all. This works until:
- You take a 2-week break and forget context
- You want to onboard a collaborator
- You need to explain decisions to users/investors

### No traceability from insight to code

When a customer complains about a feature, can you trace back to:
- The original problem you were solving?
- The alternatives you considered?
- Why you chose this approach?

Most systems can't. Product Ledger can.

---

## 3. What is Product Ledger

### Core Concept

One table (`DECISIONS.md`) that tracks the full lifecycle of every product decision, supported by four mandatory files where the actual thinking happens.

### The 5 Columns

| Column | Question it answers |
|--------|---------------------|
| **ID** | Unique identifier for tracing (P1, P2, P3...) |
| **Problem** | What pain point are we solving? |
| **Feature** | What are we building? |
| **Arch** | How are we building it technically? |
| **GTM** | How will users discover this? |
| **Status** | Where is this in the lifecycle? |

### The Circular Flow

```
DECISIONS.md (INPUT)
   Raw idea, problem spotted, customer insight
              ↓
         problem.md
   Ponder: Is this worth solving? For whom?
              ↓
         features.md
   Ponder: What's the minimal solution?
              ↓
      architecture.md
   Ponder: How do we build this?
              ↓
           gtm.md
   Ponder: How will users discover this?
              ↓
DECISIONS.md (OUTPUT)
   Accept with summary → Implement
   OR Reject with reason → Archive
```

### Key Insight

**DECISIONS.md is both inbox and verdict.**

Ideas enter raw (just a problem statement). They exit processed (full row with accept/reject status). The supporting files are where the actual deliberation happens — they are not optional documentation.

---

## 4. How It's Different from Existing Frameworks

| Framework | What it is | Product Ledger Difference |
|-----------|------------|---------------------------|
| **PRD** | Verbose product requirements document | Lightweight table + focused supporting files; iterative not upfront |
| **ADR** | Architecture Decision Records | Covers full lifecycle (problem → GTM), not just technical decisions |
| **Jira/Linear** | Task tracking tools | No tool lock-in; plain markdown; decisions not tickets |
| **PRFAQ** | Amazon's Press Release + FAQ | Iterative deliberation vs. heavy upfront planning; works for small bets |
| **README-driven** | Write README before code | More structured; tracks evolution over time; handles multiple features |
| **Jobs-to-be-Done** | Framework for understanding user needs | Living document vs. one-time exercise; includes implementation |
| **Notion databases** | Custom relational databases | No tool dependency; works in any text editor; git-friendly |

### The Key Differentiator

Most frameworks either:
1. Focus on one phase (ADR = architecture only, JTBD = problem only)
2. Require heavy tooling (Jira, Notion, Confluence)
3. Are one-time exercises (PRFAQ, design sprints)

Product Ledger covers the **full lifecycle** in **plain markdown** as a **living system**.

---

## 5. The Structure

### 5.1 DECISIONS.md (The Ledger)

This is your command center. It contains three tables:

#### Active Table
Decisions currently being worked on.

```markdown
## Active

| ID | Problem | Feature | Arch | GTM | Status |
|----|---------|---------|------|-----|--------|
| P1 | ... | ... | ... | ... | ✅ Done |
| P2 | ... | ... | ... | ... | 🔄 In Progress |
| P3 | ... | ... | ... | ... | 📋 Planned |
| P4 | ... | - | - | - | 💡 Idea |
```

#### Backlog Table
Ideas not yet prioritized.

```markdown
## Backlog

| ID | Problem | Notes |
|----|---------|-------|
| P10 | Users want audio responses | Waiting for TTS API costs |
| P11 | Multi-language support | Post-launch consideration |
```

#### Dropped Table
Rejected ideas with reasons (institutional memory).

```markdown
## Dropped

| ID | Problem | Why Dropped |
|----|---------|-------------|
| P9 | Real-time chat | Adds complexity; async WhatsApp is fine |
| P8 | User accounts | Overkill; phone number is identity |
```

### 5.2 Supporting Files (Mandatory)

These are the **deliberation layer**. Every idea MUST flow through them.

#### problem.md
Deep understanding of the problem.

```markdown
## P1: Users can't find relevant shlokas

### Evidence
- 8/10 test users tried typing shloka numbers (2.47)
- Users don't know chapter/verse structure
- Keyword search fails for emotional queries ("I feel lost")

### Who experiences this?
- Elderly users unfamiliar with Gita structure
- Young users searching by life situation, not scripture

### Impact if unsolved
- Users give up after failed searches
- Core value proposition breaks

### Ideal state
User describes their situation → Gets relevant wisdom
No Gita knowledge required
```

#### features.md
What exactly to build.

```markdown
## P1: Semantic Search

### Behavior
- Input: Natural language in Hindi or English
- Process: Embed query → Vector similarity → Top 3 matches
- Output: Formatted shlokas with meanings

### Scope
- IN: Natural language queries, Hindi/English
- OUT: Voice input, image search

### Edge cases
| Case | Behavior |
|------|----------|
| Empty query | Show help message |
| Single word | Use keyword search |
| No matches above threshold | Fallback to keyword search |

### Success criteria
- 80% of queries return at least 1 relevant shloka
- Users engage with returned shlokas (expand, share)
```

#### architecture.md
How to build it technically.

```markdown
## P1: Semantic Search

### Components
- **Embedding model**: Cohere embed-multilingual-v3.0 (Hindi + English)
- **Vector store**: ChromaDB with persistent storage
- **Index**: 100 curated shlokas from gita_tagged.json

### Data flow
```
User query
    → Sanitize (remove special chars, limit length)
    → Embed with Cohere
    → Query ChromaDB (top 3, threshold 0.7)
    → If below threshold, fallback to keyword search
    → Format response
```

### Tradeoffs considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| OpenAI embeddings | Better quality | Cost, API dependency | No |
| Cohere multilingual | Hindi support, free tier | Slightly lower quality | Yes |
| Local embeddings | No API calls | Poor Hindi support | No |

### Dependencies
- cohere Python SDK
- chromadb
- gita_tagged.json (curated subset)
```

#### gtm.md
How users will discover and adopt this.

```markdown
## P1: Semantic Search

### Positioning
"Ask any life question, get Gita wisdom"
Not: "Search our shloka database"

### Discovery
- WhatsApp forward chains (viral loop via share feature)
- Hindi spiritual content groups

### Messaging
- Emphasize: No Gita knowledge needed
- Avoid: Technical terms (semantic, vector, AI)

### Success metric
- Query volume per user
- Share rate of search results
```

### 5.3 File Organization

```
project/
├── DECISIONS.md        ← Inbox + Verdict (command center)
├── docs/
│   ├── problem.md      ← Deliberation: Why
│   ├── features.md     ← Deliberation: What
│   ├── architecture.md ← Deliberation: How (technical)
│   └── gtm.md          ← Deliberation: How (distribution)
└── src/                ← Implementation
```

### 5.4 ID Linking

Every section in supporting files starts with the ID:

```markdown
## P1: Semantic Search
## P2: Topic Menu
## P3: Daily Inspiration
```

This enables:
- Grep for `P1` to find all related content
- Reference in commit messages: `feat(P1): implement semantic search`
- Trace from code back to original problem

---

## 6. Why It Works

### 1. Forced deliberation

You can't fill the Feature column without thinking through the Problem. You can't fill Architecture without defining the Feature. The structure enforces the thinking.

### 2. Separates thinking from summary

Deep pondering happens in supporting files (as much detail as needed). DECISIONS.md stays scannable (one-liners only). You get both depth and overview.

### 3. Shows gaps visually

| ID | Problem | Feature | Arch | GTM | Status |
|----|---------|---------|------|-----|--------|
| P5 | Users want audio | - | - | - | 💡 Idea |

Empty cells immediately show: "This idea hasn't been thought through yet."

### 4. Full traceability

```
Customer complaint
    → DECISIONS.md row (P3)
    → problem.md ## P3 section
    → features.md ## P3 section
    → architecture.md ## P3 section
    → git commits mentioning P3
    → specific code implementing P3
```

No archaeology required.

### 5. Accept/Reject clarity

Ideas don't linger in ambiguous states. They either:
- Get accepted → Progress through statuses → Ship
- Get rejected → Move to Dropped table with documented reason

### 6. Tool-agnostic

Plain markdown. Works in:
- VS Code
- Obsidian
- Notion (paste as markdown)
- GitHub (renders natively)
- Any text editor

No vendor lock-in. No subscription. No learning curve.

### 7. Prevents premature building

The structure makes it awkward to jump to code. You'd have empty cells staring at you. The methodology nudges you toward thinking before building.

### 8. Prioritization built-in

Status column shows what to focus on:
- 💡 Idea → Needs deliberation
- 📋 Planned → Ready to build
- 🔄 In Progress → Currently building (should be 1-3 max)
- ✅ Done → Shipped

### 9. Historical context preserved

Dropped table keeps rejected ideas with reasons. Six months later, when someone asks "why didn't you add user accounts?", the answer is documented.

### 10. Single navigation point

DECISIONS.md tells you **what exists**. Supporting files tell you **why it exists**. You never hunt across disconnected documents.

---

## 7. Where It Fails / Limitations

Product Ledger is not for everyone or every situation. Be honest about its limits.

### 1. Team coordination

No assignment, ownership, dependencies, or handoffs. If you need "P3 blocked by P2, assigned to Alice, reviewed by Bob", use a proper project management tool.

### 2. Complex products (50+ decisions)

The table becomes unwieldy. At scale, you need:
- Filtering/sorting (tool-dependent)
- Hierarchy (epics → features → tasks)
- Views by status, priority, owner

### 3. Design artifacts

Doesn't track mockups, wireframes, prototypes, or user flows. If design is a major part of your workflow, you need Figma or similar alongside this.

### 4. Detailed specifications

Table cells are too small for comprehensive specs. For enterprise features with 50 edge cases, you'll outgrow features.md sections.

### 5. External stakeholder communication

Too terse for investors, clients, or executives. They want polished decks and formal documents, not markdown tables.

### 6. Time tracking

No dates, estimates, deadlines, or velocity. If "when will this ship?" is a constant question, add tooling.

### 7. Multi-product portfolios

Each product needs its own ledger. No rollup view across products. If you're managing 10 products, you need a portfolio layer above this.

### 8. Compliance requirements

Regulated industries need audit trails, approval workflows, and formal sign-offs. Plain markdown won't satisfy SOC2 or FDA requirements.

---

## 8. When to Use vs. When to Skip

### Use Product Ledger when:

| Situation | Why it fits |
|-----------|-------------|
| Solo maker | No coordination overhead needed |
| Team of 2-3 | Simple enough to share via git |
| Products shipping in days/weeks | Lightweight process matches speed |
| <30 active decisions | Table stays manageable |
| Speed over process | Minimal overhead |
| Learning what works | Deliberation helps crystallize thinking |

### Skip Product Ledger when:

| Situation | Why it doesn't fit |
|-----------|-------------------|
| Team >5 people | Need assignments, dependencies |
| Enterprise product | Compliance, formal approvals |
| Multiple stakeholders | Different views needed |
| Time tracking critical | No date/estimate fields |
| Design-heavy product | Can't track visual artifacts |
| Long development cycles (6+ months) | Needs more structure |

### The Decision Heuristic

> If you can hold all active decisions in your head but want them documented, use Product Ledger.
>
> If you can't hold them in your head, you need more tooling.

---

## 9. Workflow: How to Use It

### Adding a New Insight (The Deliberation Flow)

**Step 1: DECISIONS.md (Input)**

Customer says something, you notice a problem, or you have an idea.

```markdown
| P6 | Users forget previous shlokas | - | - | - | 💡 Idea |
```

Add a row with just the Problem column. Status = 💡 Idea.

**Step 2: problem.md**

Create a section and ponder deeply.

```markdown
## P6: Users forget previous shlokas

### Evidence
- Users ask similar questions repeatedly
- No way to revisit past conversations
- WhatsApp doesn't persist message history

### Is this worth solving?
- Frequency: 3/10 test users mentioned this
- Impact: Medium (nice-to-have, not critical)
- Effort: Medium (need storage, user identity)

### Verdict
Worth exploring, but not priority. Backlog.
```

**Step 3: features.md** (if proceeding)

Define what to build.

```markdown
## P6: Saved Shlokas

### Behavior
- User sends "save" → Last shloka saved to their list
- User sends "my shlokas" → See saved list

### Scope
- IN: Save, list, delete
- OUT: Categories, notes, sharing saved lists
```

**Step 4: architecture.md** (if proceeding)

Design the technical approach.

```markdown
## P6: Saved Shlokas

### Storage
- Key-value store: phone_number → [shloka_ids]
- Options: Redis, DynamoDB, or JSON file for MVP

### Tradeoffs
- JSON file: Simple but won't scale
- Redis: Fast but another service to manage
- Decision: JSON file for MVP, migrate if needed
```

**Step 5: gtm.md** (if proceeding)

Plan distribution.

```markdown
## P6: Saved Shlokas

### Positioning
"Your personal Gita collection"

### Discovery
- Mention in help command
- Prompt after sharing a shloka
```

**Step 6: DECISIONS.md (Output)**

Fill the row with one-liners summarizing deliberation.

```markdown
| P6 | Users forget shlokas | Save command | JSON storage | Help prompt | 📋 Planned |
```

Or move to Dropped:

```markdown
## Dropped
| P6 | Users forget shlokas | Low priority, adds complexity |
```

### Daily Workflow

1. **Check DECISIONS.md** for 💡 Ideas → Run through deliberation
2. **Filter by 🔄 In Progress** → Focus on implementation
3. **Look for empty cells** → Incomplete deliberation to address
4. **Review Dropped quarterly** → Mine for patterns or revisit

### When Things Change

1. Update the supporting file first (that's where thinking lives)
2. Then update the one-liner in DECISIONS.md
3. If fundamentally changed, consider new ID (P6a or P7)

---

## 10. Template

Copy-paste this to start a new project.

### DECISIONS.md

```markdown
# [Project Name] - Decisions

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
| P1 | | | | | 💡 Idea |

---

## Backlog

| ID | Problem | Notes |
|----|---------|-------|

---

## Dropped

| ID | Problem | Why Dropped |
|----|---------|-------------|
```

### problem.md

```markdown
# Problem Deliberations

For each problem, document evidence, impact, and whether it's worth solving.

---

## P1: [Problem Title]

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

### features.md

```markdown
# Feature Specifications

For each feature, define behavior, scope, and success criteria.

---

## P1: [Feature Name]

### Behavior
- Input: What does the user provide?
- Process: What happens?
- Output: What does the user receive?

### Scope
- IN: What's included
- OUT: What's explicitly excluded

### Edge cases
| Case | Behavior |
|------|----------|
| | |

### Success criteria
- How will we know this worked?
```

### architecture.md

```markdown
# Architecture Decisions

For each feature, document technical design and tradeoffs.

---

## P1: [Feature Name]

### Components
- What technical pieces are needed?

### Data flow
- How does data move through the system?

### Tradeoffs considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| | | | |

### Dependencies
- External services, libraries, APIs
```

### gtm.md

```markdown
# Go-to-Market Plans

For each feature, document positioning and distribution.

---

## P1: [Feature Name]

### Positioning
- One sentence that captures the value

### Discovery
- How will users find out about this?

### Messaging
- Key points to emphasize
- Terms to avoid

### Success metric
- How will we measure adoption?
```

---

## 11. Real Example: GitaGPT

Applying the methodology to a real product.

### DECISIONS.md

```markdown
# GitaGPT - Decisions

## Status Legend
- 💡 Idea | 📋 Planned | 🔄 In Progress | ✅ Done | ❌ Dropped

---

## Active

| ID | Problem | Feature | Arch | GTM | Status |
|----|---------|---------|------|-----|--------|
| P1 | Users can't find relevant shloka | Semantic search | ChromaDB + Cohere | "Ask any question" | ✅ Done |
| P2 | Users want to browse by mood | Topic menu (7 topics) | curated_topics.json | "Browse by feeling" | ✅ Done |
| P3 | Users forget the bot exists | Daily inspiration | Random from curated | WhatsApp status | ✅ Done |
| P4 | Users want to share wisdom | Share command | wa.me deep links | Viral loop | ✅ Done |
| P5 | Spam and abuse risk | Rate limit + filter | In-memory sessions | - | ✅ Done |
| P6 | Users want deeper explanation | Expand (1/2/3) | Gemini interpretation | - | 🔄 In Progress |

---

## Backlog

| ID | Problem | Notes |
|----|---------|-------|
| P7 | Users want audio | TTS API costs unclear |
| P8 | Users forget to return | Push notifications via Twilio |

---

## Dropped

| ID | Problem | Why Dropped |
|----|---------|-------------|
| P9 | Multi-language support | Overcomplicates; users are Hindi-first |
| P10 | User accounts/login | Overkill; phone number is identity |
| P11 | Web interface | WhatsApp is the interface; web adds maintenance |
```

### problem.md (excerpt)

```markdown
## P1: Users can't find relevant shloka

### Evidence
- 8/10 test users typed chapter numbers (2.47) — they don't know them
- Users described feelings: "I'm anxious", "my son doesn't listen"
- Keyword search failed for emotional, colloquial queries

### Who experiences this?
- Elderly users unfamiliar with Gita structure
- Young users searching by life situation

### Impact if unsolved
- Core value proposition fails
- Users leave after first failed query

### Ideal state
User describes their situation in natural Hindi → Gets 2-3 relevant shlokas
No Gita knowledge required.
```

---

## 12. Anti-Patterns (Common Mistakes)

### 1. Skipping deliberation

**Wrong:** Fill DECISIONS.md directly without writing in supporting files.

**Why it fails:** You skip the thinking. The methodology's value is in the deliberation, not the table. The table is just the summary.

**Fix:** No row gets past 💡 Idea status without corresponding sections in all supporting files.

### 2. Over-documenting in the table

**Wrong:**
```markdown
| P1 | Users struggle to find relevant shlokas because they don't know chapter numbers and keyword search fails for emotional queries in Hindi | ...
```

**Why it fails:** Table becomes unreadable. Cells should be scannable.

**Fix:** 10 words max per cell. Details go in supporting files.

### 3. Skipping the Problem column

**Wrong:** "Let's add a share button" → Jump straight to Feature.

**Why it fails:** No grounding in user need. Building for building's sake.

**Fix:** Every feature must trace to a documented problem.

### 4. Not updating Status

**Wrong:** Features ship but stay as 🔄 In Progress for weeks.

**Why it fails:** Ledger becomes untrustworthy. You stop looking at it.

**Fix:** Update status same day as the change happens.

### 5. Too many "In Progress"

**Wrong:** 8 items marked 🔄 In Progress.

**Why it fails:** Signals lack of focus. Nothing is actually progressing.

**Fix:** Limit to 1-3 items. Finish before starting.

### 6. Never dropping ideas

**Wrong:** Backlog grows to 50 items, never pruned.

**Why it fails:** Backlog becomes a graveyard. Overwhelms decision-making.

**Fix:** Monthly review. Move stale items to Dropped with honest reasons.

### 7. Duplicating content

**Wrong:** Full spec in both features.md AND DECISIONS.md cell.

**Why it fails:** Maintenance burden. They drift out of sync.

**Fix:** Table has one-liners only. Files have details. Never duplicate.

### 8. Making it a Jira replacement

**Wrong:** Add columns for Assignee, Due Date, Story Points, Sprint.

**Why it fails:** It's not a project management tool. Adding these makes it heavy.

**Fix:** Keep the 5 core columns. Use Jira/Linear alongside if needed.

### 9. Forgetting GTM

**Wrong:** Columns filled for Problem, Feature, Arch. GTM stays empty.

**Why it fails:** Features ship without distribution plan. No one discovers them.

**Fix:** GTM is mandatory. Even "mention in help text" is better than empty.

### 10. Not reviewing Dropped

**Wrong:** Ideas go to Dropped and are never seen again.

**Why it fails:** Lose learnings. Might reject the same idea twice. Miss pattern recognition.

**Fix:** Quarterly review of Dropped table.

### 11. Treating it as write-once

**Wrong:** Write DECISIONS.md once at project start, never update.

**Why it fails:** Reality diverges from docs. Documentation becomes fiction.

**Fix:** It's a living system. Update as you learn. Weekly minimum.

---

## 13. Variations and Extensions

The core methodology is intentionally minimal. Extend based on your needs.

### Add a "Metric" column

For data-driven teams, track success criteria.

```markdown
| ID | Problem | Feature | Arch | GTM | Metric | Status |
|----|---------|---------|------|-----|--------|--------|
| P1 | Can't find shloka | Semantic search | ChromaDB | Ask anything | 80% relevant | ✅ Done |
```

### Add a "Date" column

For time-sensitive products, track when decisions were made.

```markdown
| ID | Problem | Feature | Status | Date |
|----|---------|---------|--------|------|
| P1 | ... | ... | ✅ Done | 2024-01-15 |
```

### Link to GitHub issues

Reference implementation work.

```markdown
| ID | Problem | Feature | Status | Issue |
|----|---------|---------|--------|-------|
| P1 | ... | ... | 🔄 In Progress | #42 |
```

### Reference in commit messages

Create traceability to code.

```
git commit -m "feat(P1): implement semantic search with ChromaDB"
git commit -m "fix(P3): daily shloka not randomizing"
```

### Version the ledger

For products with releases, snapshot DECISIONS.md at each version.

```
docs/
├── DECISIONS.md          ← Current
├── DECISIONS-v1.0.md     ← Snapshot at v1.0
└── DECISIONS-v1.1.md     ← Snapshot at v1.1
```

### Add a "Priority" column

For larger backlogs, add priority ranking.

```markdown
| ID | Problem | Feature | Priority | Status |
|----|---------|---------|----------|--------|
| P1 | ... | ... | P0 - Critical | ✅ Done |
| P7 | ... | ... | P2 - Nice to have | 📋 Planned |
```

---

## Summary

Product Ledger is a methodology for solo makers and small teams shipping products fast.

**The core insight:**
> Ideas enter DECISIONS.md raw. They pass through mandatory deliberation in supporting files. They exit as accepted features or documented rejections.

**The files:**
- `DECISIONS.md` — Inbox and verdict (the command center)
- `problem.md` — Why are we building this?
- `features.md` — What are we building?
- `architecture.md` — How are we building it?
- `gtm.md` — How will users find it?

**The workflow:**
1. Add raw idea to DECISIONS.md
2. Deliberate through supporting files
3. Update DECISIONS.md with verdict
4. Implement or archive

**The benefits:**
- Forced thinking before building
- Full traceability from insight to code
- Lightweight enough for fast shipping
- Structured enough for context preservation

Start with the template. Adapt as you learn what works.

---

*Product Ledger is not a formal framework or trademarked methodology. It's a practical system that emerged from shipping small products. Use it, modify it, make it yours.*
