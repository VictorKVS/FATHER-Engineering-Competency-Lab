from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import time
import uuid

import yaml

from father_runtime.adapters import ChatCompletionsHTTPAdapter


class AlinaLiteraryRuntime:
    def __init__(self, repo_root: str | Path='.', evidence_dir: str | Path='.father/alina_literary_runs') -> None:
        self.root=Path(repo_root)
        self.profile_dir=self.root/'agents'/'alina'/'profiles'/'literary'
        self.evidence_dir=Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def _text(self, rel: str) -> str:
        return (self.profile_dir/rel).read_text(encoding='utf-8')

    def _knowledge_sections(self) -> list[str]:
        text=self._text('KNOWLEDGE_BASE.md')
        chunks=[]
        cur=[]
        for line in text.splitlines():
            if line.startswith('## ') and cur:
                chunks.append('\n'.join(cur).strip())
                cur=[line]
            else:
                cur.append(line)
        if cur:
            chunks.append('\n'.join(cur).strip())
        return [c for c in chunks if c]

    @staticmethod
    def _tokens(text: str) -> set[str]:
        punct='.,!?;:\"\'()[]{}—–-'
        return {w.strip(punct).lower() for w in text.split() if len(w.strip(punct)) > 3}

    def _retrieve(self, story: str, limit: int=4) -> list[str]:
        q=self._tokens(story)
        scored=[]
        for chunk in self._knowledge_sections():
            score=len(q & self._tokens(chunk))
            scored.append((score,chunk))
        scored.sort(key=lambda x:x[0], reverse=True)
        return [chunk for _,chunk in scored[:limit]]

    def run(self, story_text: str, endpoint: str, model_id: str, target_length: int=500, constraints: list[str] | None=None) -> dict[str,Any]:
        if not story_text.strip():
            raise ValueError('story_text must not be empty')

        retrieved=self._retrieve(story_text)
        output_contract=yaml.safe_load(self._text('OUTPUT_CONTRACT.yaml'))
        context={
            'agent_id':'AG-001',
            'profile':'LITERARY',
            'capability':'STORY_CONTINUATION',
            'prompt':self._text('PROMPT.md'),
            'story_input':{
                'story_text':story_text,
                'target_length':target_length,
                'constraints':constraints or [],
            },
            'retrieved_knowledge':retrieved,
            'output_contract':output_contract,
            'domain_invariants':yaml.safe_load(self._text('DOMAIN_MODEL.yaml')).get('domain_model',{}).get('invariants',[]),
        }

        adapter=ChatCompletionsHTTPAdapter(endpoint,model_id)
        started=time.time()
        result=adapter.run(context)
        latency_ms=int((time.time()-started)*1000)
        parsed=result.parsed_output

        required=output_contract['output_contract']['required']
        missing=[name for name in required if name not in parsed]
        contract_valid=not missing

        record={
            'run_id':str(uuid.uuid4()),
            'agent_id':'AG-001',
            'profile':'LITERARY',
            'capability':'STORY_CONTINUATION',
            'model_id':model_id,
            'latency_ms':latency_ms,
            'retrieved_chunks':len(retrieved),
            'contract_valid':contract_valid,
            'missing_fields':missing,
            'input':context['story_input'],
            'output':parsed,
        }
        out=self.evidence_dir/f"alina-literary-{record['run_id']}.json"
        out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
        record['evidence_path']=str(out)
        return record
