# Views & RecyclerView

Collapsed by default — try to answer before revealing.

## Classic Views, Custom Views & RecyclerView

??? question "What's the difference between `measure`, `layout`, and `draw` passes in the View system?"
    `measure` determines each View's size based on constraints (`MeasureSpec`), `layout` positions Views within their parent, and `draw` renders the actual pixels via `Canvas` — always in that order per frame.

    ```kotlin
    override fun onMeasure(w: Int, h: Int) { setMeasuredDimension(width, height) }
    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) { /* position children */ }
    override fun onDraw(canvas: Canvas) { canvas.drawCircle(cx, cy, radius, paint) }
    ```

??? question "What is a `MeasureSpec` and what are its three modes?"
    It encodes a parent's sizing constraint for a child as a single int (size + mode); modes are `EXACTLY` (fixed size), `AT_MOST` (max size, like wrap_content within a bound), and `UNSPECIFIED` (no constraint).

    ```kotlin
    val mode = MeasureSpec.getMode(widthMeasureSpec) // EXACTLY, AT_MOST, or UNSPECIFIED
    val size = MeasureSpec.getSize(widthMeasureSpec)
    ```

??? question "What's the difference between `invalidate()` and `requestLayout()`?"
    `invalidate()` schedules a redraw only (no size/position change assumed); `requestLayout()` triggers a full measure+layout pass because the View's size or position may have changed.

    ```kotlin
    paint.color = Color.RED
    invalidate()      // just redraw

    someDimension = 200
    requestLayout()   // size changed — remeasure first
    ```

??? question "How do you create a performant custom View that draws with Canvas?"
    Override `onDraw()` for drawing only (avoid allocations there), override `onMeasure()` to report proper size, avoid unnecessary `invalidate()` calls, and cache expensive objects like `Paint`/`Path` as fields rather than recreating them per frame.

    ```kotlin
    class Gauge(context: Context) : View(context) {
        private val paint = Paint() // reused, not allocated per frame
        override fun onDraw(canvas: Canvas) { canvas.drawArc(rect, 0f, sweep, false, paint) }
    }
    ```

??? question "Why is allocating objects inside `onDraw()` considered a performance mistake?"
    `onDraw()` can be called many times per second during animation/scrolling; allocating objects there increases GC pressure and can cause jank from frequent garbage collection pauses.

    ```kotlin
    override fun onDraw(canvas: Canvas) {
        val paint = Paint() // BAD — allocates on every single frame
        canvas.drawCircle(cx, cy, r, paint)
    }
    ```

??? question "What's the difference between `ViewGroup.onLayout()` and `View.onLayout()`?"
    `ViewGroup.onLayout()` is responsible for positioning its children by calling `child.layout()` for each; a plain `View` doesn't have children, so its `onLayout()` typically does nothing beyond the default.

    ```kotlin
    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        getChildAt(0).layout(0, 0, childWidth, childHeight) // ViewGroup positions its children
    }
    ```

??? question "How does RecyclerView's view-recycling mechanism improve on the old ListView?"
    `RecyclerView` formalizes the ViewHolder pattern (previously optional convention in ListView), enforces recycling via a pluggable `LayoutManager` and `RecycledViewPool`, and supports item animations and multiple layout types (linear, grid, staggered) more flexibly.

    ```kotlin
    class MyViewHolder(view: View) : RecyclerView.ViewHolder(view) // enforced, not just convention
    ```

??? question "What is `DiffUtil` and what problem does it solve?"
    It calculates the minimal set of insert/remove/move operations between two list versions (via a diffing algorithm), allowing `RecyclerView` to animate only the specific changed items instead of calling `notifyDataSetChanged()` and redrawing everything.

    ```kotlin
    val diff = DiffUtil.calculateDiff(MyDiffCallback(oldList, newList))
    diff.dispatchUpdatesTo(adapter) // animates only what actually changed
    ```

