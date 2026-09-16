---
name: pattern-page
description: Create a new docs/learnings/patterns/*.md page for a software design pattern (Builder, Singleton, Factory, Observer, etc.), following this repo's established page pattern, and wire it into the nav and hub pages. Use when the user asks to add/write a page for a design pattern.
---

# Design pattern page

Full pattern and rationale live in `CLAUDE.md` under "`docs/learnings/` —
term reference" — read it before writing.

`args` (if given) name the pattern, e.g. `Singleton` or `Observer`. If none
was given, ask which pattern to write up before guessing from "Still to
write" in `docs/learnings/patterns/index.md`.

Before writing, check whether Kotlin already has a built-in feature that
covers (or replaces) this pattern — e.g. `docs/learnings/kotlin/object-declarations.md`
already *is* the Singleton pattern, and `docs/learnings/kotlin/companion-objects.md`
covers most Factory use cases. If so, say so explicitly in the page (see
`docs/learnings/patterns/builder.md`'s "When to use it", which points at
named/default arguments as the idiomatic-Kotlin alternative) rather than
just presenting the classic GoF version uncritically.

## Steps

1. Pick a kebab-case filename, e.g. `singleton.md`, `observer.md`. Create
   it at `docs/learnings/patterns/<slug>.md`.
2. Write the page in this shape (see `docs/learnings/patterns/builder.md`
   as the reference example):
   - `# <Name> Pattern` — the name as it's known in standard references
     (Wikipedia, the GoF book).
   - A short intro paragraph: what problem it solves, in a few sentences.
   - `## Example` — an annotated Kotlin code block (`// (1)!` markers +
     matching numbered list) showing the pattern, ideally in a Kotlin-idiomatic
     form rather than a literal Java-style transliteration.
   - `## Advantages / Disadvantages` — a compact two-column table.
   - `## When to use it` — a couple of concrete scenarios, and — if
     relevant — the idiomatic-Kotlin alternative that makes the classic
     pattern unnecessary.
   - `## See also` — bullet list, **one line per bullet, name or a short
     inline-code snippet only**. Cross-link the Kotlin feature that
     overlaps with this pattern, if any.
   - `## Further reading` — bullet list of external links, one link per
     bullet (a Wikipedia article is usually the right anchor).
3. Wire the new page in:
   - `docs/learnings/patterns/index.md` — add a row to the `## Pages`
     table (remove it from "Still to write" if listed there).
   - `mkdocs.yml` — add `<Name>: learnings/patterns/<slug>.md` under
     `Learnings > Patterns` in `nav:`.
   - `docs/learnings/glossary.md` — add a row under `## Design patterns`.
   - `docs/learnings/by-level.md` — add the page under Beginner/
     Intermediate/Expert/Pro.
4. If a Python venv with `mkdocs-material` is available, run `mkdocs build`
   (from the repo root) and check for warnings other than expected forward
   links to pages that genuinely don't exist yet.
