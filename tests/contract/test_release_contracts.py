# SPDX-License-Identifier: Apache-2.0
"""Release provenance must not substitute for feature or deployment checks."""

import json
from dataclasses import replace

import pytest
from meridian_storage.errors import CompatibilityError
from meridian_storage.runtime.config import BindingConfig
from valkey.exceptions import NoPermissionError

from meridian_storage.adapters.valkey import ValkeyAdapterFactory
from meridian_storage.adapters.valkey.configuration import ValkeySettings
from meridian_storage.adapters.valkey.descriptor import capability_manifest
from meridian_storage.adapters.valkey.probe import REQUIRED_COMMANDS, ValkeyProbe
from tests.conftest import fake_builder, make_context, settings_mapping
from tests.fakes import FakeValkey


@pytest.mark.parametrize("sentinel", [False, True])
@pytest.mark.parametrize("release", ["8.1.8", "999.0.0-unverified"])
def test_unlisted_selected_release_keeps_contract_and_fingerprint_checks(sentinel, release):
    client = FakeValkey()
    client.engine_version = release
    client.replicas = 2 if sentinel else 0
    context = make_context(client, sentinel=sentinel, engine_version=release)
    runtime = ValkeyAdapterFactory(client_builder=fake_builder(client)).create(context)
    runtime.open()
    probe = runtime.probe()
    assert probe.evidence["observedEngineVersion"] == release
    assert probe.evidence["selectedEngineVersion"] == release
    assert probe.evidence["releaseConformance"] == "unverified-by-probe"
    serialized = json.loads(json.dumps(context.binding.to_dict(), sort_keys=True))
    assert BindingConfig.from_mapping(serialized, "binding").to_dict() == context.binding.to_dict()
    client.engine_version = "changed-after-startup"
    with pytest.raises(CompatibilityError, match="changed after startup"):
        runtime.probe()


@pytest.mark.parametrize("command", REQUIRED_COMMANDS)
def test_missing_required_command_fails_even_on_historical_release(command):
    class MissingCommand(FakeValkey):
        def execute_command(self, *args, **kwargs):
            result = super().execute_command(*args, **kwargs)
            result[REQUIRED_COMMANDS.index(command)] = None
            return result

    client = MissingCommand()
    with pytest.raises(CompatibilityError, match="required command"):
        ValkeyAdapterFactory(client_builder=fake_builder(client)).create(
            make_context(client)
        ).open()


@pytest.mark.parametrize("response", [None, [], b"OK", [[b"wrong", 1]] * len(REQUIRED_COMMANDS)])
def test_malformed_command_protocol_fails(response):
    class Malformed(FakeValkey):
        def execute_command(self, *args, **kwargs):
            return response

    client = Malformed()
    with pytest.raises(CompatibilityError, match="response"):
        ValkeyAdapterFactory(client_builder=fake_builder(client)).create(
            make_context(client)
        ).open()


def test_script_digest_and_permission_fail_closed():
    class WrongDigest(FakeValkey):
        def script_load(self, script):
            return "0" * 40

    class Denied(FakeValkey):
        def script_load(self, script):
            raise NoPermissionError("private credential must not appear")

    for client in (WrongDigest(), Denied()):
        with pytest.raises(Exception) as exc:
            ValkeyAdapterFactory(client_builder=fake_builder(client)).create(
                make_context(client)
            ).open()
        assert "private credential" not in str(exc.value)


def test_release_change_changes_deployment_fingerprint_without_feature_claim():
    settings = ValkeySettings.from_mapping(settings_mapping())
    assert (
        capability_manifest("8.1.8", settings).fingerprint
        != capability_manifest("8.1.9", settings).fingerprint
    )
    client = FakeValkey()
    context = make_context(client)
    context = replace(
        context,
        binding=replace(context.binding, required_capability_fingerprint="sha256:" + "0" * 64),
    )
    with pytest.raises(CompatibilityError, match="fingerprint"):
        ValkeyAdapterFactory(client_builder=fake_builder(client)).create(context).open()


def test_direct_probe_does_not_invent_selected_provenance():
    probe = ValkeyProbe(
        FakeValkey(), ValkeySettings.from_mapping(settings_mapping()), tls_mode="disabled"
    ).probe()
    assert probe.evidence["selectedEngineVersion"] == "unavailable"
