<!-- SPDX-License-Identifier: Apache-2.0 -->

# Changelog

All notable changes use semantic versioning.

## 1.1.0 - 2026-09-08

- Separate deployment-selected releases from historical conformance recipes;
  consume public Core 1.1 and Semantics 2 APIs with compatible package bounds.
- Probe required commands and verify loaded script digests while retaining
  auth/TLS, namespace, topology, memory/eviction, TTL and deployment drift gates.
- Fix adapter-owned Lua to use the Valkey server's `redis.call` API, exposed by
  real-engine CAS contention; refresh script digests and capability fixtures.
- Exercise standalone and Sentinel 8.1.9/8.1.8 with real PIFA/CAS races,
  stampede coordination, TTL expiry, authority rejection, eviction and failover.

## 1.0.0 - 2026-08-26

- Implement the Meridian Cache Catalog Valkey adapter against Core and
  Semantics 1.0.0.
- Add canonical JSON and raw-byte envelopes, TTL and staleness enforcement,
  exact-key and namespace-generation invalidation, cache-aside single flight,
  PIFA, CAS, and Schema-declared numeric increment helpers.
- Add authenticated standalone and Sentinel profiles, startup/physical probes,
  safe degradation, redacted errors and telemetry, conformance vectors, and
  real Valkey 8.1.9 standalone/failover tests.
- Add Apache-2.0 packaging, deterministic build verification, CI, and release
  provenance.
