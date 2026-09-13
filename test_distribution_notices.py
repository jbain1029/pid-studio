import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import collect_notices


class DistributionNoticesTests(unittest.TestCase):
    def test_supplied_notices_are_copied_with_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = collect_notices.collect(Path(temporary) / 'NOTICES')
            inventory = json.loads((output / 'inventory.json').read_text(encoding='utf-8'))
            packages = {item['name']: item for item in inventory['packages']}
            self.assertIn('Python', packages)
            self.assertIn('PySide6_Essentials', packages)
            for package in packages.values():
                self.assertTrue(package['version'])
                self.assertTrue(package['notices'], package['name'])
                for notice in package['notices']:
                    actual = hashlib.sha256((output / notice['path']).read_bytes()).hexdigest()
                    self.assertEqual(actual, notice['sha256'])
            self.assertIn('not legal advice', (output / 'README.md').read_text(encoding='utf-8'))
            with self.assertRaises(FileExistsError):
                collect_notices.collect(output)

    def test_notice_filter_excludes_code(self):
        self.assertTrue(collect_notices.is_notice('licenses/LICENSE.BSD'))
        self.assertTrue(collect_notices.is_notice('COPYING'))
        self.assertFalse(collect_notices.is_notice('licenses.py'))
        self.assertFalse(collect_notices.is_notice('licenses/__init__.py'))


if __name__ == '__main__':
    unittest.main()
