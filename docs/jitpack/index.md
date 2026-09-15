# JitPack

Publishing and consuming libraries via JitPack.

## Topics to fill in

- How JitPack builds a repo on demand from a Git tag/commit
- Adding the JitPack repository in `settings.gradle.kts`
- Publishing your own library (required `maven-publish` setup)
- Versioning with tags vs. `-SNAPSHOT` (`jitpack.io` commit builds)
- Troubleshooting failed builds (checking the JitPack build log)

## Example: consuming a library

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        maven { url = uri("https://jitpack.io") }
    }
}

// module build.gradle.kts
dependencies {
    implementation("com.github.User:Repo:Tag")
}
```
