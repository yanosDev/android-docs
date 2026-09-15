# Coroutines & Flow

Structured concurrency on Kotlin/Android.

## Topics to fill in

- `suspend` functions, `CoroutineScope`, `Job`, `Dispatchers`
- Structured concurrency, `coroutineScope` vs `supervisorScope`
- Exception handling (`CoroutineExceptionHandler`, `try/catch` boundaries)
- `Flow`, `StateFlow`, `SharedFlow`
- `viewModelScope`, `lifecycleScope`
- Testing coroutines (`runTest`, `TestDispatcher`)

## Example

```kotlin
class MyViewModel(private val repo: Repository) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            _state.value = runCatching { repo.load() }
                .fold(UiState::Content, UiState::Error)
        }
    }
}
```
