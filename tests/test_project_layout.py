from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_DIR = ROOT / "custom_components" / "kaleidescape_strato"


def test_integration_files_exist() -> None:
    required = [
        INTEGRATION_DIR / "manifest.json",
        INTEGRATION_DIR / "__init__.py",
        INTEGRATION_DIR / "config_flow.py",
        INTEGRATION_DIR / "remote.py",
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
