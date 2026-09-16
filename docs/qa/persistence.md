# Persistence

Collapsed by default — try to answer before revealing.

## Persistence (Room, DataStore, SharedPreferences)

??? question "What's the difference between Room's `@Query`, `@Insert(onConflict = ...)`, and raw SQL usage?"
    `@Query` lets you write custom SQL validated at compile time against your schema; `@Insert(onConflict = ...)` provides declarative conflict resolution strategies (e.g., `REPLACE`, `IGNORE`) for simple insert operations without writing SQL; raw SQL via `SupportSQLiteDatabase` bypasses Room's compile-time checks entirely for cases the DSL can't express.

??? question "How does Room support returning `Flow`/`LiveData` from a DAO query?"
    Room generates an observer using its `InvalidationTracker`, which watches the underlying tables for changes (via triggers) and re-runs the query automatically to emit a fresh result whenever relevant data changes.

??? question "What's the difference between Room's `@Embedded` and a foreign-key relationship modeled with `@Relation`?"
    `@Embedded` flattens a nested object's fields into the same table (no separate table); `@Relation` links data across separate tables (one-to-many, etc.) and is resolved via a separate query when Room maps results back into POJOs.

??? question "Why does Room require you to run queries off the main thread by default, and what happens if you don't?"
    SQLite I/O can block for an unpredictable duration; running on the main thread risks ANRs, so Room throws an `IllegalStateException` by default unless you explicitly allow main-thread queries (discouraged) or use suspend/Flow-returning DAO methods.

??? question "What is a Room database Migration, and what happens if you don't provide one when the schema version changes?"
    A `Migration` defines the SQL steps to transform an old schema version into a new one; without it (and without `fallbackToDestructiveMigration()`), Room throws an exception at runtime when it detects a version mismatch it can't resolve.

??? question "What's the difference between `fallbackToDestructiveMigration()` and writing an explicit `Migration`?"
    Destructive migration wipes and recreates the database (data loss) — acceptable for non-critical cached data; an explicit `Migration` preserves user data by executing precise `ALTER TABLE`/data-transform SQL statements.

??? question "What's the difference between `SharedPreferences` and `DataStore`, and why did Google recommend migrating?"
    `SharedPreferences` is synchronous on first load (can block the UI thread), lacks transactional guarantees on multi-key edits, and has no type-safe error handling; `DataStore` (Preferences or Proto) is fully asynchronous via Flow/coroutines, handles errors as part of the Flow, and Proto DataStore adds compile-time type safety with schema evolution support.

??? question "What's the difference between Preferences DataStore and Proto DataStore?"
    Preferences DataStore is a simple key-value store similar to SharedPreferences but reactive/async; Proto DataStore stores a strongly-typed object defined via Protocol Buffers, giving compile-time type safety and structured schema versioning.

??? question "How would you design offline-first sync with local writes and eventual server sync?"
    Write changes locally immediately (optimistic UI update) with a "dirty"/"pending sync" flag per record, queue a background sync job (e.g., WorkManager) to push changes when connectivity allows, and resolve conflicts (last-write-wins, server-wins, or merge logic) when the server acknowledges or rejects the sync.

??? question "What's a common conflict resolution strategy for offline-first apps, and its tradeoff?"
    Last-write-wins by timestamp is simple but can silently discard a user's concurrent edit; a more robust approach (versioning/CRDTs/manual merge prompts) preserves more data but adds significant complexity.

??? question "Why should you avoid storing large binary blobs (like images) directly in a Room/SQLite database?"
    SQLite isn't optimized for large BLOB storage, bloating the DB file and cache; better to store the file on disk and keep only the file path/URI in the database row.

??? question "What's the difference between `Room.databaseBuilder` on-disk vs `Room.inMemoryDatabaseBuilder`?"
    In-memory databases exist only for the process's lifetime and are wiped on process death — useful for tests or ephemeral caches, not for persistent user data.

??? question "How does Room's `@TypeConverter` work, and give an example use case."
    It registers custom serialization logic for types SQLite can't store natively (e.g., converting a `Date` to/from a `Long` timestamp, or a custom enum to/from its string name).

??? question "What's the difference between encrypting a Room database (e.g., via SQLCipher) and relying on Android's file-based encryption alone?"
    Android's file-based encryption protects data at rest when the device is locked, but a rooted device or a backup extraction could still expose the raw DB file; SQLCipher-style encryption additionally encrypts the DB content itself, protecting it even if the file is exfiltrated, at the cost of some performance overhead.

## Room Advanced (FTS, Indices, Transactions)

??? question "What is Room's Full-Text Search (FTS) support, and when would you use an `@Fts4`/`@Fts3` entity?"
    It backs a table with SQLite's virtual FTS table implementation, enabling efficient text-search queries (`MATCH`) across large text columns; use it when you need fast substring/keyword search across significant text content rather than exact-match `LIKE` queries, which don't scale well.

??? question "What's the difference between adding a database index via `@Index` on an entity versus relying on the primary key alone?"
    The primary key is automatically indexed for lookups by that key; a separate `@Index` on other frequently-queried/filtered columns (e.g., a foreign key or a commonly sorted-by column) significantly speeds up queries filtering/joining on those columns, at the cost of slightly slower writes and extra storage.

??? question "What does `@Transaction` on a Room DAO method guarantee?"
    It ensures multiple queries within that method execute atomically as a single database transaction — either all succeed or none are committed — important when a logical operation spans multiple related writes (or a read that must see a consistent snapshot across multiple queries).

??? question "Why would a `@Transaction`-annotated method combining a `@Query` returning `@Relation` data still need the annotation even though it's 'just reading'?"
    Reading a parent entity plus its related child entities (via `@Relation`) actually issues multiple separate queries under the hood; wrapping them in a transaction ensures a consistent snapshot (no data changing between the parent and child queries) rather than each query independently viewing potentially different states.

??? question "What's the difference between Room's `@Dao` suspend functions running each in its own transaction versus explicitly wrapping multiple DAO calls together?"
    Individual suspend DAO calls are each their own implicit transaction by default; if you need multiple separate DAO method calls (e.g., insert into two different tables) to succeed/fail together atomically, you must wrap them explicitly using `RoomDatabase.withTransaction {}`.

??? question "What's a performance consideration when inserting a large batch of rows into Room?"
    Use a single bulk `@Insert(list: List<Entity>)` call (which Room executes as one prepared-statement batch inside a transaction) rather than looping and calling a single-row insert method repeatedly, which would otherwise incur per-row transaction overhead.

??? question "What is `PRAGMA foreign_keys` and why does Room require enabling it explicitly for cascading behavior to work?"
    SQLite disables foreign key constraint enforcement by default for backward compatibility; Room lets you declare `@ForeignKey` relationships with `onDelete`/`onUpdate` cascade behavior, but that enforcement only actually takes effect if foreign key checking is enabled on the connection, which Room does via its own configuration.
