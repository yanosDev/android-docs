# Kotlin Multiplatform & Misc

Collapsed by default — try to answer before revealing.

## Kotlin Multiplatform & Misc Best Practices

??? question "What is Kotlin Multiplatform (KMP) and what's a typical Android+iOS sharing strategy?"
    A Kotlin feature letting shared business logic (networking, data models, use cases) compile to both JVM/Android and native iOS targets, typically sharing the Domain/Data layers while keeping Presentation/UI (Compose for Android, SwiftUI for iOS, or Compose Multiplatform for both) platform-specific or shared depending on the chosen strategy.

    ```kotlin
    // commonMain — compiled for both Android and iOS
    class UserRepository(private val api: UserApi) {
        suspend fun getUser(id: String): User = api.fetchUser(id)
    }
    ```

??? question "What's the difference between `expect`/`actual` declarations in KMP?"
    `expect` declares an API in shared code without implementation; each platform provides an `actual` implementation matching that signature, letting shared code call platform-specific functionality (e.g., accessing platform-specific storage) through a common interface.

    ```kotlin
    // commonMain
    expect fun platformName(): String
    // androidMain
    actual fun platformName() = "Android"
    // iosMain
    actual fun platformName() = "iOS"
    ```

??? question "What is Compose Multiplatform and how does it differ from just sharing business logic via KMP?"
    It extends Compose's declarative UI toolkit to also run on iOS/desktop/web, letting you share not just business logic but the actual UI code itself across platforms, rather than writing separate native UI per platform.

    ```kotlin
    @Composable
    fun SharedScreen() {
        Text("Same UI code, compiled for Android, iOS, and desktop")
    }
    ```

??? question "What's a common challenge when sharing a networking layer (e.g., Ktor) across KMP targets?"
    Ensuring platform-specific engine configuration (e.g., different underlying HTTP engines per platform) and certificate pinning/TLS behavior are consistent, since low-level networking still ultimately depends on each platform's native stack.

    ```kotlin
    val client = HttpClient {
        // engine differs per target: OkHttp (Android), Darwin (iOS) — configured separately
    }
    ```

??? question "What is the SOLID Single Responsibility Principle, and how does it typically manifest in Android architecture?"
    A class should have one reason to change; in Android this often means separating a "God Activity" doing UI, business logic, and data access into distinct ViewModel/UseCase/Repository classes, each with a focused responsibility.

    ```kotlin
    class OrderViewModel(private val getOrders: GetOrdersUseCase)  // UI state only
    class GetOrdersUseCase(private val repo: OrderRepository)      // business logic only
    ```

??? question "What is the Dependency Inversion Principle, and how does it justify defining Repository interfaces in the Domain layer?"
    High-level modules shouldn't depend on low-level implementation details; defining the Repository interface in Domain (with the Data layer providing the implementation) means Domain depends only on an abstraction it owns, not on networking/DB specifics, keeping Domain framework-independent.

    ```kotlin
    // :domain module — no Android/network dependency
    interface OrderRepository { suspend fun getOrders(): List<Order> }
    // :data module — implements it
    class DefaultOrderRepository(private val api: OrderApi) : OrderRepository { /* ... */ }
    ```

??? question "Why is defensive/excessive nullability (`String?` everywhere 'just in case') considered an anti-pattern in Kotlin code?"
    It pushes null-handling burden onto every caller and obscures the actual invariants of the data, when often the real fix is ensuring the value is guaranteed non-null earlier (e.g., via validation at the boundary) so the type system can express a stronger guarantee.

    ```kotlin
    // Anti-pattern: fun greet(name: String?) { ... } // "just in case"
    // Better: validate once at the boundary, then trust the type everywhere after
    fun greet(name: String) = "Hi $name"
    ```

??? question "What's the difference between 'fail fast' and 'fail silently' error handling philosophies, and where does each fit in production Android code?"
    Fail fast surfaces errors immediately/loudly (e.g., crashing in debug builds on invariant violations) to catch bugs early; fail silently degrades gracefully in production (e.g., falling back to cached/default data) to avoid crashing on the user — many teams use assertions/`check()` that crash in debug but are stripped or downgraded to logging in release.

    ```kotlin
    check(id > 0) { "id must be positive" }      // fail fast — crashes in debug
    val data = cache.get(key) ?: fallbackData    // fail silently — degrades in production
    ```

??? question "What's the value of writing architecture decision records (ADRs) on a senior-level Android team?"
    They document the context and reasoning behind significant technical decisions (e.g., "why MVI over MVVM," "why this DI framework"), so future team members understand tradeoffs already considered rather than re-litigating or accidentally reversing decisions without full context.

    ```text
    # ADR-0007: Use MVI instead of MVVM
    Status: Accepted
    Context: ...
    Decision: ...
    Consequences: ...
    ```

