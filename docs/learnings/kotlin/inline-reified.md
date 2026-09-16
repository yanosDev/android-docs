# Inline Functions & Reified Type Parameters

Kotlin generics are erased at runtime ([JVM type erasure](../general/type-erasure.md)) —
`List<String>` and `List<Int>` are both just `List` once compiled, so a
generic function normally can't write `T::class`, `is T`, or `T()`.
Marking a type parameter `reified` lifts that restriction — but only on an
[`inline`](../general/inline.md) function, because the compiler pastes the
function's body into each call site, where the real type is known.

## Example

```kotlin
inline fun <reified T> Gson.fromJson(json: String): T =           // (1)!
    fromJson(json, T::class.java)                                  // (2)!

inline fun <reified T> Iterable<*>.filterIsInstance(): List<T> =  // (3)!
    filter { it is T }.map { it as T }                              // (4)!

val users: List<User> = gson.fromJson(json)                        // (5)!
```

1. `reified` is only legal on a type parameter of an `inline` function —
   the compiler needs to splice this body into every call site to know
   what `T` actually is there.
2. `T::class` doesn't compile on a regular (non-inline) generic function —
   there's no `T` left at runtime to ask about. Here it's replaced with the
   real class before the code runs.
3. Same requirement applies to `filterIsInstance` — `is T` is illegal for
   an erased type parameter.
4. `it is T` and `it as T` are safe here because the compiler replaces `T`
   with the concrete type (e.g. `User`) before this ever becomes bytecode.
5. The caller never passes `User::class.java` — the compiler infers
   `T = User` from the expected return type and reifies it in.

## Cheat sheet

| | `fun <T>` | `inline fun <reified T>` |
|---|---|---|
| `T::class` / `is T` / `T()` | compile error (erased) | works |
| Compiles to | one shared method | copied into every call site |
| Typical use | general algorithms | `fromJson<T>()`, `filterIsInstance<T>()` |

## Explanation

Reification isn't a runtime trick — the compiler pastes the inline
function's body into each call site with `T` already substituted for the
concrete type, so the JVM never sees a generic `T` to erase. That's also
why it only works on `inline` functions: a normal function is compiled once
and has no way to know what type each future caller will use.

## See also

- [Scope Functions](scope-functions.md) — `inline`, no call overhead
- [Generics & Variance](generics-variance.md)
- [Type Erasure](../general/type-erasure.md)
- [Inline (Inlining)](../general/inline.md)

## Further reading

- [Kotlin docs: Inline functions — reified type parameters](https://kotlinlang.org/docs/inline-functions.html#reified-type-parameters)
