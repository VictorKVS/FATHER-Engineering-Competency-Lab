from pathlib import Path
import tempfile

from father_runtime.agent_discovery import discover_local_agents


def test_agent_discovery_finds_agent_manifest_read_only():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        agent_dir=root/"demo-agent"
        agent_dir.mkdir()
        (agent_dir/"agent.yaml").write_text(
            "agent_id: AG-X\nrole: tester\ncapabilities: [x]\nprompt: P1\n",
            encoding="utf-8",
        )
        result=discover_local_agents([root])
        assert result["mode"]=="READ_ONLY"
        assert result["count"]==1
        assert result["candidates"][0]["confidence"]=="HIGH"
        assert result["candidates"][0]["detected_name"]=="demo-agent"
