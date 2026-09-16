# System APIs & Hardware

Collapsed by default — try to answer before revealing.

## Jetpack Libraries (Navigation, Paging, WorkManager, CameraX, Media3)

??? question "What problem does the Navigation component solve compared to manually managing Fragment transactions?"
    It provides a centralized, visualized graph of app destinations and actions, handles the back stack automatically, standardizes argument passing (type-safe with Safe Args), and integrates deep linking declaratively.

??? question "What is Safe Args and what problem does it solve?"
    A Gradle plugin that generates type-safe classes for passing arguments between navigation destinations, eliminating manual Bundle key/value boilerplate and catching argument type mismatches at compile time.

??? question "What's the difference between a nested navigation graph and a top-level one?"
    A nested graph groups related destinations (e.g., an onboarding flow) as a self-contained sub-graph with its own start destination, which can be included/reused within a larger graph and treated as a single unit for navigation/back-stack purposes.

??? question "How does Navigation Component handle passing data back from a screen (e.g., a result from a picker)?"
    Via a shared `SavedStateHandle` on the back stack entry (`getBackStackEntry().savedStateHandle`), letting a destination set a result that the previous destination observes when it becomes the current back stack entry again.

??? question "What is the Paging 3 library's core purpose, and what are its main components?"
    It loads and displays large datasets incrementally from a data source (network/DB); core components are `PagingSource` (defines how to load a page), `Pager`/`PagingData` (the stream of paged data), and `PagingDataAdapter` (RecyclerView integration with built-in diffing).

??? question "What's the difference between `PagingSource` and `RemoteMediator` in Paging 3?"
    `PagingSource` loads pages from a single source (e.g., just network, or just DB); `RemoteMediator` coordinates loading from network into a local DB cache, letting the UI observe the DB as the single source of truth while the mediator handles fetching more pages as needed.

??? question "How does Paging 3 integrate with Room to support offline-first pagination?"
    Room's `PagingSource` (generated from a `@Query` returning `PagingSource<Int, T>`) serves pages directly from the local DB, while a `RemoteMediator` fetches additional network pages and inserts them into the DB, triggering the DB-backed PagingSource to emit updated pages automatically.

??? question "What's the difference between WorkManager's `ExistingWorkPolicy.REPLACE`, `KEEP`, and `APPEND`?"
    `REPLACE` cancels any existing work with the same unique name and starts fresh; `KEEP` ignores the new request if existing work is already enqueued/running; `APPEND` chains the new work to run after the existing work completes.

??? question "How would you chain multiple WorkManager tasks with dependencies?"
    Use `WorkManager.beginWith(workA).then(workB).enqueue()` to create a chain where `workB` only starts after `workA` succeeds, optionally passing output data between them via `InputMerger`.

??? question "What's the difference between CameraX and the legacy Camera2 API?"
    CameraX provides a simplified, lifecycle-aware abstraction (use cases like Preview, ImageCapture, ImageAnalysis) that handles device-specific quirks internally, while Camera2 gives lower-level, more verbose control requiring manual handling of device compatibility across manufacturers.

??? question "What is Media3/ExoPlayer used for, and why not just use Android's built-in `MediaPlayer`?"
    Media3 (successor combining ExoPlayer) supports adaptive streaming (DASH/HLS), custom track selection, extensible media source pipelines, and better format/DRM support than the basic `MediaPlayer`, which is limited and harder to customize for advanced playback scenarios.

??? question "What's the difference between a notification's 'data message' and 'notification message' in FCM?"
    A notification message has a predefined payload automatically displayed by the system tray when the app is backgrounded, with limited customization; a data message is delivered entirely to the app's code (even in background, within limits) letting the app fully control how/whether to display it, useful for custom notification logic or silent data sync.

??? question "What's a security implication of using FCM data messages vs notification messages?"
    Data messages are delivered to app code directly and could theoretically be spoofed/intercepted if not properly validated server-side with authenticated requests; notification messages rendered by the system reduce the app's exposure to malformed payloads but offer less control.

