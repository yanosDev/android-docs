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

Pages with `comments: true` in their front matter get a threaded
comment/reply box at the bottom, backed by
[giscus](https://giscus.app) → GitHub Discussions on this repo. Because the
repo is **private**, only accounts with read access to it (you, plus anyone
you add as a collaborator) can view or post comments — this is effectively a
personal annotation layer, not public commenting.

It's currently enabled on `readings/`, `ideas/`, and `learnings/`. To enable
it on any other page, add this to the top of the `.md` file:

```markdown
---
comments: true
---
```

### One-time GitHub setup

1. Repo → **Settings → General → Features** → enable **Discussions**.
2. Repo → **Discussions** tab → create a category named `Comments` with
   format **Announcement** (so only you can start a new discussion thread —
   giscus creates one automatically per page on the first comment; visitors
   with access can still reply to existing ones).
3. Install the [giscus GitHub App](https://github.com/apps/giscus) and grant
   it access to this repo only.
4. Go to <https://giscus.app>, enter `yanosDev/android-docs` as the
   repository, choose **pathname** as the page ↔ discussion mapping, pick the
   `Comments` category, and copy the `data-repo-id` and `data-category-id`
   values it shows you (the repo being private just means giscus will note
   that comments won't be publicly visible — that's expected here).
5. Open `overrides/main.html` and replace `GISCUS_REPO_ID` and
   `GISCUS_CATEGORY_ID` with those two values.
6. Rebuild (`docker compose up --build`) and open a page with
   `comments: true` — the comment box should appear at the bottom, themed to
   match whichever light/dark mode is active.
