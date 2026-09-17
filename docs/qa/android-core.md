# Android Core & Internals

Collapsed by default — try to answer before revealing.

## Android Core Components & Lifecycle

??? question "What are the four main Android component types?"
    Activity, Service, BroadcastReceiver, and ContentProvider — all declared in the manifest and managed by the system rather than instantiated directly by app code.

    ```kotlin
    class MyActivity : Activity()
    class MySyncService : Service()
    class MyReceiver : BroadcastReceiver()
    class MyProvider : ContentProvider()
    ```

??? question "Describe the Activity lifecycle callbacks in order for a normal launch."
    `onCreate()` -> `onStart()` -> `onResume()`, then on backgrounding `onPause()` -> `onStop()` -> `onDestroy()`, with `onRestart()` before `onStart()` if returning from stopped state.

    ```kotlin
    override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState) }
    override fun onStart() { super.onStart() }
    override fun onResume() { super.onResume() }
    // ... then, on the way out: onPause() -> onStop() -> onDestroy()
    ```

??? question "What's the difference between `onPause()` and `onStop()`?"
    `onPause()` fires when the Activity loses foreground focus but may still be visible (e.g., a dialog appears on top); `onStop()` fires when it's no longer visible at all.

    ```kotlin
    override fun onPause() { /* still may be partially visible, e.g. a dialog on top */ }
    override fun onStop() { /* no longer visible at all */ }
    ```

??? question "What happens to an Activity's state on a configuration change like rotation by default?"
    The Activity is destroyed and recreated (`onDestroy()` then `onCreate()`), unless `configChanges` is declared in the manifest to handle it manually or the state is preserved via `ViewModel`/`onSaveInstanceState`.

    ```xml
    <!-- opt out of destroy/recreate and handle it yourself instead: -->
    <activity android:configChanges="orientation|screenSize" />
    ```

??? question "What's the difference between `onSaveInstanceState()` and `ViewModel` for surviving configuration changes?"
    `onSaveInstanceState()` uses a `Bundle` (limited size, must be serializable/parcelable) and survives process death; `ViewModel` retains arbitrary in-memory objects across config changes but is cleared on process death.

    ```kotlin
    override fun onSaveInstanceState(outState: Bundle) {
        outState.putString("key", value) // Bundle — survives process death too
    }
    class MyViewModel : ViewModel() { var value = "" } // survives rotation, not process death
    ```

??? question "How does `SavedStateHandle` complement `ViewModel`?"
    It gives the `ViewModel` access to a `Bundle`-backed key-value store that survives process death, unlike the ViewModel's own in-memory state, letting you restore critical UI state after the system kills and recreates the process.

    ```kotlin
    class MyViewModel(private val state: SavedStateHandle) : ViewModel() {
        var value: String
            get() = state["key"] ?: ""
            set(v) { state["key"] = v } // survives process death too
    }
    ```

??? question "What's the difference between a Fragment's lifecycle and its view lifecycle?"
    The Fragment object itself can outlive its view (e.g., when placed on the back stack, the view is destroyed but the Fragment instance remains); `viewLifecycleOwner` tracks only the view's lifecycle, which is what LiveData/Flow observers touching UI should use.

    ```kotlin
    override fun onDestroyView() { /* the view is gone */ }
    override fun onDestroy() { /* the Fragment instance itself is gone */ }
    ```

??? question "Why is it a common bug to observe LiveData using the Fragment's own lifecycle instead of `viewLifecycleOwner`?"
    Because the Fragment lifecycle can outlive the view (e.g., in a back-stack), the observer may try to update a destroyed view, or the observer isn't properly removed/re-added across view recreation, causing crashes or duplicate observers.

    ```kotlin
    // Risky:
    liveData.observe(this) { render(it) } // `this` = Fragment, can outlive its view
    // Correct:
    liveData.observe(viewLifecycleOwner) { render(it) }
    ```

??? question "What is the difference between `onCreateView()` and `onViewCreated()` in a Fragment?"
    `onCreateView()` inflates and returns the view hierarchy; `onViewCreated()` is called after the view exists, the correct place to set up view references, LiveData observers, and click listeners.

    ```kotlin
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View =
        inflater.inflate(R.layout.fragment, container, false)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        view.findViewById<Button>(R.id.button).setOnClickListener { }
    }
    ```

