# Glossary

Every term covered in [Learnings](index.md), one line each, for scanning
rather than reading. Grouped foundations-first: general concepts, then
Kotlin's specific keywords that build on them. Looking for a verb instead
of a noun — the right word for what code is *doing*? See the
[Phrasebook](phrasebook.md).

## General concepts

| Term | Meaning | Page |
|---|---|---|
| Compiler | Translates source code before the program runs; the compile-time/runtime split | [Compiler](general/compiler.md) |
| Generics | Parameterizing a function/type over a placeholder type `T` instead of one copy per type | [Generics](general/generics.md) |
| Type erasure | Generic type info is discarded at runtime — a JVM `List<String>` is just a `List` | [Type Erasure](general/type-erasure.md) |
| Inline / inlining | Splicing a function's body into its call site at compile time, instead of a separate call | [Inline (Inlining)](general/inline.md) |
| Higher-order function | A function that takes and/or returns another function | [Higher-Order Functions](general/higher-order-functions.md) |
| Statement vs. expression | Whether a construct produces a usable value | [Statement vs. Expression](general/statement-vs-expression.md) |

## Design patterns

| Term | Meaning | Page |
|---|---|---|
| Builder pattern | Step-by-step object construction via chained calls | [Builder](patterns/builder.md) |
| Singleton pattern | One globally accessible instance — Kotlin's `object` does this natively | [Singleton](patterns/singleton.md) |
| Factory pattern | Creating objects without exposing which concrete type gets built | [Factory](patterns/factory.md) |
| Observer pattern | Notifying listeners whenever a subject's state changes | [Observer](patterns/observer.md) |
| Strategy pattern | Swappable algorithm/behavior via an interface | [Strategy](patterns/strategy.md) |
| Decorator pattern | Wrapping an object to add behavior, same interface | [Decorator](patterns/decorator.md) |
| Adapter pattern | Making one interface look like another | [Adapter](patterns/adapter.md) |
| Repository pattern | Hiding where data comes from behind one interface | [Repository](patterns/repository.md) |

## Kotlin — scope functions

| Term | Meaning | Page |
|---|---|---|
| `let` | Object as `it`, returns the lambda result — null-checks (`?.let`), transforms | [Scope Functions](kotlin/scope-functions.md) |
| `run` | Object as `this`, returns the lambda result | [Scope Functions](kotlin/scope-functions.md) |
| `with` | Object as `this`, returns the lambda result — not an extension function | [Scope Functions](kotlin/scope-functions.md) |
| `apply` | Object as `this`, returns the object — builder-style configuration | [Scope Functions](kotlin/scope-functions.md) |
| `also` | Object as `it`, returns the object — side effects mid-chain | [Scope Functions](kotlin/scope-functions.md) |

## Kotlin — inline & reified

| Term | Meaning | Page |
|---|---|---|
| `inline` (keyword) | Forces the compiler to splice this function's body into every call site | [Inline Functions & Reified Type Parameters](kotlin/inline-reified.md) |
| `reified` | Type parameter usable at runtime (`T::class`, `is T`) — only legal on an `inline` function | [Inline Functions & Reified Type Parameters](kotlin/inline-reified.md) |

## Kotlin — classes & interfaces

| Term | Meaning | Page |
|---|---|---|
| Inheritance (`extend`) | `open` + `:` — Kotlin's `extends`; classes/members are final by default | [Inheritance](kotlin/inheritance.md) |
| `interface` | A contract; abstract or default-body members, multiple per class | [Interfaces](kotlin/interfaces.md) |
| `data class` | Generates `equals`/`hashCode`/`toString`/`copy`/`componentN` | [Data Classes](kotlin/data-classes.md) |
| `sealed` class/interface | Closed hierarchy, known at compile time — exhaustive `when` | [Sealed Classes & Interfaces](kotlin/sealed.md) |
| `object` | Declares a class and its one (lazy, thread-safe) instance together | [Object Declarations](kotlin/object-declarations.md) |
| `companion object` | One shared object per class, accessed via the class name — Kotlin's `static` | [Companion Objects](kotlin/companion-objects.md) |
| `value class` | Wraps one property; inlined at compile time, usually no allocation | [Value Classes](kotlin/value-classes.md) |

## Kotlin — annotations

| Term | Meaning | Page |
|---|---|---|
| `@Annotation` / `annotation class` | Attaches metadata to code; does nothing until something reads it | [Annotations](kotlin/annotations.md) |

## Kotlin — coroutines

| Term | Meaning | Page |
|---|---|---|
| Coroutine / `suspend` | Suspendable computation — pauses without blocking its thread | [Coroutines](kotlin/coroutines.md) |
| Structured concurrency | A coroutine can't outlive the scope (`coroutineScope`/`supervisorScope`) that started it | [Structured Concurrency](kotlin/structured-concurrency.md) |
| `Flow` | Cold asynchronous stream of values, built on `suspend` | [Flow](kotlin/flow.md) |
| `Dispatchers` | Assigns which thread(s) a coroutine runs and resumes on | [Dispatchers](kotlin/dispatchers.md) |
