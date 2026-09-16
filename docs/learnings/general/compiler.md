# Compiler

A program that translates source code into another form — usually
something closer to what a machine (or a virtual machine) can run —
*before* the program executes. The distinction that matters for reading
any language's docs: **compile time** (the compiler translating/checking
your code) vs. **runtime** (the translated program actually executing).

## Example

```kotlin
fun <T> identity(value: T): T = value   // (1)!

val x = identity(42)                    // (2)!
```

1. The compiler checks that `T` is used consistently, then discards it —
   see [Type Erasure](type-erasure.md).
2. At compile time, the compiler infers `T = Int` from the argument. At
   runtime, there's no `T` — the JVM just sees a call returning an `Int`.

## Explanation

"Compile time" vs. "runtime" is the split almost every language feature
falls into: type-checking, generics resolution, and `inline` splicing all
happen at compile time; reflection and anything erased only exist at
runtime. Kotlin compiles to JVM bytecode by default (also Native/JS,
depending on target) — "the compiler" means `kotlinc`, "runtime" means the
JVM (or the equivalent for the other targets).

## See also

- [Generics](generics.md)
- [Type Erasure](type-erasure.md)
- [Inline (Inlining)](inline.md)

## Further reading

- [Wikipedia: Compiler](https://en.wikipedia.org/wiki/Compiler)
