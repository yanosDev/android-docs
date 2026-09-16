# Coroutines

A suspendable computation — it can pause at a `suspend` call and resume
later without blocking the thread it's running on. Kotlin's coroutines
are lightweight (thousands can run on a handful of threads) and let
asynchronous code read top-to-bottom instead of nested in callbacks.

## Example

```kotlin
suspend fun fetchUser(id: String): User {   // (1)!
    delay(100)                               // (2)!
    return User(id)
}

fun main() = runBlocking {                   // (3)!
    val user = fetchUser("42")                // (4)!
    println(user)
}
```

1. `suspend` marks a function that can pause and resume — callable only
   from another `suspend` function or a coroutine builder.
2. `delay` suspends this coroutine without blocking the underlying
   thread — a `Thread.sleep` here would block it entirely.
3. `runBlocking` is a coroutine builder that starts a coroutine and
   blocks the current thread until it finishes — normally only used at a
   program's entry point or in tests.
4. Reads like ordinary sequential code, even though `fetchUser` genuinely
   suspends and resumes — no callback, no explicit thread hand-off.

## Comparison

| | OS threads | Callbacks | Kotlin coroutines |
|---|---|---|---|
| Cost | Heavy (~MBs of stack each, OS-scheduled) | Cheap, but nested ("pyramid of doom") | Lightweight — many per thread, cooperatively scheduled |
| Reads as | Sequential | Inverted control flow | Sequential |
| Cancellation | Manual, error-prone (`Thread.interrupt`) | Manual bookkeeping per callback | Built-in, propagates automatically — see [Structured Concurrency](structured-concurrency.md) |

## Explanation

A coroutine isn't a thread — the Kotlin compiler rewrites a `suspend`
function into a state machine it can pause and resume. Whether that
resumption happens on the same or a different thread is a separate
decision, made by a [Dispatcher](dispatchers.md).

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Sequential-looking code for async work; cheap enough to launch thousands | `suspend` is viral — one suspending call forces every caller up the chain to be `suspend` too, or launch a new coroutine |
| Structured cancellation and error propagation by default | A new concurrency model to learn on top of "just threads" |

## When to use it

Any I/O-bound or long-running work you'd otherwise block a thread for
(network calls, disk access) — especially on Android, where blocking the
main thread freezes the UI.

## See also

- [Structured Concurrency](structured-concurrency.md)
- [Dispatchers](dispatchers.md)
- [Flow](flow.md)

## Further reading

- [Kotlin docs: Coroutines overview](https://kotlinlang.org/docs/coroutines-overview.html)
