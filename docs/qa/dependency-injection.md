# Dependency Injection

Collapsed by default — try to answer before revealing.

## Dependency Injection (Dagger/Hilt)

??? question "What problem does Dagger solve compared to manual dependency injection?"
    At scale, manually wiring dependencies (constructing objects and passing them down) becomes unmanageable across large object graphs; Dagger generates the wiring code at compile time via annotation processing, catching missing/circular dependencies at build time.

    ```kotlin
    // manual: you wire everything by hand, easy to get wrong at scale
    val repo = UserRepository(UserApi(), UserDao())

    // Dagger: generates this wiring, catches mistakes at build time
    class UserRepository @Inject constructor(private val api: UserApi, private val dao: UserDao)
    ```

??? question "What's the difference between constructor injection, field injection, and method injection?"
    Constructor injection passes dependencies via the constructor (preferred — enables immutability and easy testing); field injection sets dependencies directly on fields after construction (needed for Android framework classes like Activities that the OS instantiates); method injection passes dependencies into a setter/method.

    ```kotlin
    class Foo @Inject constructor(private val repo: Repo) // constructor injection — preferred

    class MyActivity : AppCompatActivity() {
        @Inject lateinit var repo: Repo // field injection — Activity has no constructor Hilt controls
    }
    ```

??? question "Why do Activities/Fragments require field injection instead of constructor injection with Hilt?"
    The Android OS instantiates Activities/Fragments itself via no-arg constructors, so Hilt can't intercept construction to inject constructor params — it injects fields after the framework creates the instance, in `onCreate()`/`onAttach()` via generated base classes.

    ```kotlin
    @AndroidEntryPoint
    class MyActivity : AppCompatActivity() {
        @Inject lateinit var repo: Repo // injected after the OS calls the no-arg constructor
    }
    ```

??? question "What's the difference between `@Module` and `@Component` in Dagger?"
    `@Module` declares how to provide certain types (via `@Provides`/`@Binds` methods); `@Component` is the interface Dagger implements to actually generate the object graph, tying together modules and defining what can be injected.

    ```kotlin
    @Module @InstallIn(SingletonComponent::class)
    object NetworkModule { @Provides fun okHttp() = OkHttpClient() }

    @Component(modules = [NetworkModule::class])
    interface AppComponent { fun okHttp(): OkHttpClient }
    ```

??? question "What's the difference between `@Provides` and `@Binds`?"
    `@Provides` is used for objects requiring construction logic (e.g., a builder pattern, factory call); `@Binds` is used purely to bind an interface to its implementation and is more efficient since it doesn't generate an extra method call at runtime.

    ```kotlin
    @Module @InstallIn(SingletonComponent::class)
    abstract class RepoModule {
        @Binds abstract fun bindRepo(impl: UserRepositoryImpl): UserRepository // pure interface binding

        companion object {
            @Provides fun okHttp() = OkHttpClient.Builder().build() // needs construction logic
        }
    }
    ```

??? question "How does Hilt simplify Dagger for Android specifically?"
    It provides predefined components tied to Android lifecycles (`SingletonComponent`, `ActivityComponent`, `ViewModelComponent`, etc.), standard scopes, and base classes/annotations (`@AndroidEntryPoint`, `@HiltViewModel`) that eliminate a lot of Dagger's boilerplate component setup.

    ```kotlin
    @HiltAndroidApp class MyApp : Application()

    @AndroidEntryPoint
    class MyActivity : AppCompatActivity() {
        private val vm: MyViewModel by viewModels() // @HiltViewModel wires this up automatically
    }
    ```

??? question "What's the difference between `@Singleton` and `@ActivityRetainedScoped` in Hilt?"
    `@Singleton` ties an instance to the application's lifetime; `@ActivityRetainedScoped` ties it to the Activity's retained lifetime (survives configuration changes, similar to `ViewModel` scoping) but is recreated if the Activity is truly finished/recreated as a new instance.

    ```kotlin
    @Singleton class AppLevelCache @Inject constructor()             // app's whole lifetime
    @ActivityRetainedScoped class ScreenState @Inject constructor()  // survives config change only
    ```

??? question "What is `@InstallIn` used for?"
    It declares which Hilt component a module belongs to, determining the scope/lifetime of the bindings it provides (e.g., `@InstallIn(SingletonComponent::class)`).

    ```kotlin
    @Module
    @InstallIn(SingletonComponent::class) // these bindings live for the app's whole lifetime
    object NetworkModule
    ```

