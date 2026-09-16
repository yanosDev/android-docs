# Inline (Inlining)

Replacing a function call with a copy of the function's own body, at
compile time, instead of leaving it as a separate call at runtime. It
trades a larger compiled output for removing call overhead.

## Example

```kotlin
inline fun square(x: Int) = x * x    // (1)!

val result = square(5)               // (2)!
```

1. `inline` tells the Kotlin compiler to splice this function's body into
   every call site rather than compiling it once and calling it.
2. Compiles roughly to `val result = 5 * 5` — no `square` call exists in
   the output at all.

## Explanation

Inlining is a general compiler technique, not unique to Kotlin — C/C++
compilers and JIT compilers do it automatically as an optimization.
Kotlin exposes it as an explicit keyword because inlining a *lambda*
parameter also removes the `Function` object it would otherwise allocate
— and, as a side effect of the body landing at a call site where the real
type is known, makes
[reified type parameters](../kotlin/inline-reified.md) possible, which
don't compile on a normal function.

## See also

- [Compiler](compiler.md)
- Kotlin's keyword: [Inline Functions & Reified Type Parameters](../kotlin/inline-reified.md)

## Further reading

- [Wikipedia: Inline expansion](https://en.wikipedia.org/wiki/Inline_expansion)
- [Kotlin docs: Inline functions](https://kotlinlang.org/docs/inline-functions.html)