??? question "What's the difference between `notifyDataSetChanged()` and targeted `notifyItemChanged()`/`ListAdapter` with `DiffUtil`?"
    `notifyDataSetChanged()` discards all item animations/state and rebinds every visible item, which is inefficient and jarring; targeted notifications or `DiffUtil`-driven updates animate and rebind only what actually changed.

    ```kotlin
    adapter.notifyDataSetChanged()       // rebinds everything, no animation
    adapter.notifyItemChanged(position)  // targeted, animates just that item
    ```

??? question "What is `ListAdapter` (androidx) and how does it simplify DiffUtil usage?"
    It wraps `RecyclerView.Adapter` with built-in asynchronous list diffing via `submitList()`, computing the diff off the main thread and dispatching minimal updates automatically.

    ```kotlin
    class MyAdapter : ListAdapter<Item, MyViewHolder>(MyDiffCallback())
    adapter.submitList(newItems) // diffs off the main thread automatically
    ```

??? question "What is the RecycledViewPool used for, and when would you share one across multiple RecyclerViews?"
    It caches unused ViewHolders for reuse; sharing a pool across RecyclerViews with the same view types (e.g., nested horizontal RecyclerViews inside a vertical one) avoids redundant view inflation across the different lists.

    ```kotlin
    val pool = RecyclerView.RecycledViewPool()
    recyclerViewA.setRecycledViewPool(pool)
    recyclerViewB.setRecycledViewPool(pool) // shares recycled views across both
    ```

??? question "What's the difference between `setHasFixedSize(true)` and leaving it false?"
    `true` tells RecyclerView that its own size doesn't change based on adapter content changes, allowing it to skip a layout pass on data changes for a performance gain — only set it when actually true.

    ```kotlin
    recyclerView.setHasFixedSize(true) // only when the RV's own size truly won't change
    ```

??? question "What's a common cause of RecyclerView item flicker/reset (e.g., a checkbox or image resetting) during scroll?"
    Not properly binding *all* relevant state in `onBindViewHolder` (relying on leftover state from a recycled view), especially forgetting to reset a view's state explicitly when the new data doesn't have that property set.

    ```kotlin
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.checkbox.isChecked = items[position].isChecked // must always set, even when false!
    }
    ```

??? question "What is `ItemAnimator` in RecyclerView, and when would you customize it?"
    It controls animations for add/remove/move/change operations; you customize it (e.g., extending `DefaultItemAnimator`) for custom transition effects beyond the default fade/move behavior.

    ```kotlin
    recyclerView.itemAnimator = object : DefaultItemAnimator() { /* custom transitions */ }
    ```

??? question "What's the difference between `LinearLayoutManager`, `GridLayoutManager`, and `StaggeredGridLayoutManager`?"
    `LinearLayoutManager` arranges items in a single row/column; `GridLayoutManager` arranges in a fixed grid with configurable span sizes; `StaggeredGridLayoutManager` allows variable item heights/widths in a staggered grid layout (like a Pinterest-style feed).

    ```kotlin
    recyclerView.layoutManager = LinearLayoutManager(context)
    recyclerView.layoutManager = GridLayoutManager(context, /* spanCount = */ 2)
    recyclerView.layoutManager = StaggeredGridLayoutManager(2, StaggeredGridLayoutManager.VERTICAL)
    ```

??? question "What is ViewBinding and how does it differ from findViewById and DataBinding?"
    ViewBinding generates a typed binding class per XML layout with direct field references (compile-time null/type safety, no reflection), unlike `findViewById` (runtime lookups, unsafe casts); it's lighter than full DataBinding since it doesn't support binding expressions/observable data in XML.

    ```kotlin
    val binding = ItemUserBinding.inflate(inflater, parent, false)
    binding.nameText.text = user.name // typed, no findViewById/casting
    ```

??? question "What is DataBinding's two-way binding (`@={}`), and what's a caveat with using it heavily?"
    It automatically syncs a UI property (e.g., EditText text) with a data model property bidirectionally; overuse can make UI logic implicit and harder to trace/debug/test compared to explicit ViewModel-driven unidirectional updates.

    ```xml
    <EditText android:text="@={viewModel.name}" /> <!-- syncs both ways automatically -->
    ```

