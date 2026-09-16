# Flow

An asynchronous stream of values, produced one at a time over time,
built on `suspend` — Kotlin's answer to "a `Sequence` that can suspend."

## Example

```kotlin
fun prices(): Flow<Int> = flow {   // (1)!
    repeat(3) {
        delay(100)                  // (2)!
        emit((it + 1) * 10)          // (3)!
    }
}

suspend fun main() {
    prices()
        .map { it * 2 }              // (4)!
        .collect { println(it) }    // (5)!
}
```

1. `flow { }` builds a **cold** stream — nothing runs until it's
   collected.
2. Suspending inside the builder is fine — that's the whole point over a
   plain `Sequence`.
3. `emit` sends one value downstream and suspends until the collector is
   ready for it — backpressure, built in.
4. Operators like `map` build a new `Flow` — nothing executes yet.
5. `collect` is what actually starts the flow running, value by value.

## Comparison

| | RxJava (`Observable`) | Kotlin `Sequence` | Kotlin `Flow` |
|---|---|---|---|
| Async? | Yes | No — synchronous only | Yes, via `suspend` |
| Cold by default? | Depends on type | Cold | Cold |
| Cancellation | Manual `Disposable` | N/A | Structured — tied to the collecting coroutine |
| Learning curve | Large operator surface, its own mental model | Familiar (like `Iterable`) | Familiar operators + coroutines you already know |

## Explanation

Because `Flow` is cold, `prices()` above does nothing on its own —
calling `collect` is what starts producing values, and each collector
gets its own independent run. `StateFlow`/`SharedFlow` are the *hot*
counterparts (state/events shared across multiple collectors at once) —
not covered on this page yet.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Built on coroutines you already know — no separate reactive mental model | Still a real learning curve: cold vs. hot, operators, dispatcher interaction |
| Structured cancellation, like any coroutine | The wrong operator (`map` vs. `flatMapLatest`) can silently change concurrency behavior |

## When to use it

A sequence of values arriving over time (sensor readings, repeated
network polling, database change notifications) — where a single
`suspend fun` returning one value isn't enough.

## See also

- [Coroutines](coroutines.md)
- [Structured Concurrency](structured-concurrency.md)

## Further reading

- [Kotlin docs: Asynchronous Flow](https://kotlinlang.org/docs/flow.html)
