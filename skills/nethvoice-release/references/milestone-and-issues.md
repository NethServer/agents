# Milestone survey and issue closing

## Survey the milestone

List every NethVoice issue of the milestone, open and closed, with its labels:

```bash
gh issue list -R NethServer/dev --label nethvoice --milestone "NethVoice 1.8" \
  --state all --limit 200 --json number,title,state,labels \
  -q '.[] | "\(.number)\t\(.state)\t\([.labels[].name]|join(","))\t\(.title)"'
```

Also check whether the milestone holds issues without the `nethvoice` label:

```bash
gh issue list -R NethServer/dev --milestone "NethVoice 1.8" --state open --limit 200 \
  --json number,labels -q '[.[] | select([.labels[].name] | index("nethvoice") | not) | .number]'
```

Group the open issues for the user:

| Group | Meaning | Action |
| --- | --- | --- |
| `verified` | QA passed | Closed after the release |
| `testing` | Under QA | Ask: wait for it, or leave it for the next release |
| No status label | Not ready | Leave it open for the next patch release |

For each `testing` issue, check whether its PRs are merged. A merged PR ships with the
release even if the issue is not verified, so the user must decide before the freeze.
Find the PRs of an issue from its cross-references:

```bash
gh api graphql -f query='{repository(owner:"NethServer",name:"dev"){issue(number:8190){
  timelineItems(itemTypes:[CROSS_REFERENCED_EVENT],first:50){nodes{... on CrossReferencedEvent{
  source{... on PullRequest{repository{nameWithOwner} number state}}}}}}}}' \
  -q '.data.repository.issue.timelineItems.nodes[].source | select(.number)
      | "\(.repository.nameWithOwner)#\(.number) \(.state)"'
```

The cross-references also show which component each issue touches. Record it, because it
decides the closing comment:

- PRs in `nethesis/ns8-nethvoice`, `nethesis/nethcti-server`, `nethesis/nethvoice-cti`,
  `nethesis/phone-island` → NethVoice. The CTI, its server and phone-island ship inside
  the ns8-nethvoice images.
- PRs in `nethesis/ns8-nethvoice-proxy` → NethVoice Proxy.
- PRs in `NethServer/nethlink` → NethLink. phone-island also ships inside NethLink.

## Closing comments

Use the same one-line format as `gh ns8 module-release comment`, one line per component
that contains the fix:

```text
Release `nethesis/ns8-nethvoice` [1.8.0](https://github.com/nethesis/ns8-nethvoice/releases/tag/1.8.0)
Release `nethesis/ns8-nethvoice-proxy` [1.8.0](https://github.com/nethesis/ns8-nethvoice-proxy/releases/tag/1.8.0)
Release `NethServer/nethlink` [v1.6.0](https://github.com/NethServer/nethlink/releases/tag/v1.6.0)
```

- Close an issue only when **every** component it touches is released. For an issue that
  touches the proxy and NethVoice, add the proxy line when the proxy is released and
  close the issue after NethVoice, with a comment that carries only the NethVoice line.
- An issue fixed only in NethLink gets only the NethLink line.
- Write one comment per issue, even when it lists several components.

`gh ns8 module-release comment` comments only the issues linked from the PR bodies, and
many PRs do not link their issue. Comment and close from the list of `verified` issues of
the milestone instead, and do not also run `comment`, or the issues get two comments.

```bash
NV='Release `nethesis/ns8-nethvoice` [1.8.0](https://github.com/nethesis/ns8-nethvoice/releases/tag/1.8.0)'
gh issue list -R NethServer/dev --label nethvoice --label verified \
  --milestone "NethVoice 1.8" --state open --limit 200 --json number -q '.[].number' > verified.txt
# remove from verified.txt the issues that wait for another component, then:
while read -r i; do
  gh issue comment "$i" -R NethServer/dev --body "$NV" &&
  gh issue close "$i" -R NethServer/dev --reason completed
done < verified.txt
```

After closing, list the open issues of the milestone again and show them to the user:
only the ones agreed for the next release must remain.