??? question "What is `MotionLayout` used for beyond ConstraintLayout?"
    Declarative, complex motion/animation choreography between multiple `ConstraintSet` states (e.g., a collapsing header), driven by gestures, keyframes, or triggers, without manual property animators.

    ```xml
    <androidx.constraintlayout.motion.widget.MotionLayout
        app:layoutDescription="@xml/scene"> <!-- ConstraintSets + transitions --> </androidx.constraintlayout.motion.widget.MotionLayout>
    ```

??? question "What's the difference between `View.GONE`, `View.INVISIBLE`, and setting alpha to 0?"
    `GONE` removes the View from layout entirely (no space reserved); `INVISIBLE` keeps its layout space but doesn't draw it; alpha 0 draws it fully transparent but it still participates in layout and is still clickable/touchable unless explicitly disabled.

    ```kotlin
    view.visibility = View.GONE      // no space reserved
    view.visibility = View.INVISIBLE // space reserved, not drawn
    view.alpha = 0f                  // drawn transparent, still clickable!
    ```

??? question "What is overdraw, and how do you detect/reduce it?"
    Overdraw is drawing the same pixel multiple times in one frame (e.g., stacked opaque backgrounds); detect via "Debug GPU Overdraw" developer option, reduce by removing unnecessary background layers/flattening view hierarchies.

    ```kotlin
    // parent has android:background="@color/white"
    // child ALSO has android:background="@color/white" — same pixel drawn twice
    ```

??? question "What's the difference between a `ViewStub` and simply setting a View's visibility to GONE?"
    A `ViewStub` doesn't inflate its referenced layout at all until explicitly made visible, saving inflation cost for rarely-shown UI; a GONE View is already inflated and just skipped during layout/draw, so it doesn't save inflation time.

    ```kotlin
    val stub = findViewById<ViewStub>(R.id.stub)
    val inflated = stub.inflate() // only now does the referenced layout actually get created
    ```

??? question "What's the purpose of the `<merge>` tag in a layout XML?"
    It avoids adding an unnecessary extra ViewGroup layer when a layout is included into another (`<include>`) or inflated directly into a parent that already provides the needed ViewGroup, reducing view hierarchy depth.

    ```xml
    <merge xmlns:android="http://schemas.android.com/apk/res/android">
        <TextView android:id="@+id/title" android:layout_width="match_parent" android:layout_height="wrap_content" />
    </merge>
    ```

## Custom Views, Canvas & Animation (View System)

??? question "What's the difference between `Canvas.drawPath()` with a `Path` object versus drawing individual primitive shapes?"
    A `Path` lets you compose complex, arbitrary vector shapes (curves, combined subpaths, fill rules) as a single drawable unit, which can also be used for clipping or animated with `PathMeasure`, whereas primitive shape calls (`drawRect`, `drawCircle`) are limited to their fixed geometric form.

    ```kotlin
    val path = Path().apply { moveTo(0f, 0f); quadTo(50f, 100f, 100f, 0f) }
    canvas.drawPath(path, paint) // an arbitrary curve, vs. canvas.drawRect()/drawCircle()
    ```

??? question "What is `PorterDuff.Mode` used for in custom drawing?"
    It defines how a new drawing operation's pixels combine with existing pixels already on the canvas/bitmap (e.g., `SRC_IN`, `DST_OVER`), commonly used for masking effects like clipping an image to a shape or tinting.

    ```kotlin
    paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.SRC_IN) // clips the image to a mask shape
    ```

??? question "What's the difference between a `ValueAnimator` and an `ObjectAnimator`?"
    `ValueAnimator` just produces animated values over time that you manually apply in an update listener; `ObjectAnimator` automatically applies the animated value to a target object's property via its setter, removing the need for a manual listener in simple cases.

    ```kotlin
    ValueAnimator.ofFloat(0f, 1f).apply {
        addUpdateListener { view.alpha = it.animatedValue as Float } // manual apply
    }
    ObjectAnimator.ofFloat(view, "alpha", 0f, 1f) // applies directly, no listener needed
    ```

