from pathlib import Path
import tempfile
import unittest

import yaml

from father_runtime.adapters import ModelResult
from father_runtime.agent_executor import AgentExecutor


class FakeAdapter:
    model_id="FAKE-STORY-1"

    def run(self, context):
        return ModelResult(
            self.model_id,
            '{"continuation":"next","continuity":{},"canon_delta":[],"model_id":"FAKE-STORY-1"}',
            {
                "continuation":"next",
                "continuity":{},
                "canon_delta":[],
                "model_id":"FAKE-STORY-1",
            },
        )


class AgentExecutorTests(unittest.TestCase):
    def test_story_agent_produces_contract_valid_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"factory/agents/story").mkdir(parents=True)
            (root/"factory/agents").mkdir(exist_ok=True)
            agent={
                "agent":{
                    "identity":{"agent_id":"AG-STORY-001","purpose":"Continue","domain":"STORY"},
                    "intelligence":{"role_version":"R1","prompt_version":"P1","rag_version":"RAG1","knowledge_snapshot":"KB1"},
                    "contracts":{"input_contract":"IN1","output_contract":"OUT1"},
                    "evaluation":{"eval_profile":"E1","pass_threshold":80,"hard_fail_rules":[]},
                }
            }
            inp={"contract":{"required":["story_text","target_length"]}}
            out={"contract":{"required":["continuation","continuity","canon_delta","model_id"]}}
            (root/"factory/agents/agent.yaml").write_text(yaml.safe_dump(agent),encoding="utf-8")
            (root/"factory/agents/story/in.yaml").write_text(yaml.safe_dump(inp),encoding="utf-8")
            (root/"factory/agents/story/out.yaml").write_text(yaml.safe_dump(out),encoding="utf-8")

            result=AgentExecutor(root).run(
                agent_path="factory/agents/agent.yaml",
                input_contract_path="factory/agents/story/in.yaml",
                output_contract_path="factory/agents/story/out.yaml",
                task_input={"story_text":"Once","target_length":100},
                adapter=FakeAdapter(),
            )
            self.assertEqual(result.status,"PASS")
            self.assertTrue(Path(result.evidence_path).exists())

    def test_missing_required_input_fails_before_model_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"factory/agents/story").mkdir(parents=True)
            (root/"factory/agents").mkdir(exist_ok=True)
            agent={"agent":{"identity":{"agent_id":"A","purpose":"P","domain":"D"},"intelligence":{"role_version":"R","prompt_version":"P","rag_version":"G","knowledge_snapshot":"K"},"contracts":{"input_contract":"I","output_contract":"O"},"evaluation":{"eval_profile":"E","pass_threshold":80,"hard_fail_rules":[]}}}
            (root/"factory/agents/agent.yaml").write_text(yaml.safe_dump(agent),encoding="utf-8")
            (root/"factory/agents/story/in.yaml").write_text(yaml.safe_dump({"contract":{"required":["story_text"]}}),encoding="utf-8")
            (root/"factory/agents/story/out.yaml").write_text(yaml.safe_dump({"contract":{"required":["continuation"]}}),encoding="utf-8")
            result=AgentExecutor(root).run(
                agent_path="factory/agents/agent.yaml",
                input_contract_path="factory/agents/story/in.yaml",
                output_contract_path="factory/agents/story/out.yaml",
                task_input={},
                adapter=FakeAdapter(),
            )
            self.assertEqual(result.status,"FAIL")
            self.assertIn("missing_input:story_text",result.hard_fails)


if __name__=="__main__":
    unittest.main()
