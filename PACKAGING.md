# Windows portable build

Run `build.cmd` from a source checkout with Python installed. It runs the tests,
builds `dist/PIDStudio/PIDStudio.exe`, and verifies that executable before reporting success. Building requires downloading PyInstaller;
running the completed folder does not require a separate Python installation.

Keep the entire `dist/PIDStudio` folder together, including `_internal`. Copy that
folder to the desired location and double-click `PIDStudio.exe`. Save drawings
outside `_internal`; it contains application resources, not user documents.
The example drawing is in `_internal/examples/transfer-system.pid`.

This is an unsigned portable application, not an installer. Windows may display
an unknown-publisher warning. There is no automatic update service, file association,
or registry installation. Layout/recovery data still uses the user's local profile.
API credentials are not bundled; OpenAI remains optional and requires the user's key.
The build targets modern 64-bit Windows with the system ICU library (tested here
on Windows 11). Third-party ICU copies found on the builder's PATH are excluded.

## Offline verification

Run `PIDStudio.exe --smoke-test "C:\some\new-output-folder"` and wait for the
process to exit. The output directory must not already exist. `result.json` must
report `passed: true` and `frozen: true`. The check creates a window offscreen,
roundtrips a drawing, reads the packaged schema/AI instructions, exports SVG,
draw.io, PDF and PNG, reopens PDF/PNG, and captures the workbench. It does not
test live API access, a physical printer, or another machine's Windows environment.

The check also exercises nudge, rotation, endpoint reconnection, actual viewport
mouse events for both click-click and drag-to-connect, new-line selection, undo, clear example
routes, review acknowledgment gating, saved review history, recovery browsing,
direct file opening, readable PDF text, and pixel-equivalence between the sheet preview and PNG export. The build
runner `verify_build.py` starts the executable in a separate working directory with
local Python/Qt/API environment settings removed and a Windows-only PATH. Evidence
is retained in a unique `build/packaged-check-*` folder: result JSON, executable
SHA-256, exported files, workbench screenshot and sheet-preview screenshot. This
does not replace clean-machine testing.

Development verification: 2026-09-11, Windows 11 x64, Python 3.14.2,
PyInstaller 6.22.2, PySide6 6.11.2. The rebuilt executable passed from a different
working directory; its workbench screenshot was inspected and PDF equipment text
was extracted successfully. `build.cmd` reruns the entire current source suite
before building; each build's test count is recorded in its command output.

The spec preserves data paths relative to the Python modules, following the
[PyInstaller resource documentation](https://pyinstaller.org/en/stable/runtime-information.html).

The build copies supplier-provided dependency notices to `_internal/NOTICES`,
with version/hash inventory and the final collected binary inventory. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for access, reproduction and
unresolved release checks. The local Qt wheels supply a commercial-reference
notice only; this does not establish a commercial license or complete open-source
notice/source obligations. Public redistribution is not declared ready by this
inventory. Resolve applicable terms before outside distribution and test on a
clean Windows machine. A same-machine smoke test is not a clean-machine test.
