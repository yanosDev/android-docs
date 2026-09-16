# Kotlin

Language fundamentals and idioms — not tutorials, but reference pages for
things I already know how to *use* and keep forgetting how to *name*.

## Page format

Every page in this section follows the same shape:

1. **Name** — the term(s) as they show up in docs/talks, so search actually
   finds it.
2. **Short example with markings** — a minimal snippet with numbered
   annotations pointing at the exact thing being named.
3. **Explanation** — what's actually going on underneath, briefly.
4. **See also** — links to related pages in this section.
5. **Further reading** — the official doc/KEEP/source for going deeper.

## Pages

| Topic | What it covers |
|---|---|
| [Scope Functions](scope-functions.md) | `let`, `run`, `with`, `apply`, `also` — how to pick one |

## Still to write

- Receivers & lambdas with receiver (`T.() -> R`, DSL builders)
- Null safety (`?`, `?:`, `!!`, safe/platform types)
- Data classes, sealed classes, sealed interfaces
- Extension functions & properties
- Delegation (`by lazy`, `by Delegates`, custom delegates)
- Collections API (`map`, `filter`, `fold`, sequences vs. eager collections)
- Generics & variance (`in`/`out`, declaration-site vs. use-site)
- Inline functions & reified type parameters