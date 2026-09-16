# Design Patterns

Recurring solutions to common design problems — not Kotlin-specific, but
written here with idiomatic Kotlin examples, including where Kotlin's own
language features already solve the problem better than the classic
pattern does. Grouped by level; see [Learnings](../index.md#levels) for
what each tier means.

## Beginner

| Pattern | What it covers |
|---|---|
| [Singleton](singleton.md) | One globally accessible instance — Kotlin's `object` does this natively |

## Intermediate

| Pattern | What it covers |
|---|---|
| [Builder](builder.md) | Step-by-step object construction via chained calls |
| [Factory](factory.md) | Creating objects without exposing which concrete type gets built |
| [Observer](observer.md) | Notifying listeners on state change |
| [Strategy](strategy.md) | Swappable algorithm/behavior via an interface |
| [Adapter](adapter.md) | Making one interface look like another |
| [Repository](repository.md) | Hiding where data comes from behind one interface |

## Expert

| Pattern | What it covers |
|---|---|
| [Decorator](decorator.md) | Wrapping an object to add behavior, same interface |
