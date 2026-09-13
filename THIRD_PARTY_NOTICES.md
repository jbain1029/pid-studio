# Supplied third-party notices

The portable application includes the `NOTICES` directory under `_internal`.
Open its `inventory.json` for installed versions, supplier-declared license
metadata, notice paths and SHA-256 hashes. Text files are copied byte-for-byte
from the build environment, not summarized or relicensed by this project.
The Python installation's `LICENSE.txt` is included in `Python/`.

This is a deliberately broad installed-dependency inventory, not a complete
software bill of materials. Build-tool notices are labeled separately; a listed
package is not proof that every module or binary from it was shipped. PySide6
Addons is listed because some optional Qt modules may be collected. The adjacent
`bundled-binaries.json` records the final PyInstaller binary destinations and
hashes, including Python, Qt, plugins and runtime DLLs. It does not determine
each binary's licensing terms.

## Findings and limits of this local inventory

At the September 2026 development snapshot, the installed PySide6, Essentials,
Addons and shiboken6 wheels supplied only `LicenseRef-Qt-Commercial.txt` in
their notice directories. Those short texts refer to separate commercial
agreements; they are **not evidence that this project or its user holds such an
agreement**. Metadata may describe alternative terms, but this collector does
not select a licensing pathway. Full applicable Qt/binding license texts,
third-party Qt module attributions, corresponding-source obligations and
replacement/relinking requirements have not been established by this inventory.
Do not mistake the supplied commercial reference for permission to distribute.

Other unresolved release checks include the applicable Microsoft VC runtime
redistribution terms, transitive native-library attributions (for example Qt
plugins and Python extension DLLs), and notices/source requirements not present
in wheel metadata. Python's supplied license contains several bundled-library
notices, but their presence does not prove complete coverage of this build.

Before public or third-party distribution, resolve the applicable terms for the
actual shipped files and provide any additional required notices, sources or
offers. This inventory records evidence and gaps; it is not legal advice, a
compliance certification, or a declaration that redistribution is authorized.

## Reproduction

`build.cmd` runs the collector through the packaging specification. Every build
uses a fresh `build/notices-*` staging directory; no dependency files are altered.
For an offline inspection without packaging, run:

```
.venv\Scripts\python.exe collect_notices.py build\my-new-notices-folder
```

That standalone command collects supplied notices only. The binary inventory is
added by the packaging specification after its final DLL selection.
