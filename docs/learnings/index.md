# Learnings

Reference pages for programming terms — things I already know how to *use*
but want a precise name and explanation for. Not a dated journal or a
post-mortem log. Split into cross-language foundations and per-language
sections; see [Kotlin](kotlin/index.md) for the page format each section
follows.

Need to look something up fast rather than read a page? See the
[Glossary](glossary.md) for terms, or the [Phrasebook](phrasebook.md) for
the verbs and phrases used to describe what code is doing.

## Sections

| Section | What's in it |
|---|---|
| [General](general/index.md) | Foundational concepts not tied to one language — compiler, generics, type erasure, inlining |
| [Patterns](patterns/index.md) | Recurring design solutions (Builder, Singleton, ...), with Kotlin examples |
| [Kotlin](kotlin/index.md) | Language fundamentals, idioms, standard library — one page per term |
| [Android](android/index.md) | Platform APIs and mechanics — not the language, the framework. Grouped into subject-area subfolders (Components & Lifecycle, App & Task Navigation, State & Process Lifecycle, Runtime & App Startup), each tiered by level like the other sections |

## Levels

Within each section above, pages are grouped by how much you need to
already know to use the term correctly — this is *my* ordering, not a
universal one, and pages move between tiers freely as they turn out
easier or harder than expected.

- **Beginner** — syntax and idioms you reach for from day one, no deep
  mechanism understanding required to use them safely.
- **Intermediate** — needed once you're building real, non-trivial code;
  using them well takes some judgment about *when*, not just *how*.
- **Expert** — using these correctly requires understanding the mechanism
  underneath (compiler behavior, concurrency semantics), not just the
  surface syntax.
- **Pro** — rarely needed day-to-day; mostly relevant when writing
  library/framework code for others, or trading correctness/readability
  for real performance gains.
