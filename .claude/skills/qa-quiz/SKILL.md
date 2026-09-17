---
name: qa-quiz
description: Run a live, interactive quiz using the Q&A bank in docs/qa/ (721 questions across 17 Android/Kotlin topics) — ask one question at a time in the conversation, wait for the user's own answer, then grade it against the reference answer with specific feedback. Use when the user asks for a survey/quiz/test/mock-interview/pop quiz from the Q&A section, e.g. "give me a small survey", "quiz me on Compose", "mid survey on coroutines", "test me, high difficulty... er I mean a big one".
---

# Q&A quiz

This is a **live conversational skill** — run it yourself in the current
turn and keep going back and forth with the user across the following
turns. Do not delegate this to a subagent or fork; a subagent can't have
the live, one-question-at-a-time exchange this needs.

## 1. Parse the request

- **Size** → question count. Words map loosely, use judgment for
  variants/typos: "small"/"short"/"quick" → 5, "medium"/"mid" → 10,
  "large"/"high"/"big"/"long" → 20. If the user gives an explicit number,
  use that instead. No size mentioned at all → default to 10.
- **Topic** (optional) → match against the 17 pages listed in
  `docs/qa/index.md` (Kotlin, Coroutines & Concurrency, Android Core &
  Internals, Compose, Views & RecyclerView, Architecture & Design
  Patterns, Dependency Injection, Testing, Networking, Persistence,
  Performance & Rendering, Security & Privacy, Build & CI/CD, System APIs
  & Hardware, System Design, Release & Ops Practices, Kotlin Multiplatform
  & Misc). No topic given, or "random"/"mixed" → pull from any/all pages.
- If the request is ambiguous about size or topic, just pick a reasonable
  default (10, mixed) rather than asking — this should feel low-friction.

## 2. Build the question pool

1. Read the target `docs/qa/<file>.md` page(s) for the matched topic(s)
   (all 17 if mixed/random).
2. Each question is one `??? question "..."` block — the quoted title is
   the question, the indented body directly under it is the reference
   answer.
3. Pick N distinct questions at random from the pool (no repeats within
   one round). If the pool has fewer than N questions, use the whole pool
   and say so up front.
4. Do not reveal any reference answers yet, and don't list the questions
   or topics up front — that turns it into a reading exercise instead of
   a test.

## 3. Run the round

- Ask exactly one question per message, plainly, no extra preamble.
- Wait for the user's answer before doing anything else.
- Grade it against the reference answer: say clearly whether it's
  correct, partially correct (name what's missing), or off (name what's
  wrong) — actually compare their claim to the reference's key point(s),
  don't just paste the reference verbatim back at them.
- Also grade *how* it was said, not just whether it was right. The user
  wants to sound professional — precise technical terms, not vague/casual
  paraphrases. If an answer is correct in substance but phrased loosely
  (e.g. "the thing that watches for changes" instead of naming the actual
  mechanism, or reversing which of two similarly-behaving things does
  what), call that out too and give the precise term/phrasing they should
  use instead — even when the content was already right. This applies on
  every question, not just wrong ones.
- If they say they don't know, or ask to skip, reveal the reference
  answer plainly and move on. Count it as missed, not "wrong," in tone.
- Keep a running tally silently; mention it briefly between questions
  only if it fits naturally, without making the score the focus.
- Then ask the next question. Repeat until N questions are done.

## Side questions during a round

If the user interrupts a round to ask a definitional/clarifying question
about a term instead of answering ("what is X", "explain Y") — answer it
directly and in full, every time this happens.

Then check whether that term already has a `??? question` entry
somewhere in `docs/qa/*.md` (grep across all 17 files, not just the
current topic's). If it's missing, add one to whichever existing page
fits topically, following the exact shape already used there: a `???
question "..."` title, the answer indented 4 spaces, and a short
illustrative code example (2-8 lines, plain comments, no `// (1)!`
annotation markers) unless the topic genuinely has none (rare — see
CLAUDE.md). Don't touch `docs/qa/index.md`'s table or `nav:` for this —
those only need updating when a whole new *page* is added, not a new
question on an existing page.

This is a side effect of the conversation, not part of the quiz itself —
don't count it as a question asked/answered toward the round's total, and
resume the round afterward from where it left off.

## 4. Wrap up

Give a short summary: the score (e.g. "7/10"), and — more usefully —
which specific questions or sub-topics they missed or were shaky on, so
they know what to go re-read. Don't just restate the score.
