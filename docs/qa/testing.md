# Testing

Collapsed by default — try to answer before revealing.

## Testing

??? question "What's the difference between a unit test, an instrumented test, and a UI test on Android?"
    Unit tests run on the local JVM without an Android device/emulator (fast, no framework classes unless mocked/Robolectric); instrumented tests run on a device/emulator with real Android framework access; UI tests (a subset of instrumented tests, e.g., Espresso/Compose tests) specifically exercise the rendered UI.

??? question "What is the Testing Pyramid and how does it apply to Android?"
    A larger base of fast unit tests, a smaller middle layer of integration tests, and a small top layer of slow end-to-end UI tests — the goal is fast feedback with the bulk of coverage in cheap unit tests rather than slow device-dependent tests.

??? question "How would you unit test a ViewModel with a coroutine-based Repository dependency?"
    Inject a fake/mock Repository, use `runTest {}` from `kotlinx-coroutines-test` to run suspend calls synchronously in a controlled test scheduler, and assert the resulting `StateFlow`/`LiveData` values.

??? question "What is `TestDispatcher`/`runTest` for, and why can't you just use `runBlocking` reliably in coroutine tests?"
    `runTest` uses a virtual-time `TestScheduler`, letting delays/timeouts execute instantly and deterministically; `runBlocking` runs real time and real dispatchers, making tests slow or flaky with any `delay()`/dispatched work.

??? question "Why must you set `Dispatchers.setMain()` in ViewModel unit tests that use `viewModelScope`?"
    `viewModelScope` defaults to `Dispatchers.Main`, which isn't available on the JVM outside Android — `Dispatchers.setMain(testDispatcher)` from `kotlinx-coroutines-test` substitutes a test dispatcher so the code runs without crashing on "Main dispatcher not present."

??? question "What's the difference between mocking and faking?"
    A mock is a dynamically generated stand-in (e.g., via Mockk/Mockito) that you configure to return specific values and can verify interactions on; a fake is a real, simplified hand-written implementation (e.g., an in-memory Repository) that behaves like the real thing without its full complexity.

??? question "When would you prefer a fake over a mock?"
    When testing a component's *behavior* against realistic-but-simplified logic (e.g., an in-memory DB fake for Repository tests) rather than just verifying specific calls were made — fakes are usually more maintainable and less brittle than heavily configured mocks.

??? question "What is Espresso used for, and how does it achieve synchronization with the UI thread automatically?"
    It drives instrumented UI tests, using `IdlingResource`s and its own message-queue-aware scheduling to wait for the UI thread and AsyncTasks/animations to become idle before performing the next action/assertion, avoiding manual `Thread.sleep()`.

??? question "What is an `IdlingResource` and when do you need to register a custom one?"
    An interface that tells Espresso when a background operation is busy/idle; you register a custom one when your app has asynchronous work outside Espresso's default awareness (e.g., a custom thread pool, or a coroutine-based operation not tied to the main looper).

??? question "What is `ComposeTestRule` and what unique challenge does testing Compose UI present compared to Views?"
    It's the entry point for Compose UI tests (`setContent`, node finders, synchronization); a unique challenge is that Compose recomposition/animation timing differs from the View system's message queue, so Compose testing has its own idle-detection mechanism separate from Espresso's.

??? question "What's the difference between `onNodeWithText` and `onAllNodesWithText` in Compose testing?"
    `onNodeWithText` expects exactly one matching node and fails if zero or multiple match; `onAllNodesWithText` returns a collection of all matches, letting you assert on count or index into a specific one.

??? question "What is Robolectric and when would you choose it over a real device/emulator test?"
    A framework that simulates the Android framework classes on the JVM, letting "instrumented-style" tests (using real Android APIs like Context, Resources) run fast as unit tests without a device — useful when you need real framework behavior but want unit-test speed and CI simplicity.

??? question "What are common causes of flaky Android tests?"
    Real time-based waits (`Thread.sleep`) instead of proper idling/synchronization, shared mutable static state between tests, unhandled animations/transitions, network calls not properly mocked, and race conditions in concurrent code under test.

??? question "How would you test a Flow that emits multiple values over time using Turbine?"
    `flow.test { assertEquals(expected1, awaitItem()); assertEquals(expected2, awaitItem()); awaitComplete() }` — Turbine suspends until each item arrives and fails the test if items are missing/extra/mistimed.

??? question "What's the difference between test doubles at the Repository layer vs mocking the network client (e.g., OkHttp) directly?"
    Faking the Repository interface isolates ViewModel tests from data-layer details entirely (faster, simpler); mocking at the network layer (e.g., with MockWebServer) tests more of the real Repository/Retrofit/parsing logic, catching bugs a pure Repository fake would miss, at the cost of being slower and more complex to set up.

??? question "What is MockWebServer used for?"
    An OkHttp-based library that runs a real local HTTP server with scripted responses, letting you test networking code (Retrofit calls, interceptors, retries) against real HTTP behavior without hitting a real backend.

??? question "What's the difference between testing a `suspend fun` Repository method versus one returning `Flow`?"
    A suspend function test simply awaits and asserts the single returned value/exception in `runTest`; a Flow-returning method test must collect emissions (often with Turbine) and can assert a sequence of values over (virtual) time, including multiple emissions or errors mid-stream.

??? question "Why is testing `equals()`/`hashCode()` correctness important for data classes used as Compose keys or Map keys?"
    Incorrect or missing equals/hashCode (e.g., due to mutable fields in a HashMap key) breaks lookups or Compose's ability to detect unchanged state correctly, causing subtle bugs that only manifest in specific data shapes.

??? question "What is contract testing / consumer-driven contract testing and where might it fit in a mobile + backend team setup?"
    A practice where the client (mobile) defines expected request/response shapes as a shared "contract" the backend CI verifies against, catching backend API-breaking changes before they reach mobile clients in production.

??? question "What's the difference between a snapshot test and an assertion-based UI test?"
    A snapshot test renders the UI (e.g., a Compose screenshot) and compares against a stored reference image to catch any visual regression; an assertion-based test checks specific semantic properties (text, state) without caring about pixel-level appearance.

## Testing Tooling Deep Dive (Espresso Intents, Scenarios, Truth, MockK)

??? question "What is Espresso-Intents, and what does it let you verify that plain Espresso view assertions can't?"
    It lets you stub and verify outgoing Intents (e.g., asserting that tapping a "share" button fired an `ACTION_SEND` Intent with expected extras) without actually launching the target app/Activity, isolating the test to just verifying your app's Intent-firing behavior.

??? question "What's the difference between `ActivityScenario` and the older `ActivityTestRule`?"
    `ActivityScenario` (from AndroidX Test) provides a more flexible, lifecycle-state-driven API (`moveToState()`) for controlling and inspecting an Activity's lifecycle during a test, decoupled from JUnit's rule-based launch/teardown timing that `ActivityTestRule` was tied to.

??? question "What is `FragmentScenario` used for, and why is it valuable for testing Fragments in isolation?"
    It launches a Fragment in an isolated, empty host Activity for testing, without needing to set up the Fragment's real parent Activity/navigation graph, letting you unit/instrumented-test Fragment behavior (including its view lifecycle) independently.

??? question "What's the difference between Google's Truth assertion library and plain JUnit assertions?"
    Truth provides more fluent, readable, and specifically-typed assertion chains (`assertThat(list).containsExactly(...)`) with clearer failure messages tailored to the asserted type, compared to JUnit's more generic `assertEquals`/`assertTrue` which often produce less informative failure output for complex objects/collections.

??? question "What's the difference between a 'relaxed' mock and a strict mock in MockK?"
    A relaxed mock automatically returns sensible default values (0, empty list, null, etc.) for any unstubbed method call instead of throwing, reducing boilerplate for large interfaces where you only care about stubbing a few specific methods; a strict mock throws if an unstubbed method is called, forcing every interaction to be explicitly accounted for.

??? question "What's the difference between a 'hermetic' test and a test that depends on real network/external services?"
    A hermetic test has no external dependencies (uses fakes/mocks for everything outside the code under test), so it's fast, deterministic, and works offline/in any environment; a test hitting real network/services is inherently flakier (subject to real-world outages, latency, rate limits) and slower, generally reserved for smaller-scale integration/smoke test suites rather than the bulk of the test pyramid.

??? question "Why would you write a custom Robolectric 'Shadow' class, and what problem does it solve?"
    Robolectric simulates Android framework behavior via Shadow classes standing in for real framework implementations; a custom Shadow lets you override the simulated behavior of a specific framework class (or a third-party library not well-supported by default) for a test scenario Robolectric's built-in shadows don't handle correctly out of the box.
