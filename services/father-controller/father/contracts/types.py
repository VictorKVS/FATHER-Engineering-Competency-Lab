from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class InputEvent:
    source: str
    type: str
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BrainRequest:
    messages: List[Dict[str, str]]
    temperature: float = 0.2
    max_tokens: int = 1024
    tools: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BrainResponse:
    brain_id: str
    provider: str
    model: str
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    finish_reason: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class KnowledgeQuery:
    text: str
    top_k: int = 5
    filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KnowledgeResult:
    items: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolResult:
    name: str
    ok: bool
    result: Any = None
    error: Optional[str] = None

@dataclass
class AgentResult:
    ok: bool
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
