# Networking

Collapsed by default — try to answer before revealing.

## Networking (Retrofit/OkHttp)

??? question "How do OkHttp interceptors work, and what's the difference between application and network interceptors?"
    Interceptors form a chain that can inspect/modify requests and responses; application interceptors run once per call regardless of retries/redirects and don't see redirected/retried requests, while network interceptors run per actual network request (including redirects/retries) and can observe/modify the raw wire-level request/response, including compression.

    ```kotlin
    class AuthInterceptor : Interceptor {              // application interceptor
        override fun intercept(chain: Interceptor.Chain): Response {
            val request = chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
            return chain.proceed(request)
        }
    }
    ```

??? question "Give an example use case for an OkHttp interceptor."
    Adding an `Authorization` header to every outgoing request automatically, or logging request/response details for debugging (`HttpLoggingInterceptor`).

    ```kotlin
    val client = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY })
        .build()
    ```

??? question "How would you implement transparent auth token refresh for concurrent requests?"
    Use OkHttp's `Authenticator` interface, synchronizing the refresh call (e.g., with a lock/mutex) so concurrent 401 responses trigger only one refresh request while others wait and reuse the new token, then retry the original requests.

    ```kotlin
    class TokenAuthenticator(private val mutex: Mutex) : Authenticator {
        override fun authenticate(route: Route?, response: Response): Request {
            val newToken = runBlocking { mutex.withLock { refreshToken() } } // only one refresh at a time
            return response.request.newBuilder()
                .header("Authorization", "Bearer $newToken")
                .build()
        }
    }
    ```

??? question "What is certificate pinning, and when would you use it?"
    Restricting which certificate(s)/public keys are trusted for a given host beyond the system's CA trust store, mitigating MITM attacks even if a rogue CA is compromised; used for high-security apps (banking, sensitive data) but requires a plan for pin rotation to avoid bricking connectivity on cert renewal.

    ```kotlin
    val client = OkHttpClient.Builder()
        .certificatePinner(
            CertificatePinner.Builder()
                .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
                .build()
        )
        .build()
    ```

??? question "What's the difference between Retrofit's `Call<T>` and `suspend fun` return types?"
    `Call<T>` requires manual `enqueue`/`execute` and callback handling; a `suspend fun` return type lets Retrofit integrate directly with coroutines, suspending until the response arrives without manual callback boilerplate.

    ```kotlin
    interface Api {
        @GET("users") fun getUsersCall(): Call<List<User>>  // manual enqueue/execute
        @GET("users") suspend fun getUsers(): List<User>    // coroutine-integrated
    }
    ```

??? question "What is a Retrofit `Converter.Factory` and give an example."
    It defines how request/response bodies are serialized/deserialized (e.g., `MoshiConverterFactory`, `GsonConverterFactory`, `kotlinx-serialization` converter) — pluggable so Retrofit isn't tied to one JSON library.

    ```kotlin
    Retrofit.Builder()
        .addConverterFactory(MoshiConverterFactory.create()) // pluggable serialization
        .build()
    ```

??? question "What's the difference between JSON parsing via reflection (Gson) and codegen (Moshi with kapt/KSP, or kotlinx.serialization)?"
    Reflection-based parsing (Gson) inspects fields at runtime, which is slower and can silently mis-handle Kotlin non-null guarantees; codegen-based approaches generate adapter code at compile time, which is faster, catches issues earlier, and better respects Kotlin null-safety and default values.

    ```kotlin
    // Gson: reflects on User's fields at runtime to populate them
    // Moshi (KSP) / kotlinx.serialization: generates a real JsonAdapter at COMPILE time
    ```

??? question "Why might Gson's reflection-based parsing cause a runtime crash on a Kotlin non-null field that's missing in JSON?"
    Gson can bypass Kotlin's constructor validation via reflection, setting a "non-null" field to null anyway if absent in the JSON, leading to a `NullPointerException` later when that field is used, rather than failing fast at parse time.

    ```kotlin
    data class User(val name: String) // non-null in Kotlin
    // Gson can still construct User(name = null) via reflection if "name" is missing from JSON —
    // crashes later, at `user.name.length`, not at parse time
    ```

??? question "What's the difference between caching strategies: cache-then-network, network-then-cache, and stale-while-revalidate?"
    Cache-then-network shows cached data first then updates with fresh data (fast but shows stale info briefly); network-then-cache waits for network before showing anything (accurate but slower/no offline); stale-while-revalidate serves cached data immediately while fetching fresh data in the background to update for next time.

    ```kotlin
    // cache-then-network:     emit(cache); emit(network)
    // network-then-cache:     emit(network)
    // stale-while-revalidate: emit(cache); launch { emit(network) } // refresh in the background
    ```

