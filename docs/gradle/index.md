# Gradle

Android build system.

## Topics to fill in

- Kotlin DSL (`build.gradle.kts`) basics
- Version catalogs (`libs.versions.toml`)
- Multi-module project setup
- Build variants, flavors, build types
- Custom Gradle tasks & plugins
- Dependency resolution & configurations (`implementation` vs `api`)
- Build performance (configuration cache, build scans)

## Example: version catalog

```toml
[versions]
kotlin = "2.0.0"
compose-bom = "2024.06.00"

[libraries]
compose-bom = { module = "androidx.compose:compose-bom", version.ref = "compose-bom" }

[plugins]
android-application = { id = "com.android.application", version = "8.5.0" }
```
