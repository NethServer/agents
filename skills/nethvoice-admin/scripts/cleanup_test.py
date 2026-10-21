#!/usr/bin/env python3
"""Recover only explicitly owned SIP test resources after controller/node failure."""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile

from sip_endpoint import TestError, protected_json, remove_owned_container, write_private, rpc
from queue_test import PBX


def recover_fixture(manifest, pbx):
    config = protected_json(manifest)
    if config.get("target_host") != socket.getfqdn() or config.get("module") != os.environ.get("MODULE_ID"):
        raise TestError("saved fixture target mismatch")
    if not re.fullmatch(r"nvtest-[a-f0-9]{12}", config.get("owner", "")):
        raise TestError("invalid fixture owner")
    extensions = config["extensions"]
    if len(extensions) != 3 or not all(re.fullmatch(r"[0-9]{4,10}", ext) for ext in extensions):
        raise TestError("invalid fixture extensions")
    errors = []
    workdir = Path(manifest).resolve().parent
    ownership = pbx.fixture("verify", config)  # Prove ownership before call-affecting actions.
    owned_extensions = ownership["owned_extensions"]
    for label, name in config.get("clients", {}).items():
        if label not in ("caller", "A", "B"):
            raise TestError("invalid fixture endpoint")
        try:
            remove_owned_container(name, label)
        except (TestError, OSError, subprocess.TimeoutExpired):
            errors.append("client-" + label)
        (workdir / label / "pjsua.conf").unlink(missing_ok=True)
        try:
            (workdir / label).rmdir()
        except FileNotFoundError:
            pass
        except OSError:
            errors.append("directory-" + label)
    # Hang up only channels whose names exactly belong to the controlled extensions.
    channels = pbx.cli("core show channels concise")
    for line in channels.splitlines():
        name = line.split("!", 1)[0]
        if any(re.fullmatch(r"(?:PJSIP/" + ext + r"-[a-fA-F0-9]+|Local/" + ext + r"@[^ !]+)", name)
               for ext in owned_extensions):
            pbx.cli("channel request hangup " + name)
    if errors:
        raise TestError("client recovery incomplete: " + ", ".join(errors))
    pbx.fixture("delete", config)  # Adapter independently verifies owner markers.
    pbx.reload()
    if pbx.fixture("inspect", config)["occupied"]:
        raise TestError("fixture removal incomplete")
    channels = pbx.cli("core show channels concise")
    if any(re.search(r"(?:PJSIP/|Local/)" + ext + r"[-@/]", channels) for ext in extensions):
        raise TestError("test channels still present")
    Path(manifest).unlink()


def recover_endpoint(state_path):
    state = protected_json(state_path)
    if state.get("target_host") != socket.getfqdn() or state.get("module") != os.environ.get("MODULE_ID"):
        raise TestError("saved endpoint target mismatch")
    try:
        rpc(state, "status")
    except (ConnectionError, OSError):
        pass
    else:
        raise TestError("controller is alive; use normal stop")
    directory = Path(state["workdir"])
    if directory.parent.resolve() != Path(tempfile.gettempdir()).resolve() or not re.fullmatch(r"nvtest-endpoint-[A-Za-z0-9_-]+", directory.name):
        raise TestError("invalid endpoint recovery directory")
    remove_owned_container(state["container"], "endpoint")
    (directory / "endpoint" / "pjsua.conf").unlink(missing_ok=True)
    for path in (directory / "endpoint", directory):
        try:
            path.rmdir()
        except FileNotFoundError:
            pass
    Path(state_path).unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorized-test", action="store_true", required=True)
    parser.add_argument("--expected-host", required=True)
    parser.add_argument("--module", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest")
    group.add_argument("--endpoint-state")
    parser.add_argument("--fixture-adapter")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    os.umask(0o077)
    if args.expected_host != socket.getfqdn() or args.module != os.environ.get("MODULE_ID"):
        parser.error("host/module identity mismatch")
    result = dict(name="recovery", expected="owned resources removed", evidence={})
    try:
        if args.manifest:
            recover_fixture(args.manifest, PBX(adapter=args.fixture_adapter))
        else:
            recover_endpoint(args.endpoint_state)
        result.update(status="PASS", actual="owned resources removed; independently verify SIP contact expiry")
    except Exception:
        result.update(status="FAIL", actual="recovery incomplete; protected manifest/state retained")
    write_private(args.report, result)
    print(json.dumps(result))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
