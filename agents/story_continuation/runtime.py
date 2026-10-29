from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
import json
import time
import uuid

import yaml

from father_runtime.adapters import ChatCompletionsHTTPAdapter


class StoryAgent:
    def __init__(self, repo_root: str | Path='.', evidence_dir: str | Path='.father/story_runs') -> None:
        self.root=Path(repo_root)
        self.agent_dir=self.root/'agents'/'story_continuation'
        self.evidence_dir=Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def _text(self, name: str) -> str:
        return (self.agent_dir/name).read_text(encoding='utf-8')

    def _knowledge_sections(self) -> list[str]:
        text=self._text('KNOWLEDGE_BASE.md')
        chunks=[]
        cur=[]
        for line in text.splitlines():
            if line.startswith('## ') and cur:
                chunks.append('\n'.join(cur).strip()); cur=[line]
            else:
                cur.append(line)
        if cur: chunks.append('\n'.join(cur).strip())
        return [c for c in chunks if c]

    def _retrieve(self, story: str, limit: int=4) -> list[str]:
        words={w.lower('.,!?;:\"\'()[]{}') for w in story.split() if len(w)>3}
        scored=[]
        for chunk in self._knowledge_sections():
            cwords={w.lower('.,!?;:\"\'()[]{}') for w in chunk.split() if len(w)>3}
            score=len(words & cwords)
            scored.append((score, chunk))
        scored.sort(key=lambda x:x[0], reverse=True)
        return [c for _,c in scored[:limit]]

    def run(self, story_text: str, endpoint: str, model_id: str, target_length: int=500, constraints: list[str] | None=None) -> dict[str, Any]:
        if not story_text.strip():
            raise ValueError('story_text must not be empty')
        retrieved=self._retrieve(story_text)
        context={
            'agent_id':'AG-STORY-001',
            'role':self._text('ROLE.md'),
            'prompt':self._text('PROMPT.md'),
            'story_input':{
                'story_text':story_text,
                'target_length':target_length,
                'constraints':constraints or [],
            },
            'retrieved_knowledge':retrieved,
            'output_contract':yaml.safe_load(self._text('OUTPUT_CONTRACT.yaml')),
        }
        adapter=ChatCompletionsHTTPAdapter(endpoint, model_id)
        started=time.time()
        result=adapter.run(context)
        latency_ms=int((time.time()-started)*1000)
        parsed=result.parsed_output
        required=['continuation','continuity','model_id']
        missing=[x for x in required if x not in parsed]
        record={
            'run_id':str(uuid.uuid4()),
            'agent_id':'AG-STORY-001',
            'model_id':model_id,
            'latency_ms':latency_ms,
            'contract_valid':not missing,
            'missing_fields':missing,
            'retrieved_chunks':len(retrieved),
            'input':context['story_input'],
            'output':parsed,
        }
        out=self.evidence_dir/f"story-{record['run_id']}.json"
        out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
        record['evidence_path']=str(out)
        return record
