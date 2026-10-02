#!/usr/bin/env python3
"""Build the theme and semantic companion from one palette. Standard library only."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = {
    "background": "#2F3D4E", "panel": "#273342", "deep": "#23303F",
    "text": "#F8F8F3", "keyword": "#C69AFF", "function": "#F5D547",
    "type": "#7DDFFF", "property": "#82B7FF", "parameter": "#FFD09B",
    "string": "#A4E57A", "number": "#FF9C7C", "constant": "#DBB5FF",
    "boolean": "#F6B4FF",
    "attribute": "#F5A0D0", "generic": "#66E0C1", "comment": "#A3AFBC",
    "doc": "#B3C3B5", "punctuation": "#B6C2CE", "operator": "#CFD8E3",
    "error": "#FFA39E", "border": "#4B5D70", "muted": "#98A9BA",
}


def build():
    p = P
    s = {}

    def colors(value, *keys):
        for key in keys:
            s[key] = value

    colors(p["panel"], "background", "surface.background", "status_bar.background",
           "title_bar.background", "tab_bar.background", "tab.inactive_background",
           "panel.background", "editor.subheader.background")
    colors(p["deep"], "title_bar.inactive_background", "element.disabled")
    colors(p["background"], "editor.background", "editor.gutter.background",
           "tab.active_background", "toolbar.background", "terminal.background",
           "terminal.ansi.background", "element.background")
    colors("#2B3A4C", "elevated_surface.background")
    colors("#34465A", "element.hover", "ghost_element.hover")
    colors("#25384D", "element.active", "element.selected", "ghost_element.active", "ghost_element.selected")
    colors("#00000000", "border.transparent", "ghost_element.background", "ghost_element.disabled",
           "scrollbar.track.background")
    colors("#9FDEFA18", "drop_target.background")
    colors(p["border"], "border", "scrollbar.thumb.border")
    colors("#3B4B5E", "border.variant", "border.disabled", "pane_group.border", "scrollbar.track.border")
    colors(p["function"], "border.focused", "border.selected", "panel.focused_border", "pane.focused_border")
    colors(p["text"], "text", "icon", "editor.foreground", "terminal.foreground")
    colors(p["comment"], "text.muted", "icon.muted", "text.placeholder", "icon.placeholder")
    colors("#8395A8", "text.disabled", "icon.disabled")
    colors(p["function"], "text.accent", "icon.accent", "editor.active_line_number")
    colors(p["type"], "link_text.hover")
    colors("#2B394A", "editor.active_line.background", "editor.highlighted_line.background")
    colors("#8DA0B5", "editor.line_number")
    colors(p["text"], "editor.hover_line_number")
    colors("#60748B", "editor.invisible", "editor.indent_guide", "panel.indent_guide")
    colors("#A38C4C", "editor.indent_guide_active", "panel.indent_guide_active")
    colors("#7C91A7", "panel.indent_guide_hover")
    colors("#B6C2CE18", "editor.wrap_guide")
    colors("#EACD4540", "editor.active_wrap_guide")
    colors("#253B49", "editor.document_highlight.read_background")
    colors("#3A354A", "editor.document_highlight.write_background")
    colors("#3B3927", "editor.document_highlight.bracket_background", "search.match_background")
    colors("#423921", "search.active_match_background")
    colors("#98A9BA50", "scrollbar.thumb.background")
    colors("#98A9BA90", "scrollbar.thumb.hover_background")
    colors("#FFFFFF", "terminal.bright_foreground")
    colors(p["comment"], "terminal.dim_foreground")

    ansi = {
        "black": ("#1B242E", "#91A2B4", "#19222C"),
        "red": (p["number"], "#FFA39E", "#D47765"),
        "green": (p["string"], "#BBE8A4", "#86B776"),
        "yellow": (p["function"], "#FFFFB0", "#C8B33F"),
        "blue": (p["property"], "#ADD0FA", "#759AC2"),
        "magenta": (p["keyword"], p["constant"], "#AA85D8"),
        "cyan": (p["type"], "#C3EBFB", "#86BCD5"),
        "white": (p["text"], "#FFFFFF", "#B6C2CE"),
    }
    for name, values in ansi.items():
        for prefix, color in zip(("", "bright_", "dim_"), values):
            s[f"terminal.ansi.{prefix}{name}"] = color

    statuses = {
        "error": (p["error"], "#433139"), "deleted": (p["error"], "#433139"),
        "warning": (p["function"], "#3B3927"), "conflict": (p["attribute"], "#3A354A"),
        "created": (p["string"], "#253D37"), "success": (p["string"], "#253D37"),
        "modified": (p["property"], "#253B49"), "renamed": (p["generic"], "#253B49"),
        "info": (p["type"], "#253B49"), "hint": (p["comment"], p["panel"]),
        "ignored": (p["muted"], p["panel"]), "hidden": (p["muted"], p["panel"]),
        "unreachable": (p["comment"], p["panel"]), "predictive": (p["muted"], p["panel"]),
    }
    for name, (fg, bg) in statuses.items():
        s.update({name: fg, name + ".background": bg, name + ".border": fg + "65"})
    for name, role in {"added": "string", "deleted": "error", "modified": "property",
                       "renamed": "generic", "conflict": "attribute", "ignored": "muted"}.items():
        s["version_control." + name] = p[role]
    # Opaque diff fills avoid Zed's faint foreground-derived overlays on blue-gray.
    s.update({"editor.diff_hunk.added.background": "#16382A",
              "editor.diff_hunk.added.hollow_background": "#19332A",
              "editor.diff_hunk.added.hollow_border": "#4C805D",
              "editor.diff_hunk.deleted.background": "#451F2D",
              "editor.diff_hunk.deleted.hollow_background": "#3B202C",
              "editor.diff_hunk.deleted.hollow_border": "#92505A",
              "version_control.word_added": "#082619", "version_control.word_deleted": "#300D1B",
              "version_control.conflict_marker.ours": "#253D37",
              "version_control.conflict_marker.theirs": "#253B49"})
    s["accents"] = [p[k] for k in ["function", "type", "keyword", "string", "attribute", "number"]]
    s["players"] = [{"cursor": p[k], "background": p[k], "selection": bg} for k, bg in [
        ("function", "#192D43"), ("type", "#21384B"), ("attribute", "#3B3044"),
        ("string", "#243C34"), ("number", "#413139"), ("keyword", "#323047")]]

    syntax = {}

    def token(names, role, italic=False):
        for name in names.split():
            syntax[name] = {"color": p.get(role, role), "font_style": "italic" if italic else "normal", "font_weight": 400}

    token("variable primary text text.jsx embedded none nested", "text")
    token("variable.parameter function.kwargs parameter", "parameter")
    token("variable.mutable", "text", italic=True)
    token("variable.parameter.mutable", "parameter", italic=True)
    token("variable.special variable.builtin", "attribute", italic=True)
    token("property property.name property.json_key attribute.jsx", "property")
    token("property.readonly", "property", italic=True)
    token("property.mutable", "property")
    token("constant constant.builtin variable.readonly", "constant")
    token("boolean", "boolean")
    token("number", "number")
    token("keyword keyword.declaration keyword.definition keyword.import keyword.directive keyword.modifier preproc", "keyword")
    token("keyword.control", "keyword")
    token("keyword.unsafe", "number")
    token("keyword.operator keyword.operator.regex operator", "operator")
    token("punctuation punctuation.bracket punctuation.delimiter punctuation.bracket.jsx punctuation.delimiter.jsx punctuation.markup", "punctuation")
    token("punctuation.special punctuation.embedded.markup", "attribute")
    token("punctuation.list_marker punctuation.list_marker.markup", "function")
    token("function function.call", "function")
    token("function.definition", "function")
    token("function.method function.method.call", "function", italic=True)
    token("function.method.definition", "function", italic=True)
    token("function.builtin", "function")
    token("function.special function.macro", "attribute")
    token("function.special.definition", "attribute")
    token("function.decorator function.decorator.call function.annotation attribute attribute.builtin attribute.special", "attribute", italic=True)
    token("type type.name type.class type.struct type.enum enum type.alias", "type")
    token("type.definition type.class.definition type.struct.definition type.enum.definition", "type")
    token("type.interface type.class.inheritance", "type", italic=True)
    token("type.interface.definition", "type", italic=True)
    token("type.builtin type.class.builtin", "type")
    token("type.self", "type", italic=True)
    token("type.parameter", "generic")
    token("type.parameter.definition", "generic")
    token("lifetime label", "generic", italic=True)
    token("namespace module", "#BDCAD8")
    token("type.enum.member variant", "constant")
    token("constructor function.method.constructor type.class.call", "type")
    token("string text.literal", "string")
    token("string.doc comment.doc comment.documentation", "doc", italic=True)
    token("string.escape string.special", "parameter")
    token("string.regex string.regexp", "generic")
    token("string.special.symbol", "constant")
    token("comment", "comment", italic=True)
    token("hint predictive", "muted", italic=True)
    token("tag tag.jsx", "keyword")
    token("tag.component.jsx", "type")
    token("tag.doctype", "comment")
    token("title title.markup", "function")
    token("link_text link_text.markup", "type")
    token("link_uri link_uri.markup", "generic", italic=True)
    token("emphasis", "text", italic=True)
    token("emphasis.strong", "function")
    token("strikethrough.markup", "comment", italic=True)
    s["syntax"] = syntax

    rules = [{"token_modifiers": ["deprecated"], "strikethrough": True}]

    def rule(kind, style, modifiers=()):
        item = {"token_type": kind}
        if modifiers:
            item["token_modifiers"] = list(modifiers)
        item["style"] = [style]
        rules.append(item)

    for kind in ["keyword", "function", "method", "operator", "punctuation"]:
        rule(kind, "keyword.unsafe", ["unsafe"])
    rule("keyword", "keyword.control", ["controlFlow"])
    rule("generic", "attribute", ["attribute"])
    for kind, style in [("variable", "variable.mutable"), ("parameter", "variable.parameter.mutable"), ("property", "property.mutable")]:
        rule(kind, style, ["mutable"])
    rule("property", "property.readonly", ["readonly"])
    rule("variable", "constant", ["readonly"])
    rule("variable", "constant", ["constant"])
    for kind, base in [("function", "function"), ("method", "function.method")]:
        for modifier in ["declaration", "definition"]:
            rule(kind, base + ".definition", [modifier])
    for kind, style in {
        "builtinType": "type.builtin", "selfTypeKeyword": "type.self", "typeAlias": "type.alias",
        "procMacro": "function.macro", "macroBang": "function.macro", "arithmetic": "operator",
        "constParameter": "type.parameter", "character": "string", "escapeSequence": "string.escape",
        "formatSpecifier": "string.special", "lifetime": "lifetime", "label": "label",
        "selfKeyword": "variable.special", "selfParameter": "variable.special", "clsParameter": "variable.special",
    }.items():
        rule(kind, style)

    companion = {"languages": {lang: {"semantic_tokens": "combined"} for lang in ["Rust", "Python", "TypeScript", "TSX"]},
                 "global_lsp_settings": {"semantic_token_rules": rules}}
    family = {"$schema": "https://zed.dev/schema/themes/v0.2.0.json", "name": "Glacier", "author": "Max Malkin",
              "themes": [{"name": "Glacier", "appearance": "dark", "style": s}]}
    for path, data in [("themes/glacier.json", family), ("settings/semantic-highlighting.json", companion), ("palette.json", p)]:
        dest = ROOT / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Built Glacier: {len(syntax)} syntax styles, {len(rules)} semantic rules")


if __name__ == "__main__":
    build()
