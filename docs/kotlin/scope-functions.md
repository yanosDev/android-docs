# Scope Functions

`let`, `run`, `with`, `apply`, `also` — five stdlib functions that run a
lambda "in the context of" an object. They don't do anything you couldn't
write by hand; they just exist so you can name a temporary scope instead of
declaring a throwaway variable. They differ on exactly two axes:

- **How you refer to the object inside the lambda** — as `it` (a regular
  lambda argument) or as `this` (the lambda has the object as its
  [receiver](receivers.md)).
- **What the expression returns** — the lambda's result, or the object
  itself.

## Example

```kotlin
data class User(var name: String, var age: Int)

val user = User("Ada", 30).apply {      // (1)!
    age += 1
}

val greeting = user.let { u ->          // (2)!
    "Hello, ${u.name}"
}

val isAdult = with(user) {              // (3)!
    age >= 18                           // (4)!
}

user.also { println("saving $it") }     // (5)!
    .let(::persist)
```

1. `apply` returns the **receiver** (`User`), so the whole expression's type
   is `User`. Reads as "configure this object, then hand it back" — the
   classic use is builder-style setup.
2. `let` returns the **lambda result** (`String` here), and the object
   arrives as an explicit lambda parameter (`u`) instead of an implicit
   receiver. Because it takes the object as an argument, it's the one you
   reach for on a nullable value: `user?.let { ... }` only runs if `user`
   isn't null.
3. `with` is the odd one out: it's **not an extension function**, it's a
   top-level function that takes the object as a parameter — `with(user) { }`
   rather than `user.with { }`. You can't chain it off a nullable receiver.
4. Inside `with`/`apply`/`run`, the object is the implicit receiver, so
   `age` resolves to `user.age` without needing `this.` in front of it.
5. `also` returns the **receiver**, like `apply`, but exposes it as `it`
   like `let`. That combination — object back out, no implicit `this` — is
   exactly what you want for a side effect (logging, asserting) dropped into
   the middle of a chain without disturbing it.

## Cheat sheet

| Function | Object as | Returns | Reach for it when |
|---|---|---|---|
| `let` | `it` | lambda result | null-checking (`?.let`) or transforming a value into something else |
| `run` | `this` | lambda result | `apply` + you want a computed result back instead of the object |
| `with` | `this` (not an extension) | lambda result | you already have a non-null object and want to group several calls on it |
| `apply` | `this` | the object | configuring/building an object, then keeping it |
| `also` | `it` | the object | a side effect (logging, validation) that shouldn't interrupt a chain |

A rule of thumb that covers most cases: **returns the object → `apply`/`also`
(builders, side effects); returns a result → `let`/`run`/`with`
(transformations, computations)**. Then pick `it` vs `this` based on whether
naming the value (`it`) or writing tersely (`this`) reads better at the call
site.

## Explanation

Each of these is a small inline/extension function in the standard library —
`apply` and `also` just call the lambda and return `this`; `let` and `run`
call the lambda and return whatever it produces. There's no runtime magic:
they're plain higher-order functions marked `inline`, so using one doesn't
allocate a `Function` object or add a stack frame — the lambda body is
spliced into the call site at compile time (see
[Inline functions & reified type parameters](inline-reified.md)).

The `this`-based ones (`run`, `with`, `apply`) work because their lambda
parameter type is a **function type with receiver**
(`T.() -> R` rather than `(T) -> R`) — the same mechanism that powers
[receivers and DSL builders](receivers.md). That's also why you can nest
them and each `this` unambiguously refers to the nearest scope.

Overusing scope functions to chain unrelated operations makes stack traces
and debugging harder (you lose a named local variable to step through) — a
good sign you've gone too far is a scope function whose lambda no longer
fits on a screen.

## See also

- [Receivers & lambdas with receiver](receivers.md) — the `T.() -> R`
  mechanism behind `run`/`with`/`apply`
- [Null safety](null-safety.md) — the `?.let { }` idiom
- [Inline functions & reified type parameters](inline-reified.md) — why
  these have no call overhead

## Further reading

- [Kotlin docs: Scope functions](https://kotlinlang.org/docs/scope-functions.html)
- [Kotlin docs: `let`](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/let.html) · [`run`](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/run.html) · [`with`](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/with.html) · [`apply`](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/apply.html) · [`also`](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/also.html)
