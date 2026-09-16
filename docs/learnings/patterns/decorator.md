# Decorator Pattern

Wraps an object to add behavior around it, while exposing the same
interface — instead of changing the class or subclassing per
combination.

## Example

```kotlin
interface Coffee {
    fun cost(): Double
}

class SimpleCoffee : Coffee {
    override fun cost() = 2.0
}

class WithMilk(private val base: Coffee) : Coffee {   // (1)!
    override fun cost() = base.cost() + 0.5             // (2)!
}

val order = WithMilk(SimpleCoffee())                    // (3)!
```

1. `WithMilk` wraps a `Coffee` and implements `Coffee` itself — same
   interface, extra behavior.
2. Delegates to the wrapped object first, then adds its own bit —
   decorators typically chain (`WithMilk(WithSugar(SimpleCoffee()))`).
3. The caller only ever sees a `Coffee` — it doesn't know, or care, how
   many layers deep the wrapping goes.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Adds behavior without a subclass per combination | A deep decorator stack is hard to read and debug |
| Each decorator stays small and focused | Kotlin's `by` (class delegation) already generates most of this boilerplate — hand-writing it, as above, is rarely necessary |

## When to use it

Adding optional, stackable behavior around an existing interface
(logging, caching, formatting) without a subclass explosion. In Kotlin,
prefer [`by` interface delegation](../kotlin/delegation.md) over
hand-writing the wrapper — it does this pattern's job with far less code.

## See also

- [Interfaces](../kotlin/interfaces.md)
- [Delegation](../kotlin/delegation.md) — `by`, Kotlin's built-in answer

## Further reading

- [Wikipedia: Decorator pattern](https://en.wikipedia.org/wiki/Decorator_pattern)