??? question "What's a key difference in reviewing a PR for a junior vs senior Android engineer's typical mistakes?"
    Junior review often focuses on correctness/syntax/basic lifecycle mistakes; senior-level review focuses more on architectural fit, testability, performance implications (e.g., recomposition stability, unnecessary allocations), and whether the change introduces tech debt or violates established module boundaries.

    ```kotlin
    // Junior review catches: "this NPEs if user is null"
    // Senior review also asks: "should this logic even live in a ViewModel, or a UseCase?"
    ```

## Feature Rollback, Navigation Testing & Multiplatform Details

??? question "What's a safe rollback strategy for a feature flag if a newly-enabled feature causes a spike in crashes/negative metrics?"
    Flip the remote flag back off (assuming the app checks it reactively/on next fetch rather than only at install time), monitor that the rollback actually reduces the affected metric, and only after confirming stability, invest in a code fix before attempting to re-enable.

    ```kotlin
    remoteConfig.setBoolean("checkout_v2_enabled", false) // app picks this up on next fetch
    ```

??? question "How would you test navigation logic (e.g., 'tapping X navigates to screen Y with argument Z') without a full instrumented UI test?"
    Test the ViewModel/reducer's emitted navigation *event* (as data, e.g., a sealed `NavigationEvent.ToDetail(id)`) in a fast unit test, keeping the actual `NavController` interaction as a thin, separately-tested layer that just reacts to those events — decoupling "did we decide to navigate correctly" from "does the Navigation library actually navigate."

    ```kotlin
    sealed interface NavigationEvent { data class ToDetail(val id: String) : NavigationEvent }

    @Test
    fun `tapping item emits ToDetail event`() {
        viewModel.onItemClicked("42")
        assertEquals(NavigationEvent.ToDetail("42"), viewModel.navigationEvents.value)
    }
    ```

??? question "What's the difference between an `expect`/`actual` class and an `expect`/`actual` function in Kotlin Multiplatform?"
    An `expect` function declares just a shared function signature with platform-specific `actual` implementations; an `expect` class can additionally declare shared properties/nested members with each platform providing a full concrete `actual class` implementation, useful when platform-specific state (not just behavior) needs to be encapsulated behind a common shared-code-facing API.

    ```kotlin
    expect class PlatformFile(path: String) {
        fun readText(): String
    }
    ```

??? question "What's a common architectural tension when sharing a Repository via KMP that needs different persistence mechanisms per platform (Room on Android vs SQLDelight/other on iOS)?"
    Either standardize on a KMP-compatible persistence library (like SQLDelight, which generates typed Kotlin APIs for both platforms from shared SQL) so the Repository's data-layer code can be fully shared, or keep the DB layer platform-specific behind an `expect`/`actual` interface while sharing everything above it (mapping/business logic) in common code.

    ```kotlin
    // commonMain — backed by SQLDelight-generated code on both platforms
    interface UserDao { suspend fun getUser(id: String): User? }
    ```

??? question "What's the difference between a security-sensitive Biometric-gated `CryptoObject` operation using `Cipher` versus `Signature`/`Mac`?"
    A `Cipher`-based CryptoObject ties biometric auth to an actual encrypt/decrypt operation (protecting data confidentiality); a `Signature`/`Mac`-based CryptoObject ties it to producing a cryptographic signature/MAC (proving data integrity/authenticity, e.g., for a server-verifiable proof of biometric approval) rather than encrypting data itself.

    ```kotlin
    val cipherCrypto = BiometricPrompt.CryptoObject(cipher)    // confidentiality
    val signCrypto = BiometricPrompt.CryptoObject(signature)   // integrity/authenticity
    ```

??? question "What is the Play Integrity API's verdict decryption process, and why can't the client just trust a plain boolean it receives?"
    The device returns a signed/encrypted integrity token that must be sent to and decrypted/verified by your own backend using Google's provided decryption keys/service — trusting a boolean check purely on-device would be trivially bypassable by a compromised/rooted client simply lying about its own integrity status.

    ```kotlin
    val token = integrityManager.requestIntegrityToken(request).await()
    // token is opaque here — only your backend can decrypt/verify it with Google's keys
    ```

## Final Miscellaneous Deep Cuts

??? question "What's the difference between `internal` visibility in a Gradle multi-module project and simply not documenting a class as 'public API'?"
    `internal` is compiler-enforced — other modules genuinely cannot reference it even accidentally — whereas an undocumented-but-public class can still be imported and depended on by other modules, creating an unintended coupling that only convention (not the compiler) discourages.

    ```kotlin
    internal class InternalHelper // compiler-enforced: other modules truly cannot see this
    class PublicHelper            // "not meant for you" only by convention/docs
    ```