??? question "What's the difference between HTTP cache headers (`Cache-Control`) handled by OkHttp automatically vs a custom local DB cache?"
    OkHttp's built-in HTTP cache respects server cache headers for raw HTTP responses (byte-level caching on disk); a custom DB cache (e.g., Room) stores parsed domain objects and gives you full control over caching policy, offline querying, and merging with local app state, independent of server cache headers.

    ```kotlin
    val client = OkHttpClient.Builder()
        .cache(Cache(cacheDir, 10L * 1024 * 1024)) // raw HTTP responses, respects Cache-Control
        .build()
    // vs: Room stores parsed User objects, with your own caching policy
    ```

??? question "What's the difference between HTTP/1.1, HTTP/2, and how does OkHttp/Retrofit leverage HTTP/2?"
    HTTP/2 supports multiplexing multiple requests over a single TCP connection, header compression, and server push; OkHttp negotiates HTTP/2 automatically via TLS ALPN when the server supports it, reducing connection overhead for apps making many concurrent requests.

    ```kotlin
    // No code change needed — OkHttp negotiates HTTP/2 automatically via TLS ALPN
    // when the server supports it, multiplexing requests over one connection.
    ```

??? question "What is gRPC and how does it differ from a typical REST/JSON API for mobile use?"
    gRPC uses Protocol Buffers (binary, schema-defined) over HTTP/2 with strongly-typed generated client/server code and supports streaming natively; it's more efficient (smaller payloads, less parsing overhead) than REST/JSON but requires more tooling/infra investment and is less human-readable for debugging.

    ```protobuf
    service UserService {
      rpc GetUser(UserRequest) returns (UserResponse); // schema-defined, binary, HTTP/2
    }
    ```

??? question "How would you handle exponential backoff retry for failed network requests using Flow?"
    Use `retryWhen` on the Flow, checking the attempt count and exception type, and `delay()` with an increasing backoff duration (e.g., `2^attempt * baseDelay`) before allowing the retry to proceed.

    ```kotlin
    fun fetchWithRetry() = flow { emit(api.fetch()) }
        .retryWhen { _, attempt ->
            if (attempt < 3) { delay(2.0.pow(attempt.toInt()).toLong() * 1000); true } else false
        }
    ```

??? question "What's the difference between a timeout at the OkHttp client level vs a coroutine `withTimeout`?"
    OkHttp timeouts (`connectTimeout`, `readTimeout`, `writeTimeout`) control the underlying socket/connection behavior itself; `withTimeout` is a coroutine-level cancellation that can wrap any suspend call (network or otherwise) regardless of what timeout mechanisms exist underneath.

    ```kotlin
    val client = OkHttpClient.Builder().readTimeout(10, TimeUnit.SECONDS).build() // socket-level

    withTimeout(5_000) { api.fetch() } // coroutine-level, wraps any suspend call
    ```

??? question "What's a WebSocket and when would you use one instead of polling/REST?"
    A persistent, full-duplex connection allowing the server to push data anytime without the client repeatedly requesting; useful for real-time features (chat, live updates) where polling would be inefficient or too high-latency.

    ```kotlin
    val request = Request.Builder().url("wss://example.com/chat").build()
    client.newWebSocket(request, object : WebSocketListener() {
        override fun onMessage(webSocket: WebSocket, text: String) { /* server pushed data */ }
    })
    ```

??? question "How would you detect and handle 'no network connectivity' gracefully in an app's architecture?"
    Observe `ConnectivityManager` network callbacks (or a Flow wrapper around it) to expose connectivity state to the Repository/UI layer, allowing the UI to show an offline indicator and the Repository to serve cached data or queue writes instead of failing network calls outright.

    ```kotlin
    val request = NetworkRequest.Builder().build()
    connectivityManager.registerNetworkCallback(request, object : ConnectivityManager.NetworkCallback() {
        override fun onLost(network: Network) { /* update UI to offline */ }
    })
    ```

## Retrofit Internals, OkHttp EventListener & Compose Testing Performance

??? question "What is a Retrofit `CallAdapter.Factory`, and why would you write a custom one?"
    It adapts Retrofit's internal `Call<T>` execution into a different return type (e.g., `Flow<T>`, `Deferred<T>`, or a custom `Result`-wrapping type); a custom one is useful when you want a project-wide return type convention (e.g., every network call returns your own sealed `ApiResult<T>`) not provided by Retrofit's built-in adapters.

    ```kotlin
    class ApiResultCallAdapterFactory : CallAdapter.Factory() {
        // adapts Call<T> into, e.g., Call<ApiResult<T>>
    }
    ```

??? question "What is OkHttp's `EventListener`, and what's a practical use case for implementing one?"
    A hook into the low-level lifecycle of a call (DNS lookup start/end, connection start/end, TLS handshake, request/response body timing); a practical use is capturing granular network performance metrics per request (e.g., feeding into your own APM/telemetry pipeline) without needing to guess timings indirectly.

    ```kotlin
    val client = OkHttpClient.Builder()
        .eventListenerFactory { object : EventListener() {
            override fun dnsStart(call: Call, domainName: String) { /* record timing */ }
        }}
        .build()
    ```

