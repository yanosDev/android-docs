# Jetpack Compose

Collapsed by default — try to answer before revealing.

## Jetpack Compose

??? question "What is recomposition?"
    The process where Compose re-executes composable functions (or parts of them) in response to observed State changes, updating only the affected UI rather than the entire tree.

    ```kotlin
    @Composable
    fun Counter(count: Int) {
        Text("Count: $count") // re-executes only when `count` actually changes
    }
    ```

??? question "How does Compose decide what to skip during recomposition?"
    It compares the new arguments of a composable to the previous ones using equality checks; if all parameters are stable and equal, the composable is skipped entirely (smart recomposition).

    ```kotlin
    @Composable
    fun Greeting(name: String) { Text("Hi $name") }
    // same `name` next frame -> Compose skips calling Greeting() at all
    ```

??? question "What makes a type 'stable' for Compose's skipping optimization?"
    Its equals() result for two instances must reliably reflect whether public properties differ, its public properties can't change without notifying Compose, and all its public property types are also stable — immutable data classes with primitives typically qualify automatically.

    ```kotlin
    data class UiState(val count: Int) // immutable, primitive props -> stable automatically
    ```

??? question "Why does a plain `List<T>` parameter make a composable 'unstable,' and what's the fix?"
    `List` is an interface whose implementations (like `ArrayList`) are mutable, so Compose can't guarantee immutability; wrapping it as an immutable collection (e.g., Kotlinx `ImmutableList`) or using `@Stable`/`@Immutable` annotations restores skippability.

    ```kotlin
    @Composable
    fun ItemList(items: List<String>) { /* unstable — could secretly be a mutable ArrayList */ }
    // fix: accept kotlinx.collections.immutable.ImmutableList<String> instead
    ```

??? question "What is the difference between `@Stable` and `@Immutable` annotations?"
    `@Immutable` promises the object's properties never change after construction; `@Stable` is a weaker promise allowing mutation as long as Compose is notified (e.g., via `State`) so it can still recompose correctly.

    ```kotlin
    @Immutable data class Point(val x: Int, val y: Int) // never changes after construction
    @Stable class Counter(var value: Int)                // can mutate, but notifies Compose
    ```

??? question "What's the difference between `remember` and `rememberSaveable`?"
    `remember` retains a value across recompositions but loses it on configuration change/process death; `rememberSaveable` persists it in the saved state (like `onSaveInstanceState`) surviving rotation and, with a custom Saver, more complex state.

    ```kotlin
    var count by remember { mutableStateOf(0) }          // lost on rotation
    var count by rememberSaveable { mutableStateOf(0) }  // survives rotation
    ```

??? question "What is a `Saver` and when do you need to write a custom one?"
    It defines how to convert an object to/from a saveable format (Bundle-compatible types); you write a custom one for `rememberSaveable` with types that aren't automatically parcelable/primitive, like a complex data class.

    ```kotlin
    val PointSaver = Saver<Point, List<Int>>(
        save = { listOf(it.x, it.y) },
        restore = { Point(it[0], it[1]) }
    )
    ```

??? question "What's the difference between `State<T>` and `MutableState<T>`?"
    `State<T>` is read-only and used to observe changes; `MutableState<T>` extends it with a settable `value`, and setting it triggers recomposition of any composable reading it.

    ```kotlin
    val readOnly: State<Int> = mutableStateOf(0)      // read-only view
    val mutable: MutableState<Int> = mutableStateOf(0)
    mutable.value = 1 // triggers recomposition of readers
    ```

??? question "What's the difference between `mutableStateOf` with `by` delegate vs `.value` access?"
    `by` delegate (using Kotlin property delegation) lets you read/write the state directly as if it were the value itself (cleaner syntax); `.value` requires explicit `.value` access each time — both trigger the same recomposition behavior.

    ```kotlin
    var count by remember { mutableStateOf(0) } // count++ works directly
    val countState = remember { mutableStateOf(0) }
    countState.value++ // same effect, explicit .value
    ```

??? question "What is `derivedStateOf` used for?"
    It computes a value from other State objects but only triggers recomposition when the *computed result* actually changes, avoiding unnecessary recompositions when an input changes but the derived output doesn't (e.g., scroll position -> "show button" boolean).

    ```kotlin
    val showButton by remember { derivedStateOf { scrollState.value > 100 } }
    // recomposes only when the Boolean flips, not on every scroll pixel
    ```