??? question "What is a JUnit5 parameterized test, and why might a team migrating from JUnit4 adopt it for a large matrix of input/expected-output cases?"
    `@ParameterizedTest` with a source of arguments (CSV, method, enum) runs the same test body once per parameter set, replacing many near-duplicate JUnit4 test methods (or a manual loop inside one test) with clearer, individually-reported results per case.

    ```kotlin
    @ParameterizedTest
    @CsvSource("1,1", "2,4", "3,9")
    fun `square works`(input: Int, expected: Int) {
        assertEquals(expected, square(input))
    }
    ```

??? question "What is a Gradle JVM toolchain, and what problem does it solve for a team with mixed local JDK installations?"
    It declares which JDK version a project's compilation/tests should use regardless of the JDK actually installed/active on a given machine, letting Gradle auto-provision or select the correct toolchain, avoiding "works on my machine" JDK-version mismatches across a team or CI.

    ```kotlin
    kotlin {
        jvmToolchain(17) // Gradle provisions/selects JDK 17, regardless of the local machine
    }
    ```

??? question "How would you implement a multipart file upload (e.g., an image) with Retrofit?"
    Define the endpoint parameter as `@Part MultipartBody.Part`, wrapping the file's bytes in a `RequestBody` with the appropriate MIME type, letting OkHttp handle the multipart boundary encoding automatically as part of the request body.

    ```kotlin
    @Multipart
    @POST("upload")
    suspend fun upload(@Part file: MultipartBody.Part): Response<Unit>

    val part = MultipartBody.Part.createFormData("file", "photo.jpg", requestBody)
    ```

??? question "Why might R8's string/resource obfuscation still leave some sensitive-looking identifiers visible in `resources.arsc`?"
    Resource names/IDs and certain resource-referencing strings aren't code symbols R8 renames the same way as class/method names, so resource identifiers can remain more legible in a decompiled APK than the actual obfuscated code logic — a reason not to rely on resource naming alone to hide sensitive functionality.

    ```text
    # class/method names  -> renamed by R8 (e.g. `a`, `b`, `c`)
    # res/drawable/ic_launcher.png -> resource name stays legible in resources.arsc
    ```

??? question "What is an accessibility 'pane title,' and when would you set one via `Modifier.semantics { paneTitle = ... }`?"
    It announces a logical grouping/region (e.g., "master list" vs "detail pane" in a two-pane layout) to assistive technology when that pane's visibility/content changes, giving screen-reader users context about which section just appeared/changed without needing to re-explore the whole screen.

    ```kotlin
    Modifier.semantics { paneTitle = "Detail pane" } // announced when this pane's content changes
    ```

??? question "What's the difference between consuming `WindowInsets` at a single top-level composable versus letting them propagate to nested children unconsumed?"
    Consuming insets at a single ancestor (e.g., via `Modifier.consumeWindowInsets`) prevents descendant composables from redundantly applying the same padding again, which would otherwise stack up as excessive spacing if every nested composable individually applied the same raw insets.

    ```kotlin
    Box(Modifier.consumeWindowInsets(WindowInsets.statusBars)) {
        // children no longer also apply status-bar padding on top of this
    }
    ```

??? question "What is a `Bundle` payload used for partial RecyclerView item rebinds (`onBindViewHolder(holder, position, payloads)`), and why is it more efficient than a full rebind?"
    Passing a specific payload (e.g., "this item's like-count changed") from `DiffUtil.ItemCallback.getChangePayload()` lets `onBindViewHolder` update only the specific changed sub-view (e.g., just the counter TextView) instead of re-binding and potentially re-triggering animations/image loads for the entire item view.

    ```kotlin
    override fun onBindViewHolder(holder: VH, position: Int, payloads: List<Any>) {
        if (payloads.contains("like_count_changed")) {
            holder.updateLikeCountOnly() // skip re-binding the whole item
        } else super.onBindViewHolder(holder, position, payloads)
    }
    ```

??? question "What's the difference between prorated and non-prorated billing when a user upgrades/downgrades a subscription mid-cycle via Play Billing?"
    Proration credits/charges the price difference for the remaining part of the current billing cycle immediately upon the plan change; non-prorated (deferred) changes wait until the next renewal to apply the new price/plan, avoiding an immediate charge but delaying when the user actually gets the new plan's benefits.

    ```kotlin
    BillingFlowParams.SubscriptionUpdateParams.newBuilder()
        .setSubscriptionReplacementMode(ReplacementMode.CHARGE_PRORATED_PRICE) // vs DEFERRED
    ```

??? question "Why can string formatting with grammatical gender agreement (common in many non-English languages) be difficult to handle with simple placeholder-based string resources?"
    A single template like `"%1$s viewed your profile"` may need an entirely different verb/adjective form depending on the subject's grammatical gender in some languages, which a flat placeholder substitution can't express — often requiring either separate full string variants selected by a gender parameter, or a more capable ICU MessageFormat-style resource format.

    ```xml
    <!-- flat placeholder can't express a gendered verb/adjective form -->
    <string name="viewed_profile">%1$s viewed your profile</string>
    ```
