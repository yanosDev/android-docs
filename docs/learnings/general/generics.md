# Generics

Writing a function or type once, parameterized over a placeholder type
(conventionally `T`), instead of once per concrete type. The placeholder
gets filled in per use — `List<String>` and `List<Int>` share one `List`
definition.

## Example

```kotlin
class Box<T>(val value: T)          // (1)!

val boxOfInt = Box(42)              // (2)!
val boxOfString = Box("hi")         // (3)!
```

1. `T` is a **type parameter** — a placeholder, not a real type, filled in
   per instance.
2. `T` is inferred as `Int` here.
3. Same class, different `T` — no duplicate `Box` definition needed.

## Explanation

Generics let the compiler catch type mismatches at compile time without
writing the same code once per type: it substitutes the concrete type at
each call site and checks it's used consistently. What happens to `T`
*after* compilation — whether any trace of it survives to runtime —
differs by language and platform; see [Type Erasure](type-erasure.md) for
how the JVM (and so Kotlin) handles it.

## See also

- [Type Erasure](type-erasure.md)
- [Compiler](compiler.md)
- Kotlin-specific variance (`in`/`out`): [Generics & Variance](../kotlin/generics-variance.md)

## Further reading

- [Wikipedia: Generic programming](https://en.wikipedia.org/wiki/Generic_programming)
- [Kotlin docs: Generics](https://kotlinlang.org/docs/generics.html)
