# Data Classes

A class whose only job is to hold data. Marking it `data` makes the
compiler generate `equals()`/`hashCode()`/`toString()`/`copy()`/`componentN()`
from the primary constructor's properties.

## Example

```kotlin
data class User(val name: String, val age: Int)  // (1)!

val a = User("Ada", 30)
val b = a.copy(age = 31)                          // (2)!
val (name, age) = a                               // (3)!
println(a == User("Ada", 30))                     // (4)!
```

1. `data` generates the boilerplate from `name`/`age` — nothing to write
   by hand.
2. `copy` makes a shallow copy with just the listed properties changed —
   the rest stay the same.
3. The generated `componentN()` functions enable destructuring, in
   constructor-parameter order.
4. Structural equality — compares property values, not reference identity
   (`===`).

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| No `equals`/`hashCode`/`toString` boilerplate | Generated `equals`/`hashCode` only see primary-constructor properties — a `var` added in the body is silently excluded |
| `copy()` fits immutable "change one field" updates well | Inheritance between data classes is restricted and its `equals` semantics get murky fast |

## When to use it

A plain, mostly-immutable value holder — a DTO, an API model, a piece of
UI state. Not for an entity with identity or mutable internal invariants,
where `copy()`'s shallow equality can hide bugs.

## See also

- [Sealed Classes & Interfaces](sealed.md)
- [Value Classes](value-classes.md)

## Further reading

- [Kotlin docs: Data classes](https://kotlinlang.org/docs/data-classes.html)
