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

## Exposed sensors

### Core playback sensors

- `media_location`: Where playback is in the title (for example `content`, `credits`, `disc_menu`).
- `play_status`: Current transport mode (for example `playing`, `paused`, `forward`, `reverse`).
- `play_speed`: Current transport speed value reported by the player.

### Playback telemetry sensors

- `title_location`: Current position within the title.
- `title_length`: Total title length.
- `chapter_location`: Current position within the chapter.
- `chapter_length`: Total chapter length.

### Video diagnostics

- `video_mode`: Current output video mode/resolution profile.
- `video_color_eotf`: Active transfer function (for example SDR/HDR).
- `video_color_space`: Active color space.
- `video_color_depth`: Active color depth.
- `video_color_sampling`: Active chroma sampling mode.

### Masking and Cinemascape diagnostics

- `screen_mask_ratio`: Reported content aspect ratio for masking.
- `screen_mask_top_trim_rel`: Top trim percentage.
- `screen_mask_bottom_trim_rel`: Bottom trim percentage.
- `screen_mask_conservative_ratio`: Conservative mask ratio recommendation.
- `screen_mask_top_mask_abs`: Absolute top mask percentage.
- `screen_mask_bottom_mask_abs`: Absolute bottom mask percentage.
- `cinemascape_mode`: Current Cinemascape mode.
- `cinemascape_mask`: Current Cinemascape mask value.

### System and UI diagnostics

- `system_readiness_state`: Player readiness state.
- `power_state`: Reported power state.
- `ui_screen`: Current on-screen UI screen.
- `ui_popup`: Current popup state.
- `ui_dialog`: Current dialog state.

## Entity ID examples

Entity IDs use your configured device name slug. If your integration name is
`Kaleidescape Strato`, examples include:

- `sensor.kaleidescape_strato_media_location`
- `sensor.kaleidescape_strato_play_status`
- `sensor.kaleidescape_strato_play_speed`
- `sensor.kaleidescape_strato_title_location`
- `sensor.kaleidescape_strato_title_length`
- `sensor.kaleidescape_strato_chapter_location`
- `sensor.kaleidescape_strato_chapter_length`
- `sensor.kaleidescape_strato_video_mode`
- `sensor.kaleidescape_strato_video_color_eotf`
- `sensor.kaleidescape_strato_video_color_space`
- `sensor.kaleidescape_strato_video_color_depth`
- `sensor.kaleidescape_strato_video_color_sampling`
- `sensor.kaleidescape_strato_screen_mask_ratio`
- `sensor.kaleidescape_strato_screen_mask_top_trim_rel`
- `sensor.kaleidescape_strato_screen_mask_bottom_trim_rel`
- `sensor.kaleidescape_strato_screen_mask_conservative_ratio`
- `sensor.kaleidescape_strato_screen_mask_top_mask_abs`
- `sensor.kaleidescape_strato_screen_mask_bottom_mask_abs`
- `sensor.kaleidescape_strato_cinemascape_mode`
- `sensor.kaleidescape_strato_cinemascape_mask`
- `sensor.kaleidescape_strato_system_readiness_state`
- `sensor.kaleidescape_strato_power_state`
- `sensor.kaleidescape_strato_ui_screen`
- `sensor.kaleidescape_strato_ui_popup`
- `sensor.kaleidescape_strato_ui_dialog`

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