??? question "When should you avoid `derivedStateOf`?"
    For simple, cheap computations — it adds overhead of its own tracking, so it's only worth it when the computation is expensive or reads frequently-changing state but produces an infrequently-changing result.

    ```kotlin
    val doubled by remember { derivedStateOf { count * 2 } } // overkill — just use `count * 2` directly
    ```

??? question "What is `LaunchedEffect` used for, and what triggers it to restart?"
    It runs a suspend-function side effect scoped to the composition, restarting whenever any of its key parameters change; if a key changes, the previous coroutine is cancelled and a new one launched.

    ```kotlin
    LaunchedEffect(userId) {
        viewModel.loadUser(userId) // cancels and restarts if `userId` changes
    }
    ```

??? question "What is `DisposableEffect` used for?"
    Side effects that need explicit cleanup when the composable leaves composition or keys change, via the mandatory `onDispose {}` block (e.g., registering/unregistering a listener).

    ```kotlin
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, _ -> }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }
    ```

??? question "What is `SideEffect` used for, and how does it differ from `LaunchedEffect`?"
    `SideEffect` runs on every successful recomposition (not suspending, no keys), typically used to publish Compose state to non-Compose code (e.g., updating an analytics tool with the latest value); `LaunchedEffect` runs a suspend block tied to specific keys.

    ```kotlin
    SideEffect {
        analytics.setUserProperty("screen", screenName) // runs after every successful recomposition
    }
    ```

??? question "What is `produceState` used for?"
    It converts non-Compose asynchronous data sources (e.g., a callback API or Flow-less source) into Compose `State`, running inside a coroutine that can push values via `value = ...`.

    ```kotlin
    val user by produceState<User?>(initialValue = null, userId) {
        value = repository.loadUser(userId)
    }
    ```

??? question "What is `rememberCoroutineScope` used for, and how does it differ from `LaunchedEffect`?"
    It gives you a `CoroutineScope` tied to the composition for launching coroutines from *event callbacks* (e.g., a button click), whereas `LaunchedEffect` launches automatically as part of composition itself.

    ```kotlin
    val scope = rememberCoroutineScope()
    Button(onClick = { scope.launch { doWork() } }) { Text("Go") }
    ```

??? question "What is a `CompositionLocal` and when should you avoid it?"
    It implicitly passes data down the composition tree without explicit parameters (e.g., theme colors); avoid it for passing plain data/business logic since it hides dependencies and makes composables harder to test/reason about — reserve it for cross-cutting concerns like theming.

    ```kotlin
    val LocalTheme = staticCompositionLocalOf { LightColors }
    CompositionLocalProvider(LocalTheme provides DarkColors) { Content() }
    ```

??? question "What's the difference between `staticCompositionLocalOf` and `compositionLocalOf`?"
    `compositionLocalOf` supports fine-grained recomposition when its value changes (only readers recompose); `staticCompositionLocalOf` is cheaper but causes the entire content block at the `CompositionLocalProvider` to recompose on change — use static for rarely-changing values like theme.

    ```kotlin
    val LocalUser = compositionLocalOf { User.Guest }        // fine-grained recomposition
    val LocalTheme = staticCompositionLocalOf { LightColors } // cheaper, coarser recomposition
    ```

??? question "How do you optimize a `LazyColumn` with thousands of items?"
    Provide stable/unique `key`s per item, use `contentType` for heterogeneous item layouts to improve slot reuse, avoid heavy work inside item composables, and keep lambdas passed to items from causing unnecessary recomposition via stable references.

    ```kotlin
    LazyColumn {
        items(items, key = { it.id }, contentType = { it.type }) { item ->
            ItemRow(item)
        }
    }
    ```

??? question "Why does providing a `key` to `LazyColumn` items matter?"
    It preserves item identity across list reordering/insertion/removal, so Compose reuses composition and state (like scroll/animation) correctly for the same logical item instead of misattributing it.

    ```kotlin
    items(list, key = { it.id }) { item -> ItemRow(item) } // identity survives reordering
    ```

