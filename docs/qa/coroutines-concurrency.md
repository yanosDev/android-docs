# Coroutines & Concurrency

Collapsed by default — try to answer before revealing.

## Coroutines

??? question "What is the difference between `launch` and `async`?"
    `launch` starts a coroutine and returns a `Job` with no result value (fire-and-forget); `async` returns a `Deferred<T>` whose result you retrieve with `await()`, and exceptions are held until `await()` is called.

    ```kotlin
    val job = scope.launch { doWork() }           // Job, no result
    val deferred = scope.async { computeValue() } // Deferred<T>
    val value = deferred.await()
    ```

??? question "What is structured concurrency?"
    A discipline where coroutines are launched within a scope that defines their lifetime; when the scope is cancelled, all child coroutines are cancelled automatically, preventing leaks and orphaned work.

    ```kotlin
    coroutineScope {
        launch { child1() }
        launch { child2() }
    } // suspends until both finish; cancelling the scope cancels both
    ```

??? question "What is a CoroutineContext and what does it typically contain?"
    An indexed set of elements describing a coroutine's environment: a `Job` (lifecycle/cancellation), a `CoroutineDispatcher` (threading), a `CoroutineName`, and a `CoroutineExceptionHandler`.

    ```kotlin
    val context = Job() + Dispatchers.IO + CoroutineName("sync") + handler
    ```

??? question "What's the difference between `Dispatchers.Main`, `IO`, `Default`, and `Unconfined`?"
    `Main` runs on the UI thread; `IO` uses a large elastic thread pool for blocking I/O; `Default` uses a CPU-core-sized pool for CPU-bound work; `Unconfined` doesn't confine to any thread and resumes in whatever thread called it, which is rarely appropriate for app code.

    ```kotlin
    withContext(Dispatchers.Main) { updateUi() }
    withContext(Dispatchers.IO) { readFile() }
    withContext(Dispatchers.Default) { heavyComputation() }
    ```

??? question "What is `withContext` used for, and how does it differ from launching a new coroutine?"
    It suspends the current coroutine and switches to another dispatcher for a block of code, returning a value, without creating a new coroutine/Job — it's structured and sequential, unlike `launch` which runs concurrently.

    ```kotlin
    suspend fun loadUser(): User = withContext(Dispatchers.IO) {
        db.getUser() // switches dispatcher, returns a value, no new Job
    }
    ```

??? question "What's the difference between `coroutineScope {}` and `supervisorScope {}`?"
    In `coroutineScope`, a failure in any child cancels the whole scope and all siblings; in `supervisorScope`, a child's failure doesn't cancel siblings, useful when independent tasks shouldn't affect each other.

    ```kotlin
    supervisorScope {
        launch { mightFail() }   // failure here doesn't cancel the sibling below
        launch { keepsRunning() }
    }
    ```

??? question "How do you handle exceptions in coroutines launched with `launch`?"
    Via a `try/catch` inside the coroutine, or a `CoroutineExceptionHandler` installed in the scope's context; uncaught exceptions in `launch` propagate up and can crash the app if unhandled, unlike `async` which defers them to `await()`.

    ```kotlin
    val handler = CoroutineExceptionHandler { _, e -> log(e) }
    scope.launch(handler) {
        try { risky() } catch (e: IOException) { /* handled locally */ }
    }
    ```

??? question "What is `CoroutineExceptionHandler` and where does it NOT catch exceptions?"
    It's a context element that intercepts uncaught exceptions from `launch`-started coroutines; it does not catch exceptions from `async` (those surface at `await()`), and it must be installed on the top-level scope, not a child, to take effect with default propagation.

    ```kotlin
    val handler = CoroutineExceptionHandler { _, e -> log(e) }
    scope.launch(handler) { throw RuntimeException() } // caught by handler
    scope.async { throw RuntimeException() }           // NOT caught — surfaces at await()
    ```

??? question "What is cooperative cancellation and why must suspending functions check for it?"
    Coroutines aren't preemptively killed; cancellation just sets a flag/throws `CancellationException` at the next suspension point or cancellation check (`isActive`, `ensureActive()`), so long-running non-suspending loops must check cancellation manually.

    ```kotlin
    while (isActive) {   // must check manually in a tight, non-suspending loop
        doChunkOfWork()
    }
    ```

