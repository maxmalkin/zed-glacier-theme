"""Preview helpers using Zed's actual queries and captured LSP token responses.

This is a review renderer, not Zed's layout engine. Full theme behavior must be
checked in Zed. Byte ranges and layered rule precedence are preserved here.
"""
import importlib
import json
from functools import cache
from pathlib import Path
import json5
from tree_sitter import Language, Parser, Query, QueryCursor

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / ".cache/reference"
THEME = json.loads((ROOT / "themes/glacier.json").read_text())["themes"][0]["style"]
SYNTAX = THEME["syntax"]
USER_RULES = json.loads((ROOT / "settings/semantic-highlighting.json").read_text())["global_lsp_settings"]["semantic_token_rules"]


def resolve(name):
    while name:
        if name in SYNTAX:
            return SYNTAX[name]
        name = name.rpartition(".")[0]
    return None


@cache
def semantic_rules(language):
    lang_path = REFERENCE / f"{language}-semantic.json"
    lang_rules = json5.loads(lang_path.read_text()) if lang_path.exists() else []
    defaults = json5.loads((REFERENCE / "default-semantic.json").read_text())
    return USER_RULES + lang_rules + defaults


def semantic_style(token, language):
    result = {}
    # Zed applies matching rules from lowest to highest priority, field by field.
    for rule in reversed(semantic_rules(language)):
        if rule.get("token_type", token["type"]) != token["type"]:
            continue
        if not set(rule.get("token_modifiers", [])).issubset(token["modifiers"]):
            continue
        style = next((s for n in rule.get("style", []) if (s := resolve(n))), {})
        result.update(style)
        if "foreground_color" in rule:
            result["color"] = rule["foreground_color"]
        for key in ["font_style", "font_weight", "strikethrough", "underline"]:
            if key in rule:
                result[key] = {"normal": 400, "bold": 700}.get(rule[key], rule[key]) if key == "font_weight" else rule[key]
    return result


def grammar(name):
    if name in ("terraform", "terraform-vars"):
        name = "hcl"
    if name in ("typescript", "tsx"):
        module = importlib.import_module("tree_sitter_typescript")
        return Language(getattr(module, "language_" + name)())
    if name == "markdown-inline":
        return Language(importlib.import_module("tree_sitter_markdown").inline_language())
    return Language(importlib.import_module("tree_sitter_" + name.replace("-", "_" )).language())


def syntax_ranges(source, name, offset=0):
    lang = grammar(name)
    tree = Parser(lang).parse(source)
    query = Query(lang, (REFERENCE / f"{name}.scm").read_text())
    entries = []
    for pattern, captures in QueryCursor(query).matches(tree.root_node):
        for capture, nodes in captures.items():
            style = resolve(capture)
            if style:
                for node in nodes:
                    entries.append((pattern, node.start_byte + offset, node.end_byte + offset, style, capture))
    # Later patterns override earlier patterns; smaller spans refine outer strings.
    entries.sort(key=lambda e: (e[0], -(e[2] - e[1])))
    return [(start, end, style, capture) for _, start, end, style, capture in entries], tree


def highlighted(source, language, semantic_report=None):
    data = source.encode()
    ranges, tree = syntax_ranges(data, language)
    if language == "markdown":
        def walk(node):
            if node.type == "inline":
                inline, _ = syntax_ranges(data[node.start_byte:node.end_byte], "markdown-inline", node.start_byte)
                ranges.extend(inline)
            if node.type == "fenced_code_block":
                info = next((n for n in node.children if n.type == "info_string"), None)
                content = next((n for n in node.children if n.type == "code_fence_content"), None)
                if info and content:
                    name = data[info.start_byte:info.end_byte].decode().strip()
                    if name in ("rust", "python", "typescript", "tsx", "json", "yaml"):
                        injected, _ = syntax_ranges(data[content.start_byte:content.end_byte], name, content.start_byte)
                        ranges.extend(injected)
            for child in node.children:
                walk(child)
        walk(tree.root_node)
    if semantic_report and semantic_report.exists():
        report = json.loads(semantic_report.read_text())
        lines = source.splitlines(keepends=True)
        offsets, total = [], 0
        for line in lines:
            offsets.append(total)
            total += len(line.encode())
        for token in report["tokens"]:
            line = lines[token["line"]]
            start = offsets[token["line"]] + len(line.encode("utf-16-le")[:token["column"] * 2].decode("utf-16-le").encode())
            end = start + len(token["text"].encode())
            style = semantic_style(token, language)
            if style:
                ranges.append((start, end, style, token["type"]))
    pixels = [(resolve("variable"), "variable") for _ in data]
    for start, end, style, name in ranges:
        for i in range(start, min(end, len(pixels))):
            pixels[i] = ({**pixels[i][0], **style}, name)
    # Coalesce bytes before decoding so Unicode characters remain intact.
    result = []
    start = 0
    while start < len(data):
        end = start + 1
        while end < len(data) and pixels[end] == pixels[start]:
            end += 1
        result.append((data[start:end].decode(), pixels[start][0], pixels[start][1]))
        start = end
    return result, tree.root_node.has_error
