# Kotlin

Collapsed by default — try to answer before revealing.

## Kotlin Fundamentals

??? question "What is the difference between `val` and `const val`?"
    `val` is a read-only reference assigned once at runtime; the object it points to can still be mutable internally. `const val` is a compile-time constant restricted to primitives/String, must be top-level or in an `object`, and is inlined at every call site at compile time.

??? question "What is the difference between `==` and `===` in Kotlin?"
    `==` calls `equals()` (structural equality); `===` checks reference identity (same object in memory).

??? question "What does `lateinit` do and what are its restrictions?"
    It defers initialization of a `var` property, avoiding null checks; it can't be used on primitives, must be a `var`, and throws `UninitializedPropertyAccessException` if accessed before assignment.

??? question "How does `by lazy` differ from `lateinit`?"
    `lazy` works on `val`, computes the value on first access via a lambda, and by default is thread-safe (`LazyThreadSafetyMode.SYNCHRONIZED`); `lateinit` requires external assignment and offers no laziness.

??? question "What are the three `LazyThreadSafetyMode` options?"
    `SYNCHRONIZED` (default, thread-safe with locking), `PUBLICATION` (allows concurrent initialization but only one result is used), and `NONE` (no thread safety, fastest).

??? question "What is a sealed class and why use it over an enum?"
    A sealed class restricts subclassing to a known hierarchy known at compile time, allowing exhaustive `when` checks; unlike enums, subclasses can hold different data and multiple instances.

??? question "What is a sealed interface and when would you prefer it over a sealed class?"
    A sealed interface allows a class to implement it while also extending another class, giving more flexibility than sealed classes which use single inheritance.

??? question "What's the difference between `apply`, `also`, `let`, `run`, and `with`?"
    `apply`/`also` return the receiver (object configuration vs side effects); `let`/`run` return the lambda result (`let` uses `it`, `run` uses `this`); `with` is like `run` but takes the receiver as a parameter, not an extension.

??? question "What are inline functions and why do they exist?"
    `inline` copies the function body to the call site at compile time, avoiding lambda object allocation and enabling non-local returns; it's essential for performant higher-order functions like `forEach`.

??? question "What do `noinline` and `crossinline` do?"
    `noinline` marks a lambda parameter that should not be inlined (e.g., to store it or pass it elsewhere); `crossinline` forbids non-local returns from a lambda parameter, needed when the lambda is invoked from another execution context (like inside another lambda).

??? question "What are Kotlin's declaration-site variance modifiers `in` and `out`?"
    `out` makes a generic type covariant (producer-only, e.g. `List<out T>`); `in` makes it contravariant (consumer-only, e.g. `Comparator<in T>`), enabling safer generic APIs than Java's use-site wildcards.

??? question "What is an inline value class and what problem does it solve?"
    `value class` wraps a single value to add type safety (e.g., `UserId(val value: String)`) without runtime allocation overhead in most cases, since the compiler unwraps it at compile time.

??? question "What are Kotlin's standard delegated properties?"
    `lazy`, `observable`, `vetoable` from `Delegates`, and custom delegates implementing `getValue`/`setValue` operator functions.

??? question "How does Kotlin implement null safety at the bytecode/runtime level?"
    The compiler inserts null checks (`Intrinsics.checkNotNull`) at boundaries for platform types and public API parameters; there's no separate "non-null" bytecode type — it's enforced at compile time plus runtime assertions at API boundaries.

??? question "What is a 'platform type' in Kotlin?"
    A type coming from Java code with unknown nullability (denoted `String!`), where Kotlin can't enforce null safety and trusts the caller.

??? question "What's the difference between `Any`, `Any?`, `Unit`, and `Nothing`?"
    `Any` is the root non-null type; `Any?` allows null; `Unit` is like `void` but is an actual singleton object; `Nothing` represents a function that never returns (e.g., always throws), useful for type inference in `when` exhaustiveness.

??? question "What is smart casting, and when does it fail?"
    The compiler auto-casts a nullable/type-checked variable within a scope after an `is`/null check; it fails on `var` properties that could change between the check and use (e.g., mutable class properties, especially with custom getters).

