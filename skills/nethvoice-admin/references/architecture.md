# NethVoice production architecture

Use this reference to build the topology and decide whether a service state is abnormal. Confirm every detail against the installed version before acting.

## Node-local topology

NethVoice is a multi-container rootless NS8 module. Its telephony core is FreePBX/Asterisk with MariaDB; current releases also include the NethCTI client, server and middleware, Janus, Tancredi, phonebook, reports, and feature-dependent Satellite services.

NethVoice Proxy is a separate rootless module containing Kamailio, RTPengine, PostgreSQL, and Redis. The supported deployment relationship is node-local: each NethVoice instance uses the proxy assigned to its own NS8 node. Do not pair a NethVoice instance with a convenient proxy on another node.

For each local NethVoice instance, construct and verify this mapping from installed/runtime data:

```text
NETHVOICE_HOST -> sip:<node address selected by service discovery>:<ASTERISK_SIP_PORT>
```

The node address is not automatically the public, primary LAN, or first interface address. Resolve the installed proxy service provider and the NethVoice runtime proxy address (for current versions, `PROXY_IP`), confirm that it belongs to the hosting node, and compare it with the proxy's domain route. `ASTERISK_SIP_PORT` is allocated per instance. Never substitute `5060` or a remembered port.

Check every NethVoice domain, every destination attached to it, duplicate destinations, and proxy routes that have no matching local installed instance. An unmatched route is evidence of a potentially stale persistent route, not permission to remove it.

## Dependency path

Use failure boundaries in this order:

```text
phone/trunk/browser
  -> DNS, firewall, NAT and certificate
  -> node-local NethVoice Proxy (Kamailio -> RTPengine; PostgreSQL/Redis state)
  -> dynamic Asterisk SIP/RTP/WSS ports
  -> FreePBX/Asterisk and MariaDB
  -> CTI/Janus/Tancredi/phonebook/reports/Satellite feature layer
  -> LDAP and approved external integrations
```

HTTP(S) routes for the administration UI, CTI UI/API/WebSocket, Janus transport, and Tancredi/provisioning are created by the module and terminated through the node's Traefik. SIP/TLS certificate material is distributed from the node certificate service into relevant containers. Certificates are node-scoped; a restored module or a module moved to another node must reacquire or reassign certificates.

## Ports and routing

- Discover the installed `get-ports-list` action and its output schema when present. Cross-check the NS8 firewall state and installed unit/container arguments.
- Proxy documentation currently describes SIP on TCP/UDP 5060-5061 and proxy RTP on UDP 10000-20000, but installed configuration is authoritative.
- NethVoice allocates per-instance SIP, SIPS, IAX, WSS, SFTP, Asterisk RTP, CTI TLS, phonebook LDAPS, and Janus RTP ports/ranges. Never copy values between instances.
- Kamailio owns the public proxy SIP entry point. Asterisk normally listens on its allocated instance port, not the proxy's public 5060/5061.
- A correct signaling route does not prove RTP correctness. Validate advertised/private/public addresses, local-network classification, RTP ranges, and the media component separately.

## Service-state expectations

Discover installed units first. The table is interpretation guidance, not a service-name command list.

| Layer | Normal expectation after full configuration | Conditions |
| --- | --- | --- |
| MariaDB and FreePBX/Asterisk | Running | Core telephony dependency |
| Kamailio, RTPengine, proxy PostgreSQL/Redis | Running | Required for the configured node-local proxy |
| NethCTI UI, Janus, Tancredi, phonebook, reports | Normally running | Confirm installed version, entitlement, and configured feature |
| NethCTI server and middleware | May be inactive before the NethVoice wizard reaches its completion gate | Do not restart-loop or label failed solely because inactive |
| Satellite application and MQTT | Feature-dependent | Expected inactive/absent when transcription features are disabled |
| Satellite PostgreSQL | Retained after Satellite initialization, including when transcription is later disabled | Middleware and users can require historical transcript data; do not stop it solely because current feature flags are off |
| Satellite recordings cleanup service/timer | Timer-driven oneshot | The timer should drive cleanup when configured; the service is normally inactive between runs, so assess its timer and last result |
| NethHotel alarm units | Feature-dependent | Expected inactive when NethHotel is disabled |
| Update/cleanup/timer-triggered and certificate units | Often oneshot, timer-driven, or active/exited | Judge by unit type, last result, timer/path trigger, and installed source |

An inactive conditional unit is not an incident by itself. A loaded failed unit, rising restart count, unhealthy container, or mismatch between feature flags and runtime state is evidence requiring correlation with a bounded time window.

## Authoring source ledger

Snapshot used to write version-aware guidance on 2026-09-04:

- `nethesis/ns8-nethvoice`: `1dc8879a1ee655eededf0cfff13f6c750263ec6f`
- `nethesis/ns8-nethvoice-proxy`: `ae79166d55fb3e8651dc937fe1419e23bc3b8c8c`
- Installed-version cross-checks: NethVoice tag `1.7.7` at `d8c5068e2d8dc40fa127511a295585c49b8522e2`; proxy tag `1.7.0` at `ffa362e7d94c77c07b29cf7c30d186bc2c7e7317`
- The `nethvoice-testing` skill at the recorded NethVoice revision was consulted as an authoring input only; it is not a runtime dependency.
- `NethServer/nethvoice-docs`: `dd555feb3cc6fdfbaf8346b9c366b6792148310c`
- `NethServer/ns8-docs`: `b5a86a855d00af3078239edc428ca678ceb6b0f9`

These revisions explain the guidance; they never override installed actions, schemas, source, or runtime state.

Primary upstreams: [ns8-nethvoice](https://github.com/nethesis/ns8-nethvoice), [ns8-nethvoice-proxy](https://github.com/nethesis/ns8-nethvoice-proxy), [NethVoice administrator manual](https://docs.nethvoice.com/docs/administrator-manual), and [NS8 administrator manual](https://docs.nethserver.org/docs/administrator-manual).
