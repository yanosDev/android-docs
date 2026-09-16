# Architecture & Design Patterns

Collapsed by default — try to answer before revealing.

## Architecture Patterns (MVVM/MVI/Clean Architecture)

??? question "What problem does MVVM solve compared to putting logic directly in an Activity/Fragment?"
    It separates UI rendering from business/state logic into a `ViewModel`, decoupling it from the Android lifecycle so it's independently testable and survives configuration changes.

??? question "What is Unidirectional Data Flow (UDF), and why is it favored in modern Android architecture?"
    State flows one direction (state -> UI) while events flow the opposite (UI -> intent/action -> state update), preventing the UI from directly mutating state ad hoc and making state changes predictable, traceable, and easier to test.

??? question "What's the difference between MVVM and MVI?"
    MVVM typically exposes multiple discrete observable properties/LiveData from the ViewModel; MVI (Model-View-Intent) consolidates all UI state into a single immutable state object emitted as a stream, with all user actions modeled as explicit "intents" processed by a reducer-like function.

??? question "What's the difference between MVP and MVVM?"
    MVP has the Presenter hold a direct reference to the View interface and imperatively calls its methods to update UI; MVVM's ViewModel exposes observable state that the View passively observes, with no direct reference back to the View.

??? question "What's a Repository pattern and what problem does it solve for testability?"
    It abstracts data source details (network, DB, cache) behind a single interface consumed by ViewModels/UseCases, so tests can substitute a fake/mock Repository without needing real network/DB access.

