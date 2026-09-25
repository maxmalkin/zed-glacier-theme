#!/usr/bin/env python3
"""Build an offline, interactive review gallery from the generated theme."""
import argparse
import html
import json
from highlighting import ROOT, THEME, highlighted

SAMPLES = [
    ("Rust", "rust", "examples/rust/src/lib.rs"),
    ("Python", "python", "examples/python/cache.py"),
    ("TypeScript", "typescript", "examples/typescript/cache.ts"),
    ("TSX", "tsx", "examples/typescript/panel.tsx"),
    ("Markdown", "markdown", "examples/guide.md"),
    ("Terraform", "terraform", "examples/main.tf"),
    ("YAML", "yaml", "examples/config.yml"),
    ("JSON", "json", "examples/config.json"),
    ("TOML", "toml", "examples/config.toml"),
    ("Bash", "bash", "examples/start.sh"),
]


def render(path, language, semantic):
    source = path.read_text()
    report = ROOT / ".cache" / f"tokens-{path.name}.json" if semantic else None
    chunks, errors = highlighted(source, language, report)
    assert not errors, (path.name, "parse errors")
    lines = [""]
    for text, style, scope in chunks:
        css = f"color:{style['color']};font-weight:{style.get('font_weight',400)};font-style:{style.get('font_style','normal')}"
        if style.get("strikethrough"):
            css += ";text-decoration:line-through"
        parts = text.split("\n")
        for index, part in enumerate(parts):
            if index:
                lines.append("")
            if part:
                lines[-1] += f'<span title="{html.escape(scope)}" style="{css}">{html.escape(part)}</span>'
    if not lines[-1]:
        lines.pop()
    return "".join(f'<div class="code-line"><span class="ln">{i}</span><span>{line or " "}</span></div>' for i, line in enumerate(lines, 1))


