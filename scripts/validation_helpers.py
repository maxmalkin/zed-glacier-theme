"""Validation helpers for Zed syntax queries and captured semantic tokens."""
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


def parse_source(source, name):
    """Parse a fixture and exercise its highlight query, including Markdown injections."""
    lang = grammar(name)
    tree = Parser(lang).parse(source)
    query = Query(lang, (REFERENCE / f"{name}.scm").read_text())
    list(QueryCursor(query).matches(tree.root_node))
    if name == "markdown":
        def walk(node):
            if node.type == "inline":
                parse_source(source[node.start_byte:node.end_byte], "markdown-inline")
            if node.type == "fenced_code_block":
                info = next((n for n in node.children if n.type == "info_string"), None)
                content = next((n for n in node.children if n.type == "code_fence_content"), None)
                if info and content:
                    language = source[info.start_byte:info.end_byte].decode().strip()
                    if language in ("rust", "python", "typescript", "tsx", "json", "yaml"):
                        parse_source(source[content.start_byte:content.end_byte], language)
            for child in node.children:
                walk(child)
        walk(tree.root_node)
    return tree