??? question "Why should you never catch `CancellationException` generically without rethrowing it?"
    Swallowing it breaks structured concurrency — the coroutine appears to continue running after being cancelled, and parent scopes lose the cancellation signal, leading to leaks or unexpected behavior.

    ```kotlin
    try {
        delay(1000)
    } catch (e: CancellationException) {
        throw e // always rethrow — never swallow
    }
    ```

??? question "What is `viewModelScope` and how is it cancelled?"
    A `CoroutineScope` tied to the `ViewModel`'s lifecycle, automatically cancelled when `onCleared()` is called, using `Dispatchers.Main.immediate` by default.

    ```kotlin
    class MyViewModel : ViewModel() {
        init {
            viewModelScope.launch { loadData() } // cancelled automatically in onCleared()
        }
    }
    ```

??? question "What is `lifecycleScope` and what's the risk of using it directly in a Fragment vs `viewLifecycleOwner.lifecycleScope`?"
    `lifecycleScope` follows the Fragment's own lifecycle, which outlives the view; if you launch UI-touching coroutines there, they can crash accessing a destroyed view — use `viewLifecycleOwner.lifecycleScope` instead.

    ```kotlin
    // In a Fragment:
    viewLifecycleOwner.lifecycleScope.launch { updateView() } // correct
    // lifecycleScope.launch { updateView() } // risky — Fragment can outlive its view
    ```

??? question "What does `repeatOnLifecycle` solve that a plain `lifecycleScope.launch { flow.collect {} }` doesn't?"
    It automatically starts/cancels collection based on lifecycle state (e.g., STARTED/STOPPED), preventing UI updates while backgrounded and avoiding the need for manual `Lifecycle.State` checks or leaking collectors.

    ```kotlin
    viewLifecycleOwner.lifecycleScope.launch {
        repeatOnLifecycle(Lifecycle.State.STARTED) {
            flow.collect { render(it) } // auto start/stop with lifecycle state
        }
    }
    ```

??? question "What is `runBlocking` and when is it appropriate to use?"
    It blocks the current thread until the coroutine completes; appropriate mainly in `main()` functions, tests, or bridging blocking code to coroutines — never on the main thread of an Android app.

    ```kotlin
    fun main() = runBlocking {
        delay(100) // blocks this thread until the coroutine completes
    }
    ```

??? question "What is `yield()` used for inside a coroutine?"
    It gives other coroutines on the same dispatcher a chance to run and checks for cancellation, useful in long CPU-bound loops to remain cooperative.

    ```kotlin
    while (isActive) {
        doSmallChunk()
        yield() // let other coroutines run, and check cancellation
    }
    ```

??? question "What's the difference between `Job` and `SupervisorJob`?"
    A regular `Job` propagates a child's failure to cancel siblings and itself; `SupervisorJob` isolates failures so one child's exception doesn't cancel other children.

    ```kotlin
    val scope = CoroutineScope(SupervisorJob()) // one child's failure won't cancel others
    ```

??? question "How do you convert a callback-based API into a suspend function?"
    Using `suspendCancellableCoroutine`, invoking `continuation.resume()`/`resumeWithException()` in the callback, and registering `invokeOnCancellation` to clean up (e.g., unregister the listener) if the coroutine is cancelled.

    ```kotlin
    suspend fun awaitResult(): String = suspendCancellableCoroutine { cont ->
        val listener = Listener { result -> cont.resume(result) }
        register(listener)
        cont.invokeOnCancellation { unregister(listener) }
    }
    ```

??? question "What is `withTimeout` vs `withTimeoutOrNull`?"
    `withTimeout` throws `TimeoutCancellationException` if the block exceeds the duration; `withTimeoutOrNull` returns `null` instead of throwing.

    ```kotlin
    withTimeout(1000) { slowCall() }       // throws TimeoutCancellationException
    withTimeoutOrNull(1000) { slowCall() } // returns null instead
    ```

??? question "What's a common cause of a coroutine leak in Android apps?"
    Launching a coroutine in `GlobalScope` or an unscoped custom scope instead of a lifecycle-aware scope (`viewModelScope`/`lifecycleScope`), so it outlives the component and keeps references alive.

    ```kotlin
    GlobalScope.launch { longRunningWork() } // not tied to any lifecycle — leaks
    ```