??? question "What is `Modifier.clickable` versus using `pointerInput` with a custom gesture detector?"
    `clickable` provides ready-made click/long-click handling with ripple and accessibility semantics built in; `pointerInput` with `detectDragGestures`/`detectTapGestures` etc. gives raw access for custom gesture logic (e.g., drag, multi-touch) at the cost of manually handling accessibility/semantics.

    ```kotlin
    Modifier.clickable { onClick() }                                // ready-made, accessible
    Modifier.pointerInput(Unit) { detectDragGestures { _, _ -> } }   // raw gesture control
    ```

??? question "What is the purpose of `Modifier` order, and give an example where order changes behavior?"
    Modifiers apply sequentially like a wrapped pipeline; e.g., `Modifier.padding(16.dp).clickable {}` makes the padding NOT clickable (click area excludes padding), while `Modifier.clickable{}.padding(16.dp)` makes the whole padded area clickable.

    ```kotlin
    Modifier.padding(16.dp).clickable {} // padding is NOT part of the click area
    Modifier.clickable {}.padding(16.dp) // the whole padded area IS clickable
    ```

??? question "What's the difference between `Box`, `Column`/`Row`, and `ConstraintLayout` in Compose?"
    `Box` stacks children with alignment; `Column`/`Row` arrange linearly; `ConstraintLayout` allows complex constraint-based positioning (useful for cases hard to express with simple linear/stack layouts, similar to the View-based ConstraintLayout).

    ```kotlin
    Box { Text("Back"); Text("Front") }    // stacked
    Column { Text("Top"); Text("Bottom") } // linear
    ConstraintLayout { /* constraint-based positioning */ }
    ```

??? question "What is a slot-based API in Compose, and why does `Scaffold` use composable lambda parameters?"
    A slot API exposes parameters as composable lambdas (e.g., `topBar: @Composable () -> Unit`) rather than fixed values, letting callers inject arbitrary custom composables into predefined layout "slots" for flexibility.

    ```kotlin
    Scaffold(topBar = { TopAppBar(title = { Text("Home") }) }) { padding ->
        Content(padding)
    }
    ```

??? question "How does Compose interoperate with the classic View system?"
    `AndroidView` embeds a legacy View/ViewGroup inside Compose; `ComposeView` embeds Compose content inside a classic View hierarchy (e.g., inside a Fragment using the old view system).

    ```kotlin
    AndroidView(factory = { context -> LegacyMapView(context) }) // legacy View, inside Compose
    ```

??? question "What's the difference between `Modifier.size()`, `requiredSize()`, and `wrapContentSize()`?"
    `size()` sets the size but constraints from the parent can still override/coerce it; `requiredSize()` forces the exact size regardless of parent constraints (can overflow); `wrapContentSize()` sizes to content while allowing extra alignment space within available constraints.

    ```kotlin
    Modifier.size(100.dp)          // parent can still shrink it
    Modifier.requiredSize(100.dp)  // exact, ignores parent constraints
    Modifier.wrapContentSize()     // sized to content
    ```

??? question "What causes unnecessary recompositions and how would you diagnose them?"
    Common causes: unstable parameter types (plain interfaces/lambdas capturing changing state), reading state too high in the tree, or missing `remember`; diagnose via Layout Inspector's recomposition counts, the Compose compiler's stability/metrics reports, or `Modifier.recomposeHighlighter` in debug builds.

    ```kotlin
    @Composable
    fun Row(onClick: () -> Unit) { /* a freshly-created lambda each call re-triggers this */ }
    ```

??? question "What are Compose compiler metrics/reports and why generate them?"
    Build-time reports listing which composables are skippable/restartable and which parameters are stable/unstable, helping identify performance bottlenecks caused by unstable types before they cause visible jank.

    ```text
    ./gradlew assembleRelease -PcomposeCompilerReports=true
    ```

??? question "What is the difference between a 'restartable' and 'skippable' composable?"
    Restartable means Compose can re-invoke just that function on state change without restarting the whole parent; skippable means Compose can additionally skip re-invoking it entirely if its inputs are unchanged — most composables aim to be both.

    ```kotlin
    @Composable
    fun Item(text: String) { Text(text) } // restartable, and skippable if `text` is stable
    ```

