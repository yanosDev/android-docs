# Build & CI/CD

Collapsed by default — try to answer before revealing.

## Build System & Gradle

??? question "What's the difference between Gradle's configuration phase and execution phase?"
    The configuration phase evaluates all build scripts and builds the task graph (runs every build unless configuration caching is used); the execution phase actually runs the tasks that are needed for the requested goal, in dependency order.

    ```kotlin
    // build.gradle.kts
    println("runs during configuration") // every build, unless config cache hits
    tasks.register("hello") {
        doLast { println("runs during execution") } // only if "hello" is actually run
    }
    ```

??? question "What is Gradle's Configuration Cache and how does it speed up builds?"
    It serializes the result of the configuration phase so subsequent builds can skip re-evaluating build scripts entirely (when inputs haven't changed), going straight to task execution.

    ```properties
    # gradle.properties
    org.gradle.configuration-cache=true
    ```

??? question "What's the difference between `implementation` and `api` in a Gradle dependency declaration?"
    `implementation` keeps the dependency internal to the module (not exposed to consumers of that module on their compile classpath); `api` exposes it transitively to anything depending on that module, which can slow builds across a multi-module project since a change ripples further.

    ```kotlin
    dependencies {
        implementation(project(":core"))  // hidden from this module's own consumers
        api(project(":network"))          // exposed transitively to everything downstream
    }
    ```

??? question "What's the difference between `compileOnly` and `implementation`?"
    `compileOnly` is available at compile time but not bundled/available at runtime (e.g., annotation-only libraries); `implementation` is included in both compile and runtime classpaths.

    ```kotlin
    dependencies {
        compileOnly("com.google.auto.value:auto-value-annotations:1.10") // not in the APK
        implementation("com.squareup.retrofit2:retrofit:2.9.0")          // compile + runtime
    }
    ```

??? question "What are build variants and how do flavors combine with build types?"
    A build variant is the cross-product of a build type (e.g., `debug`/`release`) and a product flavor (e.g., `free`/`paid`), letting you generate distinct APKs/behavior (like `paidRelease`) from the same codebase with variant-specific source sets and config.

    ```kotlin
    android {
        buildTypes { getByName("debug") {}; getByName("release") {} }
        flavorDimensions += "tier"
        productFlavors {
            create("free") { dimension = "tier" }
            create("paid") { dimension = "tier" }
        }
        // -> freeDebug, freeRelease, paidDebug, paidRelease
    }
    ```

??? question "What's a practical use case for product flavors?"
    Producing a "free" vs "paid" version of an app with different feature sets, or targeting different backend environments (dev/staging/prod) with different `BuildConfig` values/base URLs per flavor.

    ```kotlin
    productFlavors {
        create("free") { applicationIdSuffix = ".free" }
        create("paid") { buildConfigField("Boolean", "ADS_ENABLED", "false") }
    }
    ```

??? question "What's the difference between a `BuildConfig` field and a resource value (`res/values`) for environment-specific config?"
    `BuildConfig` fields are compile-time Java/Kotlin constants generated per variant (type-safe, e.g., `Boolean`/`String`), accessible in code; resource values are XML-defined and can be swapped per flavor via resource overlay, more suited for values also needed by XML layouts/manifest placeholders.

    ```kotlin
    buildConfigField("String", "BASE_URL", "\"https://staging.example.com\"")
    // vs: res/values-staging/strings.xml -> <string name="base_url">...</string>
    ```

??? question "What is R8, and how does it differ from the older ProGuard?"
    R8 is Google's replacement for ProGuard, combining shrinking, obfuscation, and (unlike ProGuard) optimization *and* the dexing step (Java bytecode -> DEX) all in a single tool, making release builds faster and smaller than the separate ProGuard+dx pipeline.

    ```kotlin
    android {
        buildTypes {
            release {
                isMinifyEnabled = true // R8: shrink + obfuscate + optimize + dex, one pass
            }
        }
    }
    ```

??? question "What issues can R8/ProGuard introduce if misconfigured?"
    Removing or renaming classes/members that are only referenced via reflection (e.g., Gson model classes, WebView JS interfaces) causes runtime crashes since the shrinker doesn't see those "hidden" usages — requiring explicit `-keep` rules.

    ```text
    -keep class com.example.model.** { *; } # needed for reflection-based Gson models
    ```

??? question "Why do reflection-based libraries often ship their own default ProGuard/R8 'consumer rules'?"
    So that any app depending on the library automatically inherits the necessary `-keep` rules for that library's reflective usage, without every consuming app having to know and write those rules manually.

    ```text
    # bundled inside the library's own .aar as consumer-rules.pro
    -keep class com.example.lib.Model { *; }
    ```

??? question "What's the difference between an APK and an AAB (Android App Bundle)?"
    An APK is a single installable package built for all device configurations bundled together; an AAB is a publishing format containing all variants' resources, from which Google Play generates and serves optimized, smaller split APKs tailored to each user's specific device (architecture, screen density, language).

    ```text
    app-release.apk  # one file, every device config bundled together
    app-release.aab  # Play generates per-device split APKs from this
    ```

??? question "Why does Google Play prefer/require AAB for new apps?"
    It significantly reduces download/install size for users (only relevant splits are delivered) and enables Play Feature Delivery (on-demand/conditional feature modules) which isn't possible with a single monolithic APK.

    ```kotlin
    android {
        bundle {
            language { enableSplit = true }
            density { enableSplit = true }
        }
    }
    ```

??? question "What are Gradle Version Catalogs (`libs.versions.toml`) and their benefit?"
    A centralized TOML file defining dependency versions/aliases once, referenced type-safely (`libs.retrofit`) across all modules' build files, avoiding version drift/duplication and enabling IDE autocomplete for dependency references.

    ```toml
    # gradle/libs.versions.toml
    [versions]
    retrofit = "2.9.0"
    [libraries]
    retrofit = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
    ```

??? question "How would you diagnose a sudden increase in build time after a dependency update?"
    Use `--profile` or the Gradle Build Scan to identify which tasks got slower, check if annotation processing (KSP/kapt) time increased, verify configuration cache/build cache are still being hit, and check for newly introduced `api`-scoped dependencies causing wider recompilation.

    ```text
    ./gradlew build --profile   # local HTML report under build/reports/profile
    ./gradlew build --scan      # uploaded, shareable Build Scan
    ```

??? question "What's the difference between `kapt` and KSP (Kotlin Symbol Processing)?"
    `kapt` generates a Java stub of Kotlin code for annotation processors originally built for Java, adding significant overhead; KSP processes Kotlin symbols natively without stub generation, making it considerably faster for compatible processors (e.g., Room, Moshi codegen).

    ```kotlin
    plugins {
        id("com.google.devtools.ksp") version "1.9.20-1.0.14"
    }
    dependencies {
        ksp("androidx.room:room-compiler:2.6.1") // instead of kapt(...)
    }
    ```

??? question "What's the difference between the Gradle build cache (local/remote) and the Configuration Cache?"
    Configuration Cache skips re-running configuration scripts entirely when unchanged; the build/task cache reuses *task outputs* from previous runs (local or a shared remote cache) when task inputs match, even across different machines/CI runs — they solve different, complementary parts of build speed.

    ```properties
    org.gradle.caching=true             # task output cache
    org.gradle.configuration-cache=true # configuration-phase cache
    ```

??? question "How would you set up a multi-module app to reduce build times?"
    Split the app into feature modules with minimal `api`-scoped inter-module dependencies (prefer `implementation`), so a change in one module doesn't force recompilation of unrelated modules, combined with parallel Gradle execution and build/configuration caching.

    ```kotlin
    dependencies {
        implementation(project(":feature-search")) // not `api` — don't leak to further consumers
    }
    ```

??? question "How do you handle signing configs securely in CI/CD without leaking secrets?"
    Store the keystore file and passwords as encrypted CI secrets/environment variables (never committed to source control), inject them into `signingConfigs` via environment variables or a gitignored local `keystore.properties` file read at build time.

    ```kotlin
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "keystore.properties")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
        }
    }
    ```

??? question "What's the difference between a debug and release signing key, and why can't you switch a published app's signing key later without special handling?"
    The signing key's certificate fingerprint is tied to the app's identity on the Play Store and for update verification; changing it breaks update compatibility for existing users unless using Play App Signing's key rotation/upgrade mechanism, since Android verifies updates come from the same signer.

    ```text
    # a new signing cert on an update -> Android rejects it as "not the same app"
    # unless Play App Signing's key-upgrade flow is used
    ```

??? question "What is Play App Signing and why does Google recommend it?"
    Google manages/holds the app signing key itself (you keep only an upload key to sign what you submit); this protects against permanent loss of the signing key and allows Google to facilitate secure key rotation/upgrades if needed.

    ```text
    Upload key      -> you use it to sign the AAB you submit to Play
    App signing key -> Google holds it, re-signs the artifact for actual distribution
    ```

## CI/CD & Tooling

??? question "What's a typical Android CI pipeline stage sequence?"
    Lint/static analysis -> unit tests -> build (debug/release variants) -> instrumented tests (emulator/device farm) -> artifact signing -> distribution (internal testing track/Play Store) -> optionally, automated screenshot/performance regression checks.

    ```text
    lint -> unit tests -> build -> instrumented tests -> sign -> distribute -> perf checks
    ```

??? question "What's the difference between running instrumented tests on an emulator in CI vs a real device farm (e.g., Firebase Test Lab)?"
    Emulators in CI are cheaper/faster to provision but may not catch device-specific bugs (OEM skins, hardware quirks); device farms test against real hardware variety, catching real-world fragmentation issues at higher cost/time.

    ```text
    CI emulator        -> cheap, fast, may miss OEM-specific bugs
    Firebase Test Lab   -> real hardware, catches real fragmentation, slower/costlier
    ```

??? question "What is Fastlane commonly used for in Android CI/CD?"
    Automating repetitive release tasks — version bumping, changelog generation, building signed artifacts, and uploading to Play Store tracks (internal/alpha/beta/production) — via scriptable "lanes."

    ```ruby
    # fastlane/Fastfile
    lane :beta do
      gradle(task: "bundleRelease")
      upload_to_play_store(track: "beta")
    end
    ```

??? question "What's the difference between Detekt/ktlint and Android Lint?"
    Detekt/ktlint focus on Kotlin code style/complexity static analysis (formatting, code smells); Android Lint focuses on Android-specific issues (resource misuse, API level compatibility, accessibility, performance anti-patterns) tied to the Android SDK/build system.

    ```kotlin
    // detekt.yml flags e.g. long methods, magic numbers — pure Kotlin style/complexity
    // Android Lint flags e.g. missing contentDescription, deprecated SDK APIs
    ```

??? question "How would you set up automated performance regression detection in CI?"
    Run Macrobenchmark tests on a consistent device/emulator profile on each CI build, store historical results, and fail/flag the build if key metrics (startup time, frame timing) regress beyond a defined threshold.

    ```kotlin
    @Test
    fun startupBenchmark() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 5
    ) { startActivityAndWait() }
    ```

??? question "What's the difference between a 'feature flag' and a 'build flavor' for controlling feature rollout?"
    A build flavor bakes the choice into the compiled artifact at build time (can't change post-release without a new build); a feature flag/remote config toggles behavior at runtime without a new release, enabling gradual rollout, A/B testing, and kill-switches.

    ```kotlin
    if (remoteConfig.getBoolean("new_checkout_enabled")) showNewCheckout() // flag: runtime
    // vs productFlavors { create("newCheckout") { } }                     // flavor: build-time
    ```

??? question "How would you design a feature flag system for gradual rollout?"
    A remote config service (e.g., Firebase Remote Config) delivering flag values keyed by user segment/percentage rollout, fetched on app start/periodically with a safe default value bundled in the app for offline/first-launch scenarios.

    ```kotlin
    val enabled = remoteConfig.getBoolean("feature_x")
        .takeIf { remoteConfig.info.lastFetchStatus == FetchStatus.SUCCESS }
        ?: DEFAULT_BUNDLED_IN_APP
    ```

??? question "What's a risk of shipping a feature permanently behind a flag that's never cleaned up?"
    Accumulating dead code paths and combinatorial complexity in testing (every flag combination is a potential state), increasing maintenance burden and bug surface over time — flags should be removed once a rollout decision is finalized.

    ```kotlin
    if (flags.useOldCheckout) legacyCheckout() else newCheckout()
    // two years later: is the "old" path still tested? still maintained? still needed?
    ```

## Gradle Composite Builds, Source Sets & R8 Full Mode

??? question "What is a Gradle composite build (`includeBuild`), and how does it differ from a standard multi-module project?"
    It lets you include an entirely separate Gradle build (potentially with its own settings.gradle) as if it were a dependency, substituting its published artifacts with local project builds for faster iteration — useful for developing a library alongside a consuming app without publishing intermediate versions.

    ```kotlin
    // settings.gradle.kts
    includeBuild("../my-library") // substitutes the published artifact with this local build
    ```

??? question "How do Gradle source sets map to build variants, and what's the folder structure convention?"
    Each variant (e.g., `debug`, `paidRelease`) can have a corresponding source set folder (`src/debug/`, `src/paidRelease/`) whose code/resources are merged with `src/main/` only for builds matching that variant, letting you override or add variant-specific files without conditional code.

    ```text
    src/main/kotlin/        # always included
    src/debug/kotlin/       # merged in only for debug builds
    src/paidRelease/kotlin/ # merged in only for the paidRelease variant
    ```

??? question "What's the difference between R8's default ('compatibility') mode and 'full mode'?"
    Compatibility mode preserves some behaviors compatible with legacy ProGuard assumptions (e.g., certain class/member removal restrictions) for safety during migration; full mode is more aggressive about optimization/shrinking, catching more dead code but requiring more careful `-keep` rules for reflection-based usage that compatibility mode might have tolerated by default.

    ```properties
    # gradle.properties
    android.enableR8.fullMode=true
    ```

??? question "What is a Gradle Build Scan, and what kind of build performance insight does it provide beyond local `--profile` output?"
    An uploaded, shareable, detailed report of a specific build's timeline, task execution, dependency resolution, and configuration — useful for diagnosing CI-specific performance issues or sharing a reproducible performance investigation with teammates, beyond a local-only profile report.

    ```text
    ./gradlew build --scan
    # -> uploaded, shareable report: task timeline, dependency resolution, config time
    ```

??? question "What's the difference between a Bill of Materials (BOM) dependency (e.g., Compose BOM) and pinning each library version individually?"
    A BOM declares one version reference that aligns compatible versions of an entire family of related libraries automatically, avoiding the need to manually track/update each individual artifact's version and reducing the risk of incompatible version combinations within that family.

    ```kotlin
    dependencies {
        implementation(platform("androidx.compose:compose-bom:2024.02.00"))
        implementation("androidx.compose.ui:ui")               // version from the BOM
        implementation("androidx.compose.material3:material3") // version from the BOM
    }
    ```

??? question "Why might a large app choose to publish some internal modules as actual Maven artifacts (even privately) instead of just Gradle project modules?"
    To enable independent versioning/release cadence for that module (e.g., a shared design system consumed by multiple separate apps/repos), and to speed up consumer builds by using a prebuilt binary artifact rather than recompiling the module's source from scratch every time.

    ```kotlin
    dependencies {
        implementation("com.example:design-system:3.1.0") // prebuilt, own release cadence
    }
    ```
