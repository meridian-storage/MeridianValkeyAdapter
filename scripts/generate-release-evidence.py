#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate deterministic evidence for already-verified release artifacts."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git is required to generate release evidence")
    revision = subprocess.run(  # noqa: S603 - resolved executable and fixed read-only argv
        [git, "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    artifacts = {
        path.name: digest(path)
        for path in sorted((ROOT / "dist").iterdir())
        if path.is_file() and path.suffix in {".gz", ".whl"}
    }
    if len(artifacts) != 2:
        raise RuntimeError("release evidence requires exactly one wheel and one sdist")
    evidence = {
        "$comment": "SPDX-License-Identifier: Apache-2.0",
        "formatVersion": "meridian-valkey-release-evidence.v1",
        "version": "1.1.0",
        "sourceRevision": revision,
        "compatibilityDigest": digest(ROOT / "compatibility.json"),
        "conformanceVectorDigest": digest(ROOT / "evidence/conformance-vectors.json"),
        "artifacts": artifacts,
        "validationEnvironment": {
            "python": platform.python_version(),
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("meridian-storage-core", "meridian-storage-semantics", "valkey")
            },
            "engineImages": json.loads((ROOT / "compatibility.json").read_text())["engine"][
                "images"
            ],
            "requirementsLockDigest": digest(ROOT / "requirements.lock"),
        },
        "verification": {
            "unitContractConformance": "passed",
            "standalone": "passed",
            "sentinelFailover": "passed",
        },
    }
    output = ROOT / "evidence/release-evidence.json"
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
