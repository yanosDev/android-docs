# System Design

Collapsed by default — try to answer before revealing.

## System Design Scenarios

??? question "How would you design a chat feature that needs to work offline and sync later, at a high level?"
    Local Room DB as the source of truth for messages with a 'pending/sent/failed' status per message; WorkManager (or a persistent connection like WebSocket when online) handles delivery; optimistic UI shows sent messages immediately, updating status once the server acknowledges; incoming messages arrive via push/WebSocket and are written to the same DB, which the UI observes via Flow.

    ```kotlin
    data class Message(val id: String, val text: String, val status: SyncStatus)
    enum class SyncStatus { PENDING, SENT, FAILED }
    ```

??? question "How would you design an image-heavy feed (like a social media timeline) for smooth scrolling performance?"
    Paging 3 for incremental loading, an image loading library (Coil/Glide) with memory+disk caching and appropriately downsampled bitmap requests matching the actual display size, stable RecyclerView/LazyColumn item keys, and prefetching upcoming images slightly ahead of scroll position.

    ```kotlin
    val pager = Pager(PagingConfig(pageSize = 20)) { FeedPagingSource(api) }
    ```

??? question "How would you design a feature flag/remote config system for gradual rollouts, at a system level?"
    A backend service assigns users to rollout buckets (by percentage or explicit segment) and serves flag values via a config endpoint; the client caches the last-fetched config locally with a safe default, refreshes periodically/on app start, and the app reads flags reactively so behavior can change without requiring a restart where feasible.

    ```kotlin
    data class FeatureFlags(val newCheckout: Boolean = false) // safe default bundled in-app
    val flags: Flow<FeatureFlags> = remoteConfig.observe()
    ```

??? question "How would you architect background location tracking (e.g., for a delivery app) considering battery and OS restrictions?"
    A Foreground Service (with the required location foreground service type declared) for active tracking sessions showing a persistent notification, using an appropriately battery-conscious location request interval, buffering location updates locally and syncing periodically rather than on every update, and stopping tracking immediately when not needed.

    ```kotlin
    class LocationTrackingService : Service() {
        override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
            startForeground(NOTIF_ID, buildNotification())
            return START_STICKY
        }
    }
    ```

??? question "How would you design a robust 'download and cache large files' (e.g., offline video/maps) feature?"
    WorkManager for the download with network/storage constraints and retry/backoff, writing to a temp file and atomically renaming on completion to avoid partial/corrupt files, tracking progress via `WorkInfo`/`setProgress`, and validating checksums post-download before marking content as usable offline.

    ```kotlin
    class DownloadWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
        override suspend fun doWork(): Result {
            setProgress(workDataOf("percent" to 0))
            // download to a temp file, then atomically rename on success
            return Result.success()
        }
    }
    ```

??? question "How would you design a system to support A/B testing of a new feature across app versions?"
    A remote config/experimentation service assigns users to variants (consistently per user, e.g., via a stable hashed user ID), the app reads its assigned variant at a defined point (e.g., app start) and renders the corresponding UI/behavior, and analytics events are tagged with the variant for later analysis — care taken that variant assignment doesn't change mid-session.

    ```kotlin
    val variant = experimentService.assignVariant(userId) // stable per user, e.g. hash(userId) % buckets
    analytics.log("checkout_viewed", mapOf("variant" to variant))
    ```

??? question "How would you handle a payment/checkout flow reliably against network flakiness (avoiding double charges)?"
    Generate an idempotency key client-side per checkout attempt sent with the request, so retries of the same logical transaction are recognized and deduplicated server-side, combined with clear UI states preventing the user from re-tapping 'Pay' while a request is in flight.

    ```kotlin
    val idempotencyKey = UUID.randomUUID().toString()
    api.charge(CheckoutRequest(amount, idempotencyKey)) // server dedupes retries by this key
    ```

??? question "How would you design push notification handling to avoid showing stale/irrelevant notifications after the user has already read the content elsewhere?"
    Include a content version/ID in the payload; on notification tap or app foreground, check current state against the latest known state and suppress/clear the notification if it's already stale, using `NotificationManager.cancel()` proactively when the underlying content changes.

    ```kotlin
    data class PushPayload(val contentId: String, val contentVersion: Int)
    if (payload.contentVersion < localVersion) notificationManager.cancel(NOTIF_ID)
    ```

