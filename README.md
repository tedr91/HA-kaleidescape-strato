# Kaleidescape Strato (Custom Home Assistant Integration)

Custom Home Assistant integration that exposes a `remote` entity for Kaleidescape Strato players with a more permissive command model than the built-in integration.

## Why this exists

The built-in integration is limited to a narrower command set on the `remote` entity. This custom integration allows:

- direct pass-through of protocol commands
- command aliases for common Home Assistant remote commands
- easy extension of supported commands in code

## Features (v0.1)

- Config Flow setup (UI)
- TCP connectivity to a Strato player
- `remote` entity with `send_command`
- Playback and diagnostic sensors, including media/playback state, video output, masking, and UI/system telemetry
- permissive command handling (unknown commands are sent as-is)

## Installation (manual)

1. Copy `custom_components/kaleidescape_strato` into your Home Assistant config `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration**.
4. Search for **Kaleidescape Strato**.
5. Enter host/port for your player.

## Installation (HACS)

1. In Home Assistant, open **HACS → Integrations**.
2. Select the menu and choose **Custom repositories**.
3. Add this repository URL and category **Integration**.
4. Find **Kaleidescape Strato** in HACS and install it.
5. Restart Home Assistant and add the integration from **Settings → Devices & Services**.

## Using commands

You can call Home Assistant service `remote.send_command` against this entity.

Example (pass-through raw protocol command):

```yaml
service: remote.send_command
target:
  entity_id: remote.kaleidescape_strato
metadata: {}
data:
  command: "PLAY"
```

Example (Home Assistant-style alias):

```yaml
service: remote.send_command
target:
  entity_id: remote.kaleidescape_strato
metadata: {}
data:
  command: "up"
```

`up` maps to `UP`, while unknown values are sent unchanged.

## Notes

- Confirm protocol-level command names and behavior with the Kaleidescape protocol reference.
- Network access from Home Assistant to the Strato host/port is required.

## Release process

- See [RELEASING.md](RELEASING.md) for annotated tag conventions and commands.

## HACS release readiness

- `hacs.json` is present at repository root.
- Integration is under `custom_components/kaleidescape_strato`.
- `manifest.json` includes versioning and integration metadata.
- GitHub Releases are triggered by `v*` tags via workflow automation.