??? question "What's the difference between `Layout` and `SubcomposeLayout`?"
    `Layout` measures/places children in a single pass with fixed composition; `SubcomposeLayout` defers composing some children until measurement-time information is known (e.g., sizing a child based on another child's measured size), at a performance cost.

    ```kotlin
    Layout(content = { /* children */ }) { measurables, constraints -> /* single pass */ }
    SubcomposeLayout { constraints -> /* compose more, now that sizes are known */ }
    ```

??? question "How does Compose handle animation state, e.g. `animateFloatAsState`?"
    It creates a `State<Float>` that automatically animates toward a target value using coroutines internally, triggering recomposition on each animation frame update without manual `Animator` listener management.

    ```kotlin
    val alpha by animateFloatAsState(if (visible) 1f else 0f)
    Box(Modifier.graphicsLayer { this.alpha = alpha })
    ```

??? question "What's the difference between `Crossfade`, `AnimatedVisibility`, and `AnimatedContent`?"
    `Crossfade` fades between two arbitrary content states; `AnimatedVisibility` animates a single composable's enter/exit with configurable transitions; `AnimatedContent` animates between different content states with customizable enter/exit + sizing transforms, more general than Crossfade.

    ```kotlin
    Crossfade(targetState = tab) { t -> Screen(t) }
    AnimatedVisibility(visible = show) { Banner() }
    AnimatedContent(targetState = count) { c -> Text("$c") }
    ```

??? question "What is `Modifier.graphicsLayer` used for and why is it more performant for certain animations?"
    It applies transformations (alpha, scale, rotation, clip) at the rendering layer without triggering full recomposition/relayout, making animations of these properties cheaper than animating layout-affecting properties.

    ```kotlin
    Modifier.graphicsLayer { alpha = 0.5f; rotationZ = 45f } // rendering-layer only, no relayout
    ```

??? question "What's the difference in Compose's three phases — composition, layout, and drawing?"
    Composition decides what UI to emit (executing composables), layout measures/places elements in the tree, and drawing renders pixels; understanding which phase a piece of state affects helps avoid unnecessarily re-triggering earlier (more expensive) phases.

    ```text
    Composition (what to show) -> Layout (measure/place) -> Draw (pixels)
    ```

??? question "How would you test a Compose UI, and what's `ComposeTestRule` for?"
    `ComposeTestRule` sets up an isolated composition host for tests, providing `setContent {}`, node finders (`onNodeWithText`), and synchronization with idle/animation state — analogous to Espresso but for Compose trees.

    ```kotlin
    @get:Rule val composeRule = createComposeRule()

    @Test fun test() {
        composeRule.setContent { MyScreen() }
        composeRule.onNodeWithText("Submit").performClick()
    }
    ```

??? question "What is `Modifier.semantics` used for?"
    Attaching accessibility/testing metadata to a composable (e.g., custom content description, test tags via `testTag`, or merging descendant semantics) so screen readers and UI tests can interact with it meaningfully.

    ```kotlin
    Modifier.semantics {
        contentDescription = "Profile picture"
        testTag = "avatar"
    }
    ```

??? question "What's the difference between `@Preview` and running the app for UI iteration?"
    `@Preview` renders a composable in isolation within Android Studio without deploying the full app, speeding up UI iteration, though it can't exercise real runtime dependencies (network, DI) without fakes/mock data.

    ```kotlin
    @Preview
    @Composable
    fun GreetingPreview() { Greeting("Ada") } // renders in Studio, no real network/DI
    ```

??? question "What is Baseline Profile's relevance to Compose specifically?"
    Compose relies heavily on JIT-compiled code paths; without a baseline profile, first-run composition/recomposition can be slower until JIT warms up — baseline profiles pre-compile hot Compose runtime paths (like the runtime package) ahead of time.

    ```text
    generateBaselineProfile task -> profiles hot Compose runtime paths for AOT compilation
    ```

## Compose Deep Dive (Navigation, State Hoisting, Advanced Layout)

??? question "What is state hoisting in Compose, and why is it recommended?"
    Moving state up to a common ancestor (often the caller) and passing it down as parameters plus an event callback to modify it, rather than having a composable own its own mutable state internally; this makes composables stateless/reusable and testable, and gives the caller control over the source of truth.

    ```kotlin
    @Composable
    fun Counter(count: Int, onIncrement: () -> Unit) { // stateless — state hoisted to the caller
        Button(onClick = onIncrement) { Text("$count") }
    }
    ```

??? question "What's the difference between a 'stateful' and 'stateless' composable?"
    A stateful composable manages its own internal `remember`ed state; a stateless composable receives all its data via parameters and reports events via callbacks, with no internal mutable state of its own — generally preferred for reusability.

    ```kotlin
    @Composable
    fun StatefulCounter() {
        var count by remember { mutableStateOf(0) } // owns its own state
        Counter(count) { count++ }
    }
    ```

??? question "How does Navigation Compose differ from the Fragment-based Navigation component?"
    It replaces destinations with composable functions directly (`composable("route") { ScreenContent() }`) instead of Fragments, and passes arguments via the route string/NavBackStackEntry rather than a Bundle with Safe Args-generated classes (though type-safe navigation APIs have since been added).

    ```kotlin
    NavHost(navController, startDestination = "home") {
        composable("home") { HomeScreen() }
        composable("detail/{id}") { entry -> DetailScreen(entry.arguments) }
    }
    ```

??? question "How do you pass complex objects (not just primitives) between Compose Navigation destinations?"
    Either pass just an ID/key and have the destination look up the full object from a shared ViewModel/repository, or use the type-safe navigation APIs with a serializable route object, since navigation arguments are fundamentally passed as part of a string-based route/back stack entry.

    ```kotlin
    composable("detail/{userId}") { entry ->
        val userId = entry.arguments?.getString("userId")
        DetailScreen(viewModel.getUser(userId)) // look up by ID, not passed directly
    }
    ```

??? question "What is `rememberNavController()` and where should it typically be hoisted?"
    It creates/remembers the `NavController` managing the navigation graph's back stack; it's typically hoisted near the top of the composable tree (e.g., at the Activity's `setContent` level) so it isn't recreated/lost across recompositions of nested screens.

    ```kotlin
    setContent {
        val navController = rememberNavController() // hoisted once, at the root
        NavHost(navController, "home") { /* ... */ }
    }
    ```

??? question "What's the difference between `Modifier.weight()` inside a `Row`/`Column` and just setting a fixed `fillMaxWidth(fraction)`?"
    `weight()` distributes remaining available space proportionally among siblings after fixed-size siblings are measured, adapting to dynamic content; `fillMaxWidth(fraction)` sets a fixed fraction of the parent's total width regardless of siblings' actual sizes.

    ```kotlin
    Row {
        Text("A", Modifier.weight(1f)) // shares remaining space
        Text("B", Modifier.weight(2f)) // gets twice as much of what's left
    }
    ```

??? question "What is `Modifier.layout {}` used for as a low-level escape hatch?"
    It lets you customize exactly how a composable measures and places its content within available constraints, useful for custom layout behavior not achievable with existing layout composables.

    ```kotlin
    Modifier.layout { measurable, constraints ->
        val placeable = measurable.measure(constraints)
        layout(placeable.width, placeable.height) { placeable.place(0, 0) }
    }
    ```

??? question "What's the difference between `IntrinsicSize.Min`/`Max` and normal constraint-based sizing?"
    Intrinsic sizing lets a composable query a child's minimum/maximum content size independent of the actual final constraints (e.g., to make all children in a Row match the tallest child's height) — an additional measurement pass with real performance cost, so used sparingly.

    ```kotlin
    Row(Modifier.height(IntrinsicSize.Min)) {
        Text("Short", Modifier.fillMaxHeight())
        VerticalDivider(Modifier.fillMaxHeight()) // matches the tallest sibling's height
    }
    ```

??? question "What is the 'phantom' recomposition problem where a lambda passed as a parameter causes unnecessary recomposition?"
    If a lambda captures unstable variables and is recreated on every parent recomposition (a "new" lambda instance each time even if functionally identical), Compose sees it as a changed parameter and recomposes the child unnecessarily — often fixed via `remember { }` around the lambda or restructuring so the lambda doesn't capture changing state directly.

    ```kotlin
    @Composable
    fun Parent() {
        Child(onClick = { doSomething() }) // a new lambda instance on every recomposition!
    }
    // fix: val onClick = remember { { doSomething() } }
    ```

??? question "What's the difference between `Modifier.pointerInput(Unit)` and `Modifier.pointerInput(someKey)`?"
    The key(s) determine when the gesture-detection coroutine restarts; `Unit` (a constant) means it never restarts across recompositions, while a changing key restarts gesture detection whenever that key's value changes, useful when the gesture logic depends on data that can change.

    ```kotlin
    Modifier.pointerInput(Unit) { detectTapGestures { } }   // never restarts
    Modifier.pointerInput(itemId) { detectTapGestures { } } // restarts when itemId changes
    ```

??? question "How would you implement a custom Compose theme supporting both light/dark and dynamic (Material You) color?"
    Define a `ColorScheme` per mode, use `dynamicLightColorScheme(context)`/`dynamicDarkColorScheme(context)` on API 31+ derived from the user's wallpaper, falling back to a static custom `ColorScheme` on older API levels, wrapped in a single `MaterialTheme` composable at the app root reading `isSystemInDarkTheme()`.

    ```kotlin
    val colors = when {
        Build.VERSION.SDK_INT >= 31 && isSystemInDarkTheme() -> dynamicDarkColorScheme(context)
        Build.VERSION.SDK_INT >= 31 -> dynamicLightColorScheme(context)
        else -> LightColors
    }
    MaterialTheme(colorScheme = colors) { Content() }
    ```

## Compose Modifier.Node API & Transition Deep Dive

??? question "What is the `Modifier.Node` API, and why was it introduced alongside the older composed-modifier approach?"
    It lets you implement a custom modifier as a long-lived node object with its own lifecycle hooks, avoiding the overhead of re-invoking a composable lambda (`Modifier.composed {}`) on every recomposition, giving significantly better performance for custom modifiers used widely across a UI.

    ```kotlin
    class MyNode : Modifier.Node() { /* created once, updated incrementally */ }
    ```

??? question "What's the difference between `Modifier.composed {}` and implementing a `Modifier.Node`-based custom modifier?"
    `composed {}` re-executes its lambda (including any `remember` calls inside it) on each recomposition of the composable it's attached to, which has real overhead at scale; a `Modifier.Node` implementation is created once and updated incrementally, avoiding that repeated re-composition cost.

    ```kotlin
    fun Modifier.oldWay() = composed { val state = remember { Any() }; this } // re-runs the lambda
    class NewWay : Modifier.Node()                                             // created once
    ```

??? question "What is the `Transition` API in Compose, and how does it differ from a single `animate*AsState` call?"
    `Transition` (via `updateTransition`) coordinates multiple animated properties together as a single named state-transition unit (e.g., animating color, size, and elevation together when a component moves between two defined states), giving a single point of control/observation for a coordinated multi-property animation, unlike independent `animateFloatAsState` calls per property.

    ```kotlin
    val transition = updateTransition(targetState = selected, label = "selected")
    val color by transition.animateColor { if (it) Color.Green else Color.Gray }
    val size by transition.animateDp { if (it) 48.dp else 24.dp } // coordinated together
    ```

??? question "What is `MutableTransitionState` used for versus a plain Boolean/enum state driving a `Transition`?"
    It lets you observe/control both the transition's target state and whether an initial "starting" animation should play from a specified start state, useful for entrance animations that should behave differently on first composition versus later state changes.

    ```kotlin
    val state = remember { MutableTransitionState(false) }.apply { targetState = true }
    AnimatedVisibility(visibleState = state) { Content() }
    ```

??? question "What's the difference between `AnimatedContent`'s `contentKey` and its `transitionSpec`?"
    `contentKey` determines when Compose treats content as a genuinely new item (versus just a re-render of the same logical content) for enter/exit purposes; `transitionSpec` defines *how* the enter/exit animation visually behaves once a content-key change triggers a transition.

    ```kotlin
    AnimatedContent(
        targetState = page,
        contentKey = { it.id },                              // "is this really new content?"
        transitionSpec = { fadeIn() togetherWith fadeOut() }  // "how does it animate?"
    ) { p -> PageContent(p) }
    ```

## Compose Shared Elements, Lookahead & Preview Providers

??? question "What is a shared element transition in Compose, and what API enables it?"
    An animation where an element visually morphs/moves smoothly from its position/size on one screen to its position/size on another during navigation (e.g., a list thumbnail expanding into a detail image), enabled via the `SharedTransitionLayout`/`Modifier.sharedElement` APIs built on Compose's Lookahead system.

    ```kotlin
    SharedTransitionLayout {
        AnimatedContent(targetState = screen) { s ->
            Image(Modifier.sharedElement(rememberSharedContentState("thumb"), this@AnimatedContent))
        }
    }
    ```

??? question "What is `LookaheadScope` used for in Compose animation?"
    It lets a layout measure/report its *final* post-animation target size/position ahead of time, so animations (like shared elements or animated layout changes) can smoothly interpolate toward the real target rather than animating toward an intermediate/incorrect layout guess.

    ```kotlin
    LookaheadScope {
        Box(Modifier.animateBounds(this)) // knows the real final position ahead of time
    }
    ```

??? question "What is a `PreviewParameterProvider` used for in Compose `@Preview`s?"
    It supplies multiple sample data sets to render the same composable preview repeatedly with different inputs (e.g., empty state, loading state, populated state) without manually writing a separate `@Preview` function for each variation.

    ```kotlin
    class StateProvider : PreviewParameterProvider<UiState> {
        override val values = sequenceOf(UiState.Loading, UiState.Content, UiState.Error)
    }

    @Preview
    @Composable
    fun Preview(@PreviewParameter(StateProvider::class) state: UiState) { Screen(state) }
    ```

??? question "What's the difference between `@Preview(showBackground = true)` and just wrapping the preview content in your app's theme?"
    `showBackground` only adds a plain background color behind the preview for visibility; wrapping in your actual `MaterialTheme`/custom theme ensures the preview reflects real typography, colors, and shapes exactly as they'd appear in the running app, catching theme-related visual issues a plain background wouldn't reveal.

    ```kotlin
    @Preview(showBackground = true)
    @Composable
    fun Bare() { Greeting("Ada") }               // just a background color

    @Preview
    @Composable
    fun Themed() { AppTheme { Greeting("Ada") } } // real typography/colors
    ```

??? question "What is `LocalContext.current` in Compose, and why should you be cautious using it for anything beyond simple resource/string lookups?"
    It provides the current `Context` via a `CompositionLocal`; overusing it for business logic (e.g., directly starting Activities or accessing system services deep in UI code) couples composables tightly to Android specifics and hurts testability — such calls are usually better delegated to a ViewModel/navigation callback instead.

    ```kotlin
    val context = LocalContext.current
    Text(stringResource(R.string.hello)) // fine
    // context.startActivity(...) // avoid — push this to a ViewModel/callback instead
    ```

## Compose Item Animations, Live Regions & Modern Notification Restrictions

??? question "What does `Modifier.animateItemPlacement()` (Compose lazy lists) do, and when does it trigger?"
    It animates an item's position change within a `LazyColumn`/`LazyRow` when the list is reordered/filtered (as long as the item's `key` is preserved across the change), producing a smooth reflow animation instead of items jumping instantly to new positions.

    ```kotlin
    LazyColumn {
        items(list, key = { it.id }) { item ->
            Row(Modifier.animateItemPlacement()) { ItemRow(item) } // smooth reflow on reorder
        }
    }
    ```

