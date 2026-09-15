# Retrofit & Networking

HTTP clients and serialization.

## Topics to fill in

- Retrofit setup, `@GET`/`@POST`/`@Body`/`@Query`
- Converters (`kotlinx.serialization`, Moshi, Gson)
- OkHttp interceptors (logging, auth headers)
- Error handling & `Result`/sealed wrapper patterns
- Coroutines + Retrofit (`suspend` functions)
- Pagination (Paging 3 + network)
- Testing with MockWebServer

## Example

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto
}

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
    .build()
```
