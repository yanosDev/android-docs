# Object Declarations

`object` declares a class and its single instance at the same time — no
constructor, created lazily and thread-safely on first access. The same
keyword also makes a one-off, unnamed implementation of a type: an
**anonymous object**.

## Example

```kotlin
object AppConfig {                        // (1)!
    var debug: Boolean = false
}

AppConfig.debug = true                    // (2)!

val listener = object : ClickListener {   // (3)!
    override fun onClick() = println("clicked")
}
```

1. Declares the class **and** its one instance together — nothing to
   instantiate.
2. Reads like a static member, but it's a real singleton object under the
   hood.
3. `object : Type { }` with no name is an **anonymous object** — a
   one-off implementation, similar to Java's anonymous inner classes.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Guaranteed single instance, thread-safe by construction | Global mutable state if it holds `var`s — the usual singleton risks (hidden coupling, hard to reset in tests) |
| No manual singleton boilerplate | Can't take constructor parameters — one instance only, ever |

## When to use it

A true app-wide singleton (config, a registry) or a quick one-off
interface implementation. Prefer a regular class plus DI when you need
more than one instance, or testability via fakes.

## See also

- [Companion Objects](companion-objects.md)
- [Sealed Classes & Interfaces](sealed.md) — `data object`

## Further reading

- [Kotlin docs: Object declarations and expressions](https://kotlinlang.org/docs/object-declarations.html)
