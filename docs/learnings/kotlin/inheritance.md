# Inheritance

Kotlin classes and members are **final by default** — extending a class or
overriding a member both require an explicit `open`. There's no `extends`
keyword: `:` both extends a class and calls its constructor.

## Example

```kotlin
open class Animal(val name: String) {      // (1)!
    open fun sound(): String = "..."        // (2)!
}

class Dog(name: String) : Animal(name) {    // (3)!
    override fun sound(): String = "Woof"   // (4)!
}
```

1. Classes are `final` by default — `open` is required before anything can
   subclass this one.
2. Members are also final by default; `open` lets a subclass override this
   specific one.
3. `:` extends `Animal` **and** calls its constructor in one place — no
   separate `super(name)` call.
4. `override` is mandatory, not optional like Java's `@Override` — the
   compiler enforces that you're actually overriding something `open`.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Reuses shared state and behavior in one place | Tight coupling — the subclass depends on superclass internals |
| Natural fit for a true "is-a" relationship | Deep hierarchies get fragile ("fragile base class" problem) |
| | `final`-by-default means an easy-to-forget `open` ("class is not open for extension") |

## When to use it

A genuine is-a relationship with shared implementation to reuse (`Dog` is
an `Animal`). Prefer an [interface](interfaces.md) — or composition —
when you only need shared behavior, not shared state.

## See also

- [Interfaces](interfaces.md)
- [Sealed Classes & Interfaces](sealed.md)

## Further reading

- [Kotlin docs: Inheritance](https://kotlinlang.org/docs/inheritance.html)
