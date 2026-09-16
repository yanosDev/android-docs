# Factory Pattern

Creates objects without the caller using their constructor directly — the
caller asks for "a `Shape`" and a factory decides which concrete
implementation to hand back.

## Example

```kotlin
sealed interface Shape {                                            // (1)!
    data class Circle(val radius: Double) : Shape
    data class Square(val side: Double) : Shape
}

fun createShape(kind: String, size: Double): Shape = when (kind) {   // (2)!
    "circle" -> Shape.Circle(size)
    "square" -> Shape.Square(size)
    else -> error("Unknown shape: $kind")
}

class ShapeRepository private constructor() {                        // (3)!
    companion object {
        fun create(): ShapeRepository = ShapeRepository()
    }
}
```

1. The factory hides which concrete `Shape` gets built.
2. `createShape` is a **factory function** — callers depend on `Shape`,
   never on `Circle`/`Square` directly.
3. A `companion object` factory function (`create()`) is Kotlin's usual
   spot for this — see [Companion Objects](../kotlin/companion-objects.md).

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Decouples callers from concrete types | Another layer of indirection to trace |
| Centralizes creation logic and validation | Can grow into a large `when`/`if` chain needing an update per new type |

## When to use it

The concrete type to construct depends on runtime input, or construction
needs validation/setup beyond a plain constructor. For a single, fixed
type, a [companion object](../kotlin/companion-objects.md) factory
function is usually enough — you don't need the full ceremony.

## See also

- [Companion Objects](../kotlin/companion-objects.md)
- [Sealed Classes & Interfaces](../kotlin/sealed.md)

## Further reading

- [Wikipedia: Factory method pattern](https://en.wikipedia.org/wiki/Factory_method_pattern)