??? question "What is a `PropertyValuesHolder` used for?"
    It lets a single `ObjectAnimator`/`ValueAnimator` animate multiple properties simultaneously (e.g., both `scaleX` and `scaleY`) in sync, rather than requiring separate animator instances per property.

    ```kotlin
    val scaleX = PropertyValuesHolder.ofFloat("scaleX", 1f, 1.5f)
    val scaleY = PropertyValuesHolder.ofFloat("scaleY", 1f, 1.5f)
    ObjectAnimator.ofPropertyValuesHolder(view, scaleX, scaleY).start() // both in sync
    ```

??? question "What's the difference between View property animations (`ObjectAnimator` on `translationX`, etc.) and legacy `Animation`-based tweening?"
    Property animations actually change the View's real properties (affecting hit-testing/layout-relevant values), while legacy tweening (`TranslateAnimation`, etc.) only changes how the View is *drawn* without moving its actual layout bounds/hit area — a common source of "the view moved visually but clicks still register at the old position" bugs.

    ```kotlin
    ObjectAnimator.ofFloat(view, "translationX", 100f).start()
    // vs. TranslateAnimation — only draws elsewhere, clicks still register at the old spot
    ```

??? question "What's the difference between `AnimatorSet.playTogether()` and `.playSequentially()`?"
    `playTogether()` starts all provided animators simultaneously; `playSequentially()` chains them so each starts only after the previous one finishes.

    ```kotlin
    AnimatorSet().apply { playTogether(fadeIn, scaleUp) }.start()
    AnimatorSet().apply { playSequentially(fadeIn, scaleUp) }.start()
    ```

??? question "What is hardware layer / `View.setLayerType(LAYER_TYPE_HARDWARE)` used for, and what's the tradeoff?"
    It renders the View into an offscreen GPU texture/layer, making certain transformations (alpha, rotation) cheaper during animation since the layer's rasterized content is reused; the tradeoff is extra GPU memory usage for the cached layer, so it should be enabled only during the animation and cleared afterward.

    ```kotlin
    view.setLayerType(View.LAYER_TYPE_HARDWARE, null) // before animating
    // ... run the animation ...
    view.setLayerType(View.LAYER_TYPE_NONE, null)      // clear it afterward
    ```

??? question "What's the difference between clipping with `Canvas.clipPath()` and clipping via `ViewOutlineProvider`?"
    `Canvas.clipPath()` is imperative clipping within a custom `onDraw()`; `ViewOutlineProvider` declaratively defines a View's outline shape used both for clipping (`clipToOutline = true`) and for shadow casting, integrating with the system's elevation/shadow rendering.

    ```kotlin
    override fun onDraw(canvas: Canvas) { canvas.clipPath(path) } // imperative

    view.outlineProvider = object : ViewOutlineProvider() {
        override fun getOutline(v: View, outline: Outline) { outline.setOval(0, 0, v.width, v.height) }
    }
    view.clipToOutline = true // declarative, also drives the shadow
    ```

??? question "What is `ItemTouchHelper` used for in RecyclerView, and what does it abstract away?"
    It provides drag-and-drop reordering and swipe-to-dismiss gestures for RecyclerView items, abstracting the touch-event handling, item translation animation, and threshold detection that would otherwise need to be implemented manually.

    ```kotlin
    val callback = object : ItemTouchHelper.SimpleCallback(UP or DOWN, LEFT or RIGHT) { /* ... */ }
    ItemTouchHelper(callback).attachToRecyclerView(recyclerView)
    ```

??? question "What is a `SnapHelper` used for?"
    It makes a RecyclerView "snap" to align an item (e.g., centered or start-aligned) after a scroll/fling gesture ends, commonly used for carousel-style horizontal lists.

    ```kotlin
    LinearSnapHelper().attachToRecyclerView(recyclerView) // snaps to the nearest item after a fling
    ```

## RecyclerView/Compose Prefetching & Layered Architecture Patterns

