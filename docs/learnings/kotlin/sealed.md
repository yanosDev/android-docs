# Sealed Classes & Interfaces

Restricts a type hierarchy to a fixed, closed set of subtypes, all known
to the compiler at compile time. The payoff: a `when` over a sealed type
can be exhaustive with no `else` branch.

## Example

```kotlin
sealed interface UiState {                        // (1)!
    data object Loading : UiState                  // (2)!
    data class Content(val items: List<String>) : UiState
    data class Error(val message: String) : UiState
}

fun render(state: UiState) = when (state) {        // (3)!
    UiState.Loading -> showSpinner()
    is UiState.Content -> showList(state.items)
    is UiState.Error -> showError(state.message)
    // no `else` needed                             // (4)!
}
```

1. `sealed` restricts subtypes to those declared in the same compilation
   unit — the compiler has a closed, complete list.
2. `data object` — a singleton [object](object-declarations.md) that also
   gets [data-class](data-classes.md)-style `toString`.
3. Because the hierarchy is closed, the compiler can verify every branch
   is covered.
4. Add a new subtype later and every `when` over `UiState` becomes a
   compile error until updated — that's the whole point of `sealed`.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Exhaustive `when` — the compiler catches a missed case | Adding a subtype is a breaking change everywhere it's matched |
| Models "one of a fixed set of things" precisely, payload and all | All subclasses must live in the same module/package — no external extension |

## When to use it

A fixed, known set of variants where forgetting one should be a compile
error (UI state, parse results, navigation events). Reach for
`enum class` instead when the variants don't carry different data.

## See also

- [Data Classes](data-classes.md)
- [Object Declarations](object-declarations.md)

## Further reading

- [Kotlin docs: Sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html)
