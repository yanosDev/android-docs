# Dispatchers

Decides which thread (or thread pool) a coroutine runs and resumes on.
Coroutines themselves are thread-agnostic — a `Dispatcher` is what
actually assigns the work to a thread.

## Example

```kotlin
suspend fun loadUser(id: String): User = withContext(Dispatchers.IO) {  // (1)!
    userDao.findById(id)                                                 // (2)!
}

suspend fun updateUi(user: User) = withContext(Dispatchers.Main) {       // (3)!
    nameLabel.text = user.name
}
```

1. `withContext` suspends the current coroutine and resumes its body on
   the given dispatcher's threads — here, a pool meant for blocking I/O.
2. Runs off the main thread, so a blocking database call doesn't freeze
   the UI.
3. `Dispatchers.Main` confines this block to the main/UI thread —
   touching UI elements off that thread crashes on Android.

## Comparison

| | Manual `Thread`/`Handler` | Java `ExecutorService` | Kotlin `Dispatchers` |
|---|---|---|---|
| Switching threads | Manual `Handler.post` / thread creation | Submit a `Runnable`/`Callable` to a pool | `withContext(Dispatcher)` — one line, suspends until done |
| Returning a result | Callback or shared mutable state | `Future.get()` (blocks) or a callback | Direct return value — reads like a normal function call |
| Built-in pools | None — manage your own | You configure the pool | `Default` (CPU), `IO` (blocking calls), `Main` (UI) ship out of the box |

## Explanation

`Dispatchers.Default` is sized for CPU-bound work (roughly one thread per
core); `Dispatchers.IO` is a much larger pool meant for blocking calls
(network, disk, database) so they don't starve CPU work. `withContext`
switches dispatcher for just its block and switches back automatically —
no manual hand-off back to the original thread.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| One-line thread switching (`withContext`), no manual thread/handler bookkeeping | Picking the wrong dispatcher (e.g. blocking I/O on `Default`) starves other coroutines sharing that pool |
| Sensible built-in pools for the common cases | Testing requires substituting a `TestDispatcher` — another concept to learn |

## When to use it

Any time a suspend function needs to run its body on a specific kind of
thread — blocking I/O (`IO`), CPU-heavy work (`Default`), or touching UI
(`Main`).

## See also

- [Coroutines](coroutines.md)
- [Structured Concurrency](structured-concurrency.md)

## Further reading

- [Kotlin docs: Coroutine context and dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
