# Publishing Glacier

The extension is prepared as `glacier-theme`, version `0.1.0`. The root manifest declares only `themes/glacier.json`; examples, settings recommendations, previews, and validation scripts are development resources.

1. Run `python3 scripts/build.py` and `python3 scripts/check_package.py` with `jsonschema` installed. Confirm `git diff --exit-code` is clean so the checked-in theme matches the generator.
2. In Zed’s Extensions page, choose **Install Dev Extension** and select this repository. Select **Glacier**, then manually review the examples at the exact commit you intend to submit. The optional semantic settings must be merged separately into user settings; the extension does not apply them automatically.
3. Fork and clone [zed-industries/extensions](https://github.com/zed-industries/extensions).
4. Add this repository as `extensions/glacier-theme` using `git submodule add https://github.com/maxmalkin/zed-glacier-theme.git extensions/glacier-theme`. Keep the submodule pinned to the tested commit.
5. Add the following to that repository’s `extensions.toml`:

   ```toml
   [glacier-theme]
   submodule = "extensions/glacier-theme"
   version = "0.1.0"
   ```

6. Run the extension registry’s required checks and open a pull request there. Include a preview and the supported language focus.

Committing this repository does not publish it to Zed’s extension store. The registry pull request is a separate step.

For updates, increment `extension.toml` and the changelog, test the new commit, then update the registry’s submodule pointer and version. Follow Zed’s current [publishing guide](https://zed.dev/docs/extensions/publishing/publishing-guide), [prerequisites](https://zed.dev/docs/extensions/publishing/prerequisites), and [license requirements](https://zed.dev/docs/extensions/publishing/license-requirements).
