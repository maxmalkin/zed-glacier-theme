# Coverage notes

The theme is validated against the official Zed theme schema and audited current source definitions. The JSON report records exact scope lists, real semantic-token counts, and minimum contrast for each tested background.

| Language | Checked | Practical limits |
| --- | --- | --- |
| Rust | Traits, structs, types, generics, lifetimes, parameters, fields, macros, attributes, enum variants, mutability, unsafe operations, format placeholders | Requires rust-analyzer to finish loading the Cargo project. Initial responses can misclassify unresolved identifiers. |
| Python | Classes, decorators, methods, parameters, properties, type parameters, `self`/`cls`, readonly constants, builtins, f-strings | Basedpyright may classify decorator factories as ordinary functions and property getters as properties. Semantic highlighting follows those reported roles. |
| TypeScript | Interfaces, classes, type parameters, aliases, fields, readonly values, parameters, enum members, methods, template strings, regex | Some distinctions share a server token type. No language-specific meaning is inferred from arbitrary identifier spelling. |
| TSX | Components, intrinsic tags, props, parameters, readonly members, embedded expressions | Semantic tokens can color callable props as functions; not every JSX identifier receives a semantic token. |
| Markdown | Headings, lists, links, emphasis, inline code, fenced Rust/Python/TypeScript | Raw editor syntax and rendered Markdown preview are separate surfaces. The theme schema has no general syntax-strikethrough field; source strikethrough markup is muted and italic. |
| Terraform / HCL | Blocks, labels, functions, scalar literals, interpolations, operators, references | The installed grammar uses `variable` for many attributes, object keys, and references, so those share white. No custom grammar patches or Terraform semantic server were used. |
| YAML | Keys, scalar values, numbers, booleans, null, anchors, aliases, tags, block strings | Some punctuation and special forms share grammar captures. |
| JSON / TOML | Keys versus values, tables, arrays, comments where legal, scalar literals | Formatting follows the language query; no schema-aware coloring is implied. |
| Bash | Commands/functions, variables, special variables, strings, regex, operators, directives | Tree-sitter validation only. |
| Dockerfile / SQL | Existing extension capture inventories and representative source files | Capture coverage was audited; language-server behavior was not exercised. |

## Validation performed

- Theme schema and explicit current-field validation.
- Every non-private capture in sixteen query sets resolves to a theme style.
- All custom semantic-rule style references exist in the theme.
- Real language-server token responses are mapped using Zed’s layered rule precedence.
- Parameter/field and enum/variant distinctions, mutable binding italics, and unsafe color are checked against real Rust fixture tokens. All syntax styles are required to use regular font weight.
- Core fixtures parse, and Rust and TypeScript pass their compilers. Python passes bytecode compilation.
- Syntax contrast is measured against eleven background states; current minimum values are recorded in `report.json`.
- Supporting fixtures and Markdown code injections are checked with their Tree-sitter highlight queries.
- Zed successfully opened the sample project after activation; recent logs contained no theme or semantic-settings errors.

Use Zed’s `dev: open highlights tree view` to investigate how a particular token is styled in the editor.

## Reproduce the full validation

On macOS with Zed’s language servers and supporting language extensions installed:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/prepare_validation.py
.venv/bin/python scripts/inspect_tokens.py rust
.venv/bin/python scripts/inspect_tokens.py python
.venv/bin/python scripts/inspect_tokens.py typescript
.venv/bin/python scripts/validate.py
```
