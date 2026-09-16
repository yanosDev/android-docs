# Kotlin

Language fundamentals and idioms — not tutorials, but reference pages for
things I already know how to *use* and keep forgetting how to *name*.
Grouped by level; see [Learnings](../index.md#levels) for what each tier
means.

## Page format

Every page in this section follows the same shape:

1. **Name** — the term(s) as they show up in docs/talks, so search actually
   finds it.
2. **Short example with markings** — a minimal snippet with numbered
   annotations pointing at the exact thing being named.
3. **Comparison** — a compact table contrasting this against other
   languages/libraries/manual approaches, when there's a real alternative
   worth contrasting (e.g. coroutines vs. threads/callbacks).
4. **Explanation** — what's actually going on underneath, briefly.
5. **Advantages / Disadvantages** — a compact pros/cons table, for pages
   about a design choice with real alternatives (a class modifier, a
   declaration style) — skip it for pages about pure mechanics with no
   alternative (e.g. what a compiler is).
6. **When to use it** — a couple of concrete scenarios, same condition as
   above.
7. **See also** — links to related pages in this section.
8. **Further reading** — the official doc/KEEP/source for going deeper.

## Beginner

| Topic | What it covers |
|---|---|
| [Scope Functions](scope-functions.md) | `let`, `run`, `with`, `apply`, `also` — how to pick one |
| [Inheritance](inheritance.md) | `open`, `:` — Kotlin's `extends`, and why classes are final by default |
| [Interfaces](interfaces.md) | `interface`, default methods, multiple inheritance of behavior |
| [Data Classes](data-classes.md) | `data class` — generated `equals`/`copy`/destructuring |
| [Object Declarations](object-declarations.md) | `object` — singletons and anonymous objects |
| [Companion Objects](companion-objects.md) | `companion object` — Kotlin's `static` |

## Intermediate

| Topic | What it covers |
|---|---|
| [Sealed Classes & Interfaces](sealed.md) | `sealed` — closed hierarchies, exhaustive `when` |
| [Annotations](annotations.md) | `@Annotation`, `annotation class`, `@Target`/`@Retention` |
| [Coroutines](coroutines.md) | `suspend`, lightweight vs. threads/callbacks |
| [Dispatchers](dispatchers.md) | `Dispatchers.Main`/`IO`/`Default`, `withContext` |

## Expert

| Topic | What it covers |
|---|---|
| [Structured Concurrency](structured-concurrency.md) | `coroutineScope`/`supervisorScope`, automatic cancellation |
| [Flow](flow.md) | Cold async streams vs. RxJava/`Sequence` |

## Pro

| Topic | What it covers |
|---|---|
| [Inline Functions & Reified Type Parameters](inline-reified.md) | `inline`, `reified`, why `T::class`/`is T` need it |
| [Value Classes](value-classes.md) | `value class` — type safety without wrapper overhead |

## Still to write

- Receivers & lambdas with receiver (`T.() -> R`, DSL builders)
- Null safety (`?`, `?:`, `!!`, safe/platform types)
- Extension functions & properties
- Delegation (`by lazy`, `by Delegates`, custom delegates)
- Collections API (`map`, `filter`, `fold`, sequences vs. eager collections)
- Generics & variance (`in`/`out`, declaration-site vs. use-site)
- Coroutine exception handling (`CoroutineExceptionHandler`, `try`/`catch` boundaries)
- `StateFlow` / `SharedFlow` (hot vs. `Flow`'s cold)
- `viewModelScope` / `lifecycleScope`
- Testing coroutines (`runTest`, `TestDispatcher`)
