# Statement vs. Expression

A **statement** does something (an action) but doesn't produce a usable
value; an **expression** evaluates to a value you can assign, pass
around, or return. Kotlin leans further toward "everything is an
expression" than Java/C-family languages — `if`, `try`, and `when` are
expressions here.

## Example

```kotlin
val status = if (code == 200) "OK" else "Error"   // (1)!

val message = try {                                 // (2)!
    fetch()
} catch (e: Exception) {
    "failed: ${e.message}"
}

println("done")                                      // (3)!
```

1. `if` is an **expression** in Kotlin — it evaluates directly to a value
   (`"OK"`/`"Error"`). In Java/C, `if` is a statement — you'd declare a
   variable first, then assign it inside each branch.
2. `try`/`catch` is also an expression here — whichever branch runs, its
   last expression becomes the value.
3. `println(...)` is a **statement** — it does something (prints), but
   the call itself returns `Unit`, not a value worth using.

## Comparison

| | Java / C | Kotlin |
|---|---|---|
| `if` | Statement only | Expression |
| `try`/`catch` | Statement only | Expression |
| `switch` / `when` | Statement (`switch`) | Expression (`when`) |
| Loops, `throw`, assignment | Statements | Statements (same in both) |

## Explanation

The dividing line is *"does it produce a value?"* — a `for` loop and a
`throw` are statements in Kotlin too. What differs from Java/C is which
control-flow constructs also double as expressions: Kotlin deliberately
made `if`/`when`/`try` expressions so you can skip the "declare a `var`,
then assign it in every branch" boilerplate.

## See also

- [Compiler](compiler.md)

## Further reading

- [Wikipedia: Statement (computer science)](https://en.wikipedia.org/wiki/Statement_(computer_science))
- [Kotlin docs: Conditions and loops](https://kotlinlang.org/docs/control-flow.html)
