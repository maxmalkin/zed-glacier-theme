#!/usr/bin/env python3
"""Download pinned Zed query references; copy supporting queries from local extensions."""
import concurrent.futures
import json
from pathlib import Path
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REVISION = "e91b82c106817f2419207ebf81f1da766698ac95"
BASE = f"https://raw.githubusercontent.com/zed-industries/zed/{REVISION}/"


def main():
    cache = ROOT / ".cache/reference"
    cache.mkdir(parents=True, exist_ok=True)
    sources = {}
    for language in ["rust", "python", "typescript", "tsx", "json", "yaml", "markdown", "markdown-inline", "bash"]:
        sources[language + ".scm"] = BASE + f"crates/grammars/src/{language}/highlights.scm"
    for language in ["rust", "python"]:
        sources[language + "-semantic.json"] = BASE + f"crates/grammars/src/{language}/semantic_token_rules.json"
    sources["default-semantic.json"] = BASE + "assets/settings/default_semantic_token_rules.json"

    def fetch(item):
        name, url = item
        if (cache / name).exists():
            return
        request = urllib.request.Request(url, headers={"User-Agent": "GlacierTheme-theme-validation"})
        data = urllib.request.urlopen(request, timeout=30).read()
        (cache / name).write_bytes(data)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(fetch, sources.items()))
    shutil.copy2(ROOT / "validation/theme-schema.json", cache / "schema.json")
    extensions = Path.home() / "Library/Application Support/Zed/extensions/installed"
    for extension in ["terraform", "toml", "dockerfile", "sql"]:
        for path in (extensions / extension).rglob("highlights.scm"):
            name = path.parent.name + ".scm"
            shutil.copy2(path, cache / name)
            sources[name] = f"installed Zed extension: {extension}/languages/{path.parent.name}/highlights.scm"
    (ROOT / "validation/sources.json").write_text(json.dumps({"zed_revision": REVISION,
        "schema_source": "https://zed.dev/schema/themes/v0.2.0.json", "references": sources}, indent=2) + "\n")
    print(f"Prepared {len(sources)} source references")


if __name__ == "__main__":
    main()
