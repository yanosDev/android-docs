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

Rule of thumb: **returns the object → `apply`/`also`; returns a result →
`let`/`run`/`with`**.

## Explanation

All five are [`inline`](../general/inline.md) stdlib functions — no extra
allocation, no stack frame. The `this`-based ones (`run`, `with`, `apply`) work because their
lambda type is `T.() -> R`, a [function type with receiver](receivers.md) —
the same mechanism behind DSL builders.

## See also

- [Receivers & lambdas with receiver](receivers.md) — `T.() -> R`
- [Null safety](null-safety.md) — `?.let { }`
- [Inline functions & reified type parameters](inline-reified.md)

## Further reading

- [Kotlin docs: Scope functions](https://kotlinlang.org/docs/scope-functions.html)