??? question "What's the difference between `Array<Int>` and `IntArray`?"
    `Array<Int>` boxes each element as an `Integer` object; `IntArray` maps directly to Java's primitive `int[]`, avoiding boxing overhead.

??? question "How do data classes generate `equals`, `hashCode`, and `toString`?"
    The compiler auto-generates them based on properties declared in the primary constructor only; properties in the class body are excluded.

??? question "Why is inheritance discouraged/restricted for data classes?"
    Data classes can't be `open` for subclassing to inherit `equals`/`copy` semantics safely; auto-generated `equals` only checks primary-constructor properties, which breaks Liskov substitution if a subclass adds identity-relevant fields.

??? question "What does `copy()` do on a data class and what's a common bug with it?"
    It creates a shallow copy, using named args for overrides; a common bug is mutating a *referenced* mutable object shared between original and copy, since `copy()` doesn't deep-copy nested objects.

??? question "What are Kotlin destructuring declarations and how do they work under the hood?"
    `val (a, b) = pair` calls `component1()`, `component2()`, etc.; data classes auto-generate these; any class can support destructuring by defining `componentN()` operator functions.

??? question "What's the difference between `Sequence` and `List` operations like `map`/`filter`?"
    `List` operations are eager and create an intermediate list per operation; `Sequence` is lazy and processes elements one at a time through the whole chain, which is more efficient for large collections or early termination (e.g., `first()`).

??? question "What is an operator function, and give an example beyond arithmetic?"
    A function marked `operator` that overloads syntax like `+`, `[]`, `in`, or `invoke`; e.g., overloading `invoke()` lets an object be called like a function: `myObject()`.

??? question "What's the difference between an extension function and a member function when both exist with the same signature?"
    Member functions always win in resolution over extension functions; extension functions are resolved statically based on the declared type, not the runtime type (no dynamic dispatch).

??? question "What is a companion object, and how does it differ from Java statics?"
    A companion object is a real singleton instance tied to the class, can implement interfaces, and can be extended with extension functions; unlike Java statics, it supports polymorphism (e.g., `companion object : Factory`).

??? question "What's the difference between `open`, `final`, `abstract`, and `sealed` on a class?"
    `final` (default) disallows subclassing; `open` allows it; `abstract` requires subclassing and can't be instantiated; `sealed` restricts subclassing to types known within the same module/package at compile time.

??? question "What is reified type parameter and why is it only allowed on inline functions?"
    `inline fun <reified T> ...` lets you access the actual runtime type of `T` inside the function (e.g., `T::class`), which is normally erased by the JVM; it only works with inline functions because the compiler substitutes the real type at each call site.

??? question "What's the difference between `Elvis operator (?:)` and safe call (`?.`)?"
    `?.` short-circuits to null if the receiver is null; `?:` provides a fallback value when the left-hand expression is null.

??? question "What does the `!!` operator do and why is it risky?"
    It force-unwraps a nullable to non-null, throwing `NullPointerException` if the value is actually null; it defeats Kotlin's null-safety guarantees and is generally a code smell outside of tests/certain interop.

??? question "What is a higher-order function?"
    A function that takes another function as a parameter or returns one, e.g., `fun process(action: () -> Unit)`.

??? question "What's the difference between a lambda and an anonymous function in Kotlin?"
    Lambdas infer return type implicitly from the last expression and can't have explicit return types easily; anonymous functions (`fun(x: Int): Int {...}`) allow explicit return types and support local `return` without labels.

??? question "What is a labeled return and when do you need it?"
    `return@label` returns from a specific lambda rather than the enclosing function; needed inside inline lambdas like `forEach` where a plain `return` would try to return from the outer function (non-local return).

??? question "What is tail recursion in Kotlin and how do you mark it?"
    `tailrec` modifier tells the compiler to optimize a recursive function into a loop, avoiding stack overflow, but only if the recursive call is the last operation in every path.

??? question "What is the difference between `List` and `MutableList` in Kotlin, given both compile to `java.util.List`?"
    Kotlin's distinction is purely a compile-time API restriction (read-only interface vs mutable interface); at runtime, both are the same Java collection, so casting a `List` to `MutableList` and mutating it is possible but breaks the API contract.