??? question "What's the difference between `@Qualifier` and just using different types to disambiguate bindings?"
    `@Qualifier` lets you provide multiple bindings of the *same type* distinguished by an annotation (e.g., two different `OkHttpClient` instances for different base URLs) without needing separate wrapper classes.

    ```kotlin
    @Qualifier annotation class AuthClient
    @Qualifier annotation class PublicClient

    @Provides @AuthClient fun authClient(): OkHttpClient = /* ... */
    @Provides @PublicClient fun publicClient(): OkHttpClient = /* ... */
    ```

??? question "What is a multibinding (`@IntoSet`/`@IntoMap`) used for in Dagger/Hilt?"
    Aggregating multiple contributions to a collection binding across different modules — e.g., collecting several `Interceptor` implementations from different feature modules into one injected `Set<Interceptor>`.

    ```kotlin
    @Provides @IntoSet
    fun provideAuthInterceptor(): Interceptor = AuthInterceptor()
    // consumed elsewhere as a plain: Set<Interceptor>
    ```

??? question "What's a common cause of a Dagger/Hilt 'missing binding' compile error, and how do you debug it?"
    Either the type has no `@Inject` constructor/`@Provides`/`@Binds` method reachable from the component, or it's requested at the wrong scope (e.g., an Activity-scoped dependency requested from a Singleton-scoped module); Dagger's error message traces the full dependency chain to pinpoint where it breaks.

    ```kotlin
    class Foo @Inject constructor(private val bar: Bar) // Bar has no @Inject constructor anywhere
    // -> "error: [Dagger/MissingBinding] Bar cannot be provided without an @Inject constructor..."
    ```

??? question "How does Hilt work with multi-module projects regarding component dependencies?"
    Modules contribute Dagger `@Module`s that get merged into the appropriate app-level Hilt component regardless of which Gradle module they live in, as long as they're on the compile classpath — Hilt aggregates them via annotation processing across the whole app at final compile time.

    ```kotlin
    // in :feature-a
    @Module @InstallIn(SingletonComponent::class)
    object FeatureAModule // merged into the app's SingletonComponent automatically
    ```

??? question "What is `@AssistedInject` used for?"
    Injecting a class that needs both Dagger-provided dependencies and runtime-provided parameters (not known at graph-construction time), like a ViewModel factory needing a navigation argument passed at creation.

    ```kotlin
    class DetailViewModel @AssistedInject constructor(
        private val repo: UserRepository,      // Dagger-provided
        @Assisted private val userId: String,  // provided at creation time, not graph-construction time
    )
    ```

??? question "What's the difference between lazy injection (`Lazy<T>`) and a `Provider<T>` in Dagger?"
    `Lazy<T>` caches and returns the same instance on repeated `.get()` calls (computed once, on first access); `Provider<T>` returns a new instance (or respects scope) on every `.get()` call.

    ```kotlin
    class Foo @Inject constructor(
        private val lazy: Lazy<Heavy>,          // same instance every call
        private val provider: Provider<Heavy>,  // new instance (or per-scope) every call
    )
    ```

??? question "Why might you use `Provider<T>` for injecting a dependency that itself has a shorter/different scope than its consumer?"
    To avoid capturing a stale instance — the consumer can fetch a fresh instance whenever needed rather than being bound permanently to whatever instance existed at injection time.

    ```kotlin
    class LongLivedSingleton @Inject constructor(private val provider: Provider<RequestScoped>) {
        fun handle() = provider.get() // always fresh — never a stale captured instance
    }
    ```

??? question "What's the difference between testing with Hilt's `@HiltAndroidTest`/`@UninstallModules` versus manual DI/fakes without Hilt?"
    Hilt's test annotations let you swap real modules for test-only fake modules within the same DI graph structure used in production; manual DI without Hilt-specific test tooling usually means constructing objects directly with fakes, bypassing any graph entirely.

    ```kotlin
    @HiltAndroidTest
    class MyTest {
        @get:Rule val hiltRule = HiltAndroidRule(this) // swaps modules within the same real graph
    }
    ```

## LiveData, ViewModel Factories & Hilt Testing Deep Dive

