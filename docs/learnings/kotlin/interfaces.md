# Interfaces

A contract of members a class must provide — can include abstract members
(no body) and members with a default body. A class can implement any
number of interfaces, unlike single class [inheritance](inheritance.md).

## Example

```kotlin
interface Clickable {
    fun click()                                   // (1)!
    fun showOff() = println("I'm clickable!")     // (2)!
}

interface Focusable {
    fun showOff() = println("I'm focusable!")     // (3)!
}

class Button : Clickable, Focusable {             // (4)!
    override fun click() = println("Clicked")
    override fun showOff() = super<Clickable>.showOff()  // (5)!
}
```

1. Abstract member — no body, every implementer must provide one.
2. Default implementation — implementers can use it as-is or override it.
3. Same method name, different interface, both with default bodies — sets
   up an ambiguity.
4. A class implements as many interfaces as it needs — no single-parent
   restriction like class inheritance.
5. Kotlin won't guess between the two `showOff()`s — it forces an explicit
   `super<Type>.method()` to disambiguate.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Multiple inheritance of behavior (unlike classes) | Default methods from two interfaces can collide — must be resolved explicitly |
| Decouples "what" from "how" — easy to fake/mock in tests | No constructor and no backing state — shared state still needs another mechanism |

## When to use it

A contract implemented by otherwise-unrelated types (`Comparable`,
`Clickable`). Prefer an [abstract class](inheritance.md) when
implementers genuinely share constructor logic or state, not just
behavior.

## See also

- [Inheritance](inheritance.md)
- [Sealed Classes & Interfaces](sealed.md)

## Further reading

- [Kotlin docs: Interfaces](https://kotlinlang.org/docs/interfaces.html)
