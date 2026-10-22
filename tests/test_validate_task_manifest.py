import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_task_manifest import DEFAULT_MANIFEST, main, validate


class TaskManifestContractTests(unittest.TestCase):
    def test_checked_in_manifest_satisfies_contract(self):
        data = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(validate(data), [])

    def test_rejects_missing_base_paths_and_rollback_fields(self):
        data = {"tasks": [{
            "task_id": "T", "title": "test", "repository": "owner/repo",
            "depends_on": [], "scope": ["src"], "outputs": ["output"],
            "acceptance": ["test"], "test_command": "python -m unittest",
            "timeout_seconds": 10, "status": "PLANNED", "evidence": [],
            "execution_evidence": None
        }]}
        errors = validate(data)
        self.assertTrue(any("base_ref" in item for item in errors))
        self.assertTrue(any("permitted_paths" in item for item in errors))
        self.assertTrue(any("rollback_ref" in item for item in errors))

    def test_running_requires_provider_instance_and_observable_evidence(self):
        data = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        task = dict(data["tasks"][0])
        task.update({"task_id": "RUNNING-TEST", "status": "RUNNING", "branch": "feature/test",
                     "rollback_ref": "refs/heads/feature/test", "execution_evidence": None})
        errors = validate({"tasks": [task]})
        self.assertTrue(any("RUNNING requires provider-reported" in item for item in errors))

    def test_rejects_path_escape(self):
        data = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        task = dict(data["tasks"][0])
        task.update({"task_id": "PATH-TEST", "permitted_paths": ["../secrets"]})
        errors = validate({"tasks": [task]})
        self.assertTrue(any("must stay relative" in item for item in errors))

    def test_cli_uses_supplied_path_and_rejects_extra_arguments(self):
        with tempfile.TemporaryDirectory() as temp:
            invalid = Path(temp) / "invalid.json"
            invalid.write_text('{"tasks":[]}', encoding="utf-8")
            self.assertEqual(main([str(invalid)]), 1)
            self.assertEqual(main([str(invalid), "ignored.json"]), 2)


if __name__ == "__main__":
    unittest.main()
