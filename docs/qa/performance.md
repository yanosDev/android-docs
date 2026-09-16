# Performance & Rendering

Collapsed by default — try to answer before revealing.

## Performance & Memory Management

??? question "What causes a memory leak involving Activities/Fragments, and how do you detect one?"
    A long-lived object (static field, singleton, background thread/callback, unclosed listener) holding a reference to an Activity/Fragment/View prevents garbage collection after it should be destroyed; detect via LeakCanary, which automatically dumps heaps and traces retained reference paths.

    ```kotlin
    object EventBus {
        private val listeners = mutableListOf<Activity>() // leak: holds the Activity forever
    }
    ```

??? question "What's the difference between a strong, weak, and soft reference, and where would you use each?"
    A strong reference (default) prevents GC as long as it exists; a weak reference (`WeakReference`) allows GC to collect the object anytime, useful for caches/callbacks that shouldn't prevent cleanup; a soft reference is collected only under memory pressure, suited for memory-sensitive caches (e.g., bitmap caches) that should persist as long as memory allows.

    ```kotlin
    val strong: User = user             // prevents GC
    val weak = WeakReference(user)       // collectible any time
    val soft = SoftReference(bitmap)     // collected only under memory pressure
    ```

??? question "How does Android's generational garbage collector work at a high level?"
    New objects are allocated in a young generation; frequent minor GCs quickly collect short-lived garbage there, promoting surviving objects to an old generation collected less often by more expensive major GCs — this reduces overall pause time since most garbage is short-lived.

    ```kotlin
    // young generation: short-lived objects, frequent cheap "minor" GCs
    // old generation:   long-lived survivors, less frequent, more expensive "major" GCs
    ```

??? question "What tools would you use to profile jank/frame drops, and what metrics matter?"
    Android Studio's Profiler (CPU/Frame timeline), Perfetto/systrace for detailed frame timing, and GPU rendering profiling overlay; key metrics are frame time vs the 16.6ms (60fps)/11ms (90fps) budget and the specific phase (input/animation/measure/layout/draw/sync/GPU) causing overruns.

    ```kotlin
    // 60fps budget: ~16.6ms per frame to stay smooth
    // 90fps budget: ~11ms per frame
    ```

??? question "What's the difference between `Bitmap.Config.ARGB_8888` and `RGB_565` in terms of memory?"
    `ARGB_8888` uses 4 bytes per pixel (full alpha+color precision); `RGB_565` uses 2 bytes per pixel (no alpha, reduced color precision) — halving memory usage at the cost of image quality/no transparency.

    ```kotlin
    val opts = BitmapFactory.Options().apply { inPreferredConfig = Bitmap.Config.RGB_565 } // 2 bytes/px
    ```

??? question "What is `inSampleSize` used for when decoding bitmaps?"
    It downsamples an image during decode (e.g., `inSampleSize=2` decodes at half resolution), avoiding loading a full-resolution bitmap into memory when only a smaller display size is needed.

    ```kotlin
    val opts = BitmapFactory.Options().apply { inSampleSize = 2 } // decode at half resolution
    BitmapFactory.decodeFile(path, opts)
    ```

??? question "What's the difference between JIT and AOT compilation in ART, and how does it affect startup time?"
    JIT (Just-In-Time) compiles hot bytecode paths at runtime as the app runs, which is flexible but has warm-up cost; AOT (Ahead-Of-Time) pre-compiles code (either fully at install time historically, or selectively via Baseline/Cloud Profiles now) so critical paths run at native speed immediately, improving cold-start time.

    ```kotlin
    // JIT: compiled at runtime, as hot paths are detected (warm-up cost)
    // AOT: precompiled ahead of time — install time, or via a Baseline Profile
    ```

??? question "What is a Baseline Profile and how does it improve startup/performance?"
    A list of classes/methods identified as 'hot' during critical user journeys (startup, common navigation), which ART uses to AOT-compile those specific paths at install time, avoiding JIT interpretation/compilation overhead on first runs.

    ```
    # baseline-prof.txt (generated from a Macrobenchmark run)
    HSPLcom/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
    ```

??? question "What's the difference between Macrobenchmark and Microbenchmark libraries?"
    Macrobenchmark measures real-world, full-app-level metrics like startup time or scroll jank on a device/emulator; Microbenchmark measures the execution time of small isolated pieces of code (e.g., a specific function) with statistical rigor, similar to JMH on the JVM.

    ```kotlin
    @Test fun startup() = benchmarkRule.measureRepeated(packageName = PKG) { startActivityAndWait() }
    ```