??? question "How do you implement a single source of truth when combining local cache and network data?"
    The Repository writes network results into the local DB, and the UI observes only the DB (e.g., via Room's Flow) — the network acts purely as a data refresher, never read directly by the UI, avoiding two conflicting sources of state.

??? question "What's the difference between a UseCase/Interactor and a Repository?"
    A Repository handles data access/source coordination; a UseCase encapsulates a specific piece of business logic that may combine one or more Repositories, useful when logic is reused across multiple ViewModels or is complex enough to warrant isolation.

??? question "When is adding a UseCase layer overkill?"
    When the ViewModel just calls a single Repository method with no additional business logic — introducing a pass-through UseCase adds indirection without real benefit; reserve UseCases for logic with actual complexity or reuse.

??? question "What are the layers in Clean Architecture as typically applied to Android?"
    Presentation (UI/ViewModel), Domain (UseCases/business models, framework-independent), and Data (Repositories/data sources); dependencies point inward, with Domain having no Android framework dependency.

??? question "Why should the Domain layer avoid depending on Android framework classes?"
    To keep business logic independently testable (pure JVM unit tests, no Android runtime needed) and reusable across platforms (e.g., in a Kotlin Multiplatform module).

??? question "What's the difference between a 'reducer' (as in MVI) and a plain ViewModel function updating state?"
    A reducer is a pure function `(currentState, action) -> newState` with no side effects, making state transitions deterministic and testable in isolation; ad hoc ViewModel functions may mix side effects (network calls) directly with state mutation, which is harder to test purely.

??? question "What's the difference between 'state' and 'event' in UI architecture, and why treat them differently?"
    State represents a persistent snapshot the UI should always reflect (e.g., "is loading"); events are one-off occurrences that shouldn't replay (e.g., "show a toast") — conflating them (e.g., storing an event in StateFlow) causes bugs like event replay on rotation.

??? question "What is the 'service locator' pattern and how does it differ from dependency injection?"
    A service locator is a global registry that objects actively pull dependencies from at runtime (hiding what a class actually needs); DI pushes dependencies into a class explicitly (usually via constructor), making dependencies visible and testable without a global registry.

??? question "What is the Facade pattern and where might you see it in Android app architecture?"
    A Facade provides a simplified unified interface over a complex subsystem; a Repository is effectively a Facade over multiple data sources (network client, DB, cache).

??? question "What is the Observer pattern and where does Android use it natively?"
    A subject notifies registered observers of state changes; `LiveData`, `Flow` collection, and `View.OnClickListener` registration are all applications of this pattern.

??? question "How would you structure error handling across Repository -> UseCase -> ViewModel layers?"
    Wrap results in a sealed `Result`/`Either`-like type (success/failure with typed error) at the Repository boundary so failures propagate as data rather than uncaught exceptions, letting the ViewModel map errors to UI state deterministically.

??? question "What's the tradeoff of using exceptions vs a sealed Result type for expected failure cases (e.g., 'no network')?"
    Exceptions are convenient but can be silently swallowed/uncaught crossing coroutine boundaries and don't show up in a function's type signature; a sealed Result type makes expected failure paths explicit and forces callers to handle them, at the cost of more verbose call sites.

??? question "What's the 'Single Activity' architecture pattern, and what problem does it address?"
    Using one Activity hosting multiple Fragments/Compose destinations via a navigation graph, rather than many Activities; it simplifies shared state/animations/transitions between screens and avoids the overhead/complexity of inter-Activity communication.

??? question "What's a tradeoff of the Single Activity approach?"
    It couples all screens to one Activity's lifecycle and can make certain isolation (e.g., a separate process, or independent deep-link entry points needing their own task) harder to achieve compared to multiple Activities.

## Design Patterns

??? question "What is the Builder pattern and where does Android use it natively?"
    It constructs a complex object step-by-step via chained method calls instead of a large constructor; `AlertDialog.Builder`, `NotificationCompat.Builder`, and OkHttp's `Request.Builder` are native examples.

??? question "What is the Factory pattern, and give an Android-relevant example."
    It encapsulates object creation logic behind a method/class so callers don't need to know the concrete type being created; a `ViewModelProvider.Factory` creates ViewModel instances with custom constructor dependencies without the caller needing to know construction details.

??? question "What is the Strategy pattern, and where might you apply it in a Repository?"
    It defines a family of interchangeable algorithms behind a common interface, selected at runtime; e.g., a caching strategy interface (`CacheThenNetworkStrategy` vs `NetworkOnlyStrategy`) injected into a Repository to vary data-fetching behavior without changing the Repository's code.

??? question "What is the Adapter pattern, and how does RecyclerView's `Adapter` relate to the classic GoF pattern?"
    The GoF Adapter pattern converts one interface into another expected by a client; `RecyclerView.Adapter` "adapts" a data set into View instances the RecyclerView can display, matching the spirit if not the exact textbook structure.

??? question "What is the Decorator pattern, and where might OkHttp interceptors resemble it?"
    Decorator wraps an object to add behavior without altering its interface; chained OkHttp interceptors each wrap the call further (adding headers, logging, retry logic) while preserving the same request/response interface to the next link in the chain.

??? question "What is the Command pattern, and where might it apply to an undo/redo feature?"
    It encapsulates an action (and its parameters) as an object that can be executed, queued, or reversed later; an undo/redo stack of Command objects (each with `execute()`/`undo()`) is a textbook application.

??? question "What is the State pattern, and how does it relate to MVI's state machine style?"
    It lets an object's behavior change based on its internal state, modeled as distinct state classes/objects rather than conditional flags; MVI's sealed-class UI states with a reducer function is a practical application of this idea to UI logic.

??? question "What is the Composite pattern, and how does Android's View hierarchy embody it?"
    It treats individual objects and compositions of objects uniformly through a shared interface; `ViewGroup` extending `View` while also containing child `View`s (which can themselves be `ViewGroup`s) is a textbook Composite structure.

??? question "What is the Proxy pattern, and where might Dagger's `Lazy<T>`/`Provider<T>` resemble it?"
    Proxy provides a stand-in controlling access to a real object; `Lazy<T>` acts as a proxy that defers actual instantiation until first access, controlling *when* the real object is created.

??? question "What's the difference between the Singleton pattern and Dagger/Hilt's `@Singleton` scope?"
    A classic Singleton enforces a single instance via a private constructor and static accessor, tightly coupling all consumers to that specific implementation; `@Singleton` scope in Hilt just means the DI graph creates one instance per component lifetime, while consumers still depend on an injected interface — making it far easier to substitute a fake for testing.

## Software Engineering Fundamentals (OOP, SOLID)

??? question "What is the Open/Closed Principle, and how does the Strategy pattern help satisfy it?"
    Classes should be open for extension but closed for modification; injecting a Strategy interface lets you add new behavior (a new Strategy implementation) without modifying the class that uses it.

??? question "What is the Liskov Substitution Principle, and give an Android-relevant violation example."
    Subtypes must be substitutable for their base type without breaking expected behavior; a subclass of a data class that overrides `equals()` to add identity fields not in the parent's primary constructor can violate substitutability if code relies on base-type equality semantics.

??? question "What is the Interface Segregation Principle, and why might a large `Repository` interface with 20 methods violate it?"
    Clients shouldn't be forced to depend on methods they don't use; a bloated Repository interface forces every consumer/mock to deal with unrelated methods — splitting it into smaller, focused interfaces per concern (e.g., `UserReader`, `UserWriter`) keeps dependencies minimal.

??? question "What's the difference between composition and inheritance, and why is composition often preferred in modern Android architecture?"
    Inheritance creates a rigid "is-a" relationship fixed at compile time and can lead to fragile base class problems; composition ("has-a," e.g., injecting collaborator objects) is more flexible, testable, and avoids deep inheritance hierarchies that are hard to reason about or modify safely.

??? question "What's the difference between an interface and an abstract class in Kotlin, and when would you choose each?"
    An interface can't hold constructor state and (until default methods) was pure contract; Kotlin interfaces can have default method bodies but not constructor parameters/state; an abstract class can hold state and constructor logic but only supports single inheritance — choose an interface for a pure contract multiple types might implement, an abstract class when sharing actual state/implementation among a closely related family.

??? question "What is the 'fragile base class' problem?"
    Changes to a base class's implementation can unexpectedly break subclasses that depended on specific (even undocumented) behavior of the base class, especially across versions/module boundaries — a key argument for preferring composition and small, well-contracted interfaces.

??? question "What's the difference between the `equals()`/`hashCode()` contract's requirements, and why must they always be overridden together?"
    If two objects are equal via `equals()`, they must produce the same `hashCode()`; overriding only one breaks hash-based collections (`HashMap`/`HashSet`), causing lookups to silently fail even for "equal" objects, since the collection uses hashCode first to locate the bucket.

??? question "What is the difference between checked and unchecked exceptions, and how does Kotlin's approach differ from Java's?"
    Java's checked exceptions must be declared/caught explicitly by the compiler; Kotlin has no checked exceptions at all — every exception is effectively unchecked, which simplifies signatures but means the compiler won't force you to handle expected failure cases (favoring sealed Result types for that instead).

??? question "What is the Template Method pattern, and where might Android's Activity lifecycle resemble it?"
    A base class defines the skeleton of an algorithm/process with certain steps left as overridable hooks for subclasses; the Activity base class calling `onCreate()`/`onStart()`/`onResume()` in a fixed order while letting your subclass override each step is a practical example.

??? question "What is the Visitor pattern, and where might it be useful for a sealed class hierarchy?"
    It separates an operation from the object structure it operates on, letting you add new operations without modifying the classes themselves; for a sealed class, an exhaustive `when` expression often serves a similar purpose more idiomatically in Kotlin than a full Visitor implementation.

## Modularization & App Architecture at Scale

??? question "Why modularize a large Android app into multiple Gradle modules?"
    Faster incremental builds (only affected modules recompile), enforced boundaries between features (preventing accidental tight coupling), enabling parallel team development, and supporting dynamic feature delivery.

??? question "What's the difference between a feature module and a core/common module in a typical modularization strategy?"
    Feature modules contain a specific user-facing feature's UI/logic and depend on core modules; core/common modules (e.g., `core-network`, `core-ui`, `core-database`) provide shared infrastructure that multiple features depend on, but core modules should never depend on feature modules (to avoid cycles).

??? question "How do you prevent circular dependencies between feature modules that need to navigate to each other?"
    Introduce a shared navigation/API module defining interfaces or route contracts that both features depend on, or use a runtime-resolved navigation mechanism (e.g., deep links/route strings) so features don't need compile-time dependencies on each other.

??? question "What is a 'dynamic feature module' and when would you use one?"
    A module delivered on-demand via Play Feature Delivery rather than bundled into the base install, useful for large, optional, or rarely-used features (e.g., an AR mode) to keep the initial app download size small.

??? question "What's the difference between install-time, on-demand, and conditional dynamic feature delivery?"
    Install-time modules are always downloaded with the base app; on-demand modules are downloaded only when requested at runtime; conditional modules are automatically included only for users/devices matching specified criteria (e.g., a minimum API level or device feature).

??? question "How would you architect a large app to support fast, isolated feature development across multiple teams?"
    Strict modularization with clear public API boundaries per module (internal visibility for implementation details), a shared design system module, contract-based navigation, and independently buildable/testable feature modules with their own sample/demo apps for isolated iteration.

??? question "What's the risk of over-modularizing a small/medium app?"
    The overhead of managing many small modules (build config duplication, more complex dependency graphs, slower initial/full builds due to module resolution overhead) can outweigh the benefits if the team/codebase isn't large enough to need the isolation.

??? question "What is a 'convention plugin' in Gradle and why use one in a multi-module project?"
    A custom Gradle plugin encapsulating shared build logic (common compile options, dependency setups) applied consistently across many modules, avoiding copy-pasted `build.gradle` boilerplate and centralizing changes to one place.
