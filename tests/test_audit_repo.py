import tempfile
import unittest
from pathlib import Path
from scripts.audit_repo import audit_repository

class AuditRepositoryTests(unittest.TestCase):
    def test_empty_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            report = audit_repository(temp)
        self.assertEqual(report['status'], 'NO_SOURCE_EVIDENCE')
        self.assertFalse(report['gates']['source_code_present'])

    def test_detects_engineering_evidence_and_heuristics(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'src').mkdir()
            (root / 'tests').mkdir()
            (root / '.github' / 'workflows').mkdir(parents=True)
            (root / 'pyproject.toml').write_text('[project]\nname="sample"\n', encoding='utf-8')
            (root / 'src' / 'network.py').write_text('import numpy as np\n# simulation harness\nadjacency = np.zeros((4,4,4))\ndef connect(): return requests.get("https://example.invalid")\n', encoding='utf-8')
            (root / 'tests' / 'test_network.py').write_text('def test_shape(): assert True\n', encoding='utf-8')
            (root / '.github' / 'workflows' / 'ci.yml').write_text('name: test\n', encoding='utf-8')
            report = audit_repository(root)
        self.assertEqual(report['status'], 'ENGINEERING_EVIDENCE_PRESENT_RUNTIME_NOT_PROVEN')
        self.assertTrue(report['gates']['tests_present'])
        self.assertTrue(report['gates']['ci_present'])
        self.assertTrue(report['gates']['multidimensional_array_or_tensor_evidence'])
        self.assertTrue(report['gates']['network_integration_evidence'])
        self.assertTrue(report['gates']['graph_or_mycelium_network_evidence'])
        self.assertGreater(report['heuristic_signals']['simulation_terms'], 0)

    def test_invalid_path(self):
        with self.assertRaises(ValueError):
            audit_repository('/path/that/does/not/exist/for-test')

if __name__ == '__main__':
    unittest.main()
