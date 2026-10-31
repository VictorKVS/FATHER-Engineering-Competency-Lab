from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = FACTORY_ROOT / "registry" / "blocks.json"
CHASSIS_DIR = FACTORY_ROOT / "chassis"
EVIDENCE_DIR = FACTORY_ROOT / "evidence"

REQUIRED_BLOCK_FIELDS = {
    "id",
    "version",
    "type",
    "inputs",
    "outputs",
    "dependencies",
    "permissions",
    "security_profile",
    "tests",
    "evidence",
    "compatibility",
}


class FactoryError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_registry() -> dict[str, dict]:
    raw = load_json(REGISTRY_PATH)
    blocks = {}
    for block in raw.get("blocks", []):
        missing = REQUIRED_BLOCK_FIELDS - set(block)
        if missing:
            raise FactoryError(
                f"Block {block.get('id', '<unknown>')} has incomplete contract: {sorted(missing)}"
            )
        if block["id"] in blocks:
            raise FactoryError(f"Duplicate block id: {block['id']}")
        blocks[block["id"]] = block
    return blocks


def load_chassis(chassis_id: str) -> dict:
    path = CHASSIS_DIR / f"{chassis_id}.json"
    if not path.exists():
        raise FactoryError(f"Unknown chassis: {chassis_id}")
    chassis = load_json(path)
    if chassis.get("id") != chassis_id:
        raise FactoryError(f"Chassis id mismatch in {path}")
    return chassis


def assemble(product_path: Path, write_evidence: bool = True) -> dict:
    product = load_json(product_path)
    product_id = product.get("product_id")
    chassis_id = product.get("chassis")
    requested = product.get("blocks", [])

    if not product_id or not chassis_id:
        raise FactoryError("Product must define product_id and chassis")

    registry = load_registry()
    chassis = load_chassis(chassis_id)

    required = chassis.get("required_blocks", [])
    declared = list(dict.fromkeys(requested))

    missing_from_product = sorted(set(required) - set(declared))
    if missing_from_product:
        raise FactoryError(
            "Product does not satisfy chassis; missing blocks: "
            + ", ".join(missing_from_product)
        )

    unknown = sorted(set(declared) - set(registry))
    if unknown:
        raise FactoryError("Unknown blocks: " + ", ".join(unknown))

    incompatible = [
        block_id
        for block_id in declared
        if chassis_id not in registry[block_id].get("compatibility", [])
    ]
    if incompatible:
        raise FactoryError(
            f"Blocks incompatible with {chassis_id}: " + ", ".join(incompatible)
        )

    unresolved_dependencies = []
    declared_set = set(declared)
    for block_id in declared:
        for dependency in registry[block_id].get("dependencies", []):
            if dependency not in declared_set:
                unresolved_dependencies.append(f"{block_id}->{dependency}")
    if unresolved_dependencies:
        raise FactoryError(
            "Unresolved dependencies: " + ", ".join(unresolved_dependencies)
        )

    manifest = {
        "manifest_version": "0.1",
        "product_id": product_id,
        "product_version": product.get("version"),
        "chassis": {
            "id": chassis["id"],
            "version": chassis["version"],
        },
        "assembly_status": "PASS",
        "blocks": [
            {
                "id": block_id,
                "version": registry[block_id]["version"],
                "type": registry[block_id]["type"],
                "security_profile": registry[block_id]["security_profile"],
            }
            for block_id in declared
        ],
        "policy": chassis.get("policy", {}),
        "product_policies": product.get("policies", {}),
        "evidence": {
            "registry": str(REGISTRY_PATH.relative_to(FACTORY_ROOT)),
            "product_config": str(product_path.resolve()),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    }

    if write_evidence:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        out = EVIDENCE_DIR / f"{product_id}-assembly.json"
        with out.open("w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2)
        manifest["evidence"]["assembly_manifest"] = str(out)

    return manifest


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python factory/runtime/factory.py <product.json>")
        return 2

    try:
        manifest = assemble(Path(argv[1]))
    except (OSError, json.JSONDecodeError, FactoryError) as exc:
        print(f"FACTORY: FAIL: {exc}")
        return 1

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print("FACTORY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
