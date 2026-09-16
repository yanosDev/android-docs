# Structured Concurrency

Every coroutine launches inside a scope, and a scope can't complete until
all coroutines launched inside it do — cancel or fail the scope, and
every child is cancelled with it. No coroutine outlives the scope that
started it.

## Example

```kotlin
suspend fun loadDashboard() = coroutineScope {  // (1)!
    val user = async { fetchUser() }             // (2)!
    val posts = async { fetchPosts() }
    Dashboard(user.await(), posts.await())        // (3)!
}
```

1. `coroutineScope` doesn't return until every coroutine launched inside
   it completes — including `user` and `posts` below.
2. `async` starts a child coroutine concurrently; if either `fetchUser`
   or `fetchPosts` throws, the other is cancelled automatically.
3. `await()` suspends until that specific child's result is ready — both
   run concurrently, not one after the other.

## Comparison

| | Unstructured / fire-and-forget | Java `ExecutorService` | Structured concurrency |
|---|---|---|---|
| Lifetime | Detached — nothing tracks when it finishes | Tracked via `Future`, but cancellation is manual and easy to skip | Tied to the enclosing scope automatically |
| A child throws | Silently lost unless explicitly checked | Wrapped in the `Future`; easy to never unwrap it | Propagates up and cancels siblings by default |
| Leak risk | High — a launched coroutine/thread can outlive its caller | Medium — forgetting `shutdown()` leaks the pool | Low — the scope enforces cleanup |

## Explanation

`coroutineScope` propagates a child's failure to cancel its siblings and
itself; `supervisorScope` is the opt-out — a failed child doesn't cancel
its siblings, useful when the children are genuinely independent (a list
of unrelated background tasks).

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| No orphaned coroutines — cancellation and completion are automatic | One misbehaving child can cancel unrelated siblings unless you deliberately use `supervisorScope` |
| Errors surface instead of vanishing silently | Requires understanding parent/child cancellation rules to avoid surprises |

## When to use it

Launching more than one coroutine to do related work, where you want
"all finish, or all get cancelled together" — the default in Kotlin,
rather than something you opt into.

## See also

- [Coroutines](coroutines.md)
- [Dispatchers](dispatchers.md)

## Further reading

- [Kotlin docs: Structured concurrency](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)