??? question "How do Notification Channels work, and why were they introduced?"
    Since Android 8, all notifications must belong to a Channel (defined once, typically at first app launch), letting users control importance/behavior (sound, vibration, visibility) per category rather than for the app as a whole, giving more granular user control.

??? question "What are the background execution limits introduced since Android 8, and how does WorkManager/Foreground Service work around them?"
    Apps in the background can no longer run arbitrary long-lived Services or receive most implicit broadcasts freely; WorkManager defers work respecting system constraints (via JobScheduler under the hood), and Foreground Services are explicitly exempted since they show a persistent user-visible notification.

??? question "What's the difference between exact and inexact alarms with `AlarmManager` on modern Android?"
    Inexact alarms (default) are batched by the system to save battery and may fire later than requested; exact alarms (`setExactAndAllowWhileIdle`) fire at a precise time but require special handling/permission on recent Android versions due to battery/security concerns around abuse.

## Permissions, Sensors, Location, Bluetooth, Camera & Hardware

??? question "What's the difference between install-time and runtime permissions?"
    Install-time (normal) permissions are granted automatically at install with no user prompt (low-risk, e.g., internet access); runtime (dangerous) permissions (camera, location, contacts) must be explicitly requested at runtime and can be granted/revoked by the user at any time, even after being granted previously.

??? question "What's the difference between `ACCESS_COARSE_LOCATION` and `ACCESS_FINE_LOCATION`, and how does Android let users choose between them?"
    Coarse gives approximate location (city-block level); fine gives precise GPS-level location; since Android 12, the system permission dialog lets users grant only approximate location even if the app requests fine, so apps must handle receiving coarse-only gracefully.

??? question "What's the difference between foreground and background location permission, and why was background location split out?"
    Foreground location works only while the app is visible/in use; background location (a separate, more heavily scrutinized permission/dialog since Android 10) is required for location access while the app isn't in the foreground, added to curb apps silently tracking users at all times.

??? question "How should an app handle a user permanently denying a permission ('don't ask again')?"
    Check `shouldShowRequestPermissionRationale()` — if false after a denial, the system won't show the prompt again, so the app should explain why the permission is needed and direct the user to app settings to grant it manually rather than repeatedly calling the request API.

??? question "What's the difference between Bluetooth Classic and Bluetooth Low Energy (BLE) from an Android API perspective?"
    Bluetooth Classic (`BluetoothSocket`) suits continuous higher-bandwidth data streams (e.g., audio); BLE (`BluetoothGatt`, GATT services/characteristics) is optimized for small, infrequent data exchanges with much lower power consumption, common for wearables/IoT sensors.

??? question "What's the difference between a sensor's 'batch' mode and continuous reporting in the SensorManager API?"
    Batching lets the sensor hardware buffer multiple readings and deliver them together at intervals (via `registerListener` with a `maxReportLatencyUs`), reducing wakeups and saving battery compared to continuous per-event delivery.

??? question "What's the difference between `Sensor.TYPE_ACCELEROMETER` and `Sensor.TYPE_LINEAR_ACCELERATION`?"
    The raw accelerometer includes gravity's constant contribution; linear acceleration is a derived/software sensor with gravity's effect filtered out, giving just the acceleration due to actual movement.

??? question "How does CameraX's `ImageAnalysis` use case support real-time processing (e.g., for ML Kit barcode scanning)?"
    It delivers a continuous stream of `ImageProxy` frames to an analyzer callback on a background executor, letting you run per-frame processing (e.g., feeding to an ML Kit detector) without manually managing a `Camera2` capture session.

??? question "What's the difference between NFC reader mode and Host Card Emulation (HCE) on Android?"
    Reader mode lets the app actively read data from NFC tags/other devices; HCE lets the Android device itself emulate a smart card, responding to reader requests from an external NFC terminal (e.g., for mobile payments), a fundamentally different role in the NFC interaction.

??? question "What's the difference between ML Kit's on-device and cloud-based APIs?"
    On-device APIs run entirely locally (faster, works offline, no data leaves the device, but sometimes less accurate/limited model capability); cloud-based APIs send data to Google's servers for processing (often more accurate/powerful, but requires network and raises data-privacy considerations).

