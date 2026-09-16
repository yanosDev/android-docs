# Annotations

Attaches metadata to code — a class, function, property, etc. — without
changing what it does by itself. Something else (a compiler plugin,
reflection, an annotation processor) has to go looking for the annotation
and act on it.

## Example

```kotlin
@Target(AnnotationTarget.FUNCTION)        // (1)!
@Retention(AnnotationRetention.RUNTIME)   // (2)!
annotation class Loggable                  // (3)!

@Loggable                                  // (4)!
fun processOrder() { /* ... */ }
```

1. `@Target` restricts where the annotation can be applied — functions
   only, here.
2. `@Retention` controls whether it survives to runtime (needed for
   reflection to see it) or is compile/source-only.
3. `annotation class` declares a new annotation type — metadata with no
   behavior of its own.
4. Attaching `@Loggable` runs no code — a separate reader (reflection,
   a processor) has to notice it and react.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Decouples metadata from logic (Retrofit's `@GET`, Room's `@Entity`) | Does nothing by itself — real behavior needs a processor/reflection elsewhere, adding indirection |
| Zero cost until something actually reads it | Runtime-retained annotations read via reflection carry their own (usually small) runtime cost |

## When to use it

Framework integration (`@GET`, `@Entity`) or lightweight, machine-readable
metadata (`@Deprecated`, `@JvmStatic`) — not as a substitute for an actual
function call or behavior.

## See also

- [Compiler](../general/compiler.md)
- [Value Classes](value-classes.md)

## Further reading

- [Kotlin docs: Annotations](https://kotlinlang.org/docs/annotations.html)