??? question "What is an accessibility 'live region,' and when should you mark a composable/View with one?"
    A live region tells assistive technology to automatically announce content changes within it without requiring explicit focus (e.g., a status message or error text that updates dynamically); mark only content that genuinely needs proactive announcement, since overusing live regions creates noisy, unpredictable announcements for screen-reader users.

    ```kotlin
    Modifier.semantics { liveRegion = LiveRegionMode.Polite } // announces text changes automatically
    ```

??? question "How have full-screen intent notifications been further restricted in recent Android versions (targeting Android 14+)?"
    Apps must now explicitly request the ability to use full-screen intents (subject to policy justification, since it's reserved for genuinely urgent/interruptive cases like calls and alarms) rather than being able to freely trigger a full-screen launch from any notification, curbing past abuse for intrusive ads/prompts.

    ```xml
    <uses-permission android:name="android.permission.USE_FULL_SCREEN_INTENT" />
    ```

??? question "What's a recommended UX pattern for requesting a 'dangerous' runtime permission, beyond just calling the request API immediately on screen load?"
    Show contextual, just-in-time rationale explaining *why* the permission is needed right before the feature that requires it (rather than requesting everything upfront at app launch), improving grant rates and user trust compared to an unexplained system dialog appearing out of context.

    ```kotlin
    if (shouldShowRequestPermissionRationale(activity, permission)) {
        showRationaleDialog() // explain *why*, right before the feature that needs it
    } else {
        requestPermissionLauncher.launch(permission)
    }
    ```
