# Kotlin

Language fundamentals and idioms.

## Topics to fill in

- Null safety (`?`, `?:`, `!!`, `let`/`run`/`apply`/`also`/`with`)
- Data classes, sealed classes, sealed interfaces
- Extension functions & properties
- Scope functions
- Delegation (`by lazy`, `by Delegates`, custom delegates)
- Collections API (`map`, `filter`, `fold`, sequences)
- Generics & variance (`in`/`out`)
- Inline functions & reified type parameters

## Example

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Content(val items: List<String>) : UiState
    data class Error(val message: String) : UiState
}
```