## Notifications, Widgets, Wear/TV/Auto & Large Screens

??? question "What's the difference between `NotificationCompat.Builder.setContentIntent()` and `.setFullScreenIntent()`?"
    `setContentIntent` fires when the user taps the notification normally; `setFullScreenIntent` can launch a full-screen Activity immediately even over the lock screen, reserved for high-priority interruptive cases like incoming calls or alarms, and is heavily restricted/deprioritized on modern Android to prevent abuse.

??? question "What is a Notification's 'importance' level, and who ultimately controls it after channel creation?"
    Importance controls how intrusive a notification is (sound, heads-up display, etc.); once a Notification Channel is created with an initial importance, only the user (via system settings) can change it afterward — the app cannot silently escalate importance later.

??? question "What's the difference between a 'foreground service type' like `location` vs `mediaPlayback`, required since recent Android versions?"
    Each Foreground Service must declare its specific type in the manifest, which determines what capabilities/exemptions it's granted and subjects it to type-specific runtime restrictions (e.g., a `location` type FGS requires location permission already granted), improving system-level accountability for why a service is running.

??? question "What is an `AppWidgetProvider`, and what's its main lifecycle constraint?"
    A `BroadcastReceiver` subclass that receives periodic/lifecycle updates (`onUpdate`, `onEnabled`, `onDisabled`) for a home-screen widget; widgets have no persistent running component, so all updates must go through `AppWidgetManager` pushing RemoteViews rather than the widget hosting live app code continuously.

??? question "How do Jetpack Glance widgets differ from classic RemoteViews-based widgets?"
    Glance lets you define widget UI using Compose-like composable functions, which are then translated into RemoteViews under the hood automatically, avoiding manual RemoteViews XML/layout management.

??? question "What's a key constraint of RemoteViews that limits what a widget/notification's custom layout can contain?"
    RemoteViews only supports a restricted subset of Views/ViewGroups (no arbitrary custom Views) since the layout is inflated and rendered in a different process (the home screen/launcher or system UI), not the app's own process.

??? question "What's different about designing UI for Wear OS compared to phone UI?"
    Much smaller screens (often round), reliance on Wear-specific Compose components (`ScalingLazyColumn`, curved text) designed for glanceability, rotary input (bezel/crown) support, and stricter battery/performance constraints given tiny hardware.

??? question "What's different about developing for Android TV compared to phone/tablet apps?"
    D-pad/remote-based navigation instead of touch (requiring clear focus states and `Modifier`/View focus handling), the '10-foot UI' design principle (larger text/spacing viewed from a distance), and the Leanback library or TV-specific Compose components for TV-appropriate layouts.

??? question "What's different about Android Auto app development compared to a normal phone app?"
    Apps must use Android Auto's constrained templated UI APIs (for driving-safety reasons, not free-form custom layouts) via the Car App Library, limiting complexity/interaction to what's safe to use while driving.

??? question "What's the difference between designing for a foldable's 'unfolded' vs 'folded' state, and what API helps detect it?"
    The `WindowManager` Jetpack library's `WindowInfoTracker`/`FoldingFeature` reports the device's fold state/hinge position, letting the app adapt layout (e.g., switching from single-pane to a two-pane view straddling the hinge) reactively as the fold state changes.

??? question "What is Window Size Classes, and why are they recommended over raw pixel/dp breakpoints for adaptive layouts?"
    They bucket available width/height into Compact/Medium/Expanded categories recommended by Material guidelines, giving a consistent adaptive layout strategy across phones, foldables, and tablets rather than hardcoding arbitrary dp breakpoints per device type.

## Scoped Storage, MediaStore & Storage Access Framework

??? question "What is Scoped Storage (introduced Android 10, enforced later), and how does it change file access?"
    Apps are restricted to their own app-specific directory and must use `MediaStore`/`SAF` APIs to access shared media/documents outside it, rather than freely reading/writing arbitrary paths on external storage as before, improving user privacy and reducing storage clutter from uninstalled apps.

