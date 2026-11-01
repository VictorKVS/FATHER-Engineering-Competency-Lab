from pathlib import Path
import yaml


def test_openapi_contains_full_assembly_contract():
    spec = yaml.safe_load(Path("factory/api/fua-001-openapi.yaml").read_text(encoding="utf-8"))
    assert spec["openapi"] == "3.1.0"
    assert "/v1/assembly/run" in spec["paths"]
    post = spec["paths"]["/v1/assembly/run"]["post"]
    assert post["operationId"] == "runFullAssembly"
    schemas = spec["components"]["schemas"]
    assert "AssemblyMissionRequest" in schemas
    assert "AssemblyMissionResult" in schemas
