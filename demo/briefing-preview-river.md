# NightRiver Daily Briefing — 2026-11-12

Generated: 2026-11-12 13:28 UTC  |  Mode: River  |  17 items from 3 sources

---

## [Migrating a Monolith to Services Without a Rewrite](https://tangent.example.com/posts/monolith-migration)

**Source:** Tangent Tech Blog  |  **Published:** 2026-11-12T07:45Z

> We spent six months moving our Rails monolith to independently deployable services by using the strangler-fig pattern on a single bounded context at a time, keeping the existing API surface unchanged throughout the migration.

## [CSS Anchor Positioning Reaches Candidate Recommendation](https://webstandards.example.net/items/css-anchor-positioning-cr)

**Source:** Web Standards Weekly  |  **Published:** 2026-11-12T06:30Z

> The W3C CSS Working Group published CSS Anchor Positioning as a Candidate Recommendation, formalising the anchor-name and position-anchor properties that allow elements to be positioned relative to arbitrary anchors elsewhere in the document.

## [Python 3.14.0 Beta 1 Released](https://oswatch.example.org/releases/python-3-14-0b1)

**Source:** Open Source Release Watch  |  **Published:** 2026-11-12T06:00Z

> The CPython development team released Python 3.14.0 beta 1, introducing experimental support for lazy imports and a new free-threading mode that removes the GIL under a build flag.

## [TC39 Advances Signals Proposal to Stage 3](https://webstandards.example.net/items/tc39-signals-stage3)

**Source:** Web Standards Weekly  |  **Published:** 2026-11-11T20:00Z

> TC39 advanced the Signals proposal to stage 3, introducing a first-class reactive primitive to JavaScript that harmonises with framework-level reactivity systems already in widespread use.

## [Rust 1.84.0 Stabilises Arbitrary Self Types](https://oswatch.example.org/releases/rust-1-84)

**Source:** Open Source Release Watch  |  **Published:** 2026-11-11T18:00Z

> Rust 1.84.0 ships with arbitrary self types v2 stabilised, allowing smart pointer types to be used as method receivers without the unstable feature flag.

## [WHATWG Merges Invoker Commands into the HTML Living Standard](https://webstandards.example.net/items/whatwg-invoker-commands)

**Source:** Web Standards Weekly  |  **Published:** 2026-11-10T15:00Z

> WHATWG merged the Invoker Commands spec into the HTML Living Standard, adding the invoketarget and invokeaction attributes to button and input elements for declarative UI interactions.

## [How We Reduced Build Times by 60% with Remote Caching](https://tangent.example.com/posts/remote-cache-builds)

**Source:** Tangent Tech Blog  |  **Published:** 2026-11-10T14:30Z

> By sharing a Bazel remote cache across all CI runners, we cut median build time from 8 minutes to under 3 minutes without changing any build targets or source files.

## [SQLite 3.48.0 Adds Indexed Expressions on Virtual Tables](https://oswatch.example.org/releases/sqlite-3-48)

**Source:** Open Source Release Watch  |  **Published:** 2026-11-10T12:00Z

> SQLite 3.48.0 extends expression indexes to virtual tables and fixes a query planner edge case that caused full scans on certain LEFT JOIN patterns.

## [curl 8.12.0 Defaults to HTTP/3 When Available](https://oswatch.example.org/releases/curl-8-12)

**Source:** Open Source Release Watch  |  **Published:** 2026-11-09T10:00Z

> curl 8.12.0 upgrades automatically to HTTP/3 when the server advertises QUIC support via Alt-Svc, with a new --http3-only flag for strict enforcement.

## [IETF RFC 9728: HTTP Resumable Uploads Published](https://webstandards.example.net/items/rfc9728-resumable-uploads)

**Source:** Web Standards Weekly  |  **Published:** 2026-11-08T12:00Z

> IETF published RFC 9728, defining a standard protocol for resumable HTTP uploads that allows clients to resume interrupted transfers from the last acknowledged byte rather than restarting from the beginning.

## [A Practical Guide to Structured Logging in Python](https://tangent.example.com/posts/structured-logging-python)

**Source:** Tangent Tech Blog  |  **Published:** 2026-11-08T10:00Z

> Switching from unstructured print statements to structlog with JSON output made log aggregation and alerting dramatically easier, and required changing fewer than twenty lines per service.

## [Git 2.48 Ships Reftable Storage Backend as Default](https://oswatch.example.org/releases/git-2-48)

**Source:** Open Source Release Watch  |  **Published:** 2026-11-07T14:00Z

> Git 2.48 makes the reftable reference storage backend the default for new repositories, replacing the packed-refs text file format and improving performance for repositories with large numbers of branches.

## [WebAssembly Garbage Collection Reaches Phase 4](https://webstandards.example.net/items/wasm-gc-phase4)

**Source:** Web Standards Weekly  |  **Published:** 2026-11-06T09:00Z

> The WebAssembly Working Group announced that the Garbage Collection extension reached Phase 4, completing the standardisation process and enabling managed-memory languages like Kotlin and Dart to compile to Wasm without bundling a custom GC.

## [Postgres JSONB vs. Dedicated Document Store: A Measured Comparison](https://tangent.example.com/posts/jsonb-vs-document-store)

**Source:** Tangent Tech Blog  |  **Published:** 2026-11-05T09:15Z

> Under our read-heavy workload, Postgres JSONB with a GIN index matched the query throughput of a dedicated document store while eliminating the operational burden of running a second database.

## [Node.js 24.0 LTS Enters Maintenance Mode](https://oswatch.example.org/releases/nodejs-24-lts)

**Source:** Open Source Release Watch  |  **Published:** 2026-11-05T08:00Z

> Node.js 24 moved to maintenance LTS status, meaning it will receive only critical bug fixes and security patches until its end-of-life date in April 2028.

## [CSS Color Level 5 Functions Land in Safari 20](https://webstandards.example.net/items/css-color-5-safari-20)

**Source:** Web Standards Weekly  |  **Published:** 2026-11-04T11:00Z

> Safari 20 shipped support for CSS Color Level 5 functions including color-mix() with all interpolation methods and relative color syntax, bringing full cross-browser parity for the new color features.

## [Writing Runbooks That Engineers Actually Read](https://tangent.example.com/posts/runbooks-engineers-read)

**Source:** Tangent Tech Blog  |  **Published:** 2026-11-03T16:00Z

> Keeping runbooks short, test-driven, and co-located with the service code reduced our mean time to recovery by 35% over the following quarter.

