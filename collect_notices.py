"""Copy installed, supplier-provided notices without rewriting their text.

Build evidence, not a license-compliance decision. No network access.
"""
from __future__ import annotations

import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import shutil
import sys


RUNTIME_DISTRIBUTIONS = (
    'PySide6', 'PySide6_Essentials', 'PySide6_Addons', 'shiboken6',
    'jsonschema', 'jsonschema-specifications', 'attrs', 'referencing',
    'rpds-py', 'keyring', 'jaraco.classes', 'jaraco.context',
    'jaraco.functools', 'more-itertools', 'pywin32-ctypes',
)
BUILD_DISTRIBUTIONS = ('pyinstaller', 'pyinstaller-hooks-contrib', 'altgraph',
                       'packaging', 'pefile', 'setuptools')


def is_notice(path):
    """Only supplied notice files, never modules named 'licenses'."""
    path = Path(path)
    name = path.name.upper()
    return (name.startswith(('LICENSE', 'COPYING', 'NOTICE', 'AUTHORS'))
            and path.suffix.lower() not in ('.py', '.pyc', '.pyd'))


def collect(output):
    output = Path(output)
    # A fresh staging directory prevents notices from a previous environment
    # being silently attributed to this build. Never remove a supplied path.
    output.mkdir(parents=True, exist_ok=False)
    entries = []

    def copy(source, relative):
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        return {'path': relative.as_posix(),
                'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}

    python_license = Path(sys.base_prefix) / 'LICENSE.txt'
    if not python_license.is_file():
        raise RuntimeError('The Python installation has no supplied LICENSE.txt')
    entries.append({'name': 'Python', 'version': sys.version.split()[0],
                    'role': 'runtime',
                    'notices': [copy(python_license, Path('Python/LICENSE.txt'))]})
    for name in RUNTIME_DISTRIBUTIONS + BUILD_DISTRIBUTIONS:
        distribution = metadata.distribution(name)
        notices = []
        for supplied in distribution.files or ():
            if not is_notice(supplied):
                continue
            # RECORD paths can include ../ scripts. Only accept safe relative
            # package paths for notices copied into this output directory.
            relative = Path(str(supplied))
            if relative.is_absolute() or '..' in relative.parts:
                continue
            source = Path(distribution.locate_file(supplied))
            if source.is_file():
                notices.append(copy(source, Path(name) / relative))
        entries.append({'name': name, 'version': distribution.version,
                        'role': ('runtime candidate' if name in RUNTIME_DISTRIBUTIONS
                                 else 'build tool; not necessarily bundled'),
                        'declared_license': distribution.metadata.get('License-Expression')
                            or distribution.metadata.get('License') or None,
                        'notices': notices})
    manifest = {'format': 'pid-studio-supplied-notices', 'version': 1,
                'scope': 'Installed dependency notice inventory; not a complete SBOM or legal approval.',
                'packages': entries}
    (output / 'inventory.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    shutil.copyfile(Path(__file__).with_name('THIRD_PARTY_NOTICES.md'), output / 'README.md')
    return output


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python collect_notices.py NEW_OUTPUT_DIRECTORY')
    print(collect(sys.argv[1]))
