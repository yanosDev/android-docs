# Glossary

Terms worth a precise name, one line each, for scanning rather than
reading. Grouped foundations-first: general concepts, then Kotlin's
specific keywords that build on them. Looking for a verb instead of a
noun — the right word for what code is *doing*? See the
[Phrasebook](phrasebook.md).

If a term below gets a full write-up in [Documentation](../documentation/index.md),
link it from that row's Meaning cell — a term with no page yet is still
worth listing here.

## General concepts

| Term | Meaning |
|---|---|
| Compiler | Translates source code before the program runs; the compile-time/runtime split |
| Generics | Parameterizing a function/type over a placeholder type `T` instead of one copy per type |
| Type erasure | Generic type info is discarded at runtime — a JVM `List<String>` is just a `List` |
| Inline / inlining | Splicing a function's body into its call site at compile time, instead of a separate call |
| Higher-order function | A function that takes and/or returns another function |
| Statement vs. expression | Whether a construct produces a usable value |

## Design patterns

| Term | Meaning |
|---|---|
| Builder pattern | Step-by-step object construction via chained calls |
| Singleton pattern | One globally accessible instance — Kotlin's `object` does this natively |
| Factory pattern | Creating objects without exposing which concrete type gets built |
| Observer pattern | Notifying listeners whenever a subject's state changes |
| Strategy pattern | Swappable algorithm/behavior via an interface |
| Decorator pattern | Wrapping an object to add behavior, same interface |
| Adapter pattern | Making one interface look like another |
| Repository pattern | Hiding where data comes from behind one interface |

## Kotlin — scope functions

| Term | Meaning |
|---|---|
| `let` | Object as `it`, returns the lambda result — null-checks (`?.let`), transforms |
| `run` | Object as `this`, returns the lambda result |
| `with` | Object as `this`, returns the lambda result — not an extension function |
| `apply` | Object as `this`, returns the object — builder-style configuration |
| `also` | Object as `it`, returns the object — side effects mid-chain |

## Kotlin — inline & reified

| Term | Meaning |
|---|---|
| `inline` (keyword) | Forces the compiler to splice this function's body into every call site |
| `reified` | Type parameter usable at runtime (`T::class`, `is T`) — only legal on an `inline` function |

## Kotlin — classes & interfaces

| Term | Meaning |
|---|---|
| Inheritance (`extend`) | `open` + `:` — Kotlin's `extends`; classes/members are final by default |
| `interface` | A contract; abstract or default-body members, multiple per class |
| `data class` | Generates `equals`/`hashCode`/`toString`/`copy`/`componentN` |
| `sealed` class/interface | Closed hierarchy, known at compile time — exhaustive `when` |
| `object` | Declares a class and its one (lazy, thread-safe) instance together |
| `companion object` | One shared object per class, accessed via the class name — Kotlin's `static` |
| `value class` | Wraps one property; inlined at compile time, usually no allocation |

## Kotlin — annotations

| Term | Meaning |
|---|---|
| `@Annotation` / `annotation class` | Attaches metadata to code; does nothing until something reads it |

## Kotlin — coroutines

| Term | Meaning |
|---|---|
| Coroutine / `suspend` | Suspendable computation — pauses without blocking its thread |
| Structured concurrency | A coroutine can't outlive the scope (`coroutineScope`/`supervisorScope`) that started it |
| `Flow` | Cold asynchronous stream of values, built on `suspend` |
| `Dispatchers` | Assigns which thread(s) a coroutine runs and resumes on |

## Android — components & lifecycle

| Term | Meaning |
|---|---|
| Activity lifecycle | `onCreate` → `onStart` → `onResume` → `onPause` → `onStop` → `onDestroy` |
| Fragment vs. view lifecycle | The Fragment object can outlive its view |
| `Service` | Background operation with no UI — started or bound |
| `WorkManager` | Deferrable, guaranteed background work with constraints |
| `BroadcastReceiver` | Listens for system-wide or app broadcasts |
| `ContentProvider` | Structured, permission-controlled cross-app data access |

## Android — app & task navigation

| Term | Meaning |
|---|---|
| `Intent` / `IntentFilter` | The message vs. what a component declares it can handle |
| Task / back stack | The stack of Activities the user navigates with back |
| `launchMode` | `standard`/`singleTop`/`singleTask`/`singleInstance` |
| Intent flags | `FLAG_ACTIVITY_NEW_TASK`, `CLEAR_TOP` + `SINGLE_TOP` |
| `taskAffinity` | Which task an Activity prefers to belong to |

## Android — state & process lifecycle

| Term | Meaning |
|---|---|
| `ViewModel` | Survives configuration changes, cleared on process death |
| `onSaveInstanceState` / `SavedStateHandle` | Bundle-backed state that survives process death |
| Application context vs. Activity context | Process-lifetime vs. Activity-lifetime context |
| Process death | What's lost, and how to recover state |
| `oom_adj` | How Android scores process importance for killing |

## Android — runtime & app startup

| Term | Meaning |
|---|---|
| Cold / warm / hot start | How much work an app launch actually does |
| `androidx.startup` | One ordered init pass instead of many ContentProviders |
| `Looper` / `Handler` | The message-queue mechanism behind the main thread |
| `Window` / `WindowManager` | An Activity's UI container vs. adding views without one |
| App startup sequence | What runs before your first `onCreate()` |
| `Zygote` | Why a new app process isn't booted from scratch |
| ART vs. Dalvik | JIT vs. AOT, and why install time changed |
| AOT (ahead-of-time) compilation | Compiling to native code before the code runs — at install, or from a profile |
| JIT (just-in-time) compilation | Compiling hot bytecode paths to native code while the app is already running |
| Binder | How processes actually talk to each other |
| UI thread vs. RenderThread | Why some animations survive a UI-thread stall |
