<!-- SPDX-License-Identifier: Apache-2.0 -->

# Deployment-owned releases and gate inventory

The adapter owns one package and two profiles: `valkey-standalone` and
`valkey-sentinel`. A direct endpoint, externally owned endpoint, seed endpoint
or service resolver all enter the same factory/probe. Managed provisioning is
owned by Constructs; no provider lifecycle is implemented here. Redis Cluster
is not an advertised topology. Hash-slot checks on private multi-key helpers
remain required and do not advertise general cluster support.

| Surface | Classification and enforcement |
| --- | --- |
| Descriptor `supportedEngineVersions`, exported `SUPPORTED_ENGINE_VERSION(S)`, compatibility recipes | Historical tested-release metadata only; no membership predicate. Core >=1.1 preserves closed profile identity without a release gate. |
| Package dependencies | Core V1 SPI >=1.1,<2; Semantics Cache expression/normalization >=2.0.1,<3; synchronous Valkey/Sentinel client APIs >=6.1.1,<7. These are API compatibility bounds, not a tested-release list. Untested installations remain unverified. |
| requirements.lock, CI image digests | Exact reproducible test/build selections. Installation uses normal dependency resolution plus hash verification and pip check; deployments choose their own locks. |
| Factory/config/client (standalone, Sentinel, seeds, resolver) | Closed adapter contract and profile/topology; bounded settings; authenticated identity, database, TLS/trust and explicit insecure test opt-in. |
| Probe commands and scripts | Authenticated PING/INFO/CONFIG; required COMMAND INFO entries; SCRIPT LOAD and owned digest/EXISTS checks. Real CAS/lease/PIFA tests prove behavior beyond declarations. Missing commands, denied ACLs, malformed protocol or script drift fail. |
| Memory/persistence/topology | Bounded maxmemory, allowed eviction, persistence policy, writable primary and minimum replicas remain provider/deployment constraints. |
| Runtime startup/reprobe | Observed release must equal deployment-selected Binding version; canonical capability fingerprint must match the selected configuration and remain stable after startup. This is deployment drift, never a compiled baseline. |
| Cache, key, codec, atomic helpers | Disposable-only Resources, Schema fingerprints, namespace generation, scoped digests, envelope format/digest, TTL bounds, same-slot atomic keys and bounded batch sizes remain semantic checks. |
| Public and private cache helpers | Cache Catalog contracts remain 1.0.0. Internal multi-get/increment/get-or-load cannot invent Catalogs, commands, authoritative behavior or release gates. |
| Physical verification | Non-Cache/authoritative placement and Schema drift still fail. No sibling repository source or new ownership. |

The wire formats remain V1: no field was reinterpreted or removed. The driver
identity is now `valkey-py`, independent of the installed client distribution.
The health-probe declaration and corrected Lua script digests change canonical
capability fingerprints; regenerate deployment capability pins explicitly.
Old pins fail closed. Key and envelope golden bytes are unchanged. Probe
`selectedEngineVersion` comes from the Binding (or `unavailable` for a direct
probe), and `observedEngineVersion` only from authenticated server INFO. Missing
or malformed observed metadata fails honestly; configured values are not used
as substitute observations. `releaseConformance=unverified-by-probe` explicitly
separates successful feature discovery from real conformance evidence.

## Verification recipes

`compatibility.json` holds exact public dependency hashes and both Valkey image
manifest digests; `requirements.lock` holds the full Python validation closure.
CI varies 8.1.9 and historically unlisted 8.1.8 independently of the package
selection, on both standalone and one-primary/two-replica/three-Sentinel
profiles. Synthetic `999.0.0-unverified` tests prove only metadata gate behavior.
No future release or untested provider is claimed conformant.

Run `./scripts/verify.sh`, then both `./scripts/test-integration.sh` and
`./scripts/test-failover.sh` for each selected image. Set
`MERIDIAN_VALKEY_VERSION` and `MERIDIAN_VALKEY_IMAGE` to the corresponding exact
recipe. The required scripts provision disposable engines; missing required
test infrastructure is a failure, never substitute acceptance by a skipped
suite. Release CI reruns both engine selections and publishes the merged
commit's artifacts, exact hashes and provenance.
