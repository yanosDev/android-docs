# Android & Kotlin Notes

Personal knowledge base covering Kotlin, Android, Jetpack Compose, Material
Design, Gradle, JitPack, Retrofit, dependency injection, and related topics.
Built with [MkDocs](https://www.mkdocs.org/) and the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

## Running locally

### With Docker (recommended)

```bash
docker compose up --build
```

Then open <http://localhost:8000>. Editing any file under `docs/` triggers
live-reload in the browser.

### Without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

## Project structure

The top nav has 4 sections: **Docs**, **Readings**, **Ideas**, **Learnings**.

```text
docs/
├── index.md                  # Landing page / table of contents (not a tab, reached via the logo)
├── kotlin/                   # Docs > Language > Kotlin
├── coroutines-flow/          # Docs > Language > Coroutines & Flow
├── android/                  # Docs > Architecture > Android
├── dependency-injection/     # Docs > Architecture > Dependency Injection
├── jetpack-compose/          # Docs > UI > Jetpack Compose
├── material/                 # Docs > UI > Material Design
├── gradle/                   # Docs > Build & Publish > Gradle
├── jitpack/                  # Docs > Build & Publish > JitPack
├── retrofit/                 # Docs > Networking > Retrofit
├── readings/                  # Notes/takeaways on articles, talks, books
│   ├── do-this/               # Practices worth adopting
│   ├── dont-do-this/          # Anti-patterns to avoid
│   ├── investigate/           # Flagged for deeper digging
│   ├── tasks-for-me/          # Action items triggered by a reading
│   ├── why-dont-we-do-this/   # Gaps vs. current practice, worth questioning
│   ├── keep-this-note/        # Quotes/snippets worth keeping
│   └── needs-more-attention/  # Didn't click yet, needs another pass
├── ideas/                    # Backlog of project ideas & experiments
├── learnings/                # Dated TIL-style entries, lessons learned
└── stylesheets/extra.css     # Black/orange theme tweaks on top of mkdocs-material
```

Add a new page by dropping a `.md` file into the relevant folder and listing
it under `nav:` in `mkdocs.yml`.

## Comments (giscus)

Every page gets a threaded comment/reply box at the bottom by default, backed
by [giscus](https://giscus.app) → GitHub Discussions on this (now **public**)
repo. To turn comments **off** on a specific page, add this to the top of
its `.md` file:

```markdown
---
comments: false
---
```

Styling: the widget uses a custom theme
(`docs/stylesheets/giscus-theme.css`) recolored to match the site's black +
orange palette, loaded via jsDelivr and swapped for a plain light theme when
you toggle to light mode. jsDelivr caches `@main` URLs for a while, so a
change to that file may take a few minutes to show up — see
<https://www.jsdelivr.com/tools/purge> if you need it sooner.

### One-time GitHub setup (already done)

1. Repo → **Settings → General → Features** → enable **Discussions**.
2. Repo → **Discussions** tab → create a category named `Comments` with
   format **Announcement** (so only you can start a new discussion thread —
   giscus creates one automatically per page on the first comment; anyone
   can still reply to existing ones).
3. Install the [giscus GitHub App](https://github.com/apps/giscus), scoped to
   this repo only.
4. Repo → **Settings → General → Danger Zone** → changed visibility to
   **public** (giscus can only read Discussions on public repos).
5. Generated the embed config at <https://giscus.app> (repo
   `yanosDev/android-docs`, **pathname** mapping, `Comments` category) and
   pasted the resulting `data-repo-id` / `data-category-id` into
   `overrides/main.html`.

### Managing threads on GitHub

giscus is just a comment/reply widget — thread management (resolving,
locking, sorting) happens on github.com, in the repo's **Discussions** tab,
not through the widget or any mkdocs setting:

- **Mark as resolved:** open the discussion (its title matches the page's
  URL path), use **Close discussion** at the bottom (or the `···` menu) and
  pick a reason — *Resolved*, *Outdated*, or *Duplicate*. Closed discussions
  are hidden from the default "Open" filter in the Discussions tab.
- **Archive / stop new replies:** use **Lock conversation** (`···` menu) on
  top of closing it — this prevents anyone (including you) from adding more
  comments to that thread. There's no per-comment archive, only per-thread.
- **Sort order:** GitHub Discussions (and giscus, which mirrors them) always
  show comments oldest-first, chronologically. There's no "newest first"
  option — that ordering is a platform limitation, not something
  configurable from the mkdocs side. Individual **replies** within a
  top-level comment are threaded/nested underneath it, though.
