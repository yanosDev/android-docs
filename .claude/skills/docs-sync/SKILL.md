---
name: docs-sync
description: Audit docs/documentation/ for pages missing a Glossary entry (and candidate Phrasebook entries), and for pages missing from mkdocs.yml nav — then fix what's found. Use when the user asks to "sync the glossary", "check for missing glossary entries", "tidy up the docs", or after any manual edits to docs/documentation/ that didn't go through the documentation-page skill.
---

# Docs sync

This is a verification/repair pass, not a content-writing task — it exists
because `docs/reference/glossary.md` and `nav:` in `mkdocs.yml` are
maintained by hand alongside every page, and hand-maintained things drift,
especially when a page was added by editing files directly rather than
through the `documentation-page` skill.

## Steps

1. List every `*.md` file under `docs/documentation/`, excluding
   `index.md`. Each one is a page that should be accounted for. If the
   directory only has `index.md` (the "empty by design" placeholder),
   there's nothing to sync — say so and stop.
2. For each page, check `docs/reference/glossary.md` for a row whose
   Meaning cell links to it (`](../documentation/<slug>.md)`-style
   relative path). A page covering multiple distinct keywords should have
   one row per keyword, not just one.
3. For each page found missing a linked glossary row, add or update the
   row now — see `CLAUDE.md`'s `docs/documentation/` section for the
   exact mechanics (append `` — [details](../documentation/<slug>.md)``
   to the Meaning cell).
4. Separately, check whether each page also appears somewhere in
   `mkdocs.yml`'s `nav:` tree under `Documentation` — a page that exists
   on disk but isn't in `nav:` is unreachable in the built site even
   though `mkdocs build` won't warn about it. Add any missing entries.
5. While you're at it, skim `docs/reference/phrasebook.md` for any
   genuinely new, distinct verb/phrase introduced by pages added since
   the last sync (not every page introduces one — most won't) and add it
   if so, following the existing category grouping there.
6. Do **not** touch `docs/qa/*.md` — the Q&A section is explicitly not
   wired into the glossary/phrasebook (see `CLAUDE.md`).
7. Rebuild (`mkdocs build` with whatever venv/Docker setup is available)
   and confirm no new warnings, then report what was found and fixed —
   including "nothing was out of sync" as a valid, expected outcome.
