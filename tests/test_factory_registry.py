from pathlib import Path
import tempfile
import yaml

from father_runtime.factory_registry import FactoryRegistry, ModelBindingRequest


def test_agent_base_returns_agent_and_filters_compatible_models():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        (root/"factory/registry").mkdir(parents=True)

        agents={"agents":[{"agent_id":"A1","model_policy":{"required_capabilities":["text_generation"]}}]}
        models={"models":[
            {
                "model_id":"M1",
                "artifact":{"path":"C:/models/m1.gguf"},
                "capabilities":{"text_generation":True,"structured_output":True,"context_window":8192},
                "resources":{"vram_estimate_gb":6},
                "lifecycle":{"state":"VERIFIED","approved_agent_classes":["ENGINEERING"]},
            },
            {
                "model_id":"M2",
                "artifact":{"path":"C:/models/m2.gguf"},
                "capabilities":{"text_generation":True,"structured_output":False,"context_window":4096},
                "resources":{"vram_estimate_gb":14},
                "lifecycle":{"state":"DISCOVERED","approved_agent_classes":[]},
            },
        ]}
        (root/"factory/registry/AGENT_REGISTRY_V1.yaml").write_text(yaml.safe_dump(agents),encoding="utf-8")
        (root/"factory/registry/MODEL_REGISTRY.yaml").write_text(yaml.safe_dump(models),encoding="utf-8")

        reg=FactoryRegistry(root)
        assert reg.get_agent("A1")["agent_id"]=="A1"
        result=reg.compatible_models(ModelBindingRequest(
            agent_id="A1",
            required_capabilities=("text_generation","structured_output"),
            local_only=True,
            max_vram_gb=12,
            security_class="ENGINEERING",
        ))
        assert [x["model_id"] for x in result]==["M1"]
