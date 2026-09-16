---
name: general-concept-page
description: Create a new docs/learnings/general/*.md reference page for a cross-language programming concept (compiler, generics, type erasure, inlining, etc.), following this repo's established page pattern, and wire it into the nav and hub pages. Use when the user asks to add/write a page for a general CS/programming term that isn't specific to one language.
---

# General concept page

Full pattern and rationale live in `CLAUDE.md` under "`docs/learnings/` —
term reference" — read it before writing, especially the "general vs.
language-specific" classification rule.

`args` (if given) name the topic, e.g. `Polymorphism` or `Garbage
Collection`. If no topic was given, ask which concept to write up.

Before writing anything, check the classification: does this term mean
roughly the same thing across languages (general), or is it a specific
keyword/mechanism of one language (belongs under
`docs/learnings/<language>/` instead — use the `kotlin-page` skill for
Kotlin)? If it's genuinely dual (a general technique that one language
also exposes as a specific keyword, like inlining/`inline`), write the
general mechanism here and the language-specific keyword semantics on the
language's own page, and cross-link both ways — see
`docs/learnings/general/inline.md` /
`docs/learnings/kotlin/inline-reified.md` for the pattern.

## Steps

1. Pick a kebab-case filename, e.g. `polymorphism.md`. Create it at
   `docs/learnings/general/<slug>.md`.
2. Write the page in this shape (see `docs/learnings/general/type-erasure.md`
   as the reference example):
   - `# <Name>` — the term as it actually appears in standard references
     (Wikipedia, language docs), not an invented label.
   - A short intro paragraph: what it is, in a few sentences, without
     tying it to one language.
   - `## Example` (optional) — a short annotated code snippet if one
     helps ground the concept. Kotlin is the default choice since it's
     what's on hand; skip this section if the concept isn't really about
     a runnable snippet.
   - `## Comparison` (optional) — a compact table contrasting this
     against other languages/libraries/manual approaches, when there's a
     real alternative worth contrasting (e.g. `Flow` vs. RxJava vs.
     `Sequence`). Columns are the approaches, rows the dimensions that
     actually differ.
   - `## Explanation` — the underlying mechanism, a couple of sentences at
     most.
   - `## See also` — bullet list, **one line per bullet, name or a short
     inline-code snippet only**, never a descriptive sentence. Link other
     `general/` pages directly (`other-concept.md`) and any relevant
     language-specific page via `../<language>/slug.md`.
   - `## Further reading` — bullet list of external links, one link per
     bullet. A Wikipedia article is usually the right anchor for the pure
     general concept; add a language doc link too if directly relevant.
3. Pick a level — Beginner/Intermediate/Expert/Pro (see
   `docs/learnings/index.md#levels`) — then wire the new page in:
   - `docs/learnings/general/index.md` — add a row to that level's table
     (add a `## <Tier>` heading if none exists yet).
   - `mkdocs.yml` — add `<Name>: learnings/general/<slug>.md` under
     `Learnings > General > <Tier>` in `nav:` (one level deeper than
     `General` itself — there's no separate top-level "by level" section).
   - Any language-specific page that already discusses this concept in
     passing — add a one-line `## See also` cross-link back to it (see
     how `docs/learnings/kotlin/inline-reified.md` links to
     `../general/type-erasure.md`).
   - `docs/learnings/glossary.md` — add a row under `## General concepts`
     (the glossary stays grouped by topic, not by level).
4. If a Python venv with `mkdocs-material` is available, run `mkdocs build`
   (from the repo root) and check for warnings other than expected forward
   links to pages that genuinely don't exist yet.
