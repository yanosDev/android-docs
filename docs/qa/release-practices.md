# Release & Ops Practices

Collapsed by default — try to answer before revealing.

## Version Control, Code Review & Team Practices

??? question "What's the difference between Git Flow and trunk-based development, and which tends to fit CI/CD-heavy mobile teams better?"
    Git Flow uses long-lived `develop`/`feature`/`release` branches with formal merge points; trunk-based development keeps a single mainline with short-lived feature branches merged frequently behind feature flags — trunk-based tends to fit teams practicing frequent CI/CD releases better since it avoids large, risky merge events.

    ```bash
    git checkout -b feature/x develop   # Git Flow
    git checkout -b feature/x main      # trunk-based — short-lived, merged behind a flag
    ```

??? question "What's the difference between a rebase and a merge when integrating a feature branch, and what's a tradeoff of rebasing shared branches?"
    Merge preserves the branch's actual commit history with a merge commit; rebase rewrites the feature branch's commits to appear as if made on top of the latest mainline, producing a cleaner linear history but rewriting commit hashes — rebasing a branch already pushed/shared with others requires force-pushing and can cause confusing history conflicts for collaborators.

    ```bash
    git merge feature/x   # keeps a merge commit, preserves real history
    git rebase main       # replays commits on top of main, rewrites hashes
    ```

??? question "Why is squash-merging commonly preferred for feature branches in a PR-based workflow?"
    It collapses potentially messy in-progress commits into a single clean commit on the mainline, making `git log`/`git bisect` easier to follow, at the cost of losing the granular intermediate commit history if that detail is ever needed.

    ```bash
    git merge --squash feature/x
    git commit -m "Add search filter"
    ```

??? question "What makes a PR description genuinely useful for a senior-level reviewer versus a junior one?"
    Beyond describing *what* changed, it should explain *why* (the problem/tradeoffs considered), call out risk areas or things specifically needing careful review, and note what testing was done — helping the reviewer focus attention where it matters most rather than re-deriving context from the diff alone.

    ```markdown
    ## What & why
    ## Risk areas to review closely
    ## Testing done
    ```

??? question "What's a key difference in reviewing a PR touching a shared/core module versus an isolated feature module?"
    Changes to shared/core code have a wider blast radius (potentially affecting many consumers), warranting extra scrutiny for backward compatibility, API stability, and broader test coverage, whereas an isolated feature module's changes are more contained and lower-risk to review in isolation.

    ```
    core-network/ change -> check every module with implementation(project(":core-network"))
    ```

??? question "What is a 'living style guide'/design system module, and why does it matter for design-engineering collaboration at scale?"
    A shared module containing reusable, documented UI components (colors, typography, buttons) that both design and engineering treat as the single source of truth, reducing inconsistency and duplicated one-off UI implementations across feature teams.

    ```kotlin
    // :core-designsystem module
    @Composable fun AppButton(text: String, onClick: () -> Unit) { /* single source of truth */ }
    ```

??? question "What's the value of writing a lightweight ADR (architecture decision record) even for a 'small' technical decision?"
    It captures the reasoning and alternatives considered at the time, preventing future contributors (or your future self) from re-debating a settled decision without the original context, or accidentally reverting it without understanding why it was made that way.

    ```markdown
    # ADR-004: Use MVI over MVVM for the checkout feature
    Status: Accepted
    Context: ...
    Decision: ...
    Consequences: ...
    ```

## Play Console, Vitals & Release Management Deep Dive

??? question "What's the difference between 'bad behavior' thresholds and 'poor excessive resource usage' thresholds in Android Vitals?"
    Bad behavior thresholds (crash rate, ANR rate, excessive wakeups) reflect broken/crashing behavior and can affect Play Store visibility if exceeded; excessive resource usage (like stuck wakelocks, background location/battery usage) reflects inefficiency that harms user experience/battery life even without literal crashes, and is also monitored/surfaced to developers and potentially users.

