#!/usr/bin/env python3
"""Portable publication checks; requires Python 3.11+ and jsonschema."""
import json
from pathlib import Path
import re
import tomllib

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def contrast(a, b):
    def luminance(color):
        values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [n / 12.92 if n <= 0.04045 else ((n + 0.055) / 1.055) ** 2.4 for n in values]
        return sum(n * weight for n, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + 0.05) / (lo + 0.05)


def main():
    manifest = tomllib.loads((ROOT / "extension.toml").read_text())
    assert manifest["id"] == "glacier-theme"
    assert manifest["schema_version"] == 1
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
    assert manifest["authors"] == ["Max Malkin"]
    assert manifest["repository"] == "https://github.com/maxmalkin/zed-glacier-theme"
    assert manifest["themes"] == ["themes/glacier.json"]
    assert "MIT License" in (ROOT / "LICENSE").read_text()
    family = json.loads((ROOT / manifest["themes"][0]).read_text())
    schema = json.loads((ROOT / "validation/theme-schema.json").read_text())
    jsonschema.validate(family, schema)
    assert family["name"] == "Glacier" and family["author"] == "Max Malkin"
    assert len(family["themes"]) == 1
    theme = family["themes"][0]
    assert theme["name"] == "Glacier" and theme["appearance"] == "dark"
    style = theme["style"]
    syntax = style["syntax"]
    assert all(s.get("font_weight", 400) == 400 for s in syntax.values())
    backgrounds = [style[name] for name in (
        "editor.background", "editor.active_line.background", "elevated_surface.background",
        "editor.document_highlight.read_background", "editor.document_highlight.write_background",
        "editor.document_highlight.bracket_background", "search.match_background", "search.active_match_background",
        "version_control.word_added", "version_control.word_deleted")]
    backgrounds.append(style["players"][0]["selection"])
    ratios = [contrast(token["color"], background) for token in syntax.values() for background in backgrounds]
    assert min(ratios) >= 4.5
    settings = json.loads((ROOT / "settings/semantic-highlighting.json").read_text())
    assert all(settings["languages"][lang]["semantic_tokens"] == "combined" for lang in ["Rust", "Python", "TypeScript", "TSX"])
    for rule in settings["global_lsp_settings"]["semantic_token_rules"]:
        assert all(name in syntax for name in rule.get("style", []))
        assert rule.get("font_weight", "normal") == "normal"
    print(f"PASS: extension manifest, theme schema, semantic settings, regular font weight, and contrast (minimum {min(ratios):.2f}:1)")


if __name__ == "__main__":
    main()