??? question "What is a Service, and what's the difference between started and bound Service?"
    A Service runs background operations without a UI; a started Service runs independently until stopped (`startService`/`stopSelf`), while a bound Service provides a client-server interface via `bindService()` and typically stops when all clients unbind.

    ```kotlin
    startService(Intent(this, MyService::class.java))         // started
    bindService(Intent(this, MyService::class.java), conn, 0) // bound
    ```

??? question "Why must long-running Services running while the app is in the background be Foreground Services on modern Android?"
    Background execution limits (since Android 8+) restrict what a regular background Service can do; a Foreground Service must show a persistent notification and is exempt from these restrictions because the user is aware it's running.

    ```kotlin
    class MyService : Service() {
        override fun onCreate() {
            startForeground(1, buildNotification()) // required for long-running background work
        }
    }
    ```

??? question "When would you choose `WorkManager` over a Service for background work?"
    WorkManager is preferred for deferrable, guaranteed background work (e.g., syncing data, uploading, retryable tasks) since it handles constraints, retries, and battery-friendly scheduling, and survives process death/reboot with persisted work.

    ```kotlin
    val request = OneTimeWorkRequestBuilder<SyncWorker>().build()
    WorkManager.getInstance(context).enqueue(request) // survives process death/reboot
    ```

??? question "What are WorkManager's constraint types and give an example use?"
    Constraints like `NetworkType`, `requiresCharging`, `requiresBatteryNotLow`, `requiresStorageNotLow` — e.g., scheduling a large upload only when connected to unmetered Wi-Fi and charging.

    ```kotlin
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.UNMETERED)
        .setRequiresCharging(true)
        .build()
    ```

??? question "What's the difference between `OneTimeWorkRequest` and `PeriodicWorkRequest`?"
    `OneTimeWorkRequest` runs once; `PeriodicWorkRequest` repeats at a minimum interval (15 minutes minimum enforced by the system) but the exact timing isn't guaranteed precisely, similar to `AlarmManager` inexact alarms.

    ```kotlin
    OneTimeWorkRequestBuilder<SyncWorker>().build()
    PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES).build() // 15 min minimum
    ```

??? question "What is a BroadcastReceiver, and why has its use declined in modern Android?"
    It listens for system-wide or app broadcasts; many implicit broadcasts were restricted starting Android 8 for battery/security reasons, and in-app event handling has largely shifted to LiveData/Flow/EventBus-like patterns instead.

    ```kotlin
    class MyReceiver : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) { /* handle the broadcast */ }
    }
    ```

??? question "What's the difference between a statically and dynamically registered BroadcastReceiver?"
    Static receivers can wake the app for a subset of exempted broadcasts even when not running; dynamic receivers only work while the registering component is alive and must be unregistered to avoid leaks.

    ```kotlin
    // Static (manifest): <receiver android:name=".MyReceiver"><intent-filter>...</intent-filter></receiver>
    // Dynamic:
    registerReceiver(receiver, IntentFilter(Intent.ACTION_BATTERY_LOW))
    unregisterReceiver(receiver) // must remember to call this
    ```

??? question "What is a ContentProvider used for, and why not just share a raw SQLite file?"
    It provides a structured, permission-controlled interface (URIs, CRUD via `ContentResolver`) for sharing data across app boundaries; sharing a raw file bypasses Android's security model and risks concurrent-access corruption.

    ```kotlin
    class MyProvider : ContentProvider() {
        override fun query(uri: Uri, projection: Array<String>?, selection: String?,
                            selectionArgs: Array<String>?, sortOrder: String?): Cursor? {
            /* structured, permission-controlled access */
            return null
        }
    }
    ```

??? question "What's the difference between `Intent` and `IntentFilter`?"
    `Intent` is the message describing an action/data to perform or deliver; `IntentFilter` declares in the manifest (or dynamically) what implicit Intents a component can respond to.

    ```kotlin
    val intent = Intent(Intent.ACTION_VIEW, uri) // the message
    // <intent-filter><action android:name="android.intent.action.VIEW"/></intent-filter> — what's accepted
    ```

??? question "What's the difference between an explicit and implicit Intent?"
    An explicit Intent names the target component class directly; an implicit Intent declares an action/category/data and lets the system resolve which component(s) can handle it.

    ```kotlin
    Intent(this, DetailActivity::class.java) // explicit — names the class
    Intent(Intent.ACTION_VIEW, uri)           // implicit — system resolves a handler
    ```

