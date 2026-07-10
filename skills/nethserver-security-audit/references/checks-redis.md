# Checks — Redis privilege boundary (`redis-privilege`)

Scope: Python `agent` package usage and any code touching Redis in core and
modules. Redis is the state store and the primary privilege boundary in NS8.

## R1. Unnecessary privileged connection
`agent.redis_connect(privileged=True)` grants a broad ACL (cluster-wide
read/write). A script that only needs its own module keys but connects
privileged expands blast radius.
- For each `privileged=True`, confirm the script genuinely needs cluster-level
  access. Unjustified = medium; privileged connection in a path reachable by
  unvalidated input (see checks-action-input) = high/critical.
- verify_hint: static-only (ACL is enforced server-side); confirm the code path
  and the ACL granted to the module user.

## R2. Attacker-influenced Redis keys/values
Input from stdin/event flowing into `hset`/`hget`/`AGENT_COMMAND` key names or
into published task payloads. Key injection can read/write unintended keys;
command injection into `AGENT_COMMAND` can enqueue arbitrary agent tasks.
- Severity: critical if input reaches `AGENT_COMMAND` / task enqueue on a
  privileged agent; high for arbitrary key read/write.
- verify_hint: on a test node, send a crafted key fragment and inspect whether
  it lands outside the module namespace (read-only inspection via `runagent`
  `redis-cli --scan`).

## R3. Secret exposure through Redis
Secrets stored in Redis (`module/<id>/secrets`, cluster credentials) read into
task output, logs, or returned over the API. Combined with A1 (GET bypass),
a secret in a GET-reachable key is exposed to any user.
- Severity: high/critical depending on the secret and reachability.
- verify_hint: as a low-priv user, attempt to read the key via the API/GET
  route; expect denial.

## R4. Missing ACL scoping for module users
Module actions should run with a Redis user scoped to the module's namespace.
Check that a module does not require or assume broader ACLs than granted, and
that privileged operations are funneled through the cluster agent rather than a
module connecting privileged directly.
- Severity: medium-high.
- verify_hint: `runagent -m <module_id>` then a scoped `redis-cli` command that
  should fail (attempt to read another module's key), expect permission error.

## R5. Cleartext secrets at rest
Secrets stored unencrypted where encryption/hashing is expected (e.g. storing a
reversible password when a hash suffices). Note NS8 commonly stores service
credentials in cleartext by design for service startup — flag only where a hash
or secret-manager reference is the correct pattern.
- Severity: medium; info if it matches accepted NS8 design.
