from __future__ import annotations

import importlib.util
from pathlib import Path

MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "kaleidescape_strato"
    / "migration.py"
)
SPEC = importlib.util.spec_from_file_location("kaleidescape_strato_migration", MIGRATION_PATH)
assert SPEC is not None
assert SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)


def test_normalizes_all_serial_whitespace() -> None:
    assert MIGRATION.normalize_serial("0703 00000878") == "070300000878"
    assert MIGRATION.normalize_serial(" 0703\t0000\n0878 ") == "070300000878"
    assert MIGRATION.normalize_serial("070300000878") == "070300000878"


def test_migrates_singleton_domains() -> None:
    assert (
        MIGRATION._migrated_unique_id(
            "media_player", "entry_media_player", "entry", "serial"
        )
        == "serial"
    )
    assert MIGRATION._migrated_unique_id("remote", "entry_remote", "entry", "serial") == "serial"


def test_migrates_sensor_key_suffix() -> None:
    assert (
        MIGRATION._migrated_unique_id("sensor", "entry_kos_version", "entry", "serial")
        == "serial-kos_version"
    )


def test_domain_controls_media_player_suffix_dispatch() -> None:
    assert (
        MIGRATION._migrated_unique_id(
            "sensor", "entry_media_player", "entry", "serial"
        )
        == "serial-media_player"
    )


def test_already_migrated_and_unrelated_ids_are_unchanged() -> None:
    assert MIGRATION._migrated_unique_id("remote", "serial", "entry", "serial") is None
    assert (
        MIGRATION._migrated_unique_id("sensor", "serial-kos_version", "entry", "serial")
        is None
    )
    assert MIGRATION._migrated_unique_id("sensor", "other_key", "entry", "serial") is None
    assert MIGRATION._migrated_unique_id("light", "entry_power", "entry", "serial") is None
    assert MIGRATION._migrated_unique_id("sensor", "entry_", "entry", "serial") is None


def test_detects_legacy_config_entry_unique_ids() -> None:
    assert MIGRATION.is_legacy_unique_id("udn:uuid:player")
    assert MIGRATION.is_legacy_unique_id("UUID:player")
    assert MIGRATION.is_legacy_unique_id("192.168.1.10:10000")
    assert MIGRATION.is_legacy_unique_id(None)
    assert MIGRATION.is_legacy_unique_id("")
    assert MIGRATION.is_legacy_unique_id("0703 00000878")
    assert MIGRATION.is_legacy_unique_id("0703\t00000878")
    assert not MIGRATION.is_legacy_unique_id("070300000878")
