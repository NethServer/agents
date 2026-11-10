# NethLink

NethLink (`NethServer/nethlink`) is an Electron app. It is released from a local clone with
`npm version`, not with `gh ns8`. Tags carry a `v` prefix (`v1.6.0`).

## Testing releases

`build-testing.yml` runs on every push to `main` and publishes a signed testing
pre-release. The name derives from the highest version tag:

- `v1.6.0` → `v1.6.1-testing.1`
- `v1.6.1-testing.1` → `v1.6.1-testing.2`

To start a new minor, push a bare tag on `main`, for example `v1.7.0-testing.0`: the next
build becomes `v1.7.0-testing.1`. A commit that already carries a version tag is skipped.

## Release

`package.json` holds the previous stable version during the testing cycle (for example
`1.5.3` during the `v1.6.0-testing.*` cycle), so `npm run publish:minor` produces `v1.6.0`.
Check the resulting version with the user before running it.

The scripts in `package.json`:

- `preversion`: `git add .` — every untracked or modified file ends up in the version commit.
- `publish:<level>`: `npm version <level> --allow-same-version -m v%s --force`
- `postversion`: `git push origin main --tags` — pushes **every** local tag.

So, before running it:

1. Check out `main` and run `git pull --ff-only`.
2. `git status --porcelain` must be empty. Move untracked files away temporarily, for
   example `tsconfig.web.tsbuildinfo`, and put them back afterwards.
3. Compare the local tags with the remote ones. A local-only tag would be pushed again,
   for example a testing tag already deleted on GitHub:
   ```bash
   comm -23 <(git tag | sort) <(git ls-remote --tags origin | sed 's#.*refs/tags/##; s#\^{}##' | sort -u)
   ```
4. Wait for the "Build and release testing apps" run of the current `HEAD` to finish.
   Otherwise its testing tag can appear after the stable cleanup and stay behind.

Then, after the user approves:

```bash
npm run publish:minor     # or publish:patch / publish:major
```

The version commit must contain only `package.json` and `package-lock.json`.

## Release workflow

The pushed `vX.Y.Z` tag runs `build-prod.yml`:

1. Builds and signs macOS (x64, arm64), Windows and Linux packages into a **draft** release.
2. `update-release-notes`: notes since the previous stable tag, plus the SBOM.
3. `clean-testing-releases`: deletes every `vX.Y.Z-testing.N` that sorts before the new
   tag, releases **and** tags. NethLink needs no manual cleanup.

The release stays a draft: publishing it is a manual step. Ask the user how:

| Choice | Command | Effect |
| --- | --- | --- |
| Pre-release, not offered to users yet | `gh release edit v1.6.0 -R NethServer/nethlink --draft=false --prerelease --latest=false` | No auto-update, no winget |
| Stable | `gh release edit v1.6.0 -R NethServer/nethlink --draft=false --latest` | Auto-update offers it to every client; `winget.yml` runs |

`winget.yml` runs on the `released` event, which fires on a stable publish or when a
pre-release is later promoted to stable. `homebrew.yml` only runs by hand
(`workflow_dispatch`). Promote a pre-release later with
`gh release edit v1.6.0 -R NethServer/nethlink --prerelease=false --latest`.

Issues fixed in NethLink can be closed when the release is published, even as a
pre-release, if the user agrees.

## Compatibility test (optional)

Users may update NethLink before their PBX. To test the new NethLink against the previous
NethVoice minor, use a fresh test instance of the previous stable version (`add-module
ghcr.io/nethesis/nethvoice:<previous> <node>`). An instance already on the new minor
cannot be downgraded: from NethVoice 1.8, MariaDB 11.8 data does not start on the
MariaDB 10.11 image of 1.7. After the test, update the same instance to the new release
with `update-module` to cover the upgrade path too.
