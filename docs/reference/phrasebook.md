# Phrasebook

Not terms — see the [Glossary](glossary.md) for those. This is the verbs
and phrases for *describing what code is doing*, for when explaining
something out loud or in a review and reaching for "...you know, when it,
uh, does the thing" instead of the precise word for it.

## Execution & control flow

| Word | Meaning | Example |
|---|---|---|
| Invoke / call | Execute a function | "The callback is invoked when the request completes." |
| Dispatch | Route a call to the implementation that actually runs | "`sound()` is dynamically dispatched to `Dog`'s override." |
| Short-circuit | Stop evaluating as soon as the result is already determined | "`&&` short-circuits on the first `false` operand." |
| Propagate | An exception passes up the call stack instead of being handled locally | "The exception propagates until a `catch` block handles it." |
| Unwind | The call stack pops frame by frame while an exception propagates | "The stack unwinds back to the nearest handler." |
| Fall through | Execution continues into the next branch instead of stopping | "Without a `break`, the `switch` falls through to the next case." |
| Recurse | A function calls itself | "`factorial` recurses until it hits the base case." |

## State & values

| Word | Meaning | Example |
|---|---|---|
| Mutate | Change a value/object in place, rather than producing a new one | "`add()` mutates the list rather than returning a new one." |
| Shadow | A name hides an outer declaration that shares its name | "The parameter `name` shadows the class property `name`." |
| Capture | A lambda holds onto a variable from its enclosing scope | "The lambda captures `count` from the outer function." |
| Hoist | Move state up to a shared/common owner instead of keeping it local | "State is hoisted from the child composable to its parent." |
| Memoize | Cache a computed result so it isn't recomputed | "The expensive lookup is memoized after the first call." |
| Leak | A reference outlives the thing it should have let go of | "The listener leaks the Activity by holding onto it after `onDestroy`." |

## Types

| Word | Meaning | Example |
|---|---|---|
| Coerce | Convert a value from one type to another, implicitly or explicitly | "The `Int` is coerced to a `Long`." |
| Cast | Explicitly assert or convert a value's type | "`as User` casts the value, throwing if it isn't actually one." |
| Box / unbox | Wrap a primitive in an object, or unwrap it back | "An `Int` gets boxed into an `Integer` when stored in a generic collection." |
| Infer | The compiler determines a type without it being written explicitly | "`val x = 5` — the type `Int` is inferred." |
| Erase | Generic type information is discarded at runtime | "Once compiled, `List<T>`'s `T` is erased — the JVM just sees `List`." |
| Narrow / widen | Convert to a more/less specific type | "Smart-casting narrows `Any` to `String` after an `is` check." |

## Concurrency

| Word | Meaning | Example |
|---|---|---|
| Block | A thread stops and waits, doing nothing else, until something completes | "`Thread.sleep` blocks the thread it's called on." |
| Suspend / resume | A coroutine pauses and later continues, without blocking its thread | "The function suspends at `delay()` and resumes on the next tick." |
| Race (race condition) | Two or more operations' outcome depends on unpredictable timing | "Reading and writing the counter from two threads is a race." |
| Deadlock | Two or more operations wait on each other forever | "Both threads deadlock, each waiting for the other's lock." |
| Starve | An operation never gets the turn/resources it needs to proceed | "Low-priority tasks starve behind an endless stream of high-priority ones." |

## Structure & OOP

| Word | Meaning | Example |
|---|---|---|
| Instantiate | Create a concrete object from a class | "A new `User` instance is instantiated." |
| Override | Replace an inherited implementation with your own | "`sound()` is overridden in `Dog` to make a different sound." |
| Implement | Provide the required members for an interface's contract | "`Button` implements `Clickable` by providing `click()`." |
| Compose | Build behavior by combining smaller objects, rather than inheriting it | "Favor composition over inheritance." |
| Delegate | Hand a call off to another object that actually does the work | "`by` delegates the interface's members to `base`." |

## See also

- [Glossary](glossary.md) — the terms these words describe
