# Builder Pattern

Constructs a complex object step by step through chained calls that each
set one part, ending in a final call that produces the built object.
Solves constructors with too many optional parameters.

## Example

```kotlin
class Pizza private constructor(                // (1)!
    val size: String,
    val toppings: List<String>,
) {
    class Builder {
        private var size: String = "medium"
        private val toppings = mutableListOf<String>()

        fun size(size: String) = apply { this.size = size }      // (2)!
        fun topping(name: String) = apply { toppings.add(name) } // (3)!
        fun build() = Pizza(size, toppings.toList())              // (4)!
    }
}

val pizza = Pizza.Builder()             // (5)!
    .size("large")
    .topping("cheese")
    .topping("mushroom")
    .build()
```

1. `private constructor` — the only way to create a `Pizza` is through its
   `Builder`.
2. Each setter returns `this` ([`apply`](../kotlin/scope-functions.md)) so
   the calls can chain.
3. Optional parts (`toppings`) get added incrementally instead of through
   one huge constructor call.
4. `build()` is the one place the real object gets constructed, once all
   parts are set.
5. Reads close to named-parameter construction, but works even in
   languages with no named/default arguments — which is also why this
   pattern is far more common in Java than in idiomatic Kotlin.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Readable step-by-step construction of a complex object; avoids constructors with many optional parameters | More boilerplate than the problem it solves in Kotlin, which already has named and default arguments |
| Can validate or compute derived state once, in `build()` | Two classes to maintain (the object and its builder) instead of one |

## When to use it

A Java-interop surface, or a genuinely complex, incrementally-assembled
object (an HTTP request builder). In idiomatic Kotlin, reach for named
arguments with default values first — a builder earns its keep once that
stops being enough (e.g. OkHttp's `Request.Builder`, which this pattern
mirrors).

## See also

- [Scope Functions](../kotlin/scope-functions.md) — `apply` powers the chain
- [Companion Objects](../kotlin/companion-objects.md) — an alternative for simpler cases

## Further reading

- [Wikipedia: Builder pattern](https://en.wikipedia.org/wiki/Builder_pattern)
