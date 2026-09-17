---
name: documentation-page
description: Create a new docs/documentation/*.md page for a topic the user found too hard to cover with just a Q&A entry, and wire it into the nav and glossary. Use when the user asks to write up/document a specific term or concept from Q&A (or anything else) as a real page.
---

# Documentation page

Full rationale lives in `CLAUDE.md` under "`docs/documentation/` — real
write-ups, built on demand" — read it before writing. This section starts
empty on purpose; only write a page when asked, for the topic asked
about, not speculatively.

`args` (if given) names the topic. If none was given, ask which
concept/term to write up before doing anything else.

## Steps

1. Pick a kebab-case filename, e.g. `structured-concurrency.md`. Create
   it at `docs/documentation/<slug>.md`.
2. Write the page — a reasonable default shape, not a rigid template:
   - `# Name` — the term as it actually appears in official docs/talks.
   - A short intro paragraph.
   - `## Example` (optional) — an annotated code block if a snippet
     helps (`// (1)!` markers + a matching numbered list —
     `content.code.annotate` in `mkdocs.yml`, needs
     `pymdownx.superfences`).
   - `## Explanation` — the underlying mechanism, briefly.
   - `## See also` / `## Further reading` (optional) — only if there's
     something worth linking; these two headings automatically mirror
     into the right-hand rail (see `CLAUDE.md`'s "TOC-sidebar mirror").
     One line per bullet for `See also`; one link per bullet for
     `Further reading`.
3. Wire it in:
   - `mkdocs.yml` — add `<Name>: documentation/<slug>.md` under
     `Documentation` in `nav:` (flat list; group only once there are
     enough pages to need it).
   - `docs/reference/glossary.md` — add or update the row for this term,
     linking to the new page from its Meaning cell (append
     `` — [details](../documentation/<slug>.md)``). If the term already
     had a row with no link, add the link now rather than duplicating
     the row.
4. If a Python venv with `mkdocs-material` is available, run `mkdocs
   build` (from the repo root) and check for warnings other than
   expected forward links to pages that genuinely don't exist yet.
