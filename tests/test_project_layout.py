from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_DIR = ROOT / "custom_components" / "kaleidescape_strato"
BRAND_DIR = INTEGRATION_DIR / "brand"


def _read_png_dimensions(file_path: Path) -> tuple[int, int]:
    with file_path.open("rb") as png_file:
        signature = png_file.read(8)
        ihdr_length = png_file.read(4)
        ihdr_type = png_file.read(4)
        ihdr_data = png_file.read(13)

    assert signature == b"\x89PNG\r\n\x1a\n", f"Invalid PNG signature: {file_path}"
    assert ihdr_length == b"\x00\x00\x00\r", f"Invalid IHDR length: {file_path}"
    assert ihdr_type == b"IHDR", f"Missing IHDR chunk: {file_path}"

    return struct.unpack(">II", ihdr_data[:8])


def test_integration_files_exist() -> None:
    required = [
        INTEGRATION_DIR / "manifest.json",
        INTEGRATION_DIR / "__init__.py",
        INTEGRATION_DIR / "config_flow.py",
        INTEGRATION_DIR / "coordinator.py",
        INTEGRATION_DIR / "media_player.py",
        INTEGRATION_DIR / "remote.py",
        INTEGRATION_DIR / "sensor.py",
        ROOT / "README.md",
        ROOT / "hacs.json",
    ]
    for file_path in required:
        assert file_path.exists(), f"Missing required file: {file_path}"


def test_manifest_domain_is_correct() -> None:
    manifest_path = INTEGRATION_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["domain"] == "kaleidescape_strato"
    assert manifest["config_flow"] is True
    assert manifest["integration_type"] == "device"
    assert manifest["version"]
    assert manifest["documentation"].startswith("https://github.com/tedr91/HA-kaleidescape-strato")


def test_hacs_metadata_is_present() -> None:
    hacs_path = ROOT / "hacs.json"
    hacs = json.loads(hacs_path.read_text(encoding="utf-8"))

    assert "kaleidescape_strato" in hacs["domains"]
    assert hacs["content_in_root"] is False


def test_local_brand_images_exist() -> None:
    required = [
        BRAND_DIR / "icon.png",
        BRAND_DIR / "logo.png",
        BRAND_DIR / "icon@2x.png",
        BRAND_DIR / "logo@2x.png",
        BRAND_DIR / "dark_icon.png",
        BRAND_DIR / "dark_logo.png",
        BRAND_DIR / "dark_icon@2x.png",
        BRAND_DIR / "dark_logo@2x.png",
    ]

    for file_path in required:
        assert file_path.exists(), f"Missing brand asset: {file_path}"


def test_local_brand_images_have_expected_hdpi_sizes() -> None:
    base_and_hdpi_pairs = [
        (BRAND_DIR / "icon.png", BRAND_DIR / "icon@2x.png"),
        (BRAND_DIR / "dark_icon.png", BRAND_DIR / "dark_icon@2x.png"),
        (BRAND_DIR / "logo.png", BRAND_DIR / "logo@2x.png"),
        (BRAND_DIR / "dark_logo.png", BRAND_DIR / "dark_logo@2x.png"),
    ]

    for base_file, hdpi_file in base_and_hdpi_pairs:
        base_width, base_height = _read_png_dimensions(base_file)
        hdpi_width, hdpi_height = _read_png_dimensions(hdpi_file)

        assert hdpi_width == base_width * 2, f"Unexpected width for {hdpi_file}"
        assert hdpi_height == base_height * 2, f"Unexpected height for {hdpi_file}"