??? question "What's the difference between `LiveData.map()`/`switchMap()` and simply observing and re-emitting manually?"
    `map`/`switchMap` (via `MediatorLiveData` under the hood) declaratively transform/chain LiveData sources while automatically handling subscription/unsubscription as sources change, avoiding manual boilerplate of adding/removing observers yourself.

    ```kotlin
    val name: LiveData<String> = userId.switchMap { id -> repo.getUserLiveData(id) }
    // vs manually: userId.observeForever { id -> repo.getUserLiveData(id).observeForever { ... } }
    ```

??? question "What's the difference between `map` and `switchMap` on LiveData?"
    `map` transforms each emitted value synchronously into a new value; `switchMap` maps each emitted value into an entirely new LiveData source and switches the returned LiveData's subscription to follow that new source, useful when the transformation itself is asynchronous (e.g., triggering a new DB query per input value).

    ```kotlin
    val upper: LiveData<String> = name.map { it.uppercase() }             // sync transform
    val user: LiveData<User> = userId.switchMap { id -> repo.getUser(id) } // new source per value
    ```

??? question "What is `MediatorLiveData` and why is it the building block behind `map`/`switchMap`?"
    It's a LiveData subclass that can observe one or more other LiveData sources and combine/react to their emissions with custom logic (`addSource`), which is exactly the mechanism `map`/`switchMap` are implemented on top of internally.

    ```kotlin
    val combined = MediatorLiveData<String>().apply {
        addSource(first) { value = "$it ${second.value}" }
        addSource(second) { value = "${first.value} $it" }
    }
    ```

??? question "Why has LiveData usage declined relative to StateFlow in modern Android codebases?"
    StateFlow/Flow are Kotlin-native, work outside Android (testable on pure JVM without Android framework dependency), integrate more richly with the coroutines ecosystem (operators like `combine`, `debounce`), whereas LiveData is Android-specific and offers a more limited operator set.

    ```kotlin
    val state: StateFlow<UiState> // testable on plain JVM, works with combine/debounce/etc.
    val state: LiveData<UiState>  // Android-specific, smaller operator set
    ```

??? question "How do you provide constructor-injected ViewModel dependencies via Hilt, and what does `@HiltViewModel` do?"
    `@HiltViewModel` on the ViewModel class combined with `@Inject constructor(...)` lets Hilt generate the necessary `ViewModelProvider.Factory` automatically, so you just call `hiltViewModel()` (Compose) or use the standard `by viewModels()` delegate without writing a custom Factory by hand.

    ```kotlin
    @HiltViewModel
    class MyViewModel @Inject constructor(private val repo: UserRepository) : ViewModel()

    class MyActivity : AppCompatActivity() {
        private val vm: MyViewModel by viewModels() // no custom Factory needed
    }
    ```

??? question "How would you inject a runtime navigation argument (not known at DI-graph-construction time) into a Hilt ViewModel?"
    Use `SavedStateHandle` (which Hilt automatically provides to `@HiltViewModel` classes) to read the navigation argument passed via the Bundle, rather than needing `@AssistedInject` for this specific common case.

    ```kotlin
    @HiltViewModel
    class DetailViewModel @Inject constructor(
        savedStateHandle: SavedStateHandle, // Hilt provides this automatically
    ) : ViewModel() {
        private val userId: String = savedStateHandle["userId"]!!
    }
    ```

??? question "How would you swap a real network module for a fake one in a Hilt instrumented test?"
    Annotate the test with `@HiltAndroidTest`, use `@UninstallModules(RealNetworkModule::class)` to remove the production module from the graph for that test, and provide a `@TestInstallIn`-annotated replacement module supplying fakes.

    ```kotlin
    @HiltAndroidTest
    @UninstallModules(RealNetworkModule::class)
    class MyTest {
        @Module
        @TestInstallIn(components = [SingletonComponent::class], replaces = [RealNetworkModule::class])
        object FakeNetworkModule { @Provides fun api(): Api = FakeApi() }
    }
    ```

??? question "Why must `@HiltAndroidTest` classes typically use a custom test runner/Application?"
    Hilt needs a Hilt-aware test Application (`HiltTestApplication`, configured via a custom `AndroidJUnitRunner`) to generate the correct test component hierarchy instead of the production Application class, since the DI graph setup differs for test doubles.

    ```kotlin
    // build.gradle: testInstrumentationRunner = "com.example.CustomTestRunner"
    class CustomTestRunner : AndroidJUnitRunner() {
        override fun newApplication(cl: ClassLoader?, name: String?, context: Context?) =
            super.newApplication(cl, HiltTestApplication::class.java.name, context)
    }
    ```
