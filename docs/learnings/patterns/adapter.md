# Adapter Pattern

Wraps one type so it satisfies an interface it wasn't originally written
for — makes two incompatible interfaces work together without changing
either one.

## Example

```kotlin
interface UsPlug { fun voltage(): Int }               // (1)!

class EuPlug { fun spannung(): Int = 230 }             // (2)!

class EuToUsAdapter(private val eu: EuPlug) : UsPlug { // (3)!
    override fun voltage() = eu.spannung()
}

fun charge(plug: UsPlug) = println("${plug.voltage()}V")
charge(EuToUsAdapter(EuPlug()))                        // (4)!
```

1. The interface the caller expects.
2. A type that does the same *job* but with a different, incompatible
   API — maybe it's from a library you can't change.
3. The adapter implements the expected interface by translating calls to
   the wrapped type's actual API.
4. The caller (`charge`) never needs to know `EuPlug` exists.

## Advantages / Disadvantages

| Advantages | Disadvantages |
|---|---|
| Connects incompatible APIs without modifying either | Another class per incompatible pair |
| Isolates the "translation" logic in one place | Can hide a design mismatch that would be better fixed at the source |

## When to use it

Integrating a third-party or legacy API you can't change into the shape
your code already expects. For a single call site, an
[extension function](../kotlin/index.md) can often adapt it even more
lightly than a whole wrapper type.

## See also

- [Interfaces](../kotlin/interfaces.md)

## Further reading

- [Wikipedia: Adapter pattern](https://en.wikipedia.org/wiki/Adapter_pattern)