??? question "Why is `GlobalScope` generally discouraged?"
    It's not tied to any component lifecycle, so coroutines launched there run for the app's entire lifetime unless manually cancelled, risking leaks and making testing/cancellation harder.

    ```kotlin
    GlobalScope.launch { neverAutomaticallyCancelled() } // lives for the whole process
    ```

??? question "What's the difference between `Dispatchers.Main` and `Dispatchers.Main.immediate`?"
    `Main.immediate` executes immediately if already on the main thread (skipping a dispatch), while `Main` always posts to the message queue even if already on the main thread; `viewModelScope` uses `immediate` for responsiveness.

    ```kotlin
    viewModelScope.launch(Dispatchers.Main.immediate) {
        updateUi() // runs right away if already on main thread — no extra dispatch
    }
    ```

??? question "What is a `Mutex` in coroutines and how does it differ from `synchronized`?"
    `Mutex` is a suspending lock usable inside coroutines without blocking the underlying thread; `synchronized` blocks the actual thread, which is problematic with coroutines sharing a limited thread pool (can cause deadlocks/starvation).

    ```kotlin
    val mutex = Mutex()
    suspend fun update() = mutex.withLock { counter++ } // suspends, doesn't block the thread
    ```

??? question "What does `Dispatchers.IO.limitedParallelism()` do?"
    It creates a view of the `IO` dispatcher with a custom max concurrency, useful to avoid exhausting shared IO threads when doing many simultaneous blocking calls (e.g., limiting DB write concurrency).

    ```kotlin
    val limitedIo = Dispatchers.IO.limitedParallelism(4) // cap concurrent IO work at 4
    ```

??? question "What is a `Channel` in coroutines, and how does it differ from `Flow`?"
    `Channel` is a hot, non-replayable communication primitive for passing values between coroutines (like a queue with suspend send/receive); `Flow` is typically cold and declarative, and `Channel` underlies hot flow implementations like `SharedFlow`'s buffer.

    ```kotlin
    val channel = Channel<Int>()
    channel.send(1)              // hot — sent regardless of a receiver being ready
    val flow = flow { emit(1) }  // cold — nothing happens until collected
    ```

??? question "What is `async` with `start = CoroutineStart.LAZY` used for?"
    It defers execution until `.start()` or `.await()` is explicitly called, useful when you want to launch concurrently but control the exact start time.

    ```kotlin
    val deferred = scope.async(start = CoroutineStart.LAZY) { compute() }
    deferred.start() // only runs once explicitly started (or awaited)
    ```

??? question "How would you run multiple independent network calls in parallel and combine results?"
    Launch each with `async` inside a `coroutineScope`, then `awaitAll()` or destructure individual `Deferred.await()` calls to get results once all complete.

    ```kotlin
    coroutineScope {
        val a = async { api.fetchA() }
        val b = async { api.fetchB() }
        Combined(a.await(), b.await()) // both requests run concurrently
    }
    ```

??? question "What's the danger of using `async` without eventually calling `await()`?"
    Exceptions thrown inside are swallowed until `await()` — if never called, a failure can go unnoticed and the coroutine may leak depending on scope structure.

    ```kotlin
    scope.async { throw RuntimeException("lost!") } // never awaited — exception vanishes
    ```

## Flow

??? question "What's the difference between a cold and a hot flow?"
    Cold flows (e.g., builder-created `flow {}`) run the producer code fresh for each collector and don't emit until collected; hot flows (`StateFlow`, `SharedFlow`) emit independent of collectors and can have multiple simultaneous subscribers sharing emissions.

    ```kotlin
    val cold = flow { emit(1) }   // runs fresh per collector
    val hot = MutableStateFlow(0) // emits regardless of collectors
    ```

??? question "What's the difference between `StateFlow` and `SharedFlow`?"
    `StateFlow` always holds a current value (requires an initial value), only emits distinct-from-last values by default via conflation, and is meant for state; `SharedFlow` has no required initial value, supports configurable replay/buffering, and is meant for one-off events.

    ```kotlin
    val state = MutableStateFlow(0)                     // always has a current value
    val events = MutableSharedFlow<String>(replay = 0)  // no required initial value
    ```

??? question "Why is `StateFlow` sometimes a poor fit for one-time UI events like showing a Snackbar?"
    Because it conflates to the latest value and re-delivers the current value to new collectors (e.g., on configuration change), a one-time event can replay and re-trigger — `SharedFlow` with no replay, or a Channel-backed event flow, avoids this.

    ```kotlin
    val snackbarState = MutableStateFlow<String?>(null) // replays on rotation — bad for events
    val snackbarEvents = MutableSharedFlow<String>()     // no replay — safer for one-off events
    ```

