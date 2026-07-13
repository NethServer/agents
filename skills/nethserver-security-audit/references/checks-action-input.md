# Checks — action & event input (`action-input`)

Scope: action step scripts and event handlers (Python/Bash) in both core and
modules. Input arrives as JSON on stdin (actions) or as an event payload.

## I1. Missing input validation schema
An action directory with no `validate-input.json` accepts **arbitrary
unvalidated JSON** on stdin. Every field the script reads is attacker-influenced
(reachable via `api-cli run [module/<id>/]<action> --data '{...}'`).
- Every action lacking `validate-input.json` = at least a finding; severity
  scales with what the script does with the input (see I2/I3).
- verify_hint: `api-cli run <action> --data '{"unexpected":"value"}'` and
  observe whether it is rejected pre-execution.

## I2. Command / shell injection sinks
Trace stdin fields to execution sinks:
- Python: `subprocess.*(..., shell=True)`, `os.system`, `os.popen`, f-strings
  built into a shell command, `agent.run_helper(...)` with interpolated input.
- Bash: unquoted `"$VAR"` in a command, `eval`, `$(...)` with input, values
  passed to `podman`/`systemctl`/`rsync` unsanitized.
- A field flowing into any of these without validation/quoting = high or
  critical (critical if the action runs privileged / as root agent).
- verify_hint: send a benign injection marker in the field (e.g. a value that
  would create a harmless side effect) — **only on a live TEST node, read-only
  intent**; otherwise static-only.

## I3. Path traversal / file write
Stdin fields used as filenames, volume paths, or Redis keys without
canonicalization. `../` traversal, absolute-path override, or key injection
into Redis.
- Severity: high if it writes outside the module boundary.
- verify_hint: `api-cli run <action> --data '{"path":"../../etc/x"}'` on a test
  node, expect rejection.

## I4. Output validation & leakage
Missing `validate-output.json`, or scripts that dump internal state/secrets to
stdout. Task output is stored in Redis and readable via the API — treat stdout
as semi-public. Diagnostics must go to stderr (`echo ... >&2`).
- Severity: medium if secrets reach stdout; low for noisy stdout.

## I5. Event payload trust
Event handlers consume payloads produced by other modules/cluster. Apply I1-I3
to event inputs too; a compromised or buggy publisher can feed hostile
payloads.
- Severity: matches the sink reached.

## I6. Numeric / type confusion
JSON Schema present but too loose (e.g. `type: string` with no pattern/enum
where a constrained value is required; missing `additionalProperties: false`).
`additionalProperties` not set to false lets attackers add fields the script
may read.
- Severity: medium; high if a smuggled field reaches a sink.
