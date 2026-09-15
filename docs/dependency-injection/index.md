# Dependency Injection

Hilt, Koin, and manual DI on Android.

## Topics to fill in

- DI principles (constructor injection, inversion of control)
- Hilt: `@HiltAndroidApp`, `@AndroidEntryPoint`, modules, scopes (`@Singleton`, `@ActivityScoped`)
- Koin: modules, `single`/`factory`, `viewModel {}`
- Manual DI containers for small projects
- Testing with DI (fakes vs. mocks, test modules)

## Example: Hilt module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService =
        retrofit.create(ApiService::class.java)
}
```