??? question "What is `collectLatest` and when do you use it?"
    It cancels the currently running collector block whenever a new value arrives before the block finishes, useful for cases like search-as-you-type where only the latest result matters.

    ```kotlin
    searchQuery.collectLatest { query ->
        delay(300)               // cancelled if a new query arrives before this finishes
        render(search(query))
    }
    ```

??? question "What's the difference between `buffer()`, `conflate()`, and `collectLatest()` for handling backpressure?"
    `buffer()` queues emissions so the producer isn't blocked waiting on a slow collector; `conflate()` drops intermediate values, keeping only the latest when the collector is slow; `collectLatest()` cancels in-progress collector work on a new emission.

    ```kotlin
    flow.buffer().collect { slowConsumer(it) }   // queues emissions
    flow.conflate().collect { slowConsumer(it) } // keeps only the latest
    flow.collectLatest { slowConsumer(it) }      // cancels in-flight work on new value
    ```

??? question "What does `flowOn()` do, and why does it only affect upstream operators?"
    It changes the dispatcher used for the upstream (producer) operators before it in the chain; downstream operators after `flowOn` still run on the collector's context, because `flowOn` inserts a boundary using a buffer to switch context only for what precedes it.

    ```kotlin
    flow { emit(loadFromDb()) } // runs upstream...
        .flowOn(Dispatchers.IO)  // ...on IO
        .collect { render(it) } // collector still runs on its own context
    ```

??? question "What's the difference between `map` and `transform` on a Flow?"
    `map` emits exactly one transformed value per input; `transform` can emit zero, one, or multiple values per input by calling `emit()` any number of times inside the lambda.

    ```kotlin
    flow.map { it * 2 }                       // exactly one output per input
    flow.transform { emit(it); emit(it * 2) } // zero, one, or many outputs per input
    ```

??? question "What does `stateIn()` do and what are its `SharingStarted` strategies?"
    It converts a cold `Flow` into a `StateFlow`; `SharingStarted.Eagerly` starts immediately, `Lazily` starts on first collector and keeps running, `WhileSubscribed` starts on first subscriber and stops (optionally after a timeout) when subscribers drop to zero.

    ```kotlin
    val uiState = repository.observe()
        .stateIn(scope, SharingStarted.WhileSubscribed(5000), initialValue)
    ```

??? question "Why is `SharingStarted.WhileSubscribed(5000)` commonly used in ViewModels?"
    It keeps the upstream flow (e.g., a network/DB observer) active briefly after the UI stops observing (like during a config change), avoiding a full restart/reload, while still stopping eventually to save resources when truly unused.

    ```kotlin
    val state = flow.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), Initial)
    // keeps observing 5s after the UI stops collecting — survives a quick config change
    ```

??? question "What is `combine()` used for versus `zip()`?"
    `combine()` emits whenever any source flow emits, pairing with the latest value from the others; `zip()` pairs emissions positionally, waiting for a new value from every source before emitting, discarding unmatched trailing values.

    ```kotlin
    combine(flowA, flowB) { a, b -> a + b } // emits on every update from either
    flowA.zip(flowB) { a, b -> a + b }      // waits for a matching pair from both
    ```

??? question "What does `distinctUntilChanged()` do and where is it implicit?"
    It suppresses consecutive duplicate emissions; `StateFlow` applies this behavior implicitly since it conflates and only emits distinct updates from its current value.

    ```kotlin
    flow.distinctUntilChanged() // skips consecutive duplicates
    // StateFlow does this implicitly already
    ```

??? question "How do you test a Flow that emits multiple values over time?"
    Use the Turbine library's `flow.test { assertEquals(...); awaitItem(); awaitComplete() }`, or manually collect into a list within a `runTest` coroutine using a `TestDispatcher`.

    ```kotlin
    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        awaitComplete()
    }
    ```

??? question "What is `flatMapLatest` used for?"
    It maps each upstream emission to a new inner flow, cancelling the previous inner flow's collection when a new upstream value arrives — common for "search query changes -> cancel old network call, start new one."

    ```kotlin
    searchQuery.flatMapLatest { query -> repository.search(query) } // cancels the old search
    ```