??? question "What's the difference between an app's internal storage and app-specific external storage directories?"
    Internal storage (`getFilesDir()`) is private, sandboxed, and removed automatically on uninstall; app-specific external storage (`getExternalFilesDir()`) may be visible to the user via a file manager but is still tied to your app's package and removed on uninstall, unlike shared external storage which persists.

??? question "What is the Storage Access Framework (SAF), and when would you use it instead of `MediaStore`?"
    SAF lets the user pick any file/folder via a system picker UI (`ACTION_OPEN_DOCUMENT`/`ACTION_CREATE_DOCUMENT`), granting your app a persistent URI permission to that specific location; use it for general document access (any file type/location) versus `MediaStore` which is specifically for structured media (photos, videos, audio) with rich queryable metadata.

??? question "How do you write a new image to the shared Photos library under Scoped Storage?"
    Insert a new row via `MediaStore.Images.Media` with a `ContentValues` describing metadata, obtain the returned content URI, and write the actual bytes to that URI's `OutputStream` via the `ContentResolver` — you don't get a raw file path anymore for shared storage.

??? question "What's the difference between a persistable URI permission and a normal Intent-granted URI permission?"
    A normal grant (e.g., from a picker result) is typically valid only for the current app session/task; calling `takePersistableUriPermission()` retains access across app restarts/reboots for URIs obtained via SAF, until explicitly released.

## Battery, Doze Mode & Background Restrictions

??? question "What is Doze mode, and how does it throttle background app behavior?"
    When the device is stationary, unplugged, and screen-off for a while, the system enters Doze, deferring network access, sync jobs, and standard alarms into periodic short 'maintenance windows' to conserve battery, with exemptions for high-priority FCM messages and a few other cases.

??? question "What is App Standby Buckets, and how does an app's bucket affect it?"
    The system classifies apps into buckets (active, working set, frequent, rare, restricted) based on usage patterns, throttling background job/alarm/network frequency more aggressively for less-used apps (e.g., a 'rare' bucket app gets far fewer background execution opportunities per day).

??? question "How would you test your app's behavior under Doze mode during development?"
    Use `adb shell dumpsys deviceidle force-idle` (and related deviceidle commands) to simulate Doze on a test device/emulator without waiting for the real inactivity timeout, then verify background work still eventually completes appropriately via WorkManager rather than being silently dropped.

??? question "What's the difference between a 'wakelock' and simply doing work on a background thread?"
    A wakelock (`PowerManager.WakeLock`) explicitly keeps the CPU (and optionally screen) awake even if the user isn't interacting with the device, overriding normal sleep behavior; background thread work alone doesn't prevent the whole device from sleeping if nothing else is keeping it awake, potentially pausing your work mid-execution.

??? question "Why are 'stuck' or excessively held wakelocks flagged as a problem in Android Vitals?"
    They directly drain battery by preventing the device from sleeping even when not actually needed, often due to a bug (forgetting to release the wakelock) — Google surfaces this metric because it's a common, high-impact class of battery-drain bug.

??? question "What's the difference between JobScheduler used directly versus through WorkManager?"
    WorkManager is a higher-level abstraction that uses JobScheduler (on newer API levels) or AlarmManager/BroadcastReceiver (as fallback on older APIs) internally, providing a single consistent API, built-in retry/backoff, chaining, and persistence across reboots that raw JobScheduler doesn't handle for you directly.