??? question "What does `FLAG_ACTIVITY_NEW_TASK` do?"
    It starts the Activity in a new task if not already running in one, commonly required when launching an Activity from a non-Activity context like a Service or BroadcastReceiver.

    ```kotlin
    val intent = Intent(this, MyActivity::class.java).apply {
        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) // needed when starting from a non-Activity Context
    }
    ```

??? question "What does `FLAG_ACTIVITY_CLEAR_TOP` combined with `FLAG_ACTIVITY_SINGLE_TOP` achieve?"
    It clears all Activities above an existing instance of the target in the task stack and reuses that instance instead of creating a new one, commonly used for "return to home" style navigation.

    ```kotlin
    intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)
    // clears everything above the existing instance and reuses it
    ```

??? question "What's the difference between `launchMode` values `standard`, `singleTop`, `singleTask`, and `singleInstance`?"
    `standard` always creates a new instance; `singleTop` reuses the top instance if it's already there; `singleTask` reuses a single instance for the whole task, clearing anything above it; `singleInstance` gives the Activity its own dedicated task that no other Activity can join.

    ```xml
    <activity android:name=".DetailActivity" android:launchMode="singleTop" />
    ```

??? question "What is a Task and how does it relate to the back stack?"
    A Task is a collection of Activities in a stack that the user navigates through with back; multiple apps' Activities can even coexist across tasks depending on launch mode/affinity.

    ```kotlin
    // Task = [Home, ListActivity, DetailActivity] <- back stack; back pops DetailActivity first
    ```

??? question "What is `taskAffinity`, and when would you change it?"
    It determines which task an Activity prefers to belong to; you'd change it to make an Activity appear in a separate task (e.g., in the recents screen) from the rest of the app, though it's a niche/legacy tool now.

    ```xml
    <activity android:name=".PipActivity" android:taskAffinity=".separateTask" />
    ```

??? question "What's the difference between `onNewIntent()` firing vs a fresh `onCreate()`?"
    `onNewIntent()` fires when an existing Activity instance is reused (e.g., `singleTop`) and receives a new Intent without full recreation; `onCreate()` runs only when a new instance is created.

    ```kotlin
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent) // existing instance reused, no full recreation
    }
    ```

??? question "How does the Android system decide which process to kill under memory pressure?"
    It uses an `oom_adj`/process importance hierarchy — foreground/visible processes are killed last, followed by service processes, then cached/background processes, roughly LRU among same-priority processes.

    ```kotlin
    // Roughly: Foreground > Visible > Service > Cached — killed in about that reverse order
    ```

??? question "What's the difference between a 'cached' process and a 'background' process in Android's process importance model?"
    Both are non-visible, but "cached" processes hold no active components (kept purely to speed up future launches) and are killed first under pressure; a service process actively running something ranks higher priority than a plain cached process.

    ```kotlin
    // Cached: no active components, kept only to speed up a future launch — killed first
    // Service: actively running work — survives longer under pressure
    ```

??? question "What happens to your app's state on process death, and how do you recover gracefully?"
    All in-memory state (including ViewModels) is lost, but the Activity stack/back-stack entry can be recreated by the system; recovery relies on `onSaveInstanceState`/`SavedStateHandle` and persisted data (DB/DataStore) rather than assuming memory survives.

    ```kotlin
    class MyViewModel(state: SavedStateHandle) : ViewModel() {
        val id: String = state["id"] ?: error("missing") // restore from SavedStateHandle, not memory
    }
    ```

??? question "What's the Application class used for, and what should you avoid doing in `Application.onCreate()`?"
    It's the single global entry point for app-wide initialization (DI graph setup, crash reporting, etc.); avoid heavy synchronous work there since it delays startup and blocks the main thread before any UI shows.

    ```kotlin
    class MyApp : Application() {
        override fun onCreate() {
            super.onCreate()
            // avoid heavy synchronous work here — it delays first-frame startup
        }
    }
    ```

??? question "What is `ActivityLifecycleCallbacks` used for?"
    Registering a global listener on the Application to observe lifecycle events across all Activities, useful for cross-cutting concerns like tracking foreground/background state or app-wide analytics without modifying each Activity.

    ```kotlin
    application.registerActivityLifecycleCallbacks(object : Application.ActivityLifecycleCallbacks {
        override fun onActivityResumed(activity: Activity) { /* track app-wide state */ }
        // ... other callbacks
    })
    ```