??? question "What's the difference between `flatMapConcat` and `flatMapMerge`?"
    `flatMapConcat` processes inner flows sequentially, one fully finishing before the next starts; `flatMapMerge` runs inner flows concurrently (with a configurable concurrency limit), interleaving emissions.

    ```kotlin
    flow.flatMapConcat { inner(it) } // one inner flow finishes before the next starts
    flow.flatMapMerge { inner(it) }  // inner flows run concurrently
    ```

??? question "What does `catch {}` do in a Flow chain, and where must it be placed?"
    It catches exceptions from upstream operators and can emit a fallback value; it must be placed after the operators it should protect, since it only catches exceptions from upstream, not downstream, of itself.

    ```kotlin
    flow
        .map { risky(it) }
        .catch { emit(fallback) } // only catches what happened above this line
        .collect { render(it) }
    ```

??? question "What is `retryWhen` used for in a Flow?"
    It allows retrying the flow's collection based on a predicate over the exception and attempt count, useful for implementing exponential backoff on network flows.

    ```kotlin
    flow.retryWhen { cause, attempt ->
        delay(2.0.pow(attempt.toInt()).toLong() * 100)
        attempt < 3
    }
    ```

??? question "Why can you not call `emit()` from a different coroutine context using `withContext` inside `flow {}`?"
    It violates the Flow's context preservation contract; use `flowOn()` instead to switch upstream context, or `channelFlow {}` if you truly need to emit from multiple coroutines/contexts.

    ```kotlin
    flow {
        emit(1) // fine
        // withContext(Dispatchers.IO) { emit(2) } // NOT allowed — breaks context preservation
    }.flowOn(Dispatchers.IO) // use this instead
    ```

??? question "What is `channelFlow` and when do you need it instead of `flow {}`?"
    It backs the flow with an actual `Channel`, allowing emission from multiple coroutines/callbacks concurrently, unlike `flow {}` which enforces sequential, single-context emission.

    ```kotlin
    channelFlow {
        launch { send(1) } // multiple coroutines can send concurrently
        launch { send(2) }
    }
    ```

??? question "What's the difference between `Flow<T>.first()` and `Flow<T>.take(1)`?"
    `first()` is a terminal operator returning a single value and cancelling collection immediately after; `take(1)` is an intermediate operator returning a new Flow limited to one emission, requiring a further terminal operator to collect.

    ```kotlin
    flow.first()             // terminal — one value, then done
    flow.take(1).collect {}  // intermediate — still needs a terminal operator
    ```

??? question "How does Room return a Flow from a DAO query, and what does it do on data changes?"
    Room generates code that re-runs the query and emits a new list automatically whenever the observed table changes, using `InvalidationTracker` internally — no manual polling required.

    ```kotlin
    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>> // re-emits automatically on table changes
    ```

??? question "What is `callbackFlow`/`awaitClose` (in `callbackFlow`) used for?"
    `callbackFlow` bridges a listener-based API into a Flow; `awaitClose {}` is mandatory to clean up (e.g., unregister the listener) when the flow's collector is cancelled.

    ```kotlin
    callbackFlow {
        val listener = Listener { trySend(it) }
        register(listener)
        awaitClose { unregister(listener) } // mandatory cleanup
    }
    ```

## Concurrency & Threading Fundamentals (JVM/Java)

??? question "What's the difference between a thread and a process?"
    A process has its own isolated memory space; threads run within a process and share its memory/resources, making inter-thread communication cheaper but requiring synchronization to avoid race conditions.

    ```kotlin
    var counter = 0
    Thread { counter++ }.start()
    Thread { counter++ }.start() // both threads see/modify the same `counter`
    ```

??? question "What is the `synchronized` keyword, and what's a downside of using it broadly?"
    It ensures only one thread executes a block/method on a given monitor (lock object) at a time; overusing it can cause thread contention/blocking and, if locks are acquired in inconsistent order across code paths, deadlocks.

    ```kotlin
    val lock = Any()
    synchronized(lock) { counter++ } // only one thread executes this at a time
    ```

??? question "What is `volatile` used for, and what does it NOT guarantee?"
    It ensures visibility of a variable's latest value across threads (preventing stale cached reads) and establishes a memory barrier; it does NOT provide atomicity for compound operations (e.g., increment), so a `volatile int` can still race under concurrent increments.

    ```kotlin
    @Volatile var ready = false // visibility guaranteed, but `ready = !ready` still isn't atomic
    ```

