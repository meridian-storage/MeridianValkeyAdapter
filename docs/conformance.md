<!-- SPDX-License-Identifier: Apache-2.0 -->

# Conformance evidence

The committed vectors in `evidence/conformance-vectors.json` cover deterministic
key encoding, envelope framing, serializer/schema validation, TTL/staleness,
negative caching, generation invalidation, single flight, PIFA/CAS, shared hash
slots, corruption cleanup, unavailable-as-miss, redaction, descriptor denial,
and packaging metadata.

`./scripts/verify.sh` runs unit, contract, conformance, packaging, lint, typing,
security, SPDX, lockfile, and reproducible-build checks. The standalone script
runs the same Cache contract against a real Valkey 8.1.9 or 8.1.8 primary with persistence
off and bounded eviction. The failover script runs Sentinel with one primary,
two replicas, and three Sentinels, stops the original primary, waits for quorum
promotion, and verifies writes/reads through the existing adapter runtime.

`evidence/release-evidence.json` is generated for a release commit and contains
the source revision, test summary, environment/profile versions, conformance
vector digest, and distribution digests. It is not embedded back into the
distribution it describes.

Both real profiles additionally run eight-way put-if-absent and CAS races,
single-flight stampede coordination, TTL expiry, and authority/Schema rejection.
Sentinel repeats those operations after promotion through the same runtime.
All four local profiles passed on Python 3.12.11 with public Core 1.1.0,
Semantics 2.0.1 and valkey-py 6.1.1. Quality validation passed 96 tests plus
3 packaging tests, 90.71% coverage, typing/lint/security/audit and deterministic
rebuilds. Exact image and dependency hashes are in `compatibility.json`; release
CI repeats these recipes and attaches merged-source provenance. No skipped test
is used as required acceptance.
