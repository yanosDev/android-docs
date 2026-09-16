# Value Classes

Wraps exactly one property, and — tagged `@JvmInline` — the compiler
represents it as just that property at runtime, with no wrapper object
allocated in most cases. Type safety without a real wrapper's cost.

## Example

```kotlin
@JvmInline
value class UserId(val value: String)   // (1)!

fun findUser(id: UserId) { /* ... */ }  // (2)!

findUser(UserId("abc-123"))             // (3)!
// findUser("abc-123")                  // (4)!
```

1. Wraps exactly one property (`value`) — `@JvmInline` tells the compiler
   to inline it at compile time instead of allocating a wrapper.
2. The parameter type is `UserId`, not `String` — a raw `String` can't be
   passed by accident.
3. Compiles down to (roughly) passing a plain `String` — `UserId` mostly
   doesn't exist at runtime.
4. Doesn't compile: `UserId` and `String` aren't interchangeable, even
   though `UserId` is "just a `String`" underneath.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Type safety (can't mix up a `UserId` and an `OrderId`, both really `String`) with usually zero allocation cost | Boxed anyway in some contexts — generics, nullable types, collections — so "zero-cost" has real exceptions |
| | Can wrap exactly one property; can't be extended by other classes |

## When to use it

Primitive-obsession-prone values that shouldn't be interchangeable (IDs,
currency amounts, validated strings) where type safety matters but a real
wrapper class's overhead doesn't feel worth it.

## See also

- [Inline (Inlining)](../general/inline.md)
- [Data Classes](data-classes.md)

## Further reading

- [Kotlin docs: Inline value classes](https://kotlinlang.org/docs/inline-classes.html)
