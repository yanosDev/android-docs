# Build & CI/CD

Collapsed by default — try to answer before revealing.

## Build System & Gradle

??? question "What's the difference between Gradle's configuration phase and execution phase?"
    The configuration phase evaluates all build scripts and builds the task graph (runs every build unless configuration caching is used); the execution phase actually runs the tasks that are needed for the requested goal, in dependency order.

??? question "What is Gradle's Configuration Cache and how does it speed up builds?"
    It serializes the result of the configuration phase so subsequent builds can skip re-evaluating build scripts entirely (when inputs haven't changed), going straight to task execution.

??? question "What's the difference between `implementation` and `api` in a Gradle dependency declaration?"
    `implementation` keeps the dependency internal to the module (not exposed to consumers of that module on their compile classpath); `api` exposes it transitively to anything depending on that module, which can slow builds across a multi-module project since a change ripples further.

??? question "What's the difference between `compileOnly` and `implementation`?"
    `compileOnly` is available at compile time but not bundled/available at runtime (e.g., annotation-only libraries); `implementation` is included in both compile and runtime classpaths.

??? question "What are build variants and how do flavors combine with build types?"
    A build variant is the cross-product of a build type (e.g., `debug`/`release`) and a product flavor (e.g., `free`/`paid`), letting you generate distinct APKs/behavior (like `paidRelease`) from the same codebase with variant-specific source sets and config.

??? question "What's a practical use case for product flavors?"
    Producing a "free" vs "paid" version of an app with different feature sets, or targeting different backend environments (dev/staging/prod) with different `BuildConfig` values/base URLs per flavor.

??? question "What's the difference between a `BuildConfig` field and a resource value (`res/values`) for environment-specific config?"
    `BuildConfig` fields are compile-time Java/Kotlin constants generated per variant (type-safe, e.g., `Boolean`/`String`), accessible in code; resource values are XML-defined and can be swapped per flavor via resource overlay, more suited for values also needed by XML layouts/manifest placeholders.

??? question "What is R8, and how does it differ from the older ProGuard?"
    R8 is Google's replacement for ProGuard, combining shrinking, obfuscation, and (unlike ProGuard) optimization *and* the dexing step (Java bytecode -> DEX) all in a single tool, making release builds faster and smaller than the separate ProGuard+dx pipeline.

??? question "What issues can R8/ProGuard introduce if misconfigured?"
    Removing or renaming classes/members that are only referenced via reflection (e.g., Gson model classes, WebView JS interfaces) causes runtime crashes since the shrinker doesn't see those "hidden" usages — requiring explicit `-keep` rules.

??? question "Why do reflection-based libraries often ship their own default ProGuard/R8 'consumer rules'?"
    So that any app depending on the library automatically inherits the necessary `-keep` rules for that library's reflective usage, without every consuming app having to know and write those rules manually.

??? question "What's the difference between an APK and an AAB (Android App Bundle)?"
    An APK is a single installable package built for all device configurations bundled together; an AAB is a publishing format containing all variants' resources, from which Google Play generates and serves optimized, smaller split APKs tailored to each user's specific device (architecture, screen density, language).

??? question "Why does Google Play prefer/require AAB for new apps?"
    It significantly reduces download/install size for users (only relevant splits are delivered) and enables Play Feature Delivery (on-demand/conditional feature modules) which isn't possible with a single monolithic APK.

??? question "What are Gradle Version Catalogs (`libs.versions.toml`) and their benefit?"
    A centralized TOML file defining dependency versions/aliases once, referenced type-safely (`libs.retrofit`) across all modules' build files, avoiding version drift/duplication and enabling IDE autocomplete for dependency references.

??? question "How would you diagnose a sudden increase in build time after a dependency update?"
    Use `--profile` or the Gradle Build Scan to identify which tasks got slower, check if annotation processing (KSP/kapt) time increased, verify configuration cache/build cache are still being hit, and check for newly introduced `api`-scoped dependencies causing wider recompilation.

??? question "What's the difference between `kapt` and KSP (Kotlin Symbol Processing)?"
    `kapt` generates a Java stub of Kotlin code for annotation processors originally built for Java, adding significant overhead; KSP processes Kotlin symbols natively without stub generation, making it considerably faster for compatible processors (e.g., Room, Moshi codegen).

??? question "What's the difference between the Gradle build cache (local/remote) and the Configuration Cache?"
    Configuration Cache skips re-running configuration scripts entirely when unchanged; the build/task cache reuses *task outputs* from previous runs (local or a shared remote cache) when task inputs match, even across different machines/CI runs — they solve different, complementary parts of build speed.

??? question "How would you set up a multi-module app to reduce build times?"
    Split the app into feature modules with minimal `api`-scoped inter-module dependencies (prefer `implementation`), so a change in one module doesn't force recompilation of unrelated modules, combined with parallel Gradle execution and build/configuration caching.

??? question "How do you handle signing configs securely in CI/CD without leaking secrets?"
    Store the keystore file and passwords as encrypted CI secrets/environment variables (never committed to source control), inject them into `signingConfigs` via environment variables or a gitignored local `keystore.properties` file read at build time.

??? question "What's the difference between a debug and release signing key, and why can't you switch a published app's signing key later without special handling?"
    The signing key's certificate fingerprint is tied to the app's identity on the Play Store and for update verification; changing it breaks update compatibility for existing users unless using Play App Signing's key rotation/upgrade mechanism, since Android verifies updates come from the same signer.

??? question "What is Play App Signing and why does Google recommend it?"
    Google manages/holds the app signing key itself (you keep only an upload key to sign what you submit); this protects against permanent loss of the signing key and allows Google to facilitate secure key rotation/upgrades if needed.

## CI/CD & Tooling

??? question "What's a typical Android CI pipeline stage sequence?"
    Lint/static analysis -> unit tests -> build (debug/release variants) -> instrumented tests (emulator/device farm) -> artifact signing -> distribution (internal testing track/Play Store) -> optionally, automated screenshot/performance regression checks.

??? question "What's the difference between running instrumented tests on an emulator in CI vs a real device farm (e.g., Firebase Test Lab)?"
    Emulators in CI are cheaper/faster to provision but may not catch device-specific bugs (OEM skins, hardware quirks); device farms test against real hardware variety, catching real-world fragmentation issues at higher cost/time.

??? question "What is Fastlane commonly used for in Android CI/CD?"
    Automating repetitive release tasks — version bumping, changelog generation, building signed artifacts, and uploading to Play Store tracks (internal/alpha/beta/production) — via scriptable "lanes."

??? question "What's the difference between Detekt/ktlint and Android Lint?"
    Detekt/ktlint focus on Kotlin code style/complexity static analysis (formatting, code smells); Android Lint focuses on Android-specific issues (resource misuse, API level compatibility, accessibility, performance anti-patterns) tied to the Android SDK/build system.

??? question "How would you set up automated performance regression detection in CI?"
    Run Macrobenchmark tests on a consistent device/emulator profile on each CI build, store historical results, and fail/flag the build if key metrics (startup time, frame timing) regress beyond a defined threshold.

??? question "What's the difference between a 'feature flag' and a 'build flavor' for controlling feature rollout?"
    A build flavor bakes the choice into the compiled artifact at build time (can't change post-release without a new build); a feature flag/remote config toggles behavior at runtime without a new release, enabling gradual rollout, A/B testing, and kill-switches.

??? question "How would you design a feature flag system for gradual rollout?"
    A remote config service (e.g., Firebase Remote Config) delivering flag values keyed by user segment/percentage rollout, fetched on app start/periodically with a safe default value bundled in the app for offline/first-launch scenarios.

??? question "What's a risk of shipping a feature permanently behind a flag that's never cleaned up?"
    Accumulating dead code paths and combinatorial complexity in testing (every flag combination is a potential state), increasing maintenance burden and bug surface over time — flags should be removed once a rollout decision is finalized.

## Gradle Composite Builds, Source Sets & R8 Full Mode

??? question "What is a Gradle composite build (`includeBuild`), and how does it differ from a standard multi-module project?"
    It lets you include an entirely separate Gradle build (potentially with its own settings.gradle) as if it were a dependency, substituting its published artifacts with local project builds for faster iteration — useful for developing a library alongside a consuming app without publishing intermediate versions.

??? question "How do Gradle source sets map to build variants, and what's the folder structure convention?"
    Each variant (e.g., `debug`, `paidRelease`) can have a corresponding source set folder (`src/debug/`, `src/paidRelease/`) whose code/resources are merged with `src/main/` only for builds matching that variant, letting you override or add variant-specific files without conditional code.

??? question "What's the difference between R8's default ('compatibility') mode and 'full mode'?"
    Compatibility mode preserves some behaviors compatible with legacy ProGuard assumptions (e.g., certain class/member removal restrictions) for safety during migration; full mode is more aggressive about optimization/shrinking, catching more dead code but requiring more careful `-keep` rules for reflection-based usage that compatibility mode might have tolerated by default.

??? question "What is a Gradle Build Scan, and what kind of build performance insight does it provide beyond local `--profile` output?"
    An uploaded, shareable, detailed report of a specific build's timeline, task execution, dependency resolution, and configuration — useful for diagnosing CI-specific performance issues or sharing a reproducible performance investigation with teammates, beyond a local-only profile report.

??? question "What's the difference between a Bill of Materials (BOM) dependency (e.g., Compose BOM) and pinning each library version individually?"
    A BOM declares one version reference that aligns compatible versions of an entire family of related libraries automatically, avoiding the need to manually track/update each individual artifact's version and reducing the risk of incompatible version combinations within that family.

??? question "Why might a large app choose to publish some internal modules as actual Maven artifacts (even privately) instead of just Gradle project modules?"
    To enable independent versioning/release cadence for that module (e.g., a shared design system consumed by multiple separate apps/repos), and to speed up consumer builds by using a prebuilt binary artifact rather than recompiling the module's source from scratch every time.