??? question "How would you design a large form (e.g., a multi-step onboarding) that must survive process death without losing user input?"
    Persist each field/step's input incrementally to `SavedStateHandle` (or a lightweight local DB/DataStore draft) rather than relying purely on in-memory ViewModel state, so a system-initiated process death and later recreation restores the user's progress rather than forcing a restart.

    ```kotlin
    class OnboardingViewModel(private val savedState: SavedStateHandle) : ViewModel() {
        var currentStep: Int
            get() = savedState["step"] ?: 0
            set(value) { savedState["step"] = value } // survives process death
    }
    ```

## Advanced System Design Scenarios

??? question "How would you design an offline-capable maps feature with downloadable regions?"
    Store map tiles/vector data for downloaded regions in local storage (indexed by region ID), use WorkManager for the background download with progress tracking, serve rendering from local storage first with an online fallback for undownloaded areas, and periodically check for tile-data updates.

    ```kotlin
    data class MapRegion(val id: String, val bounds: LatLngBounds, val downloaded: Boolean)
    ```

??? question "How would you design a video streaming feature that must handle variable network conditions gracefully?"
    Use adaptive bitrate streaming (DASH/HLS) via Media3/ExoPlayer, which automatically switches quality based on measured bandwidth, combine with a prebuffering strategy tuned to balance startup latency vs rebuffering risk, and surface network-quality-aware UI (e.g., a lower-quality warning) rather than silent stalls.

    ```kotlin
    val trackSelector = DefaultTrackSelector(context) // ExoPlayer adapts bitrate to bandwidth
    val player = ExoPlayer.Builder(context).setTrackSelector(trackSelector).build()
    ```

??? question "How would you design a ride-hailing app's real-time driver-location tracking feature?"
    A persistent WebSocket (or MQTT) connection while a ride is active for low-latency location pushes, a Foreground Service with the `location` type to keep tracking alive reliably, throttled/batched location updates to balance accuracy vs battery, and graceful reconnection/backoff handling if the connection drops mid-ride.

    ```kotlin
    class DriverLocationService : Service() {
        // persistent WebSocket connection + Foreground Service with type="location"
    }
    ```

??? question "How would you design an e-commerce app's checkout flow to handle app kill mid-purchase gracefully?"
    Persist checkout progress (cart state, selected shipping/payment) to local storage incrementally rather than only in memory, use an idempotency key for the actual payment submission so a retry after recovery doesn't double-charge, and reconcile the local 'pending' state against the backend's authoritative order status on next app launch.

    ```kotlin
    data class CheckoutDraft(val cartId: String, val shippingId: String?, val status: CheckoutStatus)
    enum class CheckoutStatus { DRAFT, SUBMITTING, PENDING_RECONCILE, CONFIRMED }
    ```

??? question "How would you design a social feed with real-time updates (new posts, likes) without excessive battery/network use?"
    A combination of a lightweight push notification (or WebSocket) signaling 'new content available' rather than continuously polling, with the actual feed refresh happening on-demand (pull-to-refresh) or the next time the user opens/returns to that screen, avoiding constant background polling.

    ```kotlin
    // push signal "new content available" -> UI shows a "New posts" banner
    // actual data refresh happens on tap / next app open, never continuous polling
    ```

??? question "How would you design a multi-tenant app that needs to support white-labeled branding for different clients from one codebase?"
    Product flavors (or a runtime remote-config-driven theming layer) per client controlling colors/logos/strings, a shared core module containing all business logic, and a resource-overlay or dynamic theming mechanism so branding differences don't require duplicating feature code per client.

    ```gradle
    productFlavors {
        create("clientA") { applicationIdSuffix = ".clienta" }
        create("clientB") { applicationIdSuffix = ".clientb" }
    }
    ```

??? question "How would you design a robust in-app update mechanism that doesn't force users into an interruptive flow for minor updates?"
    Use the Play Core In-App Updates API's 'flexible' flow for non-critical updates (downloads in the background, prompts to install at a convenient moment) versus the 'immediate' flow only for critical/security updates that must block continued use until updated.

    ```kotlin
    appUpdateManager.startUpdateFlowForResult(
        info, AppUpdateType.FLEXIBLE, activity, REQUEST_CODE // vs IMMEDIATE for critical updates
    )
    ```

??? question "How would you design analytics event tracking to avoid both under- and over-instrumentation?"
    Define a small, deliberate taxonomy of events tied to actual product questions/decisions (not 'track everything just in case'), centralize event-firing through a single typed interface/wrapper (avoiding scattered raw string event names), and periodically audit for events that are never actually queried/used.

    ```kotlin
    interface AnalyticsEvent { val name: String }
    data class CheckoutViewed(val cartSize: Int) : AnalyticsEvent { override val name = "checkout_viewed" }
    ```
