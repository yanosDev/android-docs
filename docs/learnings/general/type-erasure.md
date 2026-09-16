# Type Erasure

The compiler checks generic types at compile time, then discards
("erases") that type information before producing the runtime
representation — so at runtime, a `List<String>` and a `List<Int>` are
both just `List`. This is how the JVM implements generics, which is why it
applies equally to Java and Kotlin.

## Example

```kotlin
fun <T> printRuntimeType(list: List<T>) {
    println(list.javaClass)           // (1)!
    // println(list is List<String>)  // (2)!
}
```

1. Prints `class java.util.ArrayList` — no trace of `T` survives to
   runtime.
2. Doesn't compile: there's no `T` left at runtime to check against. This
   is exactly the restriction Kotlin's `reified` type parameters exist to
   lift — see [Inline Functions & Reified Type Parameters](../kotlin/inline-reified.md).

## Explanation

Erasure is a deliberate trade-off, not a bug: it's how Java added generics
without changing the bytecode format, and Kotlin inherited it by
targeting the same JVM. The cost is that generic type information simply
isn't there at runtime unless a language gives you a specific way around
it — Kotlin's `inline fun <reified T>` is exactly that: the compiler
substitutes the real type at each call site instead of compiling one
shared, erased method.

## See also

- [Generics](generics.md)
- [Compiler](compiler.md)
- Kotlin's workaround: [Inline Functions & Reified Type Parameters](../kotlin/inline-reified.md)

## Further reading

- [Wikipedia: Type erasure](https://en.wikipedia.org/wiki/Type_erasure)
