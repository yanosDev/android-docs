# Singleton Pattern

Ensures a type has exactly one instance, globally accessible. In Kotlin
this is a built-in language feature, not something you need to hand-roll.

## Example

```kotlin
class LegacyLogger private constructor() {                    // (1)!
    companion object {
        @Volatile private var instance: LegacyLogger? = null
        fun getInstance() =                                    // (2)!
            instance ?: synchronized(this) {
                instance ?: LegacyLogger().also { instance = it }
            }
    }
}

object Logger                                                  // (3)!
```

1. The classic (Java-style) singleton: a private constructor blocks direct
   instantiation.
2. Double-checked locking manually ensures only one instance is ever
   created, even under concurrent first access.
3. Kotlin's `object` does all of the above — lazy, thread-safe, single
   instance — in one line. See
   [Object Declarations](../kotlin/object-declarations.md) for the
   mechanics.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Guaranteed single, globally accessible instance | Global state — hidden coupling, hard to substitute in tests |
| Kotlin's `object` gives this for free: thread-safe, zero boilerplate | If it holds mutable state, that state is shared everywhere, always |

## When to use it

Stateless utilities, app-wide config or registries. Prefer dependency
injection over a singleton once you need to substitute a fake for
testing, or support more than one configuration at a time.

## See also

- [Object Declarations](../kotlin/object-declarations.md)
- [Companion Objects](../kotlin/companion-objects.md)

## Further reading

- [Wikipedia: Singleton pattern](https://en.wikipedia.org/wiki/Singleton_pattern)
