# Sensitive-data handling

Apply this reference before retrieving, storing, transmitting, or quoting NethVoice evidence. Production telephony data can identify people and reveal communications even when it is not a password.

## Data classes and default handling

| Data | Examples | Default |
| --- | --- | --- |
| Secrets | SIP/LDAP/database passwords, API/JWT tokens, provisioning URL tokens, private keys, integration credentials, subscription identifiers | Never print or include; report presence/validity only |
| Communications content | Audio, recordings, voicemail, packet payloads, transcripts, summaries | Do not collect without explicit purpose, approval, owner, retention, and deletion plan |
| Communications metadata | Caller/callee/contact URIs, extensions, CDR/CEL, unique/linked IDs, call forwards, queue membership, trunk patterns | Aggregate first; use opaque labels and narrow time filters |
| Customer identifiers | Names, domains tied to people/tenants, email, MAC/IP/device/user IDs, customer cards | Minimize and pseudonymize; retain infrastructure FQDN/IP only when topology verification requires it |
| Operational evidence | Unit/container state, versions, restart counts, aggregate health, certificate state, route shape | Preferred, but still scope to the incident |

## Collection rules

- Ask for the symptom and decision the evidence must support. Do not collect “everything.”
- Filter at the source. Prefer counts, booleans, status classes, hashes, and bounded timestamps over raw rows or command dumps.
- Never output full environment/password files, verbose authenticated requests, raw Asterisk contacts/endpoints, call-forward databases, queue rosters, trunk rules, logs, database rows, CDR/CEL, recordings, transcripts, or packet captures.
- Check that a “read-only” module action does not return secrets or integration values before invoking it. Whitelist output fields; do not rely on blacklisting key names after dumping the payload.
- Silence/capture command stderr when it can contain credentials or customer data. Convert failures to fixed stage/error codes; never attach raw stderr automatically.
- Do not put secrets in command arguments, shell history, process listings, filenames, URLs, incident titles, chat, or audit descriptions. Use protected stdin/files or the supported secret field mechanism when an approved action requires them.

## Logs and databases

Use a bounded incident window, component filter, maximum row count, and high-signal pattern. Redact authorization headers, URIs/user parts, phone numbers, IP/MAC/email/user IDs, unique call IDs, message bodies, and database values before sharing. If redaction could destroy the evidence, keep the original only in an approved restricted location and share a sanitized derivative with a hash linkage.

Database access starts with schema/version proof and aggregate queries. Do not enumerate users, devices, contacts, call forwards, queues, trunks, or calls simply because SQL is available. Never expose passwords through process arguments or expand them into stdout/stderr.

## Captures, recordings, and transcripts

SIP traces and packet captures can include credentials, numbers, SDP addresses, and message bodies; RTP capture can reconstruct audio. Require explicit approval for interfaces, endpoint/port filter, start/stop time, maximum size, encryption, authorized viewers, transfer path, retention, and deletion verification. Disable debug/tracing and prove it is off when finished.

Recordings and transcripts require the same controls as communications content. Do not copy them into the repository or a general support bundle. Validate existence, size/hash, state, and timestamps when content is unnecessary.

## Incident-report redaction

Use stable opaque labels such as `extension-A`, `trunk-1`, and `call-1`. Include exact module IDs and infrastructure route addresses only when needed to reproduce the topology. Represent secret fields as `configured`, `missing`, `invalid`, or `not checked`; never preserve prefixes/suffixes. Before finalizing, search the report/artifacts for known canaries, tokens, authorization headers, phone/email patterns, provisioning paths, and private-key markers.

If sensitive output reaches an unsafe channel, stop collection, do not repeat it, tell the user what category escaped, follow their incident-handling policy, and rotate/revoke credentials when applicable.