def main(screenshots):
    records = []
    for label, language, file in SAMPLES:
        path = ROOT / file
        records.append({"label": label, "language": language, "name": path.name,
                        "base": render(path, language, False), "semantic": render(path, language, True),
                        "hasSemantic": (ROOT / ".cache" / f"tokens-{path.name}.json").exists()})
    palette = json.loads((ROOT / "palette.json").read_text())
    swatches = "".join(f'<div class="swatch"><i style="background:{palette[role]}"></i><span>{role}</span><code>{palette[role]}</code></div>'
                        for role in ["keyword", "function", "type", "property", "parameter", "string", "number", "constant", "attribute", "generic", "comment"])
    tabs = "".join(f'<button data-index="{i}">{record["label"]}</button>' for i, record in enumerate(records))
    ansi = "".join(f'<i style="background:{THEME["terminal.ansi."+prefix+color]}"></i>'
                   for prefix in ("", "bright_") for color in ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"))
    template = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Glacier — syntax review</title>
<style>
:root{color-scheme:dark;--bg:#2F3D4E;--panel:#273342;--fg:#F8F8F3;--gold:#EACD45;--muted:#A3AFBC;--border:#4B5D70}
*{box-sizing:border-box}body{margin:0;padding:36px;background:#1B242E;color:var(--fg);font:14px -apple-system,BlinkMacSystemFont,sans-serif}
main{max-width:1440px;margin:auto}header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;gap:24px}
h1{font-size:30px;letter-spacing:-.7px;margin:0 0 8px;font-weight:600}.intro{color:var(--muted);margin:0;font-size:14px;line-height:1.6}
.tag{color:var(--gold);border:1px solid #796F3C;border-radius:20px;padding:8px 14px;white-space:nowrap;font-size:12px}
.workbench{overflow:hidden;border:1px solid var(--border);border-radius:10px;background:var(--bg);box-shadow:0 12px 32px #0003}
.titlebar{background:var(--panel);padding:14px 20px;border-bottom:1px solid #3B4B5E;display:flex;gap:20px;align-items:center;color:var(--muted);font-size:12px}
.traffic{display:flex;gap:8px}.traffic i{width:11px;height:11px;border-radius:50%;background:#F08B75}.traffic i:nth-child(2){background:#EACD45}.traffic i:nth-child(3){background:#A0D88A}
.titlebar label{margin-left:auto;display:flex;gap:8px;align-items:center;cursor:pointer}input{accent-color:var(--gold)}
nav{display:flex;overflow-x:auto;background:var(--panel);border-bottom:1px solid #3B4B5E}
nav button{background:none;color:var(--muted);border:0;border-bottom:2px solid transparent;padding:15px 20px;font:inherit;cursor:pointer;white-space:nowrap}
nav button[aria-selected=true]{background:var(--bg);color:var(--fg);border-bottom-color:var(--gold)}button:hover{color:var(--fg)}button:focus-visible{outline:2px solid var(--gold);outline-offset:-3px}
.editor{display:grid;grid-template-columns:180px minmax(0,1fr)}aside{background:var(--panel);border-right:1px solid #3B4B5E;padding:22px 16px;color:var(--muted);font-size:12px}
.caption{font-size:10px;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:18px;color:var(--fg)}.tree{line-height:2.2}.tree .file{color:var(--gold)}
.code-scroll{height:700px;overflow:auto;padding:18px 16px 30px 0}.code-line{display:flex;white-space:pre;font:14px/1.85 Menlo,Consolas,monospace;min-height:25.9px}.code-line:hover{background:#2B394A}
.ln{display:inline-block;flex-shrink:0;min-width:58px;text-align:right;padding-right:22px;color:#8DA0B5;user-select:none}
.code-line::selection,.code-line span::selection{background:#192D43}.status{display:flex;gap:20px;justify-content:space-between;background:var(--panel);color:var(--muted);font-size:11px;padding:11px 18px;border-top:1px solid #3B4B5E}
.status b{font-weight:500;color:var(--gold)}.palette{display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:12px;margin:22px 0}.swatch{display:grid;grid-template-columns:13px 1fr;align-items:center;gap:6px;color:var(--fg);font-size:12px}.swatch i{width:10px;height:10px;border-radius:3px}.swatch code{grid-column:2;font-size:10px;color:var(--muted)}
.details{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:22px}.detail{background:var(--panel);border:1px solid #3B4B5E;border-radius:8px;padding:18px 20px}.detail h2{margin:0 0 12px;font-size:13px;font-weight:500}.detail p{color:var(--muted);font-size:12px;line-height:1.6;margin:10px 0 0}.ansi{display:grid;grid-template-columns:repeat(8,1fr);max-width:400px}.ansi i{height:20px}
.states{display:flex;gap:8px;flex-wrap:wrap}.states span{padding:7px 10px;border-radius:4px;font:12px Menlo,monospace}.selected{background:#192D43;color:#C296F8}.search{background:#3B3927;color:#EACD45}.added{background:#253D37;color:#A0D88A}.deleted{background:#433139;color:#FFA39E}
footer{font-size:11px;line-height:1.6;color:var(--muted);margin-top:20px}a{color:#9FDEFA}@media(max-width:800px){body{padding:16px}.editor{grid-template-columns:1fr}aside{display:none}.details{grid-template-columns:1fr}.tag{display:none}.titlebar{padding:12px}.code-line{font-size:12px}nav button{padding:12px}.code-scroll{height:600px}}
</style>
<main><header><div><h1>Glacier</h1><p class="intro">Blue-gray surfaces. Gold accents. A distinct role for every useful color.</p></div><div class="tag">Maximum syntax distinction</div></header>
<section class="workbench" aria-label="Interactive syntax preview"><div class="titlebar"><div class="traffic" aria-hidden="true"><i></i><i></i><i></i></div><span>glacier / examples</span><label><input id="semantic" type="checkbox" checked> Semantic highlighting</label></div>
<nav role="tablist" aria-label="Sample language">@@TABS@@</nav>
<div class="editor"><aside><div class="caption">Explorer</div><div class="tree">⌄ examples<br>　⌄ <span id="folder">rust</span><br>　　<span class="file" id="file">lib.rs</span></div><div class="caption" style="margin-top:32px">Syntax guide</div><div class="tree">Regular weight<br>Italic: semantic detail<br>Gold: callable<br>Cyan: type<br>Peach: parameter<br>Blue: property<br>Mint: generic / lifetime</div></aside><div class="code-scroll" id="code" role="tabpanel" aria-label="Highlighted sample code"></div></div>
<div class="status"><span><b>Glacier</b> &nbsp; • &nbsp; 117 syntax styles</span><span id="mode">Tree-sitter + semantic tokens</span><span id="language">Rust</span></div></section>
<section class="palette" aria-label="Syntax palette">@@SWATCHES@@</section>
<section class="details"><div class="detail"><h2>Editor states</h2><div class="states"><span class="selected">selection</span><span class="search">search match</span><span class="added">+ added</span><span class="deleted">− removed</span></div><p>All syntax foregrounds maintain at least 4.5:1 contrast across the eleven backgrounds checked.</p></div><div class="detail"><h2>Integrated terminal</h2><div class="ansi" aria-label="Normal and bright ANSI palette">@@ANSI@@</div><p>Colors derived from the reference image, brightened for readable terminal output.</p></div></section>
<footer>This browser preview uses Zed highlight queries and recorded responses from the installed language servers. It approximates editor rendering; it is not a screenshot of Zed. Hover a token to inspect its category. Terraform’s grammar groups some attributes and references together.</footer>
</main><script>
const samples=@@RECORDS@@;let selected=0;
const buttons=[...document.querySelectorAll('nav button')],toggle=document.querySelector('#semantic');
function show(index){selected=index;const s=samples[index];buttons.forEach((b,i)=>{b.setAttribute('role','tab');b.setAttribute('aria-selected',String(i===index));b.tabIndex=i===index?0:-1});document.querySelector('#code').innerHTML=toggle.checked?s.semantic:s.base;document.querySelector('#code').scrollTop=0;document.querySelector('#file').textContent=s.name;document.querySelector('#folder').textContent=s.language;document.querySelector('#language').textContent=s.label;document.querySelector('#mode').textContent=toggle.checked&&s.hasSemantic?'Tree-sitter + semantic tokens':'Tree-sitter';toggle.disabled=!s.hasSemantic;document.title=`${s.label} — Glacier`;}
buttons.forEach((b,i)=>{b.addEventListener('click',()=>show(i));b.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();const n=(i+(e.key==='ArrowRight'?1:-1)+samples.length)%samples.length;show(n);buttons[n].focus()}})});toggle.addEventListener('change',()=>show(selected));show(0);
</script></html>'''
    for old, new in [("#EACD45", palette["function"]), ("#C296F8", palette["keyword"]), ("#A0D88A", palette["string"]), ("#9FDEFA", palette["type"])]:
        template = template.replace(old, new)
    for marker, value in {"TABS": tabs, "SWATCHES": swatches, "ANSI": ansi, "RECORDS": json.dumps(records).replace("</", "<\\/")}.items():
        template = template.replace("@@" + marker + "@@", value)
    dest = ROOT / "previews/index.html"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(template)
    print(f"Built {len(records)} interactive language previews")
    if screenshots:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1200}, device_scale_factor=1)
            page.goto(dest.as_uri())
            for i, name in [(0, "rust"), (1, "python"), (2, "typescript"), (3, "tsx"), (5, "terraform")]:
                page.locator(f'button[data-index="{i}"]').click()
                page.screenshot(path=str(dest.parent / f"{name}.png"), full_page=True)
            browser.close()
        print("Saved five preview screenshots")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshots", action="store_true")
    main(parser.parse_args().screenshots)
