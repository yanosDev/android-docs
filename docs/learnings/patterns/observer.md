# Observer Pattern

One object (the subject) notifies a list of listeners whenever its state
changes, without knowing anything about them beyond the observer
contract.

## Example

```kotlin
fun interface Listener {                        // (1)!
    fun onChange(value: Int)
}

class Counter {
    private val listeners = mutableListOf<Listener>()
    var value = 0
        set(v) {
            field = v
            listeners.forEach { it.onChange(v) }   // (2)!
        }

    fun addListener(listener: Listener) {
        listeners += listener
    }
}

counter.addListener { println("Now: $it") }     // (3)!
```

1. `fun interface` — a **functional interface** (SAM): one abstract
   method, so a lambda can implement it directly.
2. Every registered listener gets called on every change — the subject
   doesn't know or care what they do with it.
3. Because `Listener` has one abstract method, a lambda stands in for a
   whole implementation.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Subject and observers stay decoupled | Hard to trace — "who's listening to this, and in what order?" |
| Any number of observers can attach/detach at runtime | Easy to leak listeners that never get removed (a classic Android leak: one holding a reference to a destroyed Activity) |

## When to use it

Broadcasting a state change to multiple, unrelated interested parties. In
modern Kotlin/Android, [`Flow`](../kotlin/flow.md) (and `StateFlow`)
usually replace hand-rolled listener lists — they add cancellation,
backpressure, and lifecycle awareness for free.

## See also

- [Flow](../kotlin/flow.md)
- [Higher-Order Functions](../general/higher-order-functions.md)
- [Interfaces](../kotlin/interfaces.md)

## Further reading

- [Wikipedia: Observer pattern](https://en.wikipedia.org/wiki/Observer_pattern)