??? question "What's the difference between `Unit` and `void` in interop?"
    Kotlin functions returning `Unit` compile to `void`-returning methods in bytecode when possible for interop simplicity, but `Unit` is a real, usable type in Kotlin (e.g., can be a generic type argument).

??? question "What is destructuring in a `when` combined with sealed class type-checking used for?"
    Combined with exhaustive `when` over a sealed hierarchy, it lets you pattern-match subclasses and extract their properties in one branch, common in reducer/state-machine code.

??? question "What's the difference between infix functions and regular functions?"
    `infix fun` allows calling without dot-and-parentheses syntax (e.g., `1 to 2` instead of `1.to(2)`), improving DSL readability; restricted to functions with exactly one parameter.

??? question "What is a typealias and when is it useful?"
    `typealias` gives an alternate name to an existing type, improving readability for complex generic types or function types (e.g., `typealias ClickListener = (View) -> Unit`); it has zero runtime cost since it's purely compile-time.

??? question "What's the difference between `Comparable` and `Comparator`?"
    `Comparable` defines a class's natural ordering via `compareTo` (implemented by the class itself); `Comparator` defines an external, often multiple, ordering strategy passed to sort functions.

## Kotlin Advanced & Language Internals

??? question "What's the difference between `Any?.toString()` behavior and calling `toString()` directly on a null reference?"
    `null.toString()` doesn't compile directly on a non-nullable-inferred null literal, but calling `toString()` via an extension on a nullable receiver (`Any?.toString()`) is safe and returns the string "null" for a null value, since Kotlin provides that specific extension.

??? question "What is the difference between `is` and `as` in Kotlin?"
    `is` checks type membership and returns a Boolean (enabling smart cast); `as` performs an unsafe cast throwing `ClassCastException` on failure, while `as?` performs a safe cast returning null on failure instead of throwing.

??? question "What's the difference between a top-level function and a function inside a companion object regarding discoverability and testing?"
    Top-level functions are package-level and can be imported/called directly, often easier to test in isolation and to make pure/stateless; companion object functions are namespaced under the class, which can be useful for factory-style construction tied conceptually to that class.

??? question "What is context receiver / multiple receivers (newer Kotlin feature) intended to solve?"
    It allows a function to require multiple implicit receivers/contexts simultaneously (beyond a single extension receiver), useful for DSLs or scoped capabilities without resorting to passing extra explicit parameters or nesting extension functions awkwardly.

??? question "What's the difference between `Iterable` and `Sequence` when using `takeWhile`?"
    On an eager `Iterable`, upstream transformations (`map`, `filter`) before `takeWhile` still fully process the whole collection first; on a lazy `Sequence`, `takeWhile` can short-circuit the entire chain per-element, avoiding wasted work on elements after the cutoff.

??? question "What's the difference between `runCatching` and a plain `try/catch`?"
    `runCatching` wraps the result in a `Result<T>` object (success or failure) that can be chained functionally (`.map`, `.onFailure`, `.getOrElse`), whereas `try/catch` handles control flow imperatively; `runCatching` can also inadvertently catch `CancellationException` if not careful, which is dangerous in coroutines.

??? question "Why is catching `CancellationException` inside `runCatching` inside a coroutine considered dangerous?"
    It suppresses the cancellation signal needed for structured concurrency to propagate correctly, potentially letting cancelled coroutines continue running unexpectedly; you should rethrow `CancellationException` explicitly when using `runCatching` in coroutine code.

??? question "What is the difference between `Nothing?` and `Unit?` as types?"
    `Nothing?` can only ever hold the value `null` (since `Nothing` itself has no instances); `Unit?` can hold either the single `Unit` instance or `null`.

??? question "What's the difference between an object declaration (`object Foo`) and a companion object?"
    An `object` declaration is a standalone singleton not tied to any other class; a companion object is specifically associated with an enclosing class and can access its private members, callable via the class name directly.

??? question "What is an anonymous object (object expression) used for in Kotlin, and how does it differ from a lambda?"
    `object : SomeInterface { ... }` creates a one-off instance implementing an interface/class with potentially multiple methods and internal state; a lambda is limited to implementing a single-method functional interface (SAM conversion) concisely.

