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
├── readings/                 # Notes/takeaways on articles, talks, books
├── ideas/                    # Backlog of project ideas & experiments
├── learnings/                # Dated TIL-style entries, lessons learned
└── stylesheets/extra.css     # Black/orange theme tweaks on top of mkdocs-material
```

Add a new page by dropping a `.md` file into the relevant folder and listing
it under `nav:` in `mkdocs.yml`.
