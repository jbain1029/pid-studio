# Windows portable folder; resource paths mirror source-module paths.
from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path
import PySide6
import hashlib
import json
import tempfile
from collect_notices import collect

notice_parent = Path(tempfile.mkdtemp(prefix='notices-', dir='build'))
notice_folder = collect(notice_parent / 'NOTICES')

a = Analysis(
    ['run_studio.py'],
    pathex=[],
    binaries=[],
    datas=[('document.schema.json', '.'), ('ai/AUTHORING.md', 'ai'),
           ('ai/OPENAI_SETUP.md', 'ai'), ('README.md', '.'),
           ('examples/transfer-system.pid', 'examples'), ('SYMBOLS.md','.'),
           ('examples/sight-glass.pidsymbol','examples'), ('SHEET_STANDARDS.md','.'), ('COMPONENTS.md','.'),
           ('LEGEND_REFERENCE.md','.'),
           ('research/SYMBOL_STUDY.md','research'), ('research/STUDY_STATUS.md','research'),
           ('research/process-audit.md','research'), ('research/valves-audit.md','research'),
           ('research/instruments-audit.md','research'),
           ('research/VALVE_DIRECTION_FOLLOWUP.md','research'),
           ('research/SPECIALIZED_INSTRUMENT_FOLLOWUP.md','research'),
           ('examples/sketch-corpus','examples/sketch-corpus'),
           (str(notice_folder), 'NOTICES')],
    hiddenimports=collect_submodules('keyring.backends'),
    hookspath=[], runtime_hooks=[], excludes=['tkinter'], noarchive=False,
)
# Python's older VC runtime can be loaded first by the bootloader. Use the
# runtime shipped with this Qt wheel consistently at the bundle root as well.
qt_folder = Path(PySide6.__file__).parent
# Qt uses Windows' ICU forwarding DLL. A third-party Poppler installation on
# PATH can otherwise supply an incompatible ICU with version-suffixed exports.
a.binaries = [entry for entry in a.binaries
              if Path(entry[0]).name.lower() not in ('icuuc.dll', 'icudt78.dll')]
for index, (destination, source, kind) in enumerate(a.binaries):
    if destination.lower() in ('vcruntime140.dll', 'vcruntime140_1.dll'):
        a.binaries[index] = (destination, str(qt_folder / destination.lower()), kind)
binary_inventory = notice_folder / 'bundled-binaries.json'
binary_inventory.write_text(json.dumps([
    {'path': destination, 'sha256': hashlib.sha256(Path(source).read_bytes()).hexdigest()}
    for destination, source, kind in a.binaries
], indent=2) + '\n', encoding='utf-8')
# This file was created after Analysis expanded the directory data entry.
a.datas.append(('NOTICES/bundled-binaries.json', str(binary_inventory), 'DATA'))
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='PIDStudio',
          debug=False, strip=False, upx=False, console=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='PIDStudio')