??? question "What's the difference between RecyclerView's `stableIds` feature and just relying on `DiffUtil`'s item callback?"
    `setHasStableIds(true)` combined with overriding `getItemId()` gives RecyclerView a persistent identity per item usable for animations/state association across dataset changes at the adapter level; `DiffUtil`'s `areItemsTheSame()` similarly identifies logical item identity for diffing purposes but is evaluated per diff computation, not stored as a persistent adapter-level id — the two mechanisms address a similar concern from different layers and are often used together.

    ```kotlin
    adapter.setHasStableIds(true)
    override fun getItemId(position: Int) = items[position].id // persistent per-item identity
    ```

??? question "How would you unit test a ViewModel that reads a navigation argument via `SavedStateHandle`?"
    Construct a `SavedStateHandle` directly with the expected key/value (e.g., `SavedStateHandle(mapOf("id" to 42))`) and pass it into the ViewModel's constructor in the test, avoiding the need for a real Activity/Fragment/Navigation setup.

    ```kotlin
    val handle = SavedStateHandle(mapOf("id" to 42))
    val viewModel = UserViewModel(handle) // no real Activity/Fragment needed
    ```

??? question "How does `TestScope`/`runTest`'s virtual clock let you test time-based Flow operators like `debounce()` deterministically?"
    The `TestScheduler` backing `runTest` lets you (or the coroutine machinery automatically) advance virtual time instantly rather than waiting real wall-clock time, so a 300ms `debounce()` resolves instantly in the test while still correctly exercising the debounce logic's timing-dependent behavior.

    ```kotlin
    @Test
    fun `debounce resolves without a real wait`() = runTest {
        val results = textChanges.debounce(300).toList() // virtual clock — no real 300ms delay
    }
    ```

??? question "What is the Database Inspector in Android Studio used for?"
    Live inspection and ad hoc SQL querying of a running app's SQLite/Room database directly from the IDE while debugging, without needing to manually pull the DB file off the device or add temporary logging code to inspect its contents.

??? question "What do the colored borders shown by Layout Inspector's 'recomposition counts' feature indicate?"
    They visually highlight which composables recomposed and how many times during a captured session, with color/count intensity helping quickly spot composables recomposing far more often than expected, guiding where to investigate stability/skippability issues.

## GraphQL, State Management Libraries & UI Test Frameworks

??? question "What's the difference between REST and GraphQL for mobile client data fetching?"
    REST typically exposes fixed-shape endpoints per resource (often requiring multiple round trips or over-fetching unrelated fields); GraphQL lets the client specify exactly which fields it needs in a single query across related resources, reducing over/under-fetching at the cost of more complex server-side query resolution and client-side caching normalization.

    ```graphql
    query {
      user(id: "1") { name email } # client picks exactly the fields it needs
    }
    ```

??? question "What's a common challenge with caching GraphQL responses compared to REST's HTTP-cache-header-based caching?"
    GraphQL typically uses a single POST endpoint for all queries, bypassing standard HTTP caching semantics tied to GET URLs; clients (e.g., Apollo) instead implement normalized in-memory/local caches keyed by object IDs extracted from the response, which is more powerful but more complex to reason about than simple HTTP caching.

    ```kotlin
    // Apollo normalizes the cache by object id, not by URL:
    // cache["User:1"] = User(name = "Ada")
    ```

??? question "What is the Mobius/Orbit MVI framework pattern, and what problem does it solve beyond a hand-rolled sealed-state reducer?"
    These libraries formalize the MVI loop (event -> effect handling -> state update) with built-in testing utilities, effect/side-effect isolation, and structured handling of asynchronous side effects, reducing boilerplate and enforcing consistency across a team compared to each feature hand-rolling its own reducer loop.

    ```kotlin
    sealed interface Event
    sealed interface Effect
    fun update(model: Model, event: Event): Pair<Model, Set<Effect>> = TODO()
    ```

??? question "What's the difference between UI Automator and Espresso?"
    Espresso is designed for testing within your own app's UI hierarchy with tight synchronization to your app's state; UI Automator can interact with UI elements across different apps/the system UI (e.g., testing a share-sheet flow into another app), at the cost of less fine-grained synchronization awareness of your specific app's internal state.

    ```kotlin
    onView(withId(R.id.button)).perform(click())  // Espresso — inside your own app
    device.findObject(By.text("Share")).click()   // UiAutomator — across apps/system UI
    ```

