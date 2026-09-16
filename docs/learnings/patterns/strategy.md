# Strategy Pattern

Extracts an algorithm behind an interface so it can be swapped at
runtime, instead of branching on type inside one class.

## Example

```kotlin
fun interface SortStrategy {                        // (1)!
    fun sort(items: List<Int>): List<Int>
}

class Sorter(private val strategy: SortStrategy) {  // (2)!
    fun sort(items: List<Int>) = strategy.sort(items)
}

val ascending = Sorter { it.sorted() }               // (3)!
val descending = Sorter { it.sortedDescending() }
```

1. The algorithm sits behind an interface — any implementation is
   interchangeable.
2. `Sorter` depends on the *contract*, not a specific algorithm — a new
   strategy plugs in without changing `Sorter`.
3. Because `SortStrategy` is a `fun interface`, a lambda supplies the
   strategy directly — no separate class needed per strategy.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Swaps behavior without touching the class that uses it | An extra type/lambda for what might be a single `if` |
| Replaces a growing `when`/`if` chain with one contract | Overkill when there are only ever two fixed options |

## When to use it

The same operation needs several interchangeable implementations chosen
at runtime (sorting, validation, pricing rules). For one or two fixed
variants, a plain `if`/`when` is simpler and clearer.

## See also

- [Higher-Order Functions](../general/higher-order-functions.md)
- [Interfaces](../kotlin/interfaces.md)

## Further reading

- [Wikipedia: Strategy pattern](https://en.wikipedia.org/wiki/Strategy_pattern)