??? question "What is `ProcessLifecycleOwner` used for?"
    It exposes a single Lifecycle representing the whole app's foreground/background state (not just one Activity), useful for app-wide behaviors like pausing analytics or showing a lock screen when the app backgrounds.

    ```kotlin
    ProcessLifecycleOwner.get().lifecycle.addObserver(object : DefaultLifecycleObserver {
        override fun onStop(owner: LifecycleOwner) { /* whole app went to background */ }
    })
    ```

??? question "What's the difference between `Context.getApplicationContext()` and an Activity context, and why can misusing it cause leaks?"
    Application context lives as long as the app process; Activity context is tied to that Activity's lifecycle. Holding an Activity context in a long-lived object (e.g., a singleton) leaks the entire Activity (and its views) after it should be destroyed.

    ```kotlin
    class LeakySingleton(context: Context) {
        val ctx = context.applicationContext // NOT `context` directly — avoids leaking an Activity
    }
    ```

??? question "Why shouldn't you inflate certain themed views with the Application context?"
    Application context doesn't carry the Activity's theme/configuration, so theme-dependent resources or views can render incorrectly or throw exceptions expecting an Activity-derived context.

    ```kotlin
    // LayoutInflater.from(applicationContext).inflate(R.layout.themed_view, null)
    // — wrong theme/config compared to inflating with an Activity context
    ```

??? question "What does `Window` represent versus `View` in the Android UI stack?"
    `Window` is the top-level container (abstract, implemented by `PhoneWindow`) managing the surface, decorations (status/nav bar insets), and root `ViewGroup`; `View`/`ViewGroup` is the actual UI content hosted inside it.

    ```kotlin
    val window: Window = activity.window  // top-level container
    val rootView: View = window.decorView // the actual UI content inside it
    ```

??? question "What is `WindowManager` used for outside of normal Activities?"
    Adding views directly to the screen outside an Activity's own window, such as system overlays (requires `SYSTEM_ALERT_WINDOW` permission) or accessibility overlays.

    ```kotlin
    val overlay = TextView(context)
    windowManager.addView(overlay, layoutParams) // e.g. a system overlay
    ```

??? question "What's the app startup sequence before your first Activity's `onCreate()` runs?"
    Zygote forks the app process, the Application object is created and `attachBaseContext`/`onCreate()` run, ContentProviders are initialized, then the launched Activity is instantiated and its `onCreate()` is called by the ActivityThread/ActivityManager.

    ```kotlin
    // Zygote fork -> Application.attachBaseContext()/onCreate() -> ContentProviders -> Activity.onCreate()
    ```

??? question "What is `Zygote` and why does Android use it for process creation?"
    A pre-initialized process holding the core Android framework/Java classes already loaded, forked to create new app processes quickly via copy-on-write memory sharing, avoiding a full VM boot per app launch.

    ```kotlin
    // fork() copies Zygote's already-loaded framework classes via copy-on-write — no VM re-boot needed
    ```

??? question "What is App Startup (Jetpack `androidx.startup`) used for?"
    It provides a declarative way to initialize multiple libraries/components at app startup in a single, ordered pass merged via a manifest-provider mechanism, avoiding the overhead of registering many separate ContentProviders just for initialization.

    ```kotlin
    class MyInitializer : Initializer<MyLib> {
        override fun create(context: Context): MyLib = MyLib.init(context)
        override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
    }
    ```

## Android Internals (ART, Binder, Process Model)

??? question "What is DEX bytecode, and how does it differ from regular JVM bytecode?"
    Android's own compiled bytecode format — Kotlin/Java source first compiles to standard JVM bytecode (`.class` files), then D8/R8 converts that into DEX: a more compact, register-based format sharing one constant pool across all classes, designed for mobile's tighter memory/storage constraints. This is what ships inside the APK and is what ART actually executes.

    ```kotlin
    // Kotlin/Java source -> javac/kotlinc -> JVM bytecode (.class)
    //                     -> D8/R8         -> DEX bytecode (.dex) -- ships in the APK
    ```

??? question "What is ART (Android Runtime) and how does it differ from the older Dalvik?"
    ART is Android's runtime executing DEX bytecode; unlike Dalvik (primarily JIT-only in its early form), ART introduced AOT compilation at install time (later evolved to a hybrid JIT+AOT with profile-guided compilation) for better runtime performance at the cost of longer install time historically.

    ```kotlin
    // ART:    AOT (install-time) + JIT hybrid, profile-guided
    // Dalvik: primarily JIT, recompiled on every run
    ```

