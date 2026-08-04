# Kaleidescape Strato (Custom Home Assistant Integration)

Custom Home Assistant integration for Kaleidescape Strato movie players. It builds on
the official [`pykaleidescape`](https://github.com/SteveEasley/pykaleidescape) library
(the same one the built-in `kaleidescape` integration uses) and adds a richer `remote`
entity, extra diagnostic sensors, and an options flow.

## Why this exists

The built-in integration limits the `remote` entity to a small, fixed command set and
exposes fewer sensors. This custom integration adds:

- a `remote` entity with a large command-alias set that maps to native player commands
- curated pass-through of protocol commands the library does not wrap
- optional raw command pass-through for arbitrary protocol commands
- additional diagnostic sensors (UI state, title/chapter position, device identity, etc.)
- an options flow for command debug logging and enabling raw commands

## Architecture

- **Transport:** `pykaleidescape` over the local network (`local_push`). State updates
  arrive via the library's event dispatcher — there is no polling.
- **Raw sender:** a thin, fire-and-forget TCP client is used only for commands that
  `pykaleidescape` does not expose natively (and for raw pass-through when enabled).
- **Scope:** Strato movie players only. Server-only devices (for example Terra) are
  rejected during setup.

## Features

- Config flow setup (UI) and SSDP discovery
- `media_player` entity (power, transport, media metadata, cover art)
- `remote` entity with `send_command`, aliases, and optional raw pass-through
- Playback and diagnostic sensors (media/playback state, video output, masking, UI/system telemetry)
- Options flow: command debug logging and "allow raw commands"
- Bundled Kaleidescape brand images for Home Assistant UI branding

## Installation (manual)

1. Copy `custom_components/kaleidescape_strato` into your Home Assistant config `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration**.
4. Search for **Kaleidescape Strato**.
5. Enter the **host** (IP address or hostname) of your Strato player.

Home Assistant will install the `pykaleidescape` dependency automatically.

## Installation (HACS)

1. In Home Assistant, open **HACS → Integrations**.
2. Select the menu and choose **Custom repositories**.
3. Add this repository URL and category **Integration**.
4. Find **Kaleidescape Strato** in HACS and install it.
5. Restart Home Assistant and add the integration from **Settings → Devices & Services**.

## Options

Open **Settings → Devices & Services → Kaleidescape Strato → Configure**:

- **Enable command debug logging** — logs raw commands sent through the raw client.
- **Allow sending raw commands to device** — permits arbitrary, unrecognized commands to
  be sent as-is via `remote.send_command`. When disabled, unknown commands raise an error.

## Using commands

Call the `remote.send_command` service against the remote entity.

Home Assistant-style alias (mapped to a native player command):

```yaml
service: remote.send_command
target:
  entity_id: remote.kaleidescape_strato
data:
  command: "up"
```

Curated protocol command (sent via the raw client even without enabling raw commands):

```yaml
service: remote.send_command
target:
  entity_id: remote.kaleidescape_strato
data:
  command: "SHOW_NAVIGATION_OVERLAY"
```

Arbitrary raw command (requires **Allow sending raw commands** enabled in options):

```yaml
service: remote.send_command
target:
  entity_id: remote.kaleidescape_strato
data:
  command: "01/0/GET_DEVICE_INFO:"
```

Command resolution order for each value:

1. If it matches a known alias, the matching native `pykaleidescape` method is called.
2. Otherwise, if it matches a curated alias, its protocol command is sent via the raw client.
3. Otherwise, if raw commands are enabled, the value is sent as-is.
4. Otherwise, an error is raised.

`num_repeats` and `delay_secs` are honored.

## Entities

### Media player

- `media_player.kaleidescape_strato` — power (turn on/off), transport (play/pause/stop/next/previous),
  and media metadata (title, cover art, position/duration, content id/type).

### Remote

- `remote.kaleidescape_strato` — `send_command`, plus turn on/off (leave/enter standby).

### Sensors

#### Core playback sensors

- `media_location`: Where playback is in the title (for example `content`, `credits`, `disc_menu`).
- `play_status`: Current transport mode (for example `playing`, `paused`, `forward`, `reverse`).
- `play_speed`: Current transport speed value reported by the player.

#### Playback telemetry sensors

- `title_location`: Current position within the title.
- `title_length`: Total title length.
- `chapter_location`: Current position within the chapter.
- `chapter_length`: Total chapter length.

#### Video diagnostics

- `video_mode`: Current output video mode/resolution profile.
- `video_color_eotf`: Active transfer function (for example SDR/HDR).
- `video_color_space`: Active color space.
- `video_color_depth`: Active color depth.
- `video_color_sampling`: Active chroma sampling mode.

#### Masking and CinemaScape diagnostics

- `screen_mask_ratio`: Reported content aspect ratio for masking.
- `screen_mask_top_trim_rel`: Top trim percentage.
- `screen_mask_bottom_trim_rel`: Bottom trim percentage.
- `screen_mask_conservative_ratio`: Conservative mask ratio recommendation.
- `screen_mask_top_mask_abs`: Absolute top mask percentage.
- `screen_mask_bottom_mask_abs`: Absolute bottom mask percentage.
- `cinemascape_mode`: Current CinemaScape mode.
- `cinemascape_mask`: Current CinemaScape mask value.

#### System and UI diagnostics

- `serial`: Player serial number.
- `cpdid`: Player CPDID.
- `device_ip`: Player IP address.
- `system_readiness_state`: Player readiness state.
- `power_state`: Reported power state.
- `ui_screen`: Current on-screen UI screen.
- `ui_popup`: Current popup state.
- `ui_dialog`: Current dialog state.

## Lovelace example card

```yaml
type: entities
title: Kaleidescape Strato
show_header_toggle: false
entities:
  - entity: media_player.kaleidescape_strato
    name: Player
  - entity: remote.kaleidescape_strato
    name: Remote
  - entity: sensor.kaleidescape_strato_play_status
    name: Play status
  - entity: sensor.kaleidescape_strato_media_location
    name: Media location
  - entity: sensor.kaleidescape_strato_video_mode
    name: Video mode
  - entity: sensor.kaleidescape_strato_power_state
    name: Power state
```

## Notes

- Only Strato movie players are supported; server-only devices are rejected at setup.
- Network access from Home Assistant to the Strato host (TCP port 10000) is required.
- Local brand assets are included under `custom_components/kaleidescape_strato/brand` and are used automatically by Home Assistant 2026.3+.

## Release process

- See [RELEASING.md](RELEASING.md) for annotated tag conventions and commands.

## HACS release readiness

- `hacs.json` is present at repository root.
- Integration is under `custom_components/kaleidescape_strato`.
- `manifest.json` includes versioning and integration metadata.
- GitHub Releases are triggered by `v*` tags via workflow automation.
