# Glacier

A blue-gray dark theme for Zed with vibrant, regular-weight syntax highlighting for Rust, Python, and TypeScript. Also supports Markdown, Terraform, YAML, and other common formats.

## Install

Clone this repository, choose **Install Dev Extension** in Zed, and select the repository folder. Then select **Glacier** in the theme selector.

Alternatively, copy [themes/glacier.json](themes/glacier.json) to `~/.config/zed/themes/` (macOS/Linux) or `%APPDATA%\Zed\themes\` (Windows).

For richer language distinctions, merge the optional [semantic settings](settings/semantic-highlighting.json) into your existing Zed settings. The extension does not enable them automatically.

## Development

Requires Python 3.11+ and `jsonschema`.

```sh
python3 scripts/build.py
python3 scripts/check_package.py
```

[Coverage and validation](validation/COVERAGE.md) · [Publishing](PUBLISHING.md) · [MIT license](LICENSE)
