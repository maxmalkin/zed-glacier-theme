#!/usr/bin/env python3
"""Inspect real semantic tokens from the language servers Zed has installed locally.

Read-only LSP requests against the bundled fixtures; writes reports under .cache.
"""
import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
SERVERS = Path.home() / "Library/Application Support/Zed/languages"


class Client:
    def __init__(self, command, cwd):
        self.process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.messages = queue.Queue()
        self.next_id = 1
        self.legend = None
        self.quiescent = False
        threading.Thread(target=self.read, daemon=True).start()

    def read(self):
        try:
            while True:
                headers = {}
                while (line := self.process.stdout.readline()) not in (b"\r\n", b"\n", b""):
                    k, v = line.decode().split(":", 1)
                    headers[k.lower()] = v.strip()
                if not line:
                    return
                body = self.process.stdout.read(int(headers["content-length"]))
                self.messages.put(json.loads(body))
        except (ValueError, OSError):
            return

    def send(self, message):
        body = json.dumps({"jsonrpc": "2.0", **message}).encode()
        self.process.stdin.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
        self.process.stdin.flush()

    def notify(self, method, params):
        self.send({"method": method, "params": params})

    def request(self, method, params, timeout=30):
        request_id = self.next_id
        self.next_id += 1
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                message = self.messages.get(timeout=min(1, max(0.01, deadline - time.monotonic())))
            except queue.Empty:
                if self.process.poll() is not None:
                    raise RuntimeError(f"Language server exited: {self.process.returncode}")
                continue
            if message.get("id") == request_id and "method" not in message:
                if "error" in message:
                    raise RuntimeError(str(message["error"]))
                return message.get("result")
            if message.get("method") == "experimental/serverStatus":
                self.quiescent = message.get("params", {}).get("quiescent", False)
            if "id" in message and "method" in message:
                if message["method"] == "workspace/configuration":
                    result = [{} for _ in message.get("params", {}).get("items", [])]
                else:
                    result = None
                if message["method"] == "client/registerCapability":
                    for registration in message.get("params", {}).get("registrations", []):
                        if registration["method"] == "textDocument/semanticTokens":
                            self.legend = registration["registerOptions"].get("legend")
                self.send({"id": message["id"], "result": result})
        raise TimeoutError(method)

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()


def inspect(language):
    node = shutil.which("node") or "node"
    if language == "rust":
        binaries = [p for p in (SERVERS / "rust-analyzer").iterdir() if p.is_file() and os.access(p, os.X_OK)]
        command = [str(max(binaries, key=lambda p: p.name))]
        directory, paths = ROOT / "examples/rust", [ROOT / "examples/rust/src/lib.rs"]
        options = {"checkOnSave": False, "cargo": {"offline": True}}
    elif language == "python":
        command = [node, str(SERVERS / "basedpyright/node_modules/basedpyright/dist/pyright-langserver.js"), "--stdio"]
        directory, paths, options = ROOT / "examples/python", [ROOT / "examples/python/cache.py"], {}
    else:
        command = [node, str(SERVERS / "vtsls/node_modules/@vtsls/language-server/bin/vtsls.js"), "--stdio"]
        directory = ROOT / "examples/typescript"
        paths, options = [directory / "cache.ts", directory / "panel.tsx"], {}
    client = Client(command, directory)
    token_types = ["namespace", "type", "class", "enum", "interface", "struct", "typeParameter",
                   "parameter", "variable", "property", "enumMember", "event", "function", "method",
                   "macro", "keyword", "modifier", "comment", "string", "number", "regexp", "operator", "decorator",
                   "angle", "arithmetic", "attributeBracket", "attribute", "bitwise", "boolean", "brace", "bracket",
                   "builtinAttribute", "builtinType", "character", "colon", "comma", "comparison", "constParameter",
                   "const", "deriveHelper", "derive", "dot", "escapeSequence", "formatSpecifier", "generic",
                   "invalidEscapeSequence", "label", "lifetime", "logical", "macroBang", "negation", "parenthesis",
                   "procMacro", "punctuation", "selfKeyword", "selfTypeKeyword", "semicolon", "static", "toolModule",
                   "typeAlias", "union", "unresolvedReference"]
    modifiers = ["declaration", "definition", "readonly", "static", "deprecated", "abstract", "async", "modification", "documentation", "defaultLibrary"]
    try:
        result = client.request("initialize", {
            "processId": os.getpid(), "rootUri": directory.as_uri(),
            "workspaceFolders": [{"uri": directory.as_uri(), "name": directory.name}],
            "capabilities": {
                "experimental": {"serverStatusNotification": True},
                "workspace": {"configuration": True, "workspaceFolders": True},
                "textDocument": {"semanticTokens": {
                    "dynamicRegistration": True, "requests": {"range": False, "full": True},
                    "tokenTypes": token_types, "tokenModifiers": modifiers, "formats": ["relative"],
                    "overlappingTokenSupport": False, "multilineTokenSupport": False,
                }},
            }, "initializationOptions": options,
        })
        client.notify("initialized", {})
        legend = result.get("capabilities", {}).get("semanticTokensProvider", {}).get("legend")
        for path in paths:
            language_id = "typescriptreact" if path.suffix == ".tsx" else language
            client.notify("textDocument/didOpen", {"textDocument": {
                "uri": path.as_uri(), "languageId": language_id, "version": 1, "text": path.read_text()}})
        if language == "rust":
            for _ in range(25):
                client.request("rust-analyzer/analyzerStatus", {"textDocument": {"uri": paths[0].as_uri()}})
                if client.quiescent:
                    break
                time.sleep(1)
            if not client.quiescent:
                raise RuntimeError("rust-analyzer did not finish loading the fixture project")
        reports = []
        for path in paths:
            data = []
            for attempt in range(4):
                try:
                    response = client.request("textDocument/semanticTokens/full", {"textDocument": {"uri": path.as_uri()}}, timeout=35)
                    data = (response or {}).get("data", [])
                    if data:
                        break
                except RuntimeError:
                    if attempt == 3:
                        raise
                time.sleep(1)
            legend = legend or client.legend
            if not legend or not data:
                raise RuntimeError(f"No semantic token data for {path.name}")
            lines = path.read_text().splitlines()
            line = column = 0
            tokens = []
            for i in range(0, len(data), 5):
                dl, dc, length, type_index, mask = data[i:i + 5]
                line += dl
                column = dc if dl else column + dc
                text = lines[line].encode("utf-16-le")[column * 2:(column + length) * 2].decode("utf-16-le")
                tokens.append({"line": line, "column": column, "length": length, "text": text,
                               "type": legend["tokenTypes"][type_index],
                               "modifiers": [m for n, m in enumerate(legend["tokenModifiers"]) if mask & (1 << n)]})
            report = {"file": str(path.relative_to(ROOT)), "server": command[-2] if language != "rust" else command[0],
                      "legend": legend, "tokens": tokens}
            dest = ROOT / ".cache" / f"tokens-{path.name}.json"
            dest.parent.mkdir(exist_ok=True)
            dest.write_text(json.dumps(report, indent=2) + "\n")
            reports.append({"file": path.name, "count": len(tokens), "types": sorted({t['type'] for t in tokens}),
                            "modifiers": sorted({m for t in tokens for m in t['modifiers']})})
        print(json.dumps({"language": language, "files": reports}, indent=2), flush=True)
    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("language", choices=["rust", "python", "typescript"])
    inspect(parser.parse_args().language)
