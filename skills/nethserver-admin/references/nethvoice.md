# NethVoice safe quick entry

This reference stops at safe NS8 discovery. Activate `nethvoice-admin` before any NethVoice SSH/shell command beyond the discovery below. If that skill is unavailable, stop and report the missing production operations layer; do not reconstruct telephony procedures from memory.

## Safe discovery

Confirm the host/node first, then list only module placement and version fields:

```bash
api-cli run get-cluster-status \
  | jq '{leader, nodes: [.nodes[] | {id, local, online}]}'
api-cli run list-installed-modules \
  | jq '[to_entries[] as $image | $image.value[]? | select(.module == "nethvoice" or .module == "nethvoice-proxy") | {id: .id, module: .module, source: .source, version: .version, node: .node}]'
```

For each exact local module ID, discover action names before inspecting an action or schema:

```bash
api-cli run module/<module_id>/list-actions | jq .
```

NethVoice depends on the proxy assigned to the same node. Each NethVoice host route must ultimately target that node's service-discovery address and the instance's dynamically allocated Asterisk SIP port. The dedicated skill owns the safe method for resolving and verifying this relationship.

After the dedicated skill is active, its allowlist-only `../../nethvoice-admin/scripts/collect_diagnostics.py` is the preferred quick topology check; it compares the discovered route without printing raw contacts, trunks, logs, or database rows.

Do not use this quick entry to print raw contacts/endpoints, call forwards, queue members, trunk patterns, log lines, database values, environment/password files, or customer identifiers. Do not perform DNS/SIP/RTP/TLS probes, test calls, traces, captures, debug toggles, service restarts, configuration, SQL, file edits, or Redis writes without the dedicated skill's preflight and approval gates.

## Voicemail architecture and diagnostic interpretation

Use this background when handing off missing voicemail email attachments to `nethvoice-admin`. It does not expand the discovery commands authorized above. These findings were checked against NethVoice 1.7.7; compare the installed image and runtime configuration with the matching source tag before applying them to another release.

### Separate email delivery from CTI events

- Asterisk generates the voicemail MIME email in the `freepbx` container. Its `mailcmd` setting in `/etc/asterisk/voicemail.conf` invokes `/var/lib/asterisk/bin/send_email`, optionally with `-f` for the sender.
- `send_email` parses the message from standard input, adjusts sender/recipient headers, and submits it through SMTP. In this path it receives the attachment from Asterisk; it does not fetch the recording BLOB to create the attachment.
- The Satellite transcription branch runs only when `SATELLITE_VOICEMAIL_TRANSCRIPTION_ENABLED` equals the string `True`. It reads an existing `audio/x-wav` or `audio/wav` MIME part and can append transcription to the text body. An unset flag leaves that branch inactive.
- `TypeError: dbconn.getVoicemailNewMsg is not a function` in `nethcti-server` indicates a missing JavaScript method in the CTI event path. Check callers and exports in the installed CTI image, but do not attribute missing Asterisk email attachments to this error solely because the timestamps coincide.

### Storage and mailbox configuration

- With `odbcstorage=asteriskcdrdb` and `odbctable=voicemessages`, recordings reside in `asteriskcdrdb.voicemessages.recording`, a `longblob`. Do not assume spool files are the authoritative storage or that an `asterisk.voicemail_users` table exists.
- For an authorized, narrowly scoped recording check, inspect the table schema first. Useful fields include `id`, `mailboxuser`, `duration`, and `recording`; derive only the BLOB byte count and a minimal format signature. A nonempty BLOB beginning with `RIFF` and `WAVE` supports the presence of WAV data, but does not prove full audio integrity or successful retrieval by Asterisk at email-generation time. Avoid extracting audio content.
- Successful CTI listen/download responses establish availability through CTI, not that Asterisk included the recording in the outgoing MIME message.
- Check both global `attach` and the selected mailbox's override. A mailbox can have `attach=no` despite global `attach=yes`. Check `format` and `attachfmt` when investigating format selection; absence of `format` alone is not proof of failure because Asterisk defaults to `wav` in the inspected implementation.
- Mailboxes may be stored directly under `[default]` in `voicemail.conf`. Inspect sections/includes rather than assuming `voicemail_additional.conf` exists. FreePBX's `Voicemail()->getVoicemail()` also exposes mailbox configuration; its raw result can contain secrets.
- Mailbox definitions can use either `extension=password,...` or `extension => password,...`. The comma-separated fields contain the PIN, name, email, pager address, then options such as `attach=yes|delete=no`. Never print the first field or a full mailbox line as a diagnostic identifier. Select the requested mailbox without emitting its definition, then allowlist only the relevant option names and values. Verify a redaction filter against synthetic examples of both separator forms before using it on production data.

### Locate where the attachment disappears

Email delivery plus `attach=yes` does not prove that the attachment was generated or preserved. Within the dedicated skill's data-handling rules, inspect the received message's MIME structure, keeping addresses, message text, and base64 audio out of diagnostic output:

- Look for a top-level `multipart/mixed` content type and matching boundaries, an audio part, and its filename/content disposition. Check for conflicting duplicate `Content-Type` headers.
- If an audio part exists but is not displayed, investigate MIME validity and client interpretation. If it is absent, the received email alone cannot distinguish omission by Asterisk from removal by a relay/filter; evidence from an earlier stage is needed.
- Correlate a bounded Asterisk log interval with the affected message. The absence of attachment-related log lines is inconclusive when the relevant logging level is disabled.

In the inspected 1.7.7 `send_email`, SMTP submission uses `message.as_string().encode('utf-8')`. A local synthetic MIME test preserved the attachment but produced LF-only line endings. Python's `smtplib.sendmail()` normalizes line endings for string input, but leaves byte input unchanged. This is a concrete serialization concern and a possible interoperability issue, **not a confirmed cause of missing attachments**. Establish causality with message evidence or an isolated reproduction before recommending a fix; a received message may already have had its line endings normalized by a relay. SMTP-aware serialization (`send_message()` or an explicit SMTP policy) is a candidate for code review, not an instruction to patch a production container.

Sources:

- [NethVoice 1.7.7 send_email](https://github.com/Nethesis/ns8-nethvoice/blob/1.7.7/freepbx/var/lib/asterisk/bin/send_email)
- [NethVoice 1.7.7 voicemail configuration](https://github.com/Nethesis/ns8-nethvoice/blob/1.7.7/freepbx/etc/asterisk/voicemail.conf)
- [FreePBX REST voicemail configuration access](https://github.com/Nethesis/ns8-nethvoice/blob/1.7.7/freepbx/var/www/html/freepbx/rest/modules/voicemails.php)
- [Asterisk voicemail configuration sample](https://github.com/asterisk/asterisk/blob/master/configs/samples/voicemail.conf.sample)
- [Python SMTP message serialization](https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail)
