"""Ensure the evidence matrix does not silently omit new built-in components."""
from pathlib import Path
import re
import unittest

import pidcore as core


class StudyInventoryTests(unittest.TestCase):
    def test_every_builtin_has_exactly_one_baseline_assessment(self):
        folder = Path(__file__).parent / 'research'
        identifiers = []
        for filename, expected in (('process-audit.md', 45),
                                   ('valves-audit.md', 49),
                                   ('instruments-audit.md', 47)):
            text = (folder / filename).read_text(encoding='utf-8')
            rows = re.findall(r'^\| `([^`]+)`(?: / [^|]+)? \| (?:SF|M|P|U|Supported family|Mismatch|Project-specific|Unresolved) \|', text, re.M)
            self.assertEqual(len(rows), expected, filename)
            identifiers.extend(rows)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(set(identifiers), set(core.CATALOG))


if __name__ == '__main__':
    unittest.main()
