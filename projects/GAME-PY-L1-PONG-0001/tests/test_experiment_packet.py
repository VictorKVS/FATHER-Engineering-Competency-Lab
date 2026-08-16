import json
from pathlib import Path
import shutil
import tempfile
import unittest

from factory.experiment_packet import build_packet, canonical_text, compare_arms, digest, preflight_inventory, verify_packet


ROOT = Path(__file__).parents[1]
BASELINE = ROOT / "experiments" / "EXP-BREAKOUT-A1"
TREATMENT = ROOT / "experiments" / "EXP-BREAKOUT-B1"


def clean_inventory(packet=BASELINE):
    manifest = json.loads((packet / "MANIFEST.json").read_text(encoding="utf-8"))
    return {"schema_version": "0.1.0", "experiment_id": manifest["experiment_id"], "context_instance_id": "isolated-run-001", "resources": sorted(manifest["allowed_files"]), "prior_topics": [], "network_enabled": False, "operator_attestation": True}


def reseal(packet):
    manifest_path = packet / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    combined = bytearray()
    for name in sorted(manifest["allowed_files"]):
        data = canonical_text(packet / name)
        manifest["allowed_files"][name] = digest(data)
        combined.extend(data)
    manifest["allowed_context_sha256"] = digest(bytes(combined))
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


class ExperimentPacketTests(unittest.TestCase):
    def test_repository_packet_hashes_are_valid(self):
        self.assertEqual(verify_packet(BASELINE)["decision"], "packet_valid")
        self.assertEqual(verify_packet(TREATMENT)["decision"], "packet_valid")

    def test_clean_inventory_passes(self):
        self.assertEqual(preflight_inventory(BASELINE, clean_inventory())["decision"], "preflight_pass")
        self.assertEqual(preflight_inventory(TREATMENT, clean_inventory(TREATMENT))["decision"], "preflight_pass")

    def test_pattern_marker_fails_baseline_preflight(self):
        inventory = clean_inventory()
        inventory["prior_topics"] = ["PAT-GAME-0001"]
        self.assertEqual(preflight_inventory(BASELINE, inventory)["decision"], "preflight_fail")

    def test_extra_resource_fails_preflight(self):
        inventory = clean_inventory()
        inventory["resources"].append("reference-solution.py")
        self.assertEqual(preflight_inventory(BASELINE, inventory)["extra_resources"], ["reference-solution.py"])

    def test_attestation_is_mandatory(self):
        inventory = clean_inventory()
        inventory["operator_attestation"] = False
        self.assertFalse(preflight_inventory(BASELINE, inventory)["controls_ok"])

    def test_both_builds_are_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            for packet in (BASELINE, TREATMENT):
                first = build_packet(packet, Path(directory) / f"{packet.name}-1.zip")
                second = build_packet(packet, Path(directory) / f"{packet.name}-2.zip")
                self.assertEqual(first["sha256"], second["sha256"])

    def test_crlf_checkout_has_same_baseline_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ("TASK.md", "result-template.json", "MANIFEST.json"):
                text = (BASELINE / name).read_text(encoding="utf-8")
                (target / name).write_bytes(text.replace("\n", "\r\n").encode())
            self.assertEqual(verify_packet(target)["decision"], "packet_valid")

    def test_changed_task_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ("TASK.md", "result-template.json", "MANIFEST.json"):
                shutil.copy2(BASELINE / name, target / name)
            (target / "TASK.md").write_text("altered", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_packet(target)

    def test_pair_diff_allows_only_factory_knowledge(self):
        result = compare_arms(BASELINE, TREATMENT)
        self.assertEqual(result["decision"], "paired_packets_valid")
        self.assertEqual(result["treatment_additions"], ["ANTI-GAME-0001.md", "PAT-GAME-0001.md"])

    def test_budget_drift_is_rejected_even_when_resealed(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            a, b = project / "experiments" / BASELINE.name, project / "experiments" / TREATMENT.name
            shutil.copytree(BASELINE, a); shutil.copytree(TREATMENT, b)
            shutil.copytree(ROOT / "factory-assets", project / "factory-assets")
            result = json.loads((b / "result-template.json").read_text())
            result["budget"]["wall_clock_minutes"] = 60
            (b / "result-template.json").write_text(json.dumps(result, indent=2) + "\n")
            reseal(b)
            with self.assertRaisesRegex(ValueError, "budget drift"):
                compare_arms(a, b)

    def test_knowledge_snapshot_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            a, b = project / "experiments" / BASELINE.name, project / "experiments" / TREATMENT.name
            shutil.copytree(BASELINE, a); shutil.copytree(TREATMENT, b)
            shutil.copytree(ROOT / "factory-assets", project / "factory-assets")
            (project / "factory-assets" / "ANTI-GAME-0001-discrete-collision.md").write_text("changed source")
            with self.assertRaisesRegex(ValueError, "snapshot drift"):
                compare_arms(a, b)
