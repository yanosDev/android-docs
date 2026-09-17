# android-docs

Personal MkDocs (Material theme) site for Kotlin/Android reference notes.
Built with `mkdocs-material==9.5.*` (see `requirements.txt`); served locally
via `docker-compose up` (mounts the repo, runs `mkdocs serve`).

Top-level `nav:` tabs, in order: `Readings`, `Ideas`, `Reference`, `Q&A`,
`Documentation`. There is no `Learnings` section anymore — it held ~50
hand-built term-reference pages (Kotlin, Android, general CS concepts,
design patterns), and was deleted because `Q&A` already covers that ground
well enough as a starting point. The current model: `Q&A` is where
learning happens day to day; `Documentation` starts empty and only grows
when a specific Q&A topic turns out to need more than a question and
answer — the user brings it up, and it gets written together at that
point. Don't pre-build pages into `Documentation` speculatively or in
bulk; only write one when asked, for the topic asked about.

## Glossary & Phrasebook are self-contained — no pages to link to

`docs/reference/glossary.md` (nouns) and `docs/reference/phrasebook.md`
(verbs) are quick-lookup tables with an inline one-line meaning per row —
they don't depend on `Documentation` pages existing. Most terms in the
glossary have no page in `Documentation` and may never get one; that's
expected, not a gap to fill.

If a term later gets a real page under `docs/documentation/`, link it from
that row's Meaning cell in the glossary (append something like
`` — [details](../documentation/slug.md) ``) — do this when the page is
written, not before.

The theme has `toc.integrate` enabled, so each page's table of contents
appears in the **left** nav, nested under that page's own entry, below the
rest of the page list. There's still a **right-hand rail**, but it's custom
and independent of the TOC: `hooks.py` extracts each page's `## See also`
and `## Further reading` sections and `overrides/main.html` renders them
there as plain nav links (title only, descriptions dropped) — see
"TOC-sidebar mirror" below. The in-body copies stay in the normal reading
flow and are hidden via CSS once the rail has room to show them instead.
This mechanism is generic (keys off heading text, not off any particular
section) — any page anywhere, including future `Documentation` pages, can
use it by adding those two headings.

## `docs/reference/` — Glossary & Phrasebook's home tab

A thin top-level section: `reference/index.md` (landing page),
`reference/glossary.md`, `reference/phrasebook.md`. All three live
together under `docs/reference/` — no cross-directory relative links to
worry about.

## `docs/documentation/` — real write-ups, built on demand

Starts as just `documentation/index.md` explaining the "empty by design,
grows when Q&A isn't enough" model above. When the user asks to write one
up:

1. Pick a kebab-case filename, create `docs/documentation/<slug>.md`.
2. A reasonable default shape (adapt as the topic calls for it — there's
   no rigid template to follow here, unlike the old `Learnings` pattern):
   - `# Name` — the term/concept as it actually appears in official
     docs/talks.
   - A short intro paragraph.
   - `## Example` (optional) — an annotated code block if a snippet helps
     (`// (1)!` markers + a matching numbered list — mkdocs-material's
     `content.code.annotate`, needs `pymdownx.superfences`).
   - `## Explanation` — the underlying mechanism, briefly.
   - `## See also` / `## Further reading` (optional) — only add these
     headings if there's something worth linking; they automatically
     mirror into the right-hand rail (see above). **One line per bullet,
     name or a short inline-code snippet only** for `See also`; **one
     link per bullet** for `Further reading` (a bullet with several links
     still renders, but each link loses its surrounding text once
     mirrored).
3. Add it to `mkdocs.yml`'s `nav:` under `Documentation` (flat list is
   fine until there's enough to need grouping).
4. Add a row to `docs/reference/glossary.md` for the term(s) it covers,
   linking to the new page (see above) — do this even if the term already
   had a glossary row with no link.
5. If a Python venv with `mkdocs-material` is available, run `mkdocs
   build` and check for warnings other than expected forward links to
   pages that genuinely don't exist yet.

Headings do **not** get a `¶` permalink icon (`toc.permalink: false` in
`mkdocs.yml`) — that was turned off deliberately.

## `docs/qa/` — Q&A self-check

One page per broad topic (`kotlin.md`, `compose.md`,
`coroutines-concurrency.md`, etc. — 17 pages, listed in `docs/qa/index.md`),
each a flat run of interview-style questions grouped under `##` headings
matching its source topics. Every question is a collapsed admonition,
answer plus a short illustrative code example:

```markdown
??? question "The question text"
    The answer, indented 4 spaces.

    ```kotlin
    // a short illustrative snippet — 2-8 lines, plain comments, no
    // `// (1)!` annotation markers (that's the Documentation-page
    // mechanism, not this one)
    ```
```

All 721 questions across all 17 files have this shape as of now (a small
number — under 20 — legitimately have no code example because the
question is about reading an IDE tool/dashboard, not an API; that's fine,
don't force one). This is mkdocs-material's own `question` admonition type
via `pymdownx.details` (already enabled) — no extra config needed, and
it's unrelated to the `## See also`/`## Further reading` TOC-sidebar
mirror mechanism above (that only fires on those two specific headings).
Numbering isn't used, so there's no sequence to keep consistent — each
`???` block is independent.

This content was bulk-imported from a single source document
(an interview-prep Q&A file) rather than hand-curated one term at a time,
and it is **not** wired into the glossary or phrasebook — it's a separate,
coarser-grained resource for self-testing breadth, not a precise-terminology
reference. If more Q&A content is added later, follow the same
topic-grouping, collapsed-admonition, and example shape, and add new pages
to both `docs/qa/index.md`'s table and `nav:` under `Q&A`.

Plain question-title text, no links out to `Documentation` — a topic only
gets that kind of cross-link once (if ever) a real page for it exists;
don't add speculative links to pages that don't exist yet.

The `qa-quiz` skill (`.claude/skills/qa-quiz/SKILL.md`) runs a live,
conversational quiz sampled from these pages on request (e.g. "give me a
small survey", "quiz me on Compose") — one question at a time, graded
against the reference answer, not just flipped open.

### TOC-sidebar mirror (`hooks.py` + `overrides/main.html`)

`hooks.py`'s `on_page_content` hook locates `## See also` / `## Further
reading` by the ids mkdocs' `toc` extension slugifies from that literal
heading text (`id="see-also"`, `id="further-reading"`) — renaming a heading
breaks the mirror silently (the section just stops appearing on the right;
the build still succeeds). It also flattens each `<li>` down to its `<a>`
tag(s), dropping any trailing text — this is why "Further reading" wants
one link per bullet: a bullet with several links still works, but each
link becomes its own unlabeled item on the right, losing the text around
it. `overrides/main.html` overrides the theme's `site_nav` block to append
this rail after `{{ super() }}`'s normal (left) sidebar output.
