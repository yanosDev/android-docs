# Higher-Order Functions

A function that takes another function as a parameter, returns one, or
both. Functions become values you can store, pass around, and compose —
not just things you call.

## Example

```kotlin
fun applyTwice(x: Int, f: (Int) -> Int): Int = f(f(x))  // (1)!

val double: (Int) -> Int = { it * 2 }                    // (2)!

applyTwice(3, double)                                    // (3)!
applyTwice(3) { it + 1 }                                 // (4)!
```

1. `f: (Int) -> Int` is a parameter whose type is itself a function —
   that's what makes `applyTwice` higher-order.
2. A function can be stored in a `val`, just like any other value.
3. Passing a named function value directly.
4. Kotlin's trailing-lambda syntax: the last argument, if it's a function,
   can be written outside the parentheses — this is how `map`, `filter`,
   and `let` all read as if the language had built-in syntax for them.

## Explanation

Not a Kotlin-only idea — it's the core of functional programming, present
in JavaScript, Python, Scala, and most modern languages. In Kotlin it's
built on function types (`(A) -> B`) and lambdas as literal values; the
standard library's `map`, `filter`, `fold`, and the
[scope functions](../kotlin/scope-functions.md) are all higher-order
functions themselves.

## See also

- [Scope Functions](../kotlin/scope-functions.md)
- [Inline (Inlining)](inline.md)

## Further reading

- [Wikipedia: Higher-order function](https://en.wikipedia.org/wiki/Higher-order_function)
- [Kotlin docs: Higher-order functions and lambdas](https://kotlinlang.org/docs/lambdas.html)
