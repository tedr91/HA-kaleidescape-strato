# Releasing

This repository uses a tag-based release workflow.

## Version tags

- Use semantic version tags prefixed with `v` (example: `v0.2.0`).
- Always create **annotated** tags with a short release summary.

## Tag message convention

Use this format for tag messages:

```text
Release vX.Y.Z

- <change summary 1>
- <change summary 2>
- <change summary 3>
```

Example:

```text
Release v0.2.0

- Add expanded Strato remote command aliases
- Improve config flow connection validation
- Update docs and CI checks
```

## Release commands

```powershell
git checkout main
git pull
git tag -a vX.Y.Z -m "Release vX.Y.Z" -m "- summary 1" -m "- summary 2" -m "- summary 3"
git push origin vX.Y.Z
```

Pushing a `v*` tag triggers `.github/workflows/release.yml`, which validates and publishes the GitHub release with generated notes.
