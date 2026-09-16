# Security & Privacy

Collapsed by default — try to answer before revealing.

## Security

??? question "What is the Android Keystore system, and why is it safer than storing keys in SharedPreferences?"
    It generates and stores cryptographic keys in hardware-backed secure storage (when available, e.g., TEE/StrongBox) such that the raw key material never enters app-process-readable memory or storage; SharedPreferences stores plain values readable by anyone with root/backup access to app data.

    ```kotlin
    val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
    keyGen.init(KeyGenParameterSpec.Builder("myKey", PURPOSE_ENCRYPT or PURPOSE_DECRYPT).build())
    val key = keyGen.generateKey() // raw key material never leaves the Keystore
    ```

??? question "How would you securely store an OAuth refresh token on-device?"
    Encrypt it using a key from the Android Keystore (e.g., via Jetpack Security's `EncryptedSharedPreferences` or `EncryptedFile`), rather than storing it in plaintext SharedPreferences or a plain file.

    ```kotlin
    val prefs = EncryptedSharedPreferences.create(
        "secure_prefs", masterKeyAlias, context,
        PrefKeyEncryptionScheme.AES256_SIV, PrefValueEncryptionScheme.AES256_GCM
    )
    prefs.edit().putString("refresh_token", token).apply()
    ```

??? question "What's the difference between symmetric and asymmetric encryption, and which does Android Keystore typically support for app data encryption?"
    Symmetric encryption uses one shared key for both encrypt/decrypt (faster, used for bulk data like `EncryptedSharedPreferences`, typically AES); asymmetric uses a public/private key pair (used for signing/verification or key exchange) — Android Keystore supports both, but symmetric AES keys are the common choice for encrypting local data.

    ```kotlin
    val secretKey = KeyGenerator.getInstance("AES").generateKey()       // symmetric
    val keyPair = KeyPairGenerator.getInstance("RSA").genKeyPair()      // asymmetric
    ```

??? question "What's the difference between an exported and non-exported component, and why does it matter for security?"
    Exported components (`exported="true"`) can be invoked by other apps on the device; non-exported ones can only be invoked from within your own app (or with matching signature-level permissions) — leaving sensitive components (e.g., ones handling internal data) exported unintentionally is a common vulnerability.

    ```xml
    <activity android:name=".InternalActivity" android:exported="false" />
    <activity android:name=".ShareTarget" android:exported="true" />
    ```

??? question "What is a deep link hijacking risk, and how do you mitigate it?"
    A malicious app could register an overlapping deep link scheme/host and intercept an Intent meant for your app; mitigate via Android App Links (HTTPS-based, verified through a `assetlinks.json` file hosted on your domain), which cryptographically ties the link to your app and prevents other apps from claiming it without domain ownership.

    ```text
    myapp://open/profile              # any app can declare this scheme
    https://example.com/open/profile  # App Link — verified via assetlinks.json
    ```

??? question "What's the difference between a custom URI scheme deep link and an Android App Link?"
    A custom scheme (`myapp://...`) can be claimed by any app declaring the same scheme, with no ownership verification; an App Link uses `https://` URLs verified via Digital Asset Links, so the system only allows your verified app to handle it (falling back to browser if unverified).

    ```xml
    <intent-filter>
        <data android:scheme="myapp" /> <!-- unverified, anyone can claim "myapp://" -->
    </intent-filter>
    <intent-filter android:autoVerify="true">
        <data android:scheme="https" android:host="example.com" /> <!-- verified -->
    </intent-filter>
    ```

??? question "What is certificate/SSL pinning's main risk if implemented carelessly?"
    If the pinned certificate/key expires or rotates without an app update deploying the new pin in time, users can lose connectivity entirely ("bricking" the app's network access) until they update.

    ```kotlin
    CertificatePinner.Builder()
        .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        .build()
    // forgetting to rotate this pin before the cert expires breaks connectivity app-wide
    ```

??? question "What's the difference between Play Integrity API and the deprecated SafetyNet Attestation?"
    Play Integrity API is Google's newer, more robust replacement providing device integrity, app integrity, and account/licensing signals in one API, with improved anti-tampering and better performance; SafetyNet Attestation is being phased out.

    ```kotlin
    val integrityManager = IntegrityManagerFactory.create(context)
    integrityManager.requestIntegrityToken(
        IntegrityTokenRequest.builder().setNonce(nonce).build()
    )
    ```

??? question "How do you protect against reverse engineering/tampering of a release APK?"
    Enable R8 with obfuscation, use Play Integrity API to detect tampered/rooted environments, avoid embedding secrets directly in code (use backend-mediated secrets/remote config instead), and consider native code (NDK) for extremely sensitive logic since it's harder to decompile than DEX bytecode.

    ```kotlin
    android {
        buildTypes {
            release {
                isMinifyEnabled = true // R8 shrinking + obfuscation
            }
        }
    }
    ```

??? question "Why is it a bad practice to hardcode API keys/secrets directly in app code, even if obfuscated?"
    Obfuscation slows but doesn't prevent extraction — a determined attacker can still recover secrets from the APK; sensitive secrets should be kept server-side, with the app authenticating to a backend that performs the sensitive operation instead.

    ```kotlin
    // Bad:    const val API_KEY = "sk_live_abc123"   // recoverable from the APK
    // Better: val token = backend.requestShortLivedToken() // secret stays server-side
    ```

??? question "What is WebView's `addJavascriptInterface` risk, and how has it been mitigated in modern Android?"
    It exposes native Java/Kotlin methods to JavaScript running in the WebView, which if the WebView loads untrusted content could be exploited via reflection-based attacks; the `@JavascriptInterface` annotation requirement (since API 17) restricts which methods are actually exposed, but you should still only load trusted content.

    ```kotlin
    class WebAppInterface(private val context: Context) {
        @JavascriptInterface // required since API 17 — only annotated methods are exposed
        fun showToast(message: String) { /* ... */ }
    }
    webView.addJavascriptInterface(WebAppInterface(context), "Android")
    ```

??? question "What's the difference between `MODE_PRIVATE` and other (deprecated) SharedPreferences file modes regarding security?"
    `MODE_PRIVATE` restricts the preferences file to your app only; the older `MODE_WORLD_READABLE`/`MODE_WORLD_WRITABLE` modes (removed in modern API levels) allowed other apps to read/write the file, a significant security risk that Android now disallows entirely.

    ```kotlin
    context.getSharedPreferences("prefs", Context.MODE_PRIVATE) // only this app can read/write
    ```

??? question "How would you implement biometric authentication (fingerprint/face) securely in an app?"
    Use the `BiometricPrompt` API tied to a Keystore-backed cryptographic key (e.g., a `CryptoObject`) so that a successful biometric match is required to unlock/use the key itself — not just a boolean "authenticated" flag that could be bypassed by hooking the check in decompiled code.

    ```kotlin
    val cipher = Cipher.getInstance(TRANSFORMATION).apply { init(Cipher.ENCRYPT_MODE, secretKey) }
    biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    ```

??? question "What's the risk of relying only on a boolean result from `BiometricPrompt` without a tied `CryptoObject`?"
    Without cryptographic binding, a "success" boolean check in your own code could theoretically be bypassed via tampering/hooking (e.g., on a rooted device with instrumentation frameworks); tying it to Keystore-backed crypto means the actual decryption operation itself requires the biometric-gated key, not just a code-level flag.

    ```kotlin
    // Risky: onAuthSucceeded = { isUnlocked = true }         // a flag that can be hooked
    // Safer: the decrypt operation itself needs the CryptoObject's Keystore-gated key
    ```

??? question "What's the difference between `FLAG_SECURE` on a Window and simply not logging sensitive data?"
    `FLAG_SECURE` prevents the screen content from appearing in screenshots, screen recordings, and the recent-apps thumbnail at the OS level; it's a UI-level protection distinct from (and complementary to) avoiding sensitive data in logs.

    ```kotlin
    window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
    ```

??? question "Why should sensitive data never be logged, even at debug/verbose log levels, in production builds?"
    Logs can be captured via `adb logcat` by any app with the right permission on older Android versions, included in bug reports, or accidentally shipped to crash-reporting tools, exposing sensitive data outside the app's intended boundary.

    ```kotlin
    Log.d("Auth", "token=$token") // visible via adb logcat, bug reports, crash tools — don't
    ```

## App Links, Network Security Config & Advanced Security

??? question "What's the step-by-step flow of Android App Links verification?"
    The app declares `autoVerify="true"` with `https` intent filters in its manifest; on install, the system fetches `https://<host>/.well-known/assetlinks.json` from the declared domain(s) and checks it lists the app's package name and signing certificate fingerprint; if verified, the system routes matching links directly to the app without a disambiguation dialog.

    ```xml
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <data android:scheme="https" android:host="example.com" />
    </intent-filter>
    ```

??? question "What's the difference between Network Security Config's `<domain-config>` and setting certificate pinning purely in OkHttp code?"
    Network Security Config is a manifest-declared XML policy enforced by the OS/WebView across all networking in the app (including WebViews and third-party libraries using the platform's default trust manager), whereas OkHttp-code-level pinning only protects requests made through that specific OkHttp client instance.

    ```xml
    <!-- res/xml/network_security_config.xml — applies app-wide, not just to one OkHttpClient -->
    <network-security-config>
        <domain-config>
            <domain includeSubdomains="true">example.com</domain>
            <pin-set><pin digest="SHA-256">AAAA...</pin></pin-set>
        </domain-config>
    </network-security-config>
    ```

??? question "What's the purpose of `<trust-anchors>` overrides in Network Security Config, and when would you use them (carefully)?"
    They let you specify additional/alternate trusted CAs (e.g., a custom internal CA for a staging/debug build talking to an internal server); using `debug-overrides` scoped only to debug builds is the safe way to do this without weakening trust in production.

    ```xml
    <debug-overrides>
        <trust-anchors>
            <certificates src="@raw/staging_ca" /> <!-- only merged into debug builds -->
        </trust-anchors>
    </debug-overrides>
    ```

??? question "What's the difference between `usesCleartextTraffic='false'` in the manifest and Network Security Config's cleartext restrictions?"
    The manifest flag is a simpler, app-wide toggle disallowing all unencrypted HTTP; Network Security Config allows finer-grained control (e.g., allowing cleartext only for specific domains like a local dev server) via `<domain-config cleartextTrafficPermitted="true">`.

    ```xml
    <application android:usesCleartextTraffic="false"> <!-- app-wide -->
    <domain-config cleartextTrafficPermitted="true">     <!-- per-domain override -->
        <domain>localhost</domain>
    </domain-config>
    ```

??? question "Why might a security-conscious app want to detect if it's running on a rooted device, and what's a limitation of doing so?"
    Rooted devices can bypass app sandboxing, tamper with runtime behavior, or extract sensitive data more easily; detection heuristics (checking for su binaries, common root-management apps) are inherently a cat-and-mouse game and can be bypassed by sufficiently sophisticated root-hiding tools, so it should be one signal among several (e.g., combined with Play Integrity API) rather than a sole security gate.

    ```kotlin
    val suspicious = listOf("/system/xbin/su", "/system/bin/su").any { File(it).exists() }
    // a heuristic only — combine with Play Integrity, never rely on this alone
    ```

??? question "What's the difference between data encrypted 'at rest' and 'in transit,' and what mechanisms handle each on Android?"
    At-rest encryption protects stored data (file-based encryption at the OS level, plus app-level encryption like Jetpack Security's `EncryptedFile` for extra-sensitive data); in-transit encryption protects data while being transmitted over the network (TLS/HTTPS, enforced via Network Security Config disallowing cleartext).

    ```kotlin
    EncryptedFile.Builder(context, file, masterKey, AES256_GCM_HKDF_4KB).build() // at rest
    // HTTPS/TLS (enforced via Network Security Config) handles "in transit" separately
    ```

## Privacy, Compliance & Consent

??? question "What's the difference between GDPR's 'consent' and 'legitimate interest' legal bases for processing user data, and why does it matter for how an app requests tracking permission?"
    Consent requires an explicit, freely-given, informed opt-in before processing (e.g., before loading tracking SDKs); legitimate interest allows processing without prior consent if the processing is reasonably expected and doesn't override the user's rights — many tracking/advertising use cases specifically require consent rather than relying on legitimate interest, shaping when an app must show a consent dialog before initializing certain SDKs.

    ```kotlin
    if (consentManager.hasConsent(Purpose.ADVERTISING)) {
        initializeAdSdk() // gated behind explicit consent, not "legitimate interest"
    }
    ```

??? question "What is a Consent Management Platform (CMP), and why do many apps integrate one (e.g., for Google's UMP SDK) rather than building consent UI from scratch?"
    A CMP provides a standardized, legally-vetted consent flow UI and stores/signals the user's choices in a format ad/analytics SDKs can read (e.g., IAB TCF strings), ensuring compliance without each app needing to independently interpret evolving privacy regulations correctly.

    ```kotlin
    UserMessagingPlatform.loadConsentInfoUpdate(activity, params, { /* ready */ }, { /* error */ })
    ```

??? question "What's the difference between COPPA compliance requirements and general GDPR/privacy requirements, in terms of what triggers extra obligations?"
    COPPA specifically applies to apps directed at or knowingly collecting data from children under 13 in the US, imposing strict limits on data collection/behavioral advertising for that audience; general privacy regulations like GDPR apply more broadly regardless of user age but with their own separate specific provisions for minors' data.

    ```kotlin
    if (userAge < 13) {
        disableBehavioralAds() // COPPA-triggered restriction, on top of baseline GDPR handling
    }
    ```

??? question "Why must ad SDK initialization sometimes be deferred until after consent is obtained, rather than initializing everything at app startup unconditionally?"
    Initializing certain SDKs can itself trigger data collection/transmission before the user has had a chance to consent or decline, which would violate a consent-required legal basis — the app must gate that initialization behind the consent flow's outcome.

    ```kotlin
    consentManager.onConsentObtained {
        MobileAds.initialize(context) // only after this callback, not in Application.onCreate()
    }
    ```

??? question "What's the difference between anonymized and pseudonymized data from a privacy-compliance perspective?"
    Anonymized data has had identifying information irreversibly removed such that the individual can't be re-identified even by the data holder; pseudonymized data replaces identifiers with a substitute (e.g., a hashed user ID) but could still be re-linked to the individual using additional information, so it typically still counts as personal data under regulations like GDPR.

    ```kotlin
    val pseudonymized = sha256(userId) // still re-linkable via the original mapping table
    // anonymized: identifying fields are permanently stripped — no mapping exists to reverse it
    ```

## Enterprise, Multi-User & Direct Boot

??? question "What's the difference between a 'work profile' (Android Enterprise) and simply having multiple user accounts on a device?"
    A work profile is a separate, isolated set of apps/data managed by an organization's MDM policy running alongside the personal profile on the same user account (badge-icon apps, separate storage); multiple user accounts are fully separate OS-level user spaces, each with entirely independent app installs/data, switchable at the lock screen.

    ```kotlin
    val userManager = context.getSystemService(UserManager::class.java)
    val isWorkProfile = userManager.isManagedProfile
    ```

??? question "What's Direct Boot, and why would an app need to support it?"
    It lets specially-registered app components run in a limited capacity before the user unlocks the device after a reboot (using device-encrypted storage rather than credential-encrypted storage), relevant for apps needing to respond to something (e.g., alarms, incoming calls) immediately after boot without waiting for first unlock.

    ```kotlin
    // manifest: android:directBootAware="true" on the component
    val deviceProtectedContext = context.createDeviceProtectedStorageContext()
    ```

??? question "What's the difference between device-encrypted and credential-encrypted storage in the context of Direct Boot?"
    Device-encrypted storage is accessible as soon as the device boots (before user unlock); credential-encrypted storage (the default for most app data) is only accessible after the user unlocks the device with their credentials, since it's encrypted using a key derived from the user's lock screen credential.

    ```kotlin
    val deviceEncrypted = context.createDeviceProtectedStorageContext() // available pre-unlock
    val credentialEncrypted = context // default — only after the user unlocks
    ```

??? question "What are app restrictions (managed configurations) in an Android Enterprise context?"
    Configuration values pushed by an EMM/MDM admin (e.g., allowed feature toggles, server URLs) that the app reads via `RestrictionsManager`, letting IT admins remotely control app behavior for managed/work-profile deployments without the end user configuring anything manually.

    ```kotlin
    val restrictions = context.getSystemService(RestrictionsManager::class.java)
    val serverUrl = restrictions.applicationRestrictions.getString("server_url")
    ```

??? question "What's the difference between a 'fully managed device' and a 'work profile' deployment mode in Android Enterprise?"
    Fully managed means the entire device is under organizational control (typically company-owned); a work profile mode isolates only a managed container on an otherwise personally-owned/controlled device (BYOD), leaving the personal side outside IT's management scope.

    ```kotlin
    val dpm = context.getSystemService(DevicePolicyManager::class.java)
    val isOrgOwnedFullyManaged = dpm.isDeviceOwnerApp(packageName)
    ```
