from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
from typing import Any


_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")
_BINDING_ONLY = {"PACKAGE_DEPENDENCY", "SIDECAR", "SHARED_SERVICE"}
_ALL_MODES = {"EMBEDDED_COPY", *_BINDING_ONLY}


def _canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_tree_hash(path: Path) -> str:
    path = path.resolve()
    if path.is_file():
        return _hash_file(path)
    if not path.is_dir():
        raise ValueError(f"artifact path does not exist: {path}")

    entries: list[tuple[str, str]] = []
    for item in sorted((p for p in path.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
        rel = item.relative_to(path).as_posix()
        entries.append((rel, _hash_file(item)))
    return sha256(_canonical({"files": entries}).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class QualifiedBlockArtifact:
    block_id: str
    version: str
    source_path: str
    canonical_hash: str
    qualification_status: str
    supported_delivery_modes: tuple[str, ...]
    capabilities: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not _SAFE_ID.fullmatch(self.block_id):
            errors.append("invalid block_id")
        if not _SAFE_ID.fullmatch(self.version):
            errors.append("invalid version")
        if self.qualification_status != "QUALIFIED":
            errors.append("block is not QUALIFIED")
        modes = set(self.supported_delivery_modes)
        if not modes or not modes.issubset(_ALL_MODES):
            errors.append("invalid supported_delivery_modes")
        if not self.canonical_hash or len(self.canonical_hash) != 64:
            errors.append("canonical_hash must be SHA-256 hex")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class BlockMaterializationRequest:
    product_id: str
    product_version: str
    workspace_path: str
    block: QualifiedBlockArtifact
    delivery_mode: str

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not _SAFE_ID.fullmatch(self.product_id):
            errors.append("invalid product_id")
        if not _SAFE_ID.fullmatch(self.product_version):
            errors.append("invalid product_version")
        if self.delivery_mode not in _ALL_MODES:
            errors.append("invalid delivery_mode")
        if self.delivery_mode not in self.block.supported_delivery_modes:
            errors.append("delivery_mode not supported by block")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class BlockMaterializationRecord:
    status: str
    product_id: str
    product_version: str
    block_id: str
    block_version: str
    delivery_mode: str
    source_hash: str
    materialized_path: str | None
    binding: dict[str, str] | None
    assembly_id: str
    assembly_hash: str
    diagnostics: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class QualifiedBlockMaterializer:
    def materialize(self, request: BlockMaterializationRequest) -> BlockMaterializationRecord:
        validation = list(request.block.validate()) + list(request.validate())
        source = Path(request.block.source_path)

        if validation:
            return self._record(request, "REJECTED", "", None, None, tuple(validation))

        if not source.exists():
            return self._record(
                request,
                "REJECTED",
                "",
                None,
                None,
                ("source artifact missing",),
            )

        actual_hash = canonical_tree_hash(source)
        if actual_hash != request.block.canonical_hash:
            return self._record(
                request,
                "REJECTED",
                actual_hash,
                None,
                None,
                ("source hash mismatch",),
            )

        if request.delivery_mode in _BINDING_ONLY:
            binding = {
                "block_id": request.block.block_id,
                "version": request.block.version,
                "delivery_mode": request.delivery_mode,
                "canonical_hash": actual_hash,
            }
            return self._record(
                request,
                "BOUND",
                actual_hash,
                None,
                binding,
                (),
            )

        workspace = Path(request.workspace_path)
        target = (
            workspace
            / "blocks"
            / request.block.block_id
            / request.block.version
        )

        if target.exists():
            existing_hash = canonical_tree_hash(target)
            if existing_hash != actual_hash:
                return self._record(
                    request,
                    "REJECTED",
                    actual_hash,
                    str(target),
                    None,
                    ("target conflict: existing content hash differs",),
                )
            return self._record(
                request,
                "MATERIALIZED",
                actual_hash,
                str(target),
                None,
                ("target already contained identical qualified block",),
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            target.mkdir(parents=True, exist_ok=False)
            shutil.copy2(source, target / source.name)

        copied_hash = canonical_tree_hash(target)
        if copied_hash != actual_hash:
            shutil.rmtree(target, ignore_errors=True)
            return self._record(
                request,
                "REJECTED",
                actual_hash,
                None,
                None,
                ("post-copy hash verification failed",),
            )

        return self._record(
            request,
            "MATERIALIZED",
            actual_hash,
            str(target),
            None,
            (),
        )

    @staticmethod
    def _record(
        request: BlockMaterializationRequest,
        status: str,
        source_hash: str,
        materialized_path: str | None,
        binding: dict[str, str] | None,
        diagnostics: tuple[str, ...],
    ) -> BlockMaterializationRecord:
        payload = {
            "status": status,
            "product_id": request.product_id,
            "product_version": request.product_version,
            "block_id": request.block.block_id,
            "block_version": request.block.version,
            "delivery_mode": request.delivery_mode,
            "source_hash": source_hash,
            "materialized_path": materialized_path,
            "binding": binding,
            "diagnostics": tuple(sorted(diagnostics)),
        }
        digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        return BlockMaterializationRecord(
            assembly_id=f"BLKASM-{digest[:16]}",
            assembly_hash=digest,
            **payload,
        )