??? question "What is the Play Console's 'Data safety' section, and why does inaccurate disclosure carry real risk?"
    A declaration of what data the app collects/shares and why, shown to users on the store listing; misrepresenting it (even unintentionally, e.g., missing a third-party SDK's data collection) can lead to policy violations, app removal, or loss of user trust if discovered.

??? question "What's a sound versioning strategy for `versionCode` across multiple build flavors (e.g., free/paid) submitted as separate Play listings?"
    Encode enough information (e.g., flavor digit + incrementing build number) into `versionCode` to guarantee strictly increasing, unique values per listing over the app's lifetime, since Play requires each new upload's versionCode to be strictly greater than any previously published one for that listing.

    ```kotlin
    // build.gradle.kts
    versionCode = flavorDigit * 1_000_000 + buildNumber // strictly increasing per listing
    ```

??? question "What's the difference between the in-app review API and directing users to leave a review via a Play Store link/Intent?"
    The in-app review API shows the native rating dialog directly within the app's flow without leaving it, subject to Google's own quota/frequency limits (you can request it, but the system decides whether to actually show it); manually linking out to the Play Store listing always works but is more disruptive and has a much higher drop-off rate.

    ```kotlin
    val manager = ReviewManagerFactory.create(context)
    manager.requestReviewFlow().addOnCompleteListener { manager.launchReviewFlow(activity, it.result) }
    ```

??? question "What is a staged rollout's typical risk-mitigation value, concretely, if a critical bug ships?"
    Limiting exposure to a small percentage of users initially means a critical bug affects far fewer people before it's caught via crash/vitals monitoring and the rollout is halted, compared to releasing to 100% of users immediately.

??? question "What's the difference between 'pre-launch report' testing on Play Console and your own manual/CI device testing?"
    Pre-launch reports run automated crawlers/tests (including accessibility and security scans) across a range of real Google-hosted devices before publishing, catching device-specific issues you might not have covered in your own test matrix, complementing rather than replacing your own testing.

## Billing, Analytics, Crash Reporting & Debugging Tools

??? question "What's the difference between a consumable and non-consumable product in Google Play Billing?"
    A consumable product (e.g., in-game currency) can be purchased repeatedly after being 'consumed' via the Billing API; a non-consumable product (e.g., 'remove ads') is purchased once and remains permanently owned by the user's account.

    ```kotlin
    billingClient.consumeAsync(consumeParams) { _, _ -> } // consumable: re-purchasable after this
    ```

??? question "What's the difference between a one-time product and a subscription in Play Billing, regarding entitlement checking?"
    One-time products are checked via a simple owned/not-owned purchase record; subscriptions require checking active status considering renewal, grace periods, and cancellation state, since entitlement can lapse or be in a grace/account-hold period rather than being a permanent binary flag.

    ```kotlin
    val isEntitled = purchase.purchaseState == Purchase.PurchaseState.PURCHASED &&
        subscriptionIsCurrentlyActive(purchase) // subscriptions need an ongoing status check
    ```

??? question "Why must purchase verification for Play Billing be done server-side for security-sensitive entitlements?"
    Client-side purchase tokens can be spoofed/tampered with on a compromised device; verifying the purchase token against Google's server-to-server API from your own backend ensures the entitlement is genuinely valid before unlocking sensitive content.

    ```
    # backend calls: androidpublisher.purchases.products.get(packageName, productId, token)
    ```

??? question "What's the difference between Firebase Crashlytics' fatal crash reports and non-fatal exception logging?"
    Fatal crashes are uncaught exceptions that terminated the app process, automatically captured; non-fatal logging (`Crashlytics.recordException()`) lets you report handled exceptions/recoverable errors for visibility without them having crashed the app, useful for tracking silent failures.

    ```kotlin
    try {
        riskyCall()
    } catch (e: Exception) {
        FirebaseCrashlytics.getInstance().recordException(e) // non-fatal, app keeps running
    }
    ```

??? question "Why is it important to attach breadcrumbs/custom keys to crash reports rather than relying solely on the stack trace?"
    A stack trace alone often lacks the app state context (which screen, what user action, what data) needed to reproduce/understand a crash; custom keys and logged breadcrumbs (Crashlytics `setCustomKey`/`log`) preserve that context alongside the crash.

    ```kotlin
    FirebaseCrashlytics.getInstance().setCustomKey("screen", "checkout")
    FirebaseCrashlytics.getInstance().log("User tapped Pay")
    ```

??? question "What's the difference between event-based analytics (e.g., Firebase Analytics) and a session-replay tool for understanding user behavior?"
    Event-based analytics aggregates discrete named events (e.g., 'button_clicked') for statistical funnels/trends; session replay tools capture a more complete reconstruction of an individual user's screen interactions, useful for qualitative debugging of specific user confusion but with more sensitive privacy implications.

    ```kotlin
    firebaseAnalytics.logEvent("button_clicked", bundleOf("button" to "checkout"))
    ```

??? question "What's the difference between `adb logcat` filtering by tag versus by priority level?"
    Filtering by tag (`adb logcat MyTag:V *:S`) isolates logs from a specific source regardless of severity; filtering by priority (`adb logcat *:E`) shows only logs at or above a severity threshold (e.g., errors) regardless of source — often combined for targeted debugging.

    ```bash
    adb logcat MyTag:V *:S   # only MyTag, any level
    adb logcat *:E           # errors and above, any tag
    ```

??? question "What is `adb shell dumpsys` used for, and give an example of useful information it exposes."
    It dumps diagnostic state from system services; e.g., `dumpsys activity` shows the current Activity stack/task state, `dumpsys meminfo <package>` shows detailed memory usage breakdown for a specific app process.

    ```bash
    adb shell dumpsys activity
    adb shell dumpsys meminfo com.example.app
    ```

??? question "What's the difference between using the Layout Inspector's live inspection versus a static screenshot-based approach for debugging UI issues?"
    Live inspection lets you click into the running app's actual view/composable tree, inspect real property values and recomposition counts in real time; a static screenshot only shows visual appearance without access to the underlying hierarchy/state data.

??? question "What is a ProGuard/R8 mapping file, and why must you keep it for every release build?"
    It maps obfuscated (renamed) class/method names back to their original source names; without archiving the mapping file per version, crash stack traces from obfuscated release builds (e.g., in Crashlytics) are unreadable, since symbol names are stripped/renamed.

    ```
    app/build/outputs/mapping/release/mapping.txt  # archive this per version
    ```

??? question "What's the difference between symbolicating native (NDK) crash stack traces and Java/Kotlin crash stack traces?"
    Native crashes require the debug symbols (`.so` files with symbols, or a separate symbol file) matching the exact build to resolve addresses back to function names; Java/Kotlin crashes use the R8 mapping file for deobfuscation instead, a completely separate toolchain/process.

    ```
    native: match the .so + symbols file to the exact build
    JVM:    use build/outputs/mapping/release/mapping.txt
    ```

## Billing Testing, Distribution Channels & Crash Grouping

??? question "What is Play Billing's 'license testing' mechanism, and why is it needed before a real production release?"
    It lets designated test accounts make real-looking purchase flows through Play Billing without being charged, verifying the full purchase/acknowledge/entitlement flow works correctly against the actual Play Billing Library before real money is involved.

    ```
    # Play Console > Setup > License testing > add test account emails
    ```

??? question "What's the difference between Firebase App Distribution and the Play Console's internal testing track for pre-release builds?"
    Firebase App Distribution lets you distribute builds (including ones never intended for Play, like early prototypes or CI builds) directly to testers via email/link without going through Play's review pipeline at all; the Play internal testing track distributes through the actual Play Store infrastructure, closer to production behavior (Play Billing, staged rollout mechanics) but requires each build to pass basic Play upload processing.

    ```bash
    ./gradlew appDistributionUploadRelease  # Firebase — no Play review pipeline at all
    ```

??? question "How do crash reporting tools (e.g., Crashlytics) group similar crashes together into a single 'issue'?"
    They typically hash a normalized version of the stack trace (top frames, ignoring line-number noise where possible) to cluster occurrences of what's likely the same underlying bug, letting you see aggregate frequency/affected-user-count per issue rather than treating every occurrence as unique.

    ```
    issue_id = hash(normalize(stackTrace.topFrames))
    ```

??? question "Why can obfuscation (R8) interfere with crash grouping if mapping files aren't properly uploaded/matched per build?"
    If the crash reporting tool can't deobfuscate a stack trace using the exact matching mapping file for that specific build, it may either fail to symbolicate at all or, worse, mis-group crashes from different builds together (or fail to group truly identical crashes) due to mismatched obfuscated names.

    ```bash
    firebase crashlytics:symbols:upload --app=1:123:android:abc mapping.txt # must match the exact build
    ```

??? question "What's the value of a centralized remote logging/telemetry pipeline (beyond crash reporting) for a production mobile app?"
    It lets you correlate non-fatal issues, performance metrics, and business events across users/sessions after the fact, supporting root-cause investigation of subtle issues (e.g., 'why did checkout conversion drop') that wouldn't manifest as an actual crash to be caught by Crashlytics-style tools alone.

??? question "What's a risk of over-logging verbose telemetry data from production apps?"
    Increased network/battery usage from frequent log uploads, higher storage/processing cost on the backend, and potential privacy/compliance risk if sensitive data ends up in logs inadvertently — logging strategy should be deliberate, not 'log everything just in case.'

## Localization Testing, Accessibility Focus Order & Snapshot Testing

??? question "What is pseudo-locale testing, and what class of bugs does it catch that regular translation review doesn't?"
    Using a synthetic locale (e.g., accented characters, extended text length, or RTL pseudo-locale) lets you test layout robustness and RTL mirroring before real translations exist, catching truncation/overflow/hardcoded-direction bugs early rather than only discovering them once real (often longer) translated strings ship.

    ```
    # Android Studio run config: Language = "Pseudolocale (en-XA)" or "en-XB" (RTL)
    ```

??? question "How does Android determine the accessibility (TalkBack) focus traversal order by default, and when would you need to override it?"
    By default it follows the visual/XML declaration order of views in the layout; you'd override it (via `accessibilityTraversalBefore`/`After` in Views, or `Modifier.semantics { }` ordering hints in Compose) when the visual layout order doesn't match the logical reading order a screen-reader user should experience (e.g., a visually reordered grid).

    ```kotlin
    Modifier.semantics { traversalIndex = 1f } // overrides default XML/visual order
    ```

??? question "What is a 'merged' versus 'unmerged' semantics tree in Compose accessibility testing?"
    The unmerged tree exposes every individual composable's raw semantics nodes; the merged tree combines child nodes into their nearest semantically-meaningful ancestor (e.g., an icon+text button merges into one accessible unit) — TalkBack and most accessibility testing operate against the merged tree, matching what an actual screen-reader user perceives as one interactive element.

    ```kotlin
    composeTestRule.onRoot(useUnmergedTree = true).printToLog("TAG")
    ```

??? question "What is snapshot/screenshot testing (e.g., via Paparazzi or Shot), and what's its main advantage over manual visual QA?"
    It renders a composable/View to an image without needing an emulator/device (Paparazzi runs entirely on the JVM) and compares it against a stored reference image, catching unintended visual regressions automatically in CI, far faster and more consistently than manual eyeballing across every PR.

    ```kotlin
    @get:Rule val paparazzi = Paparazzi()
    @Test fun default() { paparazzi.snapshot { MyScreen() } }
    ```

??? question "What's a common flakiness risk with screenshot tests, and how do teams mitigate it?"
    Font rendering, animation timing, or device-specific rendering differences can cause false-positive diffs; mitigations include disabling animations for the test render, pinning a specific rendering environment/font set, and using tools (like Paparazzi) designed to produce deterministic, environment-independent rendering.

    ```kotlin
    paparazzi.snapshot { CompositionLocalProvider(LocalInspectionMode provides true) { MyScreen() } }
    ```

??? question "Why should UI tests generally disable system animations (via `adb shell settings put global window_animation_scale 0`, etc.) in CI?"
    Animations introduce timing variability that Espresso/Compose test synchronization must wait out, slowing tests and increasing flakiness risk if a test proceeds before an animation visually completes despite the underlying state already being correct.

    ```bash
    adb shell settings put global window_animation_scale 0
    adb shell settings put global transition_animation_scale 0
    ```

## Image Loading, Push Notifications Deep Dive & Remote Config

??? question "What's the difference between Coil and Glide's underlying approach to image loading on Android?"
    Coil is built Kotlin-first on coroutines/OkHttp with a smaller footprint and Compose-friendly API; Glide uses a more mature, highly optimized custom bitmap pooling and request-lifecycle-management engine with broader legacy Android version support and more granular low-level caching controls.

    ```kotlin
    AsyncImage(model = url, contentDescription = null) // Coil, Compose-first
    Glide.with(context).load(url).into(imageView)       // Glide, View-first
    ```

??? question "What's the difference between an image loading library's memory cache and disk cache?"
    The memory cache holds decoded `Bitmap` objects for instant redisplay (cleared on process death, limited by available RAM); the disk cache stores the downloaded/encoded image bytes on persistent storage, avoiding a network refetch (but still requiring decode) across app restarts.

    ```kotlin
    ImageLoader.Builder(context)
        .memoryCache { MemoryCache.Builder(context).maxSizePercent(0.25).build() }
        .diskCache { DiskCache.Builder().directory(cacheDir).build() }
        .build()
    ```

??? question "Why do image loading libraries automatically cancel a load tied to a RecyclerView item's ImageView when the view is recycled?"
    To avoid wasted network/decode work for a view that's no longer displaying that image, and to prevent a late-arriving image from a previous bind incorrectly appearing on a since-recycled/rebound view showing different data.

    ```kotlin
    override fun onViewRecycled(holder: ViewHolder) {
        Glide.with(holder.imageView).clear(holder.imageView) // cancels the in-flight load
    }
    ```

??? question "What's the difference between `NotificationCompat.MessagingStyle` and a plain text notification for a chat app?"
    `MessagingStyle` renders a threaded conversation view directly in the notification (multiple messages, sender avatars) and integrates with Android's 'Bubbles' and smart reply features, whereas a plain notification just shows a single title/text with no conversational structure.

    ```kotlin
    NotificationCompat.MessagingStyle(me).addMessage("Hi!", timestamp, sender)
    ```

??? question "What are Notification Bubbles, and what API supports them?"
    A floating, chat-head-style persistent UI for ongoing conversations, backed by `BubbleMetadata` attached to a `MessagingStyle` notification, letting the user keep a conversation accessible as a small overlay while using other apps.

    ```kotlin
    NotificationCompat.BubbleMetadata.Builder(pendingIntent, icon).build()
    ```

??? question "What's the difference between Firebase Remote Config's 'default values' bundled in-app versus fetched values, and why does caching matter?"
    Bundled defaults ensure sane behavior on first launch/offline before any fetch succeeds; fetched values are cached locally with a configurable minimum fetch interval, so the app doesn't hit the Remote Config backend on every single launch, and `activate()` must be called explicitly to apply newly fetched values without disrupting the current session unexpectedly.

    ```kotlin
    remoteConfig.setDefaultsAsync(R.xml.remote_config_defaults)
    remoteConfig.fetchAndActivate() // fetched values only apply after activate()
    ```

??? question "Why might you deliberately delay activating newly fetched Remote Config values until the next app restart rather than applying them immediately mid-session?"
    To avoid a jarring experience where UI/behavior changes unexpectedly while the user is actively using a screen; applying config changes at a natural boundary (app start) gives a more predictable, less disruptive user experience.

    ```kotlin
    remoteConfig.fetch().addOnCompleteListener {
        pendingConfig = true // apply on next app start, not mid-session
    }
    ```

## Accessibility, Localization & Publishing

??? question "What's the difference between `contentDescription` and visible text for accessibility?"
    `contentDescription` provides a label for screen readers (e.g., TalkBack) on elements without visible text (icons/images); it should be omitted or set to null on purely decorative elements so screen readers skip them rather than announcing redundant/meaningless content.

    ```kotlin
    imageView.contentDescription = "Profile photo" // or null for purely decorative images
    ```

??? question "How do you test accessibility beyond just adding `contentDescription`?"
    Enable TalkBack and navigate the app using only screen-reader gestures, use Accessibility Scanner/Lint checks for touch target size and contrast, and verify focus order is logical for both switch-access and screen-reader users.

    ```
    # Settings > Accessibility > TalkBack > On, then navigate with gestures only
    ```

??? question "What's the minimum recommended touch target size for accessibility, and why does it matter?"
    Generally 48x48dp; smaller targets are harder for users with motor impairments (or anyone with imprecise touch, e.g., on a moving vehicle) to reliably tap, increasing accidental mis-taps.

    ```kotlin
    Modifier.size(48.dp) // minimum recommended touch target
    ```

??? question "How does Android handle RTL (right-to-left) layout support, and what's a common mistake?"
    Using `start`/`end` instead of `left`/`right` in layout attributes lets the system automatically mirror layouts for RTL locales; a common mistake is hardcoding `left`/`right` margins/padding, which breaks mirroring for RTL languages like Arabic or Hebrew.

    ```xml
    <View android:layout_marginStart="16dp" android:layout_marginEnd="8dp" /> <!-- not left/right -->
    ```

??? question "What's the difference between `string.xml` pluralization (`<plurals>`) and simple string formatting for count-based text?"
    `<plurals>` lets you define grammatically correct variants per locale's plural rules (which differ significantly across languages, not just singular/plural like English), whereas manual string formatting with a count often produces grammatically incorrect text in many locales.

    ```xml
    <plurals name="num_items">
        <item quantity="one">%d item</item>
        <item quantity="other">%d items</item>
    </plurals>
    ```

??? question "Why should you avoid concatenating translated string fragments together in code (e.g., `getString(R.string.hello) + name`)?"
    Word order and grammar vary by language; concatenation assumes English-like structure, which can produce nonsensical or incorrect sentences in other languages — use a single formatted string resource with a placeholder (`"Hello, %1$s"`) instead.

    ```kotlin
    // Bad:  getString(R.string.hello) + name
    getString(R.string.hello_format, name) // "Hello, %1$s"
    ```

??? question "What's the difference between staged rollout and a full production release on the Play Store?"
    A staged rollout releases the update to only a percentage of users initially, letting you monitor crash rates/vitals before increasing the percentage, reducing blast radius if a critical bug slips through.

    ```
    # Play Console > Production > Create release > Rollout: 10%
    ```

??? question "What are Android Vitals, and what key metrics does Google Play surface to developers?"
    A dashboard of app health metrics including crash rate, ANR rate, excessive wakeups, stuck wake locks, and startup time, used both to inform developers and to affect an app's visibility/ranking on the Play Store if thresholds are exceeded.

    ```text
    Play Console > Quality > Android vitals
      Crash rate:        0.4%   (bad behavior threshold: 1.09%)
      ANR rate:          0.1%   (bad behavior threshold: 0.47%)
      Excessive wakeups:  ok
      Stuck wake locks:   ok
    ```

??? question "What's the difference between 'internal testing,' 'closed testing,' and 'open testing' tracks on Play Console?"
    Internal testing is for a small trusted group (fast, minimal review) typically the dev team; closed testing targets a defined larger group (e.g., beta testers) via email lists or a private community; open testing is available to anyone who opts in via a public Play Store listing, before a full production release.

    ```
    # Play Console > Testing > Internal testing / Closed testing / Open testing
    ```

??? question "What is the 'Generate Signed Bundle/APK' release checklist typically responsible for verifying before submission?"
    That version code/name is incremented correctly, R8/ProGuard rules don't break functionality (tested on a release build, not just debug), signing config uses the correct release keystore, and required Play Console metadata/policy compliance (privacy policy, data safety form) is up to date.

    ```kotlin
    // build.gradle.kts
    versionCode = 42
    versionName = "2.3.1"
    ```