??? question "What is the Binder IPC mechanism, and why does Android rely on it so heavily?"
    Binder is Android's kernel-level inter-process communication driver enabling efficient, secure calls between processes (e.g., app <-> system services); it's central because Android's architecture isolates apps into separate processes for security/stability while still needing them to communicate with system services constantly.

    ```kotlin
    // app process <--Binder--> system_server (e.g. ActivityManagerService, WindowManagerService)
    ```

??? question "What's the difference between a 'one-way' (`oneway`) and a normal synchronous Binder call?"
    A oneway call is asynchronous/non-blocking from the caller's perspective (fire-and-forget, no return value waited on); a normal Binder call blocks the calling thread until the remote process responds.

    ```kotlin
    interface IMyService : IInterface {
        fun blockingCall(): String // blocks until the remote process responds
    }
    // in the .aidl file: oneway void fireAndForget(); // doesn't block waiting for a response
    ```

??? question "What is the Binder thread pool, and why can a poorly designed AIDL/Service implementation cause ANRs indirectly?"
    Each process has a limited pool of Binder threads handling incoming IPC calls; if a Service's AIDL method handler blocks for a long time, it can exhaust available Binder threads, delaying other IPC calls (potentially including ones that matter for UI responsiveness) to that process.

    ```kotlin
    // A slow AIDL method handler can exhaust the Binder thread pool,
    // delaying other incoming IPC calls to this process -> ANR risk
    ```

??? question "What is `oom_adj`/process importance and how does the system use it beyond just choosing what to kill?"
    It's an internal priority score reflecting how important a process is (foreground, visible, service, cached, etc.); besides guiding LMK (low memory killer) decisions, it also affects CPU/scheduling priority given to the process by the kernel.

    ```kotlin
    // lower oom_adj = killed later AND scheduled with higher CPU priority by the kernel
    ```

??? question "What happens at the kernel/OS level when Zygote forks a new app process?"
    `fork()` creates a near-identical copy of the Zygote process's memory space using copy-on-write pages, so the new process shares most framework class data/memory with Zygote until it actually writes to those pages, making process creation much faster than starting from scratch.

    ```kotlin
    // fork() -> copy-on-write pages shared with Zygote until the child actually writes to them
    ```

??? question "What's the difference between a 'cold start,' 'warm start,' and 'hot start' in terms of what the system must do?"
    Cold start creates a new process (Zygote fork, Application init, Activity creation) — slowest; warm start reuses an existing process but recreates the Activity (e.g., returning after backgrounding with the process still alive); hot start just brings an existing, still-resumed Activity back to the foreground — fastest.

    ```kotlin
    // cold: new process (slowest) | warm: existing process, new Activity | hot: just resume (fastest)
    ```

??? question "What is the Low Memory Killer (LMK) and how does it differ from a standard Linux OOM killer?"
    LMK (or its modern successor, the kernel-integrated `lmkd`) proactively kills lower-priority processes *before* the system runs out of memory entirely, using Android's process importance hierarchy, rather than waiting for an actual out-of-memory condition like the generic Linux OOM killer.

    ```kotlin
    // lmkd kills low-priority processes proactively, BEFORE real OOM —
    // unlike the generic Linux OOM killer, which waits until memory is actually exhausted
    ```

??? question "What's the difference between the main/UI thread and the render thread in Android's rendering pipeline?"
    The UI thread handles measure/layout/input and issues drawing commands; since Android 5.0, a separate RenderThread executes the actual GPU rendering commands (via OpenGL/Vulkan) asynchronously, so some animations (e.g., `RenderThread`-driven ones) can continue smoothly even if the UI thread briefly stalls.

    ```kotlin
    // UI thread:     measure/layout/input, records a display list
    // RenderThread:  (since 5.0) executes the actual GPU commands from that display list
    ```

??? question "What's the difference between `Looper.getMainLooper()` and creating your own `Looper` on a background thread?"
    The main Looper is created automatically by the system for the app's main thread and processes the core UI event queue; a custom Looper (via `HandlerThread` or manually calling `Looper.prepare()`/`loop()`) creates an independent message queue on a background thread for sequential background task processing.

    ```kotlin
    Handler(Looper.getMainLooper()).post { }  // the app's automatic main-thread queue
    val thread = HandlerThread("bg").apply { start() }
    Handler(thread.looper).post { }            // a custom background message queue
    ```
