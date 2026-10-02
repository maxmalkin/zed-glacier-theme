#!/usr/bin/env python3
"""Validate schema, source capture coverage, overlays, and real semantic distinctions."""
import json
import re
import jsonschema
from validation_helpers import ROOT, REFERENCE, THEME, SYNTAX, USER_RULES, resolve, semantic_style, parse_source


def luminance(color):
    rgb = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return sum(v * w for v, w in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + 0.05) / (lo + 0.05)


def main():
    family = json.loads((ROOT / "themes/glacier.json").read_text())
    schema = json.loads((REFERENCE / "schema.json").read_text())
    jsonschema.validate(family, schema)
    # The hosted schema lags several fields shipped in current Zed; audit these explicitly.
    current = {"editor.hover_line_number", "search.active_match_background"} | {
        "version_control." + key for key in ["added", "deleted", "modified", "renamed", "ignored", "conflict",
                                            "word_added", "word_deleted", "conflict_marker.ours", "conflict_marker.theirs"]} | {
        f"editor.diff_hunk.{kind}.{field}" for kind in ("added", "deleted")
        for field in ("background", "hollow_background", "hollow_border")}
    assert not set(THEME) - set(schema["definitions"]["ThemeStyleContent"]["properties"]) - current
    capture_report = {}
    for path in sorted(REFERENCE.glob("*.scm")):
        captures = sorted(c for c in set(re.findall(r"@([\w.]+)", path.read_text())) if not c.startswith("_"))
        missing = [c for c in captures if resolve(c) is None]
        assert not missing, (path.name, missing)
        capture_report[path.stem] = {"count": len(captures), "captures": captures}
    for rule in USER_RULES:
        for name in rule.get("style", []):
            assert name in SYNTAX, name
    backgrounds = {key: THEME[key] for key in [
        "editor.background", "editor.active_line.background", "elevated_surface.background",
        "editor.document_highlight.read_background", "editor.document_highlight.write_background",
        "editor.document_highlight.bracket_background", "search.match_background", "search.active_match_background",
        "editor.diff_hunk.added.background", "editor.diff_hunk.added.hollow_background",
        "editor.diff_hunk.deleted.background", "editor.diff_hunk.deleted.hollow_background",
        "version_control.word_added", "version_control.word_deleted"]}
    backgrounds["selection"] = THEME["players"][0]["selection"]
    contrast_report = {}
    for name, background in backgrounds.items():
        ratios = {scope: contrast(style["color"], background) for scope, style in SYNTAX.items()}
        assert min(ratios.values()) >= 4.5, (name, min(ratios.items(), key=lambda p: p[1]))
        contrast_report[name] = round(min(ratios.values()), 2)
    semantic_report = {}
    for name, lang in [("lib.rs", "rust"), ("cache.py", "python"), ("cache.ts", "typescript"), ("panel.tsx", "tsx")]:
        path = ROOT / ".cache" / f"tokens-{name}.json"
        report = json.loads(path.read_text())
        unmapped = [t["type"] for t in report["tokens"] if not semantic_style(t, lang)]
        assert not unmapped, (name, set(unmapped))
        semantic_report[name] = {"tokens": len(report["tokens"]), "types": sorted({t['type'] for t in report['tokens']})}
        for required in ("property", "typeParameter") if name != "panel.tsx" else ("property", "parameter"):
            assert required in semantic_report[name]["types"], (name, required)
        tree = parse_source((ROOT / report["file"]).read_bytes(), lang)
        assert not tree.root_node.has_error, name
    # Functional distinctions: imported types, parameters, fields, variants, mutability.
    rust = json.loads((ROOT / ".cache/tokens-lib.rs.json").read_text())["tokens"]
    def find(kind, text=None, modifier=None):
        return next(t for t in rust if t['type'] == kind and (text is None or t['text'] == text)
                    and (modifier is None or modifier in t['modifiers']))
    assert semantic_style(find("parameter", "label"), "rust")["color"] != semantic_style(find("property", "label"), "rust")["color"]
    assert semantic_style(find("enumMember", "Hit"), "rust")["color"] != semantic_style(find("enum", "CacheResult"), "rust")["color"]
    assert semantic_style(find("variable", "count", "mutable"), "rust")["font_style"] == "italic"
    assert semantic_style(find("keyword", "unsafe"), "rust")["color"] == SYNTAX["keyword.unsafe"]["color"]
    assert all(style.get("font_weight", 400) == 400 for style in SYNTAX.values()), "All syntax must use regular weight"
    for file, lang in [("config.json", "json"), ("config.yml", "yaml"), ("guide.md", "markdown"),
                       ("config.toml", "toml"), ("main.tf", "terraform"), ("start.sh", "bash")]:
        tree = parse_source((ROOT / "examples" / file).read_bytes(), lang)
        assert not tree.root_node.has_error, file
    report = {"schema": "pass", "syntax_styles": len(SYNTAX), "semantic_rules": len(USER_RULES),
              "capture_coverage": capture_report, "minimum_contrast": contrast_report, "semantic_tokens": semantic_report}
    dest = ROOT / "validation/report.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: schema; {len(SYNTAX)} styles; {len(capture_report)} query sets; {sum(v['tokens'] for v in semantic_report.values())} real semantic tokens")
    print(f"PASS: all syntax colors >= 4.5:1 across {len(backgrounds)} backgrounds; minimum {min(contrast_report.values()):.2f}:1")


if __name__ == "__main__":
    main()