??? question "How would you diagnose and fix an ANR (Application Not Responding)?"
    Analyze the ANR trace (main thread stack trace at the time of the freeze, available via `adb bugreport` or Play Console's Android vitals) to find what was blocking the main thread (e.g., a synchronous DB/network call, a deadlock, or excessive work in `onCreate`), then move that work off the main thread or reduce its duration.

    ```
    adb bugreport  # captures the ANR trace showing exactly what blocked the main thread
    ```

??? question "What's StrictMode used for, and what kinds of issues does it catch?"
    A developer tool that detects accidental disk/network I/O on the main thread, leaked SQLite cursors/closeable resources, and other performance anti-patterns, throwing/logging violations during development so they're caught before release.

    ```kotlin
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder().detectNetwork().penaltyLog().build()
    )
    ```

??? question "What's the difference between `Debug.startMethodTracing()`/systrace and using the Android Studio Profiler UI?"
    They're largely the same underlying data (method traces, system traces); the Profiler UI provides interactive visualization and live sampling during a debug session, while systrace/Perfetto captures are often used for post-hoc analysis, CI-based performance regression tracking, or scripted trace capture.

    ```kotlin
    Debug.startMethodTracing("trace") // ... work happens here ...
    Debug.stopMethodTracing()
    ```

??? question "What causes 'overdraw' and how do you reduce it?"
    Overlapping opaque backgrounds cause the GPU to render the same pixel multiple times per frame; reduce it by removing redundant background colors/views, flattening view hierarchies, and using tools like the GPU overdraw debug overlay to identify problem areas.

    ```kotlin
    // Debug GPU Overdraw dev option highlights areas redrawn 2x/3x/4x+
    // fix: remove redundant background colors on stacked views
    ```

??? question "What's the difference between View-based lazy inflation techniques (`ViewStub`, `include`) and Compose's inherent laziness?"
    View-based lazy inflation is a manual opt-in technique to defer creating a subtree; Compose composables are inherently only 'created' (composed) when actually invoked in the composition, and lazy layouts (`LazyColumn`) additionally only compose/measure items actually visible on screen.

    ```kotlin
    val stub = findViewById<ViewStub>(R.id.stub)
    stub.inflate() // only inflates when explicitly called
    // vs Compose: a composable simply isn't invoked until it's actually part of composition
    ```

??? question "What is a memory profiler heap dump used for, and what should you look for?"
    It's a snapshot of all live objects and their reference chains at a point in time; you look for unexpectedly large retained object counts (e.g., many Activity instances alive simultaneously) or unexpected retention paths pointing back to a destroyed component.

??? question "What's the difference between 'Allocation Tracking' and a 'Heap Dump' in the memory profiler?"
    Allocation tracking records every object allocation over a time window (useful for spotting excessive/unexpected allocations causing GC churn); a heap dump is a single point-in-time snapshot of what's currently alive (useful for finding leaks/retained memory).

??? question "Why can excessive object allocation cause jank even without an actual leak?"
    Frequent allocations increase GC frequency; even short 'minor' GC pauses, if they happen during an animation/scroll frame, can push that frame over its time budget and cause visible stutter.

    ```kotlin
    override fun onDraw(canvas: Canvas) {
        val paint = Paint() // allocated every single frame — GC pressure, no leak, still jank
    }
    ```

??? question "What's the difference between `WeakHashMap` and a regular `HashMap` combined with `WeakReference` values?"
    `WeakHashMap` holds weak references to its *keys* (entries are removed once a key is no longer strongly referenced elsewhere); wrapping values in `WeakReference` inside a normal `HashMap` instead makes the *values* collectible while keys remain strongly referenced, which is a different retention shape entirely.

    ```kotlin
    val cacheA = WeakHashMap<Key, Bitmap>()              // weak KEYS
    val cacheB = HashMap<Key, WeakReference<Bitmap>>()   // weak VALUES
    ```

??? question "How would you reduce APK/app size for a large production app?"
    Enable R8 shrinking/obfuscation, use Android App Bundles with Play Feature Delivery for on-demand features, strip unused resources (`shrinkResources`), use vector drawables instead of multiple PNG densities, and audit large dependencies/duplicate libraries.

    ```gradle
    android {
        buildTypes {
            release {
                isMinifyEnabled = true    // R8
                isShrinkResources = true  // shrinkResources
            }
        }
    }
    ```

??? question "What's the difference between `shrinkResources` and R8 code shrinking?"
    R8 removes unused/unreachable *code* (classes/methods); `shrinkResources` (works alongside R8) removes unused *resources* (layouts, drawables, strings) that are no longer referenced by the shrunk code.

    ```gradle
    isMinifyEnabled = true     // R8: removes unused CODE
    isShrinkResources = true   // removes unused RESOURCES referenced only by removed code
    ```

## Rendering Pipeline Internals (Choreographer, VSync, SurfaceFlinger)

??? question "What is `Choreographer`, and how does it coordinate frame rendering?"
    It's the system component that schedules and synchronizes animation, input, and drawing callbacks to the display's VSync (vertical sync) signal, ensuring the app produces exactly one frame per display refresh interval rather than rendering out of sync with the screen's actual refresh rate.

    ```kotlin
    Choreographer.getInstance().postFrameCallback { frameTimeNanos ->
        // called once per VSync, in sync with the display's refresh
    }
    ```

??? question "What is VSync, and why does rendering 'miss' a VSync deadline cause visible jank?"
    VSync is the hardware signal marking when the display is ready to accept a new frame; if the app's rendering work for a frame isn't finished by the next VSync, the display shows the previous frame again (a dropped/duplicated frame), perceived as stutter.

    ```kotlin
    // if frame work isn't done by the next VSync, the display repeats the previous frame -> jank
    ```

??? question "What is SurfaceFlinger's role in the Android rendering pipeline?"
    It's the system service that composites all visible surfaces (from different apps/windows/system UI layers) into the final image sent to the display, working with the GPU/hardware compositor to combine layers efficiently.

??? question "What's the difference between the UI thread and the RenderThread in terms of what work each performs per frame?"
    The UI thread handles input processing, measure/layout, and records drawing commands into a display list; the RenderThread (since Android 5.0) takes that display list and actually executes the GPU drawing commands and syncs with VSync, allowing certain animations to continue smoothly even if the UI thread is briefly busy.

    ```kotlin
    view.animate().translationX(100f) // recorded by the UI thread, executed by RenderThread on the GPU
    ```

??? question "What does 'triple buffering' refer to in the Android graphics pipeline, and what problem does it solve?"
    Using three buffers (rather than two) for frame production/display/consumption lets the GPU continue rendering a new frame while a previous one is being displayed and another is queued, reducing the chance that a single slow frame causes the app to miss producing the *next* frame too, at the cost of slightly increased latency.

??? question "What's the difference between `Window.setFrameRate()`-style adaptive refresh control and just relying on the display's fixed refresh rate?"
    Adaptive/variable refresh rate APIs let the app hint its desired frame rate to match content needs (e.g., a static-content screen requesting a lower rate to save battery on displays supporting variable refresh), rather than the display always running at a single fixed maximum rate regardless of actual content motion.

    ```kotlin
    window.attributes = window.attributes.apply { preferredRefreshRate = 60f }
    ```

## Advanced Debugging & Profiling Tools

??? question "What is Perfetto, and how does it differ from the older systrace tool?"
    Perfetto is Android's modern unified tracing system (successor to systrace) capturing detailed system-wide and app-level trace events (CPU scheduling, app method traces, memory) into a single trace file, viewable in a powerful web-based UI with SQL-queryable trace data, offering deeper analysis than systrace's simpler timeline view.

??? question "What is Battery Historian used for, and what kind of data does it visualize?"
    A tool (fed from `adb bugreport` battery stats) visualizing historical battery usage events over time — wakelocks, wakeups, network activity, per-app battery contribution — helping pinpoint what's draining battery and when, beyond just an aggregate percentage.

??? question "What's the difference between 'sample-based' and 'trace-based' (instrumented) CPU profiling?"
    Sample-based profiling periodically snapshots the call stack at intervals (lower overhead, statistical picture, can miss very short-lived calls); trace-based/instrumented profiling records every method entry/exit precisely (complete picture, but adds significant overhead that can itself distort timing-sensitive measurements).

??? question "What is the APK Analyzer in Android Studio used for?"
    Inspecting the contents and size breakdown of a built APK/AAB — DEX method counts, individual resource/file sizes, manifest contents — useful for diagnosing unexpectedly large app size or investigating what a specific dependency actually contributes to the final binary.

??? question "How would you identify and remove unused dependencies from a large Gradle project?"
    Use Gradle's dependency insight/analysis tooling (or third-party plugins like the Dependency Analysis Gradle Plugin) to detect declared dependencies with no actual used symbols, and check for `api`-scoped dependencies that could be downgraded to `implementation` to tighten the build graph.

    ```
    ./gradlew :app:dependencies  # or the Dependency Analysis Gradle Plugin
    ```

??? question "What is code coverage tooling (e.g., Jacoco) used for, and what's a limitation of chasing a high coverage percentage as a goal?"
    It measures what percentage of code lines/branches are executed by your test suite; a high percentage doesn't guarantee tests actually assert meaningful behavior (a test can execute a line without checking its result), so coverage should be treated as a signal for untested gaps, not as proof of test quality.

    ```kotlin
    @Test fun addsTwoNumbers() {
        add(2, 2) // executes the line, "covers" it — but asserts nothing!
    }
    ```

??? question "What is mutation testing, and how does it address code coverage's blind spot?"
    It automatically introduces small deliberate bugs ('mutants') into the code and checks whether the existing test suite fails as a result; a mutant that survives (tests still pass despite the bug) reveals a test that merely executes code without actually verifying its correctness.

    ```kotlin
    // original: if (x > 0)
    // mutant:   if (x >= 0)   // if tests still pass, they never actually checked the boundary
    ```

??? question "What's the difference between using `adb shell dumpsys gfxinfo <package>` and the Profiler's frame timeline for jank analysis?"
    `dumpsys gfxinfo` provides a quick command-line historical breakdown of frame render times/janky frame counts useful for scripted CI checks; the Profiler's frame timeline gives an interactive, detailed visual breakdown of each frame's phases (input, animation, layout, draw, GPU) for deep manual investigation.

    ```
    adb shell dumpsys gfxinfo com.example.app  # quick CLI historical breakdown
    ```