??? question "What is Maestro, and how does its approach to UI testing differ from Espresso/Compose testing?"
    Maestro is a black-box, YAML-defined UI testing tool that interacts with the app like a real user (via the accessibility tree/screen), without needing to compile test code into the app itself, making it faster to write simple flows and usable across platforms, at the cost of less fine-grained access to internal app state than white-box tests.

    ```yaml
    - launchApp
    - tapOn: "Login"
    - assertVisible: "Welcome"
    ```

??? question "What's the difference between testing a reducer function in isolation versus testing the full MVI loop with real effect handlers?"
    Testing the pure reducer in isolation is fast and deterministic (given state + event, assert new state) with no async/side-effect concerns; testing the full loop with real (or faked) effect handlers additionally verifies that side effects are triggered/sequenced correctly, closer to integration testing.

    ```kotlin
    val newState = reducer(currentState, Event.Loaded(items)) // pure, no side effects
    assertEquals(expected, newState)
    ```

## Networking Internals, Graphics APIs & Monorepo Tooling

??? question "What's the difference between OkHttp's connection pool reuse and opening a new TCP connection per request?"
    Connection pooling reuses an already-established (and TLS-handshaken) connection for subsequent requests to the same host, avoiding the latency cost of TCP/TLS handshakes on every request, especially impactful on high-latency mobile networks.

    ```kotlin
    val client = OkHttpClient() // ConnectionPool reused automatically for the same host
    repeat(3) { client.newCall(request).execute() } // 2nd/3rd skip the TCP/TLS handshake
    ```

??? question "What's the difference between DNS resolution happening per-request versus OkHttp's `Dns` abstraction allowing custom resolution?"
    OkHttp's pluggable `Dns` interface lets you implement custom resolution strategies (e.g., a fallback list of IPs, or a DNS-over-HTTPS resolver) rather than relying solely on the platform's default `InetAddress` resolution, useful for reliability or privacy-focused networking.

    ```kotlin
    val client = OkHttpClient.Builder()
        .dns(object : Dns { override fun lookup(hostname: String) = customResolve(hostname) })
        .build()
    ```

??? question "What's the difference between Camera2's manual controls and CameraX's default automatic behavior?"
    Camera2 exposes fine-grained manual control over exposure, ISO, focus, and white balance via `CaptureRequest` parameters for advanced use cases (e.g., a pro camera app); CameraX's standard use cases apply sensible automatic behavior by default, though it does expose a `Camera2Interop` extension for apps that still need that manual control while keeping CameraX's simpler lifecycle management.

    ```kotlin
    val preview = Preview.Builder().build() // CameraX — sensible defaults, no manual CaptureRequest
    ```

??? question "What's the difference between Skia (used by Android's Canvas/View rendering) and directly using OpenGL ES/Vulkan?"
    Skia is a higher-level 2D graphics library that Android's `Canvas` API is built on, handling most app UI drawing needs without touching the GPU API directly; OpenGL ES/Vulkan are lower-level GPU APIs used directly for custom 3D rendering, GPU compute, or specialized rendering pipelines (e.g., games) needing more control than Canvas/Skia provides.

    ```kotlin
    canvas.drawRect(rect, paint) // Skia — Android's Canvas API, no direct GPU calls
    ```

??? question "What replaced RenderScript after its deprecation, and why was it deprecated?"
    RenderScript (a framework for parallelized, hardware-accelerated compute-like image processing) was deprecated due to fragmentation/inconsistent driver behavior across devices and its own maintenance complexity; recommended replacements are Vulkan compute shaders for GPU-side work or standard multithreaded CPU code (e.g., using coroutines with `Dispatchers.Default`) for many prior use cases.

    ```kotlin
    withContext(Dispatchers.Default) { processImage(bitmap) } // CPU-side replacement
    // or: Vulkan compute shaders, for GPU-side work
    ```

??? question "What's the difference between a monorepo and a multi-repo strategy for a large mobile codebase, and what tooling challenges does a monorepo introduce?"
    A monorepo keeps all modules/apps in one repository, easing atomic cross-module changes and shared tooling but requiring investment in selective build/test execution (only building what's affected by a change) to keep CI fast at scale; multi-repo keeps things independently versioned/released but complicates cross-repo coordinated changes and dependency version alignment.

    ```text
    Monorepo:              Multi-repo:
    repo/                  app-repo/
      app/                   app/
      feature-a/           feature-a-repo/
      feature-b/             feature-a/
      core-network/        feature-b-repo/
                              feature-b/
    ```

??? question "What is SARIF (Static Analysis Results Interchange Format), and why does it matter for integrating multiple static analysis tools into one CI pipeline?"
    A standardized JSON-based format for static analysis findings, letting different tools (lint, Detekt, security scanners) feed results into a common dashboard/PR-annotation pipeline (e.g., GitHub code scanning) rather than each tool needing bespoke integration.

    ```json
    { "runs": [ { "tool": { "driver": { "name": "detekt" } }, "results": [] } ] }
    ```
