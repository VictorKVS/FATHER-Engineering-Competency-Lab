from __future__ import annotations
import hashlib, json
from dataclasses import dataclass


@dataclass(frozen=True)
class PromptPackage:
    messages: tuple[dict,...]
    sha256: str


def assemble_prompt(*, system: str, role: str, task: str, context: list[dict]) -> PromptPackage:
    messages=(
        {"role":"system","content":system},
        {"role":"system","content":f"ROLE: {role}"},
        {"role":"user","content":task},
        {"role":"user","content":{"untrusted_context":context}},
    )
    raw=json.dumps(messages,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()
    return PromptPackage(messages,hashlib.sha256(raw).hexdigest())
