---
name: nethvoice-release
description: Use when the user asks to release a NethVoice milestone, or to release ns8-nethvoice, ns8-nethvoice-proxy or NethLink together, close the issues of a NethVoice milestone, or clean up NethVoice testing releases.
---

# NethVoice release

A NethVoice milestone ships up to three components, each in its own repository:

| Component | Repository | Released with |
| --- | --- | --- |
| NethVoice module | `nethesis/ns8-nethvoice` | `gh ns8 module-release` |
| NethVoice Proxy module | `nethesis/ns8-nethvoice-proxy` | `gh ns8 module-release` |
| NethLink desktop app | `NethServer/nethlink` | `npm run publish:<level>` |

The issues live in `NethServer/dev`, with the `nethvoice` label and the `NethVoice X.Y`
milestone. The board is NethServer project 11, view 7, sliced by milestone.

This skill adds the NethVoice coordination on top of `nethserver-release`. Load
`nethserver-release` too: its approval, versioning and semver rules apply unchanged.

## Rules that always apply

1. **Explicit approval for each publish.** Creating a stable release, publishing a draft,
   pushing a NethLink version tag, closing issues and deleting releases are all public.
   Show the exact version, target commit and repository, then wait for an explicit "yes"
   to that step. Approval for one component does not cover the others.
2. **Draft first.** Create stable releases with `--draft`, review the notes with the user,
   then publish. A draft creates no tag and triggers no workflow.
3. **Pin the commit.** Release the commit that was tested (`--release-refs <sha>`), and
   check that its image build succeeded first. `main` keeps moving: Renovate merges and
   direct pushes can land while issues are being verified.
4. **Never delete tags.** Testing cleanup deletes GitHub releases only. In
   `ns8-nethvoice` and `ns8-nethvoice-proxy`, `clean-registry.yml` deletes the ghcr images
   of any deleted ref, so deleting a tag also deletes its images.
5. **Leave unfinished issues alone.** Issues that are not `verified` stay open in the
   milestone for the next patch release. Do not move or close them unless the user asks.

## Order of operations

1. Survey the milestone and agree the scope with the user: `references/milestone-and-issues.md`.
2. Freeze: wait for the last verifications, merge only what the user includes, and record
   the commit to release for each repository.
3. Release the proxy, then NethVoice: `references/ns8-modules.md`.
4. Release NethLink, or leave it as a pre-release if the user says so: `references/nethlink.md`.
5. Close the issues with the release comments: `references/milestone-and-issues.md`.
6. Clean up the testing releases and check the next testing cycle: `references/ns8-modules.md`
   and `references/nethlink.md`.
7. Make sure the documentation PRs of the milestone (`NethServer/nethvoice-docs`) are merged.

## Reference map

| Task | Read |
| --- | --- |
| Milestone survey, scope decisions, issue comments and closing, mixed-component issues | `references/milestone-and-issues.md` |
| ns8-nethvoice and proxy: testing flow, stable release, release notes, images, cleanup, new minor | `references/ns8-modules.md` |
| NethLink: `npm run publish`, release workflow, pre-release, winget, cleanup, compatibility test | `references/nethlink.md` |