??? question "What is `GapWorker` in RecyclerView, and what problem does it solve?"
    A background helper that pre-inflates/pre-binds upcoming off-screen ViewHolders during idle frame time (predicting scroll direction), so that when the user actually scrolls to reveal them, the work is already done, reducing jank from inflating/binding views synchronously during an active scroll gesture.

    ```kotlin
    // no API to call directly — GapWorker runs automatically during idle frame time,
    // pre-binding the next few off-screen ViewHolders based on scroll direction
    ```

??? question "How does `LazyColumn`/`LazyRow` prefetching in Compose achieve a similar goal to RecyclerView's GapWorker?"
    It composes and measures items just outside the visible viewport ahead of time during idle periods between frames, so scrolling into them doesn't require composing/measuring on the critical frame path, analogous in spirit though implemented natively within Compose's own scheduling.

    ```kotlin
    LazyColumn { items(list, key = { it.id }) { ItemRow(it) } } // Compose prefetches nearby items itself
    ```

??? question "What's the difference between naming a class 'Repository' versus 'DataSource' in a layered architecture, and why does the distinction matter for clarity?"
    A DataSource typically wraps a single specific origin (e.g., `RemoteUserDataSource`, `LocalUserDataSource`) with no cross-source logic; a Repository coordinates *between* multiple DataSources (deciding when to hit network vs cache, merging results) — conflating the two names can obscure whether a class is a simple wrapper or actually contains meaningful coordination logic.

    ```kotlin
    class RemoteUserDataSource(private val api: UserApi)  // wraps ONE source
    class UserRepository(
        private val remote: RemoteUserDataSource,
        private val local: UserDao,
    ) // coordinates BETWEEN sources
    ```

??? question "How would you design a layered cache (memory -> disk -> network) Repository, and in what order should each layer typically be checked on read?"
    Check the fastest layer first (in-memory cache) for an immediate hit, then disk/DB cache (which is a Room-backed observed Flow, itself already faster than network), and only hit the network if data is missing/stale, writing results back down through disk and memory caches as they're obtained so subsequent reads benefit from all layers.

    ```kotlin
    suspend fun getUser(id: String): User =
        memoryCache[id]
            ?: dao.getUser(id)
            ?: api.fetchUser(id).also { dao.insert(it); memoryCache[id] = it }
    ```

??? question "How would you design error handling to preserve a root cause across Repository -> UseCase -> ViewModel layers rather than losing context?"
    Wrap or chain the original exception (Kotlin's `cause` parameter, or a sealed error type carrying the original throwable) rather than catching-and-rethrowing a generic new exception, so the original failure detail is still available for logging/debugging at higher layers even after being translated into a domain-specific error type for UI handling.

    ```kotlin
    sealed class AppError(cause: Throwable? = null) : Exception(cause)
    class NetworkError(cause: Throwable) : AppError(cause) // original exception preserved
    ```

??? question "What's a practical use of Kotlin's reified generics beyond simple `T::class` access — e.g., replacing Gson's `TypeToken` pattern?"
    An inline reified function can capture and reconstruct full generic type information (including nested generics like `List<User>`) at each call site to pass to a JSON parser needing the complete type, avoiding the verbose anonymous `TypeToken<List<User>>(){}` boilerplate Java-based reflection APIs require.

    ```kotlin
    inline fun <reified T> Gson.fromJsonTyped(json: String): T =
        fromJson(json, object : TypeToken<T>() {}.type) // no manual TypeToken at each call site
    ```

??? question "What is `PropertyDelegateProvider` in Kotlin, and when would you need it instead of a plain delegated property?"
    It lets a delegate's creation logic access the property's own metadata (like its name) at the point of delegation, useful for building generic delegate factories (e.g., a preference-delegate library) that need to know which property they're backing without the caller manually passing the key/name.

    ```kotlin
    class PrefDelegateProvider<T>(val default: T) :
        PropertyDelegateProvider<Any?, ReadWriteProperty<Any?, T>> {
        override fun provideDelegate(thisRef: Any?, property: KProperty<*>) =
            PrefDelegate(property.name, default) // knows the property's name automatically
    }
    ```
