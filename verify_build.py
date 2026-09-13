"""Run the real portable executable, with no source checkout in its working path."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parent
    executable = root / 'dist' / 'PIDStudio' / 'PIDStudio.exe'
    if not executable.is_file():
        raise SystemExit('Build PIDStudio.exe first.')
    parent = Path(tempfile.mkdtemp(prefix='packaged-check-', dir=root / 'build'))
    output = parent / 'results'
    environment = os.environ.copy()
    # Keep verification independent of local Python/Qt/Poppler installations.
    for key in list(environment):
        if key.startswith(('PYTHON', 'QT_', 'PYSIDE', 'OPENAI_')):
            environment.pop(key)
    system_root = Path(environment.get('SystemRoot', 'C:/Windows'))
    environment['PATH'] = os.pathsep.join([str(system_root / 'System32'), str(system_root)])
    result = subprocess.run([str(executable), '--smoke-test', str(output)],
                            cwd=parent, env=environment, timeout=60, check=False,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    error_file = Path(str(output) + '.error.txt')
    if result.returncode or not (output / 'result.json').is_file():
        detail = error_file.read_text(encoding='utf-8') if error_file.exists() else 'No result file.'
        raise SystemExit(f'Packaged check failed ({result.returncode}): {detail}\nArtifacts: {parent}')
    report = json.loads((output / 'result.json').read_text(encoding='utf-8'))
    if report.get('passed') is not True or report.get('frozen') is not True:
        raise SystemExit(f'Packaged check did not confirm a frozen executable: {report}')
    report['executable_sha256'] = hashlib.sha256(executable.read_bytes()).hexdigest()
    report['sanitized_environment'] = True
    notices = executable.parent / '_internal' / 'NOTICES'
    inventory = json.loads((notices / 'inventory.json').read_text(encoding='utf-8'))
    for package in inventory['packages']:
        for notice in package['notices']:
            path = (notices / notice['path']).resolve()
            if not path.is_relative_to(notices.resolve()):
                raise SystemExit('Notice inventory contains an unsafe path.')
            if hashlib.sha256(path.read_bytes()).hexdigest() != notice['sha256']:
                raise SystemExit(f'Bundled notice differs from its inventory: {notice["path"]}')
    binaries = json.loads((notices / 'bundled-binaries.json').read_text(encoding='utf-8'))
    for binary in binaries:
        path = (executable.parent / '_internal' / binary['path']).resolve()
        if not path.is_relative_to((executable.parent / '_internal').resolve()):
            raise SystemExit('Binary inventory contains an unsafe path.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != binary['sha256']:
            raise SystemExit(f'Bundled binary differs from its inventory: {binary["path"]}')
    report['checks'].extend(['custom symbol library and contextual AI types',
                             'supplier notice and binary inventory hashes'])
    (parent / 'verified-build.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'Packaged application checks passed. Evidence: {parent}')


if __name__ == '__main__':
    main()
