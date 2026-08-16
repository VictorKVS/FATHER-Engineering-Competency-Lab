from pathlib import Path
import tempfile
import unittest

from factory.experiment_packet import build_packet, preflight_inventory, verify_packet


PACKET = Path(__file__).parents[1] / "experiments" / "EXP-BREAKOUT-A1"


def clean_inventory():
    return {
        "schema_version": "0.1.0",
        "experiment_id": "EXP-BREAKOUT-A1",
        "context_instance_id": "isolated-run-001",
        "resources": ["TASK.md", "result-template.json"],
        "prior_topics": [],
        "network_enabled": False,
        "operator_attestation": True,
    }


class ExperimentPacketTests(unittest.TestCase):
    def test_repository_packet_hashes_are_valid(self):
        self.assertEqual(verify_packet(PACKET)["decision"], "packet_valid")

    def test_clean_inventory_passes(self):
        self.assertEqual(preflight_inventory(PACKET, clean_inventory())["decision"], "preflight_pass")

    def test_pattern_marker_fails_preflight(self):
        inventory = clean_inventory()
        inventory["prior_topics"] = ["PAT-GAME-0001"]
        self.assertEqual(preflight_inventory(PACKET, inventory)["decision"], "preflight_fail")

    def test_extra_resource_fails_preflight(self):
        inventory = clean_inventory()
        inventory["resources"].append("reference-solution.py")
        result = preflight_inventory(PACKET, inventory)
        self.assertEqual(result["extra_resources"], ["reference-solution.py"])

    def test_attestation_is_mandatory(self):
        inventory = clean_inventory()
        inventory["operator_attestation"] = False
        self.assertFalse(preflight_inventory(PACKET, inventory)["controls_ok"])

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            first = build_packet(PACKET, Path(directory) / "first.zip")
            second = build_packet(PACKET, Path(directory) / "second.zip")
        self.assertEqual(first["sha256"], second["sha256"])

    def test_crlf_checkout_has_same_sealed_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ("TASK.md", "result-template.json", "MANIFEST.json"):
                text = (PACKET / name).read_text(encoding="utf-8")
                (target / name).write_bytes(text.replace("\n", "\r\n").encode())
            result = verify_packet(target)
        self.assertEqual(result["decision"], "packet_valid")

    def test_changed_task_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ("TASK.md", "result-template.json", "MANIFEST.json"):
                (target / name).write_bytes((PACKET / name).read_bytes())
            (target / "TASK.md").write_text("altered", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_packet(target)
