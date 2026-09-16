---
name: kotlin-page
description: Create a new docs/learnings/kotlin/*.md reference page for a Kotlin concept, following this repo's established page pattern, and wire it into the nav and hub pages. Use when the user asks to add/write a new Kotlin topic page (e.g. "add a page for delegation", "write up generics & variance").
---

# Kotlin reference page

Full pattern and rationale live in `CLAUDE.md` under "`docs/learnings/` —
per-language term reference" — read it before writing. This skill is the
step-by-step for producing one page from that pattern.

`args` (if given) name the topic, e.g. `Delegation` or `Generics & Variance`.
If no topic was given, ask which concept to write up before doing anything
else — don't guess from the "Still to write" list without confirming.

## Steps

1. Pick a kebab-case filename from the topic name, e.g. `delegation.md`,
   `generics-variance.md`. Create it at `docs/learnings/kotlin/<slug>.md`.
2. Write the page in this exact shape (see
   `docs/learnings/kotlin/scope-functions.md` as the reference example):
   - `# <Name>` — the term as it actually appears in official docs/talks,
     not an invented label.
   - A short intro paragraph: what it is, in a few sentences.
   - `## Example` — one Kotlin code block with `// (1)!`-style annotation
     markers, immediately followed by a numbered markdown list explaining
     each marker. Keep the snippet minimal — it exists to be annotated, not
     to be a complete program.
   - `## Cheat sheet` (optional) — only if the concept has several variants
     worth comparing in a table.
   - `## Comparison` (optional) — a compact table contrasting this against
     other languages/libraries/manual approaches, when a real alternative
     exists (e.g. coroutines vs. threads/callbacks; `Flow` vs. RxJava).
     Columns are the approaches, rows the dimensions that actually differ.
   - `## Explanation` — the underlying mechanism, a couple of sentences at
     most — one or two facts worth remembering, not a write-up. Link
     sibling pages inline with normal markdown links (`[text](slug.md)`)
     where they clarify something.
   - `## Advantages / Disadvantages` (a compact two-column table) and
     `## When to use it` (two or three one-line scenarios) — only for a
     page about a design choice with real alternatives (a class modifier,
     a declaration style). Skip both for pure mechanics with no
     alternative to weigh.
   - `## See also` — bullet list of related pages in
     `docs/learnings/kotlin/`, **one line per bullet, name or a short
     inline-code snippet only** (e.g.
     `` - [Null safety](null-safety.md) — `?.let { }` ``) — never a
     descriptive clause or sentence. Links to pages that don't exist yet
     are fine (expect a build warning until they're written).
   - `## Further reading` — bullet list of external links, **one link per
     bullet**. A build hook mirrors both sections into the right-hand rail
     (see `CLAUDE.md`'s "TOC-sidebar mirror" section) by flattening each
     `<li>` to its `<a>`(s) — a bullet with several links still renders
     fine in the body but loses its grouping text once mirrored.
3. Wire the new page in:
   - `docs/learnings/kotlin/index.md` — add a row to the `## Pages` table
     (and remove the corresponding line from `## Still to write` if it was
     listed there).
   - `mkdocs.yml` — add `<Name>: learnings/kotlin/<slug>.md` under
     `Learnings > Kotlin` in `nav:`.
   - `docs/learnings/glossary.md` — add one row per keyword/term the page
     covers (several rows can point at the same page, e.g. `let`/`run`/
     `with`/`apply`/`also` all point at "Scope Functions") under a
     `## Kotlin — <topic>` group, adding a new group if none fits.
   - `docs/learnings/by-level.md` — add the page (once, not once per term)
     under Beginner/Intermediate/Expert/Pro.
4. If a Python venv with `mkdocs-material` is available, run `mkdocs build`
   (from the repo root) and check for warnings other than expected forward
   links to pages that genuinely don't exist yet.
