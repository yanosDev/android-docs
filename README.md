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

```text
docs/
├── index.md                  # Landing page / table of contents
├── kotlin/                   # Language fundamentals, idioms
├── coroutines-flow/          # Coroutines, Flow, structured concurrency
├── android/                  # Android framework, architecture, lifecycle
├── jetpack-compose/          # Compose UI, state, navigation
├── material/                 # Material Design 3 components & theming
├── gradle/                   # Build system, version catalogs, plugins
├── jitpack/                  # Publishing & consuming libraries via JitPack
├── retrofit/                 # Networking, Retrofit, OkHttp, serialization
└── dependency-injection/     # Hilt, Koin, manual DI
```

Add a new page by dropping a `.md` file into the relevant folder and listing
it under `nav:` in `mkdocs.yml`.