??? question "What is SAM conversion, and does it apply to Kotlin functional interfaces the same way as Java ones?"
    SAM (Single Abstract Method) conversion lets a lambda be used where a functional interface is expected; Kotlin requires the interface be marked `fun interface` for this to apply to Kotlin-defined interfaces directly (Java functional interfaces get SAM conversion automatically due to how Kotlin interoperates with them).

??? question "What's the difference between `Array` covariance issues in Java vs Kotlin's generic collections?"
    Java arrays are covariant but unsafely so at runtime (`Object[] arr = new String[1]; arr[0] = 1;` compiles but throws `ArrayStoreException` at runtime); Kotlin's `List<out T>` achieves safe covariance at compile time via the type system without needing risky runtime checks, since read-only lists can't have elements inserted that would violate it.

??? question "What's the difference between `Sequence.constrainOnce()` and a regular `Sequence`?"
    `constrainOnce()` ensures the sequence can only be iterated a single time, throwing if iterated again — useful for wrapping a one-shot source (like reading a stream) where re-iteration would be a logic error, unlike a regular Sequence which can typically be re-iterated freely if the underlying source allows it.

??? question "What is the `by` keyword used for beyond delegated properties — i.e., class delegation?"
    `class Foo(base: Base) : Base by base` delegates interface implementation to a wrapped instance automatically, implementing the Decorator pattern with minimal boilerplate compared to manually forwarding every method.

??? question "What's the difference between `equals()` structural checks on a `List<Int>` versus a `Set<Int>` with the same elements?"
    `List` equality (`==`) considers order and duplicates (two lists are equal only if elements match in the same sequence); `Set` equality only considers membership regardless of order, so a `Set` and `List` with "the same elements" in different structures are never `==` equal to each other despite conceptually overlapping content.

## Kotlin Collections & Standard Library Deep Dive

??? question "What's the difference between `map` and `flatMap`?"
    `map` transforms each element into exactly one new element; `flatMap` transforms each element into a collection and then flattens all resulting collections into a single one.

??? question "What's the difference between `fold` and `reduce`?"
    `fold` takes an explicit initial value and can return a different type than the collection's elements; `reduce` uses the first element as the initial accumulator and thus requires the accumulator type to match the element type, and throws on an empty collection while `fold` does not.

??? question "What's the difference between `groupBy` and `partition`?"
    `groupBy` buckets elements into a `Map` keyed by an arbitrary selector function (any number of groups); `partition` splits elements into exactly two lists based on a Boolean predicate (matching and non-matching).

??? question "What's the difference between `associateBy` and `groupBy`?"
    `associateBy` produces a `Map` with one value per key (later duplicates overwrite earlier ones for the same key); `groupBy` produces a `Map` where each key maps to a `List` of all matching elements.

??? question "What's the difference between `sortedBy` and `sortedWith`?"
    `sortedBy` sorts using a selector function producing a `Comparable` key; `sortedWith` sorts using an explicit `Comparator`, useful for more complex or multi-field ordering logic.

??? question "What's the difference between `chunked` and `windowed`?"
    `chunked(n)` splits a collection into non-overlapping groups of size `n`; `windowed(n)` produces overlapping sliding windows of size `n`, advancing one element at a time by default (configurable step).

??? question "What does `zipWithNext()` do?"
    It pairs each element with the one immediately following it, useful for comparing consecutive elements (e.g., detecting increases in a sorted list) without manual indexing.

??? question "What's the difference between `first { }` and `firstOrNull { }`?"
    `first { }` throws `NoSuchElementException` if no element matches the predicate; `firstOrNull { }` returns `null` instead of throwing.

??? question "What's the difference between `all { }`, `any { }`, and `none { }`?"
    `all` returns true only if every element matches the predicate (vacuously true for an empty collection); `any` returns true if at least one matches; `none` returns true if zero elements match.

??? question "What's the difference between `Collection.toList()` on a `MutableList` and just assigning the reference?"
    `toList()` creates a new, independent read-only copy (snapshot at that point in time); assigning the reference directly still points to the same mutable underlying list, so later mutations through the original reference would be reflected even in the "old" variable.

??? question "What's the difference between `Map.getOrDefault()` and `Map.getOrElse()` in Kotlin?"
    `getOrDefault` (from Java interop) requires a fixed default value computed regardless of whether it's needed; `getOrElse` takes a lambda computing the default lazily only when the key is actually missing, avoiding unnecessary computation.

