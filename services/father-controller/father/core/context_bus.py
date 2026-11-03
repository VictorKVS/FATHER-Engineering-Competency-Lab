from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class ContextEnvelope:
    task_id: str
    task_type: str
    input_text: str
    producer: str = "input"
    history: List[Dict[str, Any]] = field(default_factory=list)
    knowledge: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_history(self, role, content, producer=None, metadata=None):
        self.history.append({
            "role": role,
            "content": content,
            "producer": producer,
            "metadata": metadata or {}
        })

    def add_knowledge(self, items):
        self.knowledge.extend(items or [])

    def handoff(self, producer, content, metadata=None):
        self.add_history("assistant", content, producer=producer, metadata=metadata)
        self.producer=producer
        self.artifacts["last_output"]=content
        return self
