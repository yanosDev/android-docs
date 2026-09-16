# android-docs

Personal MkDocs (Material theme) site for Kotlin/Android reference notes.
Built with `mkdocs-material==9.5.*` (see `requirements.txt`); served locally
via `docker-compose up` (mounts the repo, runs `mkdocs serve`).

The theme has `toc.integrate` enabled, so each page's table of contents
appears in the **left** nav, nested under that page's own entry, below the
rest of the page list. There's still a **right-hand rail**, but it's custom
and independent of the TOC: `hooks.py` extracts each page's `## See also`
and `## Further reading` sections and `overrides/main.html` renders them
there as plain nav links (title only, descriptions dropped) — see
"TOC-sidebar mirror" below. The in-body copies stay in the normal reading
flow and are hidden via CSS once the rail has room to show them instead.

`Docs > Language` no longer exists — it used to hold a `Kotlin` stub and a
`Coroutines & Flow` stub; both were migrated into `docs/learnings/kotlin/`
once that section's page pattern was established. If a term feels like it
"should" be a language-fundamentals topic, it almost certainly belongs
under `docs/learnings/<language>/`, not a new `Docs` subsection.

## `docs/learnings/` — term reference

`Learnings` is **not** a dated journal or post-mortem log — that's what the
section name might suggest, but it isn't the intent here. It's reference
pages for programming terms, each covering one named concept the user
already knows how to *use* but wants a precise name and explanation for.
`docs/learnings/index.md` lists the sections below; each section's own
`index.md` lists its pages. Two standalone lookup pages sit alongside the
sections, at the top level of `nav:` (not inside any section): `glossary.md`
(nouns — terms and their meanings) and `phrasebook.md` (verbs — the words
for describing what code is *doing*, e.g. "propagate", "shadow",
"dispatch"). Both are curated free-standing references, not derived
mechanically from the term pages — update `glossary.md` whenever a new
term page is added (mandatory, see below), but only add to
`phrasebook.md` when a genuinely new, distinct verb/phrase comes up
worth having a precise word for.

Three kinds of section, side by side:

- `docs/learnings/general/` — cross-language concepts: not tied to one
  language (e.g. compiler, generics, type erasure, inlining, higher-order
  functions). A term goes here if it means roughly the same thing in
  Java, C++, Kotlin, etc.
- `docs/learnings/patterns/` — recurring design solutions (Builder,
  Singleton, ...): also cross-language, but about *design*, not language
  mechanics — written with idiomatic Kotlin examples, noting where a
  Kotlin language feature already solves the problem better than the
  classic pattern (see `docs/learnings/patterns/builder.md`, which points
  at named/default arguments as the idiomatic-Kotlin alternative).
- `docs/learnings/<language>/` (e.g. `kotlin/`) — one folder per language,
  for that language's own keywords/idioms (e.g. Kotlin's `reified` — no
  other mainstream language has that exact keyword).

A concept can be dual: Kotlin's `inline` keyword is a specific language
mechanism, but "function inlining" is also a general compiler technique —
in that case, write the general mechanism on the `general/` page and the
language-specific keyword semantics on the language's own page, and
cross-link both ways (see `docs/learnings/general/inline.md` and
`docs/learnings/kotlin/inline-reified.md` for the pattern). When in doubt,
ask which side a term belongs on rather than guessing.

### The page pattern

New pages must follow this shape (see
`docs/learnings/kotlin/scope-functions.md` for a full language-specific
example, `docs/learnings/general/type-erasure.md` for a general one). Keep
the whole page tight — the goal is branding a term in memory, not a
tutorial:

