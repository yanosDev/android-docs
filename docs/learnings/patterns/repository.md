# Repository Pattern

Not classic GoF — the standard Android/backend data-layer pattern: hides
where data actually comes from (network, database, cache) behind one
interface, so the rest of the app only ever talks to "the repository."

## Example

```kotlin
interface UserRepository {                                // (1)!
    suspend fun getUser(id: String): User
}

class DefaultUserRepository(                               // (2)!
    private val api: UserApi,
    private val dao: UserDao,
) : UserRepository {
    override suspend fun getUser(id: String): User =
        dao.getUser(id) ?: api.fetchUser(id).also { dao.insert(it) }  // (3)!
}
```

1. Callers (ViewModels, use cases) depend on this interface, never on
   `UserApi`/`UserDao` directly.
2. The implementation is where the actual data-source juggling lives.
3. Cache-first: read the local DB, fall back to the network, then cache
   the result — callers don't need to know any of this happens.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Swappable/fakeable data source behind one seam — easy to test with a fake `UserRepository` | For a trivial app, an extra interface + class for little benefit |
| Centralizes caching/offline logic in one place | Can turn into a dumping ground (network + cache + mapping + business logic) if not kept disciplined |

## When to use it

More than one data source (network + local cache/DB) needs to look like
one thing to the rest of the app, or you want to substitute a fake in
tests. For a single, simple network call with no caching, calling the API
client directly is often enough.

## See also

- [Interfaces](../kotlin/interfaces.md)
- [Companion Objects](../kotlin/companion-objects.md) — a factory for the `Default*` implementation

## Further reading

- [Android docs: Data layer](https://developer.android.com/topic/architecture/data-layer)