??? question "What's the difference between `Map.getValue()` and plain `Map.get()`/`[]` access?"
    `getValue()` throws `NoSuchElementException` immediately if the key is missing (useful with delegated map-backed properties); plain `get()`/`[]` returns `null` for a missing key, requiring separate null-handling.

??? question "What's the difference between `Iterable.sumOf { }` and manually looping with a mutable accumulator?"
    `sumOf { }` is a built-in, type-inferring, allocation-minimal reduction (returns Int/Long/Double/etc. matching the selector's return type); functionally equivalent to a manual loop but more concise and less error-prone (no risk of forgetting to initialize the accumulator correctly).

??? question "What's the difference between a `Sequence` built from `generateSequence {}` versus `sequenceOf()`?"
    `sequenceOf()` wraps a fixed, finite set of known elements; `generateSequence {}` lazily produces a potentially infinite sequence via a generator function, only computing as many elements as are actually consumed downstream (e.g., via `take(n)`).

## Generics, Annotations & Java Interop

??? question "What is a star projection (`List<*>`) in Kotlin generics, and when is it necessary?"
    It represents "a List of some unknown specific type," used when you don't know or care about the exact type parameter but still need type safety for read operations (you can read as `Any?` but can't safely write); necessary when working generically across different parameterized types without needing their specific type argument.

??? question "What's the difference between an upper-bounded generic constraint (`<T : Number>`) and no constraint at all?"
    An upper bound restricts `T` to that type or its subtypes, letting you call that bound's methods on values of type `T` inside the generic function/class; without a constraint, `T` is treated as `Any?` and only methods available on `Any` can be called.

??? question "What does `@JvmStatic` do, and why is it needed for companion object methods?"
    It makes a companion object method also accessible as a true static method from Java (without needing `Companion.method()`), since Kotlin companion objects are real singleton instances by default and Java sees their methods as instance methods on that singleton without this annotation.

??? question "What does `@JvmOverloads` do?"
    It generates overloaded Java-callable method signatures for a Kotlin function with default parameter values, since Java has no concept of default parameters and would otherwise require all arguments explicitly.

??? question "What does `@JvmName` solve?"
    It lets you specify a different method/class name as seen from Java bytecode, useful for resolving signature clashes (e.g., a property getter and an extension function that would otherwise generate colliding JVM signatures) or providing a more Java-idiomatic name.

??? question "What's the difference between a custom annotation with `@Retention(RUNTIME)` versus `@Retention(SOURCE)`?"
    `RUNTIME` retention keeps the annotation available via reflection at runtime (needed if code inspects it dynamically); `SOURCE` retention discards it after compilation entirely (useful for annotations only meant to guide the compiler/tooling, like lint checks, with zero runtime footprint).

??? question "What's the difference between annotation processing (kapt/KSP) and runtime reflection-based annotation usage?"
    Annotation processing inspects annotations at compile time to generate additional code (zero runtime cost after generation); runtime reflection reads annotations dynamically while the app is running, which is slower and can be a target for R8/ProGuard-related stripping issues if not configured with proper keep rules.

??? question "Why does mixing Kotlin's null safety with Java code require careful attention to platform types?"
    Java has no compile-time null safety, so a Kotlin function receiving a Java-returned reference sees it as a "platform type" with unknown nullability, meaning null-safety guarantees can silently be violated at the Java boundary unless explicitly checked.

??? question "What's the difference between `@Nullable`/`@NonNull` Java annotations and Kotlin's native null types when calling Java code from Kotlin?"
    If the Java code is properly annotated with `@Nullable`/`@NonNull` (JSR-305 or similar), Kotlin respects those annotations and treats the type as genuinely nullable or non-null rather than an ambiguous platform type, improving interop safety.

??? question "What's a common Kotlin-Java interop gotcha with Kotlin's `Unit` return type in a Java-called API design?"
    A Kotlin function returning `Unit` compiles to `void` for simple cases, but if used generically (e.g., a lambda parameter type `() -> Unit`), Java sees it as returning the actual `Unit` singleton object rather than `void`, requiring an explicit `return Unit.INSTANCE;` when implementing such a functional interface from Java.