1. `# Name` — the term as it actually appears in official docs/talks.
2. A short intro paragraph — what it is, in a few sentences.
3. `## Example` — one annotated code block using numbered markers
   (`// (1)!`), followed immediately by a matching numbered markdown list
   (mkdocs-material's built-in code annotation feature —
   `content.code.annotate` in `mkdocs.yml`, needs `pymdownx.superfences`;
   don't reinvent it with plain comments). On a `general/` page the
   snippet just needs to illustrate the concept — Kotlin is the default
   choice since it's what's on hand, but the section is optional if the
   concept genuinely isn't about a runnable snippet.
4. Optional `## Cheat sheet` — a compact table, when the concept has a
   handful of variants worth comparing at a glance.
5. Optional `## Comparison` — a compact table contrasting this against
   other languages/libraries/manual approaches, when there's a real
   alternative worth contrasting (e.g. coroutines vs. threads/callbacks;
   `Flow` vs. RxJava/`Sequence`). Columns are the approaches, rows are the
   dimensions that actually differ (cost, cancellation, readability) —
   not a place for prose.
6. `## Explanation` — the underlying mechanism, in a couple of sentences at
   most. This is not the place for a full write-up or style advice — one or
   two facts worth remembering, then stop.
7. `## Advantages / Disadvantages` — a compact two-column table (not
   bullet essays), **only for a page about a design choice with real
   alternatives** (a class modifier, a declaration style, a pattern).
   Skip it for pure mechanics with no alternative to weigh (e.g. what a
   compiler is).
8. `## When to use it` — two or three concrete scenarios, same condition
   as above; often just one line each.
9. `## See also` — bullet list linking to related pages in this section.
   **One line per bullet, name or a short inline-code snippet only** — e.g.
   `` - [Null safety](null-safety.md) — `?.let { }` `` — never a
   descriptive clause or sentence. Forward links to a page that doesn't
   exist yet are fine (mkdocs just warns at build time until it's written).
10. `## Further reading` — bullet list of external links, one link per
    bullet.

Every section (`general/`, `patterns/`, `<language>/`) groups its own
pages by level — Beginner/Intermediate/Expert/Pro — both in `nav:` and in
that section's own `index.md`. See `docs/learnings/index.md#levels` for
what distinguishes each tier; picking one is a judgment call the same way
glossary grouping is — make the call rather than skipping it. There is no
separate "by level" section elsewhere; the level grouping lives inside
each topic section, not as a redirect layer on top of it.

After writing a page:

- Add it to the matching level's table in that section's `index.md` (e.g.
  under `## Intermediate` in `docs/learnings/kotlin/index.md`; move it out
  of "Still to write" if it was listed there; add a `## <Tier>` heading if
  that section doesn't have one yet).
- Add it to `nav:` in `mkdocs.yml` under `Learnings > General >
  <Tier>`, `Learnings > Patterns > <Tier>`, or `Learnings > <Language> >
  <Tier>` — nested one level deeper than the section itself, not as a
  flat list directly under the section.
- Add each term the page covers as a row in `docs/learnings/glossary.md`
  (one row per keyword/term, even if several share one page — see how
  `let`/`run`/`with`/`apply`/`also` each get their own row pointing at the
  same "Scope Functions" page). Put the row under the matching `##` group
  ("General concepts", or "`<Language>` — `<topic>`"), adding a new group
  if none fits. The glossary itself stays grouped by topic, not by level.

Headings do **not** get a `¶` permalink icon (`toc.permalink: false` in
`mkdocs.yml`) — that was turned off deliberately.

## `docs/qa/` — Q&A self-check (distinct from `Learnings`)

A separate top-level section, unrelated to the `Learnings` page pattern
above: one page per broad topic (`kotlin.md`, `compose.md`,
`coroutines-concurrency.md`, etc. — 17 pages, listed in `docs/qa/index.md`),
each a flat run of interview-style questions grouped under `##` headings
matching its source topics. Every question is a collapsed admonition:

```markdown
??? question "The question text"
    The answer, indented 4 spaces.
```

This is mkdocs-material's own `question` admonition type via
`pymdownx.details` (already enabled) — no extra config needed, and it's
unrelated to the `## See also`/`## Further reading` TOC-sidebar mirror
mechanism below (that only fires on those two specific headings).
Numbering isn't used, so there's no sequence to keep consistent — each
`???` block is independent.

Unlike `Learnings`, this content was bulk-imported from a single source
document (an interview-prep Q&A file) rather than hand-curated one term
at a time, and it is **not** wired into the glossary or phrasebook — it's
a separate, coarser-grained resource for self-testing breadth, not a
precise-terminology reference. Don't try to reconcile or merge the two;
they serve different purposes. If more Q&A content is added later, follow
the same topic-grouping and collapsed-admonition shape, and add new pages
to both `docs/qa/index.md`'s table and `nav:` under `Q&A`.

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
