# Jetpack Compose

Declarative UI toolkit for Android.

## Topics to fill in

- Composable functions, recomposition rules
- State: `remember`, `mutableStateOf`, `rememberSaveable`, state hoisting
- Side effects: `LaunchedEffect`, `DisposableEffect`, `derivedStateOf`
- Layouts: `Row`/`Column`/`Box`, `ConstraintLayout`, custom layouts
- Navigation (Compose Navigation)
- Theming with Material 3
- Previews & testing (`@Preview`, `ComposeTestRule`)
- Performance (stability, `@Stable`/`@Immutable`)

## Example

```kotlin
@Composable
fun Counter(modifier: Modifier = Modifier) {
    var count by rememberSaveable { mutableStateOf(0) }
    Button(onClick = { count++ }, modifier = modifier) {
        Text("Clicked $count times")
    }
}
```
