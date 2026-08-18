from __future__ import annotations


def is_legacy_unique_id(unique_id: str | None) -> bool:
    """Return whether a config entry unique ID predates serial-based IDs."""
    if not unique_id:
        return True

    normalized = unique_id.lower()
    return normalized.startswith(("udn:", "uuid:")) or ":" in unique_id


def _migrated_unique_id(
    domain: str, unique_id: str, entry_id: str, serial: str
) -> str | None:
    """Return the serial-based replacement for a legacy entity unique ID."""
    prefix = f"{entry_id}_"
    if not unique_id.startswith(prefix):
        return None

    suffix = unique_id[len(prefix) :]
    if not suffix:
        return None

    if domain in {"media_player", "remote"}:
        return serial if suffix == domain else None
    if domain == "sensor":
        return f"{serial}-{suffix}"
    return None