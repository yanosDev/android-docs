# Companion Objects

An [object](object-declarations.md) declared inside a class — at most one
per class, shared across all instances, accessed through the class name.
Kotlin's closest equivalent to Java's `static`, except it's a real object.

## Example

```kotlin
class User private constructor(val name: String) {
    companion object {                     // (1)!
        fun create(name: String): User {    // (2)!
            require(name.isNotBlank())
            return User(name)
        }
    }
}

val user = User.create("Ada")              // (3)!
```

1. At most one `companion object` per class — shared across all
   instances, not per-instance.
2. A common use: a factory function that validates/normalizes before
   constructing, paired with a `private constructor` so `create` is the
   only way in.
3. Called through the class name, reading like Java's `static` — but it's
   a real object, so it can implement interfaces and be passed around as
   a value.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Reads like `static`, but can implement interfaces (a real `static` can't) | Still global mutable state if it holds `var`s |
| Can access the class's `private` members | Only one per class; slightly slower than a real JVM `static` unless annotated `@JvmStatic` |

## When to use it

Factory functions, constants tied to a class, or anything reaching for
Java's `static`. Prefer a top-level function or `val` if it isn't really
tied to instances of the class.

## See also

- [Object Declarations](object-declarations.md)
- [Value Classes](value-classes.md)

## Further reading

- [Kotlin docs: Companion objects](https://kotlinlang.org/docs/object-declarations.html#companion-objects)