??? question "What's the difference between `AtomicInteger`/`AtomicReference` and a `volatile` field?"
    Atomic classes provide compound atomic operations (compare-and-swap, increment) safely without external locking; `volatile` alone only guarantees visibility, not atomicity of multi-step operations.

    ```kotlin
    val counter = AtomicInteger(0)
    counter.incrementAndGet() // atomic — safe under concurrent access
    ```

??? question "What is a deadlock, and what are the classic conditions that cause it?"
    A situation where two or more threads wait on each other's held locks indefinitely; classic conditions are mutual exclusion, hold-and-wait, no preemption, and circular wait — breaking any one (e.g., consistent lock ordering) prevents it.

    ```kotlin
    // Thread A: synchronized(lock1) { synchronized(lock2) { } }
    // Thread B: synchronized(lock2) { synchronized(lock1) { } } // opposite order -> deadlock
    ```

??? question "What's the difference between `Handler`/`Looper` and coroutines for main-thread work on Android?"
    `Handler`/`Looper` is the low-level message-queue mechanism Android itself uses for the main thread's event loop (posting `Runnable`s/`Message`s); coroutines are a higher-level abstraction built on top of dispatchers, which under the hood can post to a `Handler` (e.g., `Dispatchers.Main` uses the main `Looper`).

    ```kotlin
    Handler(Looper.getMainLooper()).post { updateUi() } // low-level
    scope.launch(Dispatchers.Main) { updateUi() }         // built on top of the same Looper
    ```

??? question "What is a `HandlerThread`, and when would you use one?"
    A `Thread` subclass with its own `Looper`, letting you post sequential tasks to a dedicated background thread's message queue — useful for a single-threaded background work queue before coroutines became the more common approach.

    ```kotlin
    val thread = HandlerThread("worker").apply { start() }
    val handler = Handler(thread.looper)
    handler.post { doSequentialWork() }
    ```

??? question "What's the difference between `Executor`, `ExecutorService`, and `ThreadPoolExecutor`?"
    `Executor` is the simplest interface (just `execute(Runnable)`); `ExecutorService` extends it with lifecycle management and futures (`submit`, `shutdown`); `ThreadPoolExecutor` is a concrete configurable implementation controlling pool size, queueing, and rejection policy.

    ```kotlin
    val executor: ExecutorService = Executors.newFixedThreadPool(4)
    executor.submit { doWork() }
    ```

??? question "What's the Java Memory Model's role in concurrent programming?"
    It defines the rules for how/when writes by one thread become visible to reads by another thread, and what reorderings the compiler/CPU are allowed to perform — without understanding it, seemingly correct concurrent code can fail unpredictably across different hardware/JIT optimizations.

    ```kotlin
    // Without proper synchronization/visibility, one thread's write
    // may never become visible to another thread's read.
    ```

??? question "What's the difference between optimistic and pessimistic locking strategies, and where might each appear in an Android context?"
    Pessimistic locking acquires a lock before accessing a resource (e.g., `synchronized`, blocking until available); optimistic locking assumes no conflict and checks/retries after the fact (e.g., compare-and-swap in `AtomicInteger`, or version-checked DB writes) — optimistic approaches avoid blocking but require a retry path on conflict.

    ```kotlin
    synchronized(lock) { mutate() }            // pessimistic — locks first
    val ok = atomicRef.compareAndSet(old, new) // optimistic — retries on conflict
    ```

## Advanced Coroutines, Flow & Concurrency Patterns

??? question "What is an 'Actor' pattern in coroutines, and how would you implement one with a Channel?"
    A coroutine that owns mutable state exclusively and processes incoming messages sequentially from a Channel, eliminating the need for locks since all state mutation happens on a single coroutine processing one message at a time.

    ```kotlin
    val messages = Channel<Message>()
    scope.launch {
        for (msg in messages) mutateState(msg) // one coroutine, sequential — no locks needed
    }
    ```

??? question "What's the difference between `Semaphore` (kotlinx.coroutines.sync) and a `Mutex`?"
    `Mutex` allows only one coroutine to hold it at a time (binary lock); `Semaphore` allows up to a configurable number of concurrent permits, useful for limiting concurrency to more than one but less than unlimited (e.g., "at most 3 simultaneous downloads").

    ```kotlin
    val semaphore = Semaphore(permits = 3) // up to 3 concurrent
    semaphore.withPermit { download() }
    ```