??? question "What is 'expedited work' in WorkManager, and how does it differ from regular deferred work?"
    Expedited work requests to run nearly immediately (subject to system quota, using JobScheduler's expedited jobs or a foreground service fallback on older APIs) rather than waiting for typical background execution windows, suited for user-visible, time-sensitive tasks that still need OS-managed constraints.

## Insets, Predictive Back, PiP & Modern UI Surfaces

??? question "What is edge-to-edge display, and what changed in recent Android versions regarding it?"
    Content drawing behind the system status/navigation bars for an immersive look; recent Android versions (targeting API 35+) make edge-to-edge the enforced default, requiring apps to explicitly handle `WindowInsets` themselves rather than relying on the system to automatically pad content away from system bars.

??? question "What's the difference between `WindowInsetsCompat` handling in the classic View system versus Compose's `WindowInsets`?"
    The View system uses `ViewCompat.setOnApplyWindowInsetsListener` to manually read/consume insets and adjust padding on specific views; Compose provides insets as composable-friendly values (`WindowInsets.statusBars`, etc.) that can be applied directly as `Modifier.windowInsetsPadding()`, integrating more naturally with recomposition.

??? question "What is the Predictive Back gesture, and what must an app do to support it correctly?"
    It shows a live preview/animation of what screen the back gesture will reveal before the user commits to it; apps must opt in (`android:enableOnBackInvokedCallback="true"`) and migrate from the older `onBackPressed()` override to the `OnBackPressedCallback`/`PredictiveBackHandler` APIs that support the animated, cancellable back gesture.

??? question "What's the difference between the legacy `Activity.onBackPressed()` override and `OnBackPressedDispatcher`/`OnBackPressedCallback`?"
    The dispatcher lets multiple components (Fragments, individual UI elements) register their own back-handling callback with priority ordering, rather than a single monolithic Activity override having to know about every possible in-app back behavior.

??? question "What is Picture-in-Picture (PiP) mode, and what's required to support it?"
    A floating, resizable mini-window mode (typically for video playback) that keeps an Activity visible while the user navigates elsewhere; requires declaring `android:supportsPictureInPicture="true"` and calling `enterPictureInPictureMode()` with appropriate `PictureInPictureParams` (aspect ratio, actions).

??? question "What's the difference between App Shortcuts types: static, dynamic, and pinned?"
    Static shortcuts are declared in a manifest XML resource (fixed, defined at build time); dynamic shortcuts are created/updated at runtime via `ShortcutManager` based on app usage/context; pinned shortcuts are explicitly added by the user to their home screen and persist independently even if the app later removes it from its own dynamic list.

??? question "What's the difference between an Adaptive Icon and a Themed (Monochrome) Icon?"
    An adaptive icon provides separate foreground/background layers so the system can apply different mask shapes (circle, squircle, etc.) consistently across devices; a themed/monochrome icon (Android 13+) provides a single-color silhouette layer the system can tint to match the user's chosen wallpaper-based theme color for a cohesive home screen look.

??? question "What's the difference between 'multi-window' (split-screen/freeform) support and simple responsive layout handling?"
    Multi-window support requires handling the Activity being resized dynamically at runtime (not just at launch) while potentially not having focus, and correctly persisting/restoring state as available space changes continuously — a superset of just having a responsive layout that reacts to a single fixed size at composition time.

## Accessibility Services, IME, Autofill & System Integration APIs

??? question "What's the difference between building a regular app with accessibility support (contentDescription, semantics) and building an Accessibility Service?"
    Regular apps expose accessibility metadata *for* assistive technologies to consume; an Accessibility Service is itself an assistive technology component that observes/interacts with *other* apps' UI trees system-wide (e.g., a screen reader or a custom automation tool), requiring a special, highly-scrutinized permission grant.

??? question "What is a custom Input Method Editor (IME/keyboard), and what's the core API surface it must implement?"
    An app implementing `InputMethodService`, providing a custom keyboard UI and handling text input/composition, registered via the system's input method framework so users can select it as their system keyboard in settings.

??? question "What is the Android Autofill Framework, and how does an app opt in to work well with it?"
    A system service that offers to save/fill form data (passwords, addresses) across apps; an app improves autofill behavior by setting appropriate `android:autofillHints` on input fields and, for more control, implementing a custom `AutofillService` if building a password-manager-type app.

??? question "What's the difference between Android's built-in Speech-to-Text (`SpeechRecognizer`) and Text-to-Speech (`TextToSpeech`) APIs in terms of what they each require/produce?"
    `SpeechRecognizer` takes microphone audio input and produces recognized text (often via an on-device or cloud model, depending on device support); `TextToSpeech` takes text input and produces synthesized spoken audio output — inverse directions of the same general speech-interaction capability.

??? question "What's the difference between a Quick Settings Tile and a regular App Widget?"
    A Quick Settings Tile lives in the system's pull-down quick settings panel for fast toggles/shortcuts to app functionality (implemented via `TileService`), accessible without opening the app or leaving the current screen; an App Widget lives on the home screen and typically shows richer, more persistent glanceable content.

## WorkManager Limits, App Startup Ordering & StrictMode Policies

??? question "What's the size limit on WorkManager's input/output `Data` object, and why does it exist?"
    Data passed to/from a `Worker` is serialized through the same underlying persistence/IPC mechanisms with a small size cap (a few hundred KB, historically similar to Binder-related limits); large payloads should instead be written to a file/DB and only a reference (ID/path) passed through WorkManager's Data.

??? question "How does the Jetpack App Startup library determine initialization order among multiple `Initializer`s?"
    Each `Initializer` declares its dependencies on other Initializers via `dependencies()`, and App Startup topologically sorts and runs them in the correct order during a single ContentProvider-triggered pass, rather than each library registering its own separate ContentProvider with implicit, harder-to-control ordering.

??? question "What's the difference between `StrictMode.ThreadPolicy` and `StrictMode.VmPolicy`?"
    `ThreadPolicy` flags problematic operations on a specific thread (like disk/network access on the main thread); `VmPolicy` flags process-wide issues not tied to a specific thread's operations, like leaked `Closeable` objects (unclosed cursors/streams) or leaked `Activity` instances via `detectActivityLeaks()`.

??? question "What's the difference between an Instant App and a regular app requiring installation?"
    An Instant App lets a user launch a lightweight, modularized slice of app functionality directly from a link or Play Store 'Try Now' without a full install, useful for frictionless first-touch experiences, though the feature has seen reduced platform emphasis/investment in recent years compared to when it launched.

??? question "What's the difference between reconnect-with-backoff strategy for a dropped WebSocket versus for a gRPC streaming call?"
    Both generally need exponential backoff with jitter to avoid thundering-herd reconnect storms after an outage, but gRPC's structured streaming (with defined message framing and status codes) makes it easier to distinguish a clean stream-end from an actual connection failure, whereas raw WebSocket reconnection logic must handle more ambiguous low-level socket closure reasons itself.

??? question "What's a design consideration for a multi-module app where several feature modules each need their own Room database versus one single shared database?"
    A single shared database simplifies cross-feature queries/joins and transactional consistency but couples schema migrations across all features; separate per-feature databases isolate schema evolution and reduce coupling but complicate any cross-feature data relationships, which would then need to be resolved at the repository/use-case layer instead of via SQL joins.

## Parcelable, Serialization & IPC Data Transfer

??? question "What's the difference between `Parcelable` and `Serializable` for passing objects between Android components?"
    `Parcelable` requires explicit implementation (or the `@Parcelize` compiler plugin) but is significantly faster since it avoids reflection, designed specifically for Android's IPC; `Serializable` is the standard Java mechanism using reflection, simpler to implement but slower and produces more garbage during serialization.

??? question "What does the `@Parcelize` annotation do?"
    It's a Kotlin compiler plugin annotation that auto-generates the boilerplate `Parcelable` implementation (`writeToParcel`, `CREATOR`) for a data class, as long as all its properties are themselves Parcelable-compatible types.

??? question "What is `TransactionTooLargeException` and when does it occur?"
    It's thrown when data passed via Binder IPC (e.g., an Intent's extras, or a Bundle passed between processes) exceeds the transaction buffer size limit (historically ~1MB shared across all in-flight transactions); avoid it by passing IDs/references instead of large objects/bitmaps directly through Intents.

??? question "Why is passing a large Bitmap directly as an Intent extra considered bad practice?"
    Beyond the `TransactionTooLargeException` risk from Binder's size limit, it also unnecessarily duplicates the bitmap's memory across the IPC transaction; better to pass a URI/file path/cache key and have the receiving component load the bitmap itself.

??? question "What's the difference between `Bundle.putSerializable()` and `Bundle.putParcelable()` regarding cross-process safety?"
    Both work across processes since Bundle transport is Binder-based, but Serializable's reflection-based deserialization is slower and can throw `ClassNotFoundException` if the receiving process doesn't have the exact same class definition available (e.g., differing app versions/modules).
