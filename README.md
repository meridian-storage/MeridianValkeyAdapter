<!-- SPDX-License-Identifier: Apache-2.0 -->

# meridian-storage-valkey

`meridian-storage-valkey` is Meridian V1's Valkey adapter for disposable Cache
Catalog data. It provides bounded key-value storage, canonical value envelopes,
mandatory TTLs, exact-key and generation invalidation, single-key atomic
operations, transparent cache-aside coordination, health verification, and
standalone or Sentinel failover profiles.

Valkey is never an authority in this adapter. Eviction, restart, corruption,
and read unavailability all resolve to a cache miss when an authoritative
loader exists. The adapter does not advertise structured, object, evidence, or
streaming behavior and cannot be selected as their fallback.

## Compatibility

| Component | API bounds / verified recipe |
| --- | --- |
| Python | 3.12, 3.13, 3.14 |
| `meridian-storage-core` | >=1.1.0,<2 |
| `meridian-storage-semantics` | >=2.0.1,<3 |
| `valkey` client | >=6.1.1,<7 (verified: 6.1.1) |
| Valkey server | deployment-selected; tested 8.1.9 and 8.1.8 |
| Engine profiles | `valkey-standalone`, `valkey-sentinel` |

The historical validation recipes and predecessor artifact digests are in
[`compatibility.json`](compatibility.json). Install the published distribution
with:

```console
python -m pip install meridian-storage-valkey==1.1.0
```

Meridian discovers `ValkeyAdapterFactory` through the
`meridian_storage.adapters` entry-point group. Platform or Vangu composition
owns the Binding, endpoint or service reference, credentials, ACLs, topology,
memory policy, recovery, and namespace-generation rollout.

Deployment selects exact package and image locks independently. Version tables
are historical evidence, never startup allowlists. API bounds describe consumed
Core SPI, Semantics Cache APIs and valkey-py client APIs; they do not promise
conformance for every admitted release. Startup evidence records observed and
selected releases separately and remains `unverified-by-probe`: real-engine
tests establish the exact verified combinations. See the exhaustive
[gate inventory](docs/release-validation.md).

## Advertised contract

The adapter advertises only the released Cache operations at version `1.0.0`:

| Operation contract | Behavior |
| --- | --- |
| `meridian.cache.get` | Validated hit, miss, or unavailable-as-miss |
| `meridian.cache.put` | TTL-bounded disposable write |
| `meridian.cache.put_if_absent` | Single-key atomic insert |
| `meridian.cache.compare_and_set` | Envelope-version or source-version CAS |
| `meridian.cache.delete` | Exact-key deletion |
| `meridian.cache.invalidate` | One key or a bounded explicit key list |

Bounded multi-get, single-flight `get_or_load`, numeric increment, leases, and
Lua scripts are private adapter coordination primitives. They are not invented
Meridian Catalog operations. Namespace-wide invalidation is a deployment
change: increment `namespaceGeneration` in IaC and roll the Binding; no key scan
is performed.

## Binding settings

Settings are closed and fail on unknown fields. This test-only example omits
real secret values, which must be resolved by the Meridian composition root:

```json
{
  "namespaceGeneration": 1,
  "resources": {
    "cache:example.items": {
      "schemaFingerprint": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "serializerId": "canonical-json",
      "defaultTtlMs": 60000,
      "maximumStalenessMs": 60000,
      "negativeCaching": true,
      "authoritative": false
    }
  },
  "limits": {
    "maxKeyBytes": 512,
    "maxValueBytes": 4194304,
    "maxBatchSize": 128
  },
  "ttl": {
    "defaultTtlMs": 60000,
    "minimumTtlMs": 10,
    "maximumTtlMs": 86400000,
    "negativeTtlMs": 5000
  },
  "singleFlight": {"leaseMs": 5000, "waitMs": 250, "pollMs": 10},
  "memory": {
    "requireMaxmemory": true,
    "allowedEvictionPolicies": ["allkeys-lru"],
    "requirePersistenceDisabled": true
  },
  "topology": {"mode": "standalone", "minimumReplicas": 0},
  "database": 0,
  "seedEndpoints": [],
  "allowInsecureTestProfile": true
}
```

Production Bindings use `valkeys://` with verified server TLS. Plaintext is
accepted only when `allowInsecureTestProfile` is explicitly true. Sentinel
Bindings use a service reference or seed endpoints plus a topology setting such
as `{"mode":"sentinel","minimumReplicas":2,"sentinelMaster":"meridian-cache"}`.

## Safety and consistency

- Physical keys contain digests, not logical keys, tenant values, or Resource
  names. Tenant and scope still participate in the digest.
- Values carry serializer, schema, source version, creation and expiry times,
  payload length and digest, and an envelope version. Non-canonical, stale,
  schema-mismatched, or corrupt entries are deleted best-effort and treated as
  misses.
- A `raw-bytes` Resource carries bytes through serialized Operations as a
  canonical unpadded base64url JSON string. Results include
  `valueEncoding: "base64url"`; internal cache-aside composition may pass bytes
  directly.
- TTL is mandatory and bounded by deployment policy and maximum staleness.
- Adapter-owned scripts have stable SHA-1 identifiers and reload only after
  `NOSCRIPT`; consumer scripts and unbounded scans are rejected by design.
- Multi-key atomic helpers require a shared Valkey hash slot. Public invalidation
  is a bounded sequence of independent exact-key deletes.
- Startup verifies authentication, required commands, selected engine release drift, maxmemory, eviction,
  persistence policy, primary role, replica count, and script permission.
- Telemetry contains event names, counters, and hashed Resource identifiers;
  it never emits keys, values, endpoints, usernames, or credentials.

See [`docs/architecture.md`](docs/architecture.md) for the design boundary,
[`docs/operations.md`](docs/operations.md) for deployment and recovery, and
[`docs/conformance.md`](docs/conformance.md) for deterministic evidence.

## Development

```console
python -m venv .venv
.venv/bin/pip install -e '.[test]'
./scripts/verify.sh
./scripts/test-integration.sh
./scripts/test-failover.sh
```

The integration scripts use disposable Valkey 8.1.9 or 8.1.8 containers. They never
provision production infrastructure. See [`CONTRIBUTING.md`](CONTRIBUTING.md)
and [`SECURITY.md`](SECURITY.md) before submitting a change.

## License

Copyright 2026 Meridian contributors. Licensed under the Apache License,
Version 2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

## Build and release (Jumbo)

This repository is jumbo-managed (Jumbo Build & Versioning Standard,
section 3.5): resolution, builds, and releases run through jumbo, never
ad-hoc pip/uv installs.

```sh
jumbo lock   # resolve internal packages from the JumboIndex, third-party from PyPI
jumbo build  # build + tests at the resolved closure
```

The internal dependencies (`meridian-storage-core`, `meridian-storage-semantics`) are resolved from the JumboIndex;
the lock records the exact promoted build of each. Consumers likewise
resolve this package (`meridian-storage-valkey`) from the JumboIndex. Releases are dispatch-only through `.github/workflows/jumbo-publish.yml`;
as a public package, external publication is driven by the jumbo-computed
version, and every artifact's SHA-256 is recorded in the append-only
JumboIndex.