??? question "What's the difference between structured concurrency's automatic child cancellation and manually tracking a list of Jobs to cancel?"
    Structured concurrency (via scopes) guarantees a parent waits for/cancels all children automatically as part of the language's coroutine builders; manually tracking Jobs is error-prone (easy to forget one, or leak if an exception skips the cleanup code) and duplicates behavior coroutines already provide safely.

    ```kotlin
    coroutineScope { launch { a() }; launch { b() } } // both auto-tracked and cancelled together
    ```

??? question "What's the difference between `awaitAll()` and calling `.await()` on each `Deferred` in a loop sequentially?"
    `awaitAll()` still requires the deferreds to have already been started concurrently (e.g., via multiple `async` calls) and just waits for all of them, propagating the first exception and cancelling the rest; awaiting sequentially in a loop after concurrent `async` starts also works, but calling `async` then `.await()` immediately in a loop (rather than launching all first) would serialize execution unintentionally.

    ```kotlin
    val deferreds = items.map { async { fetch(it) } } // start all first
    val results = deferreds.awaitAll()                 // then await together
    ```

??? question "What's a subtle bug with launching multiple `async` calls in a loop without collecting them into a list first?"
    If you call `.await()` immediately inside the same loop iteration that calls `async`, you accidentally serialize execution (each iteration waits before starting the next); the fix is to store each `Deferred` in a list during the loop, then await them all afterward.

    ```kotlin
    // Bug: serializes execution
    items.forEach { async { fetch(it) }.await() }
    // Fix: start all, then await
    val jobs = items.map { async { fetch(it) } }
    jobs.awaitAll()
    ```

??? question "What's the difference between `Flow.shareIn()` and `Flow.stateIn()`?"
    `stateIn()` produces a `StateFlow` (always has a current value, conflated); `shareIn()` produces a `SharedFlow` with configurable replay count and no requirement for an initial value, suited for sharing a cold flow's emissions among multiple collectors without necessarily representing "current state."

    ```kotlin
    flow.stateIn(scope, SharingStarted.Eagerly, initial)    // StateFlow, always has a value
    flow.shareIn(scope, SharingStarted.Eagerly, replay = 1) // SharedFlow, no required initial value
    ```

??? question "What is `emitAll()` used for inside a `flow {}` builder?"
    It delegates emission to another Flow entirely (forwarding all its values as if emitted directly), useful for combining/chaining flow logic without manually iterating and re-emitting each value.

    ```kotlin
    flow {
        emitAll(otherFlow) // forwards every value from otherFlow as if emitted here
    }
    ```

??? question "What's the difference between cancellation propagating through `withContext` versus through a `launch` inside it?"
    `withContext` is part of the same coroutine (sequential, no new Job in the structured-concurrency child sense) so cancellation of the outer coroutine directly cancels the `withContext` block; a nested `launch` creates an actual child Job which is cancelled as part of structured concurrency when the parent is cancelled, but represents concurrent (not sequential) execution.

    ```kotlin
    coroutineScope {
        withContext(Dispatchers.IO) { } // same coroutine, cancels directly with the parent
        launch { }                       // a real child Job, cancelled via structured concurrency
    }
    ```

??? question "What's the risk of catching a broad `Exception` around a suspend function call that might internally use `withContext(Dispatchers.IO)`?"
    Generally low risk for regular exceptions, but if `CancellationException` (a subclass of `Exception` in Kotlin's hierarchy) is swallowed by an overly broad catch without rethrowing, it silently breaks cancellation propagation — always exclude/rethrow `CancellationException` explicitly in broad catch blocks within coroutines.

    ```kotlin
    try {
        withContext(Dispatchers.IO) { risky() }
    } catch (e: Exception) {
        if (e is CancellationException) throw e // must rethrow, even in a broad catch
    }
    ```

??? question "How would you implement a debounced search-as-you-type feature using Flow operators?"
    Convert text input events into a Flow, apply `.debounce(300)` to wait for a pause in typing, then `.distinctUntilChanged()` to skip redundant identical queries, then `.flatMapLatest { repository.search(it) }` to cancel any in-flight search when a newer query arrives.

    ```kotlin
    searchQueryFlow
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { repository.search(it) }
        .collect { render(it) }
    ```
