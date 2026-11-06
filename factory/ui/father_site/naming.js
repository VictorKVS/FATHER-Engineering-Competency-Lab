window.NEXUS_NAMING = {
  version: "1.0.0",
  entities: {
    "SYS-001": { public_name: "NEXUS AI Systems Engineering", code_name: "FATHER", type: "SYSTEM" },
    "ROLE-001": { public_name: "Knowledge & Reasoning Engineer", code_name: "ALINA", type: "ROLE" },
    "WS-001": { public_name: "Agent Designer", code_name: "FIELD_01", type: "WORKSPACE" },
    "BLK-001": { public_name: "Input Contract", code_name: "INPUT", type: "BLOCK" },
    "BLK-002": { public_name: "Role", code_name: "ROLE", type: "BLOCK" },
    "BLK-003": { public_name: "Prompt", code_name: "PROMPT", type: "BLOCK" },
    "BLK-004": { public_name: "RAG", code_name: "RAG", type: "BLOCK" },
    "BLK-005": { public_name: "Knowledge Base", code_name: "KB", type: "BLOCK" },
    "BLK-006": { public_name: "Model Slot", code_name: "MODEL_SLOT", type: "BLOCK" },
    "BLK-007": { public_name: "Output Contract", code_name: "OUTPUT", type: "BLOCK" },
    "BLK-008": { public_name: "Evals", code_name: "EVAL", type: "BLOCK" },
    "BLK-009": { public_name: "Evidence", code_name: "EVIDENCE", type: "BLOCK" },
    "EXT-001": { public_name: "OSINT Research Agent", code_name: "OSINT", type: "EXTERNAL_AGENT" },
    "GATE-001": { public_name: "Research Sufficiency Gate", code_name: "RESEARCH_SUFFICIENCY_GATE", type: "GATE" }
  },
  name(id, fallback="") {
    return this.entities[id]?.public_name || fallback || id;
  },
  code(id, fallback="") {
    return this.entities[id]?.code_name || fallback || id;
  }
};