const naming=window.NEXUS_NAMING;
if(naming){
 const roleName=naming.name("ROLE-001","Knowledge & Reasoning Engineer");
 const rolePublic=document.getElementById("rolePublicName");
 const roleTitle=document.getElementById("rolePageTitle");
 if(rolePublic)rolePublic.textContent=roleName;
 if(roleTitle)roleTitle.textContent=roleName;
}

const params=new URLSearchParams(location.search);
const deepBlock=params.get("block")||null;

const alinaModels=[
 {id:"MDL-QWEN25-14B-1M-Q4",name:"Qwen2.5 14B Instruct 1M Q4_K_M",status:"ELIGIBLE"},
 {id:"MDL-GIGACHAT20-V15-Q4",name:"GigaChat 20B A3B v1.5 Q4_K_M",status:"ELIGIBLE"},
 {id:"MDL-GIGACHAT3-10B-Q4KS",name:"GigaChat3 10B A1.8B Q4_K_S",status:"ELIGIBLE"},
 {id:"MDL-DEEPSEEK-CODER-V2-LITE-Q4",name:"DeepSeek Coder V2 Lite Q4_K_M",status:"EXPERIMENTAL"}
];
let alinaModel="MDL-QWEN25-14B-1M-Q4";

const artifacts={
 role:{
  label:"ROLE",title:"Role Engineering",eyebrow:"ROLE ENGINEERING",version:"0.2.0",
  path:"agents/alina/profiles/literary/README.md",
  content:`purpose: Continue stories while preserving canon and continuity.
responsibilities:
  - preserve established facts
  - maintain character consistency
  - use declared knowledge and tools
boundaries:
  - do_not_invent_hidden_context
  - do_not_override_security_policy
decision_rights:
  - generate_proposals
  - request_research
escalation:
  - insufficient_evidence
  - policy_conflict`,
  structure:[["Purpose","Why the agent exists"],["Responsibilities","Accountabilities"],["Boundaries","Prohibited behavior"],["Decision rights","Autonomous decisions"],["Escalation","Required handoff"],["Traceability","Role → tests → evidence"]]
 },
 analysis:{
  label:"SITUATION ANALYSIS",title:"Situation Analysis",eyebrow:"ANALYTICAL FOUNDATION",version:"0.1.0",
  path:"intelligence/ANALYSIS_REPORT.yaml",
  content:`objective:
stakeholders: []
business_context:
current_process:
target_process:
constraints: []
risks: []
known_facts: []
unknowns: []
assumptions: []
research_gaps: []
success_criteria: []`,
  structure:[["Objective","Problem and desired outcome"],["Context","Business/domain situation"],["Known facts","Evidence-backed"],["Unknowns","Research gaps"],["Constraints","Business/security/technical"],["Success","Measurable outcome"]]
 },
 requirements:{
  label:"REQUIREMENTS",title:"Requirements Map",eyebrow:"REQUIREMENTS ENGINEERING",version:"0.1.0",
  path:"intelligence/REQUIREMENTS_MAP.yaml",
  content:`requirements:
  functional: []
  non_functional: []
  business: []
  security: []
  data: []
  knowledge: []
  training: []
  acceptance: []
traceability: []`,
  structure:[["Business","Value and process"],["Functional","Agent capabilities"],["NFR","Quality/performance"],["Security","Controls and boundaries"],["Knowledge","What must be known"],["Acceptance","How readiness is proven"]]
 },
 research:{
  label:"RESEARCH",title:"Research Questions",eyebrow:"RESEARCH GRAPH",version:"0.1.0",
  path:"intelligence/RESEARCH_GRAPH.yaml",
  content:`questions:
  - id: RQ-001
    origin:
    business_process:
    decision:
    knowledge_gap:
    question:
    why_needed:
    expected_evidence: []
    downstream_targets: []
    priority: HIGH`,
  structure:[["Origin","Idea/requirement/process"],["Gap","Missing knowledge"],["Question","Research task"],["Evidence","Expected proof"],["Destination","Prompt/RAG/KB/etc."],["Priority","Business/technical criticality"]]
 },
 osint:{
  label:"OSINT ORDERS",title:"OSINT Research Orders",eyebrow:"RESEARCH HANDOFF",version:"0.1.0",
  path:"intelligence/RESEARCH_REQUESTS.yaml",
  content:`research_requests:
  - request_id: RR-001
    target_agent:
    purpose:
    questions: []
    source_requirements:
      primary_sources_preferred: true
      freshness_required: true
    evidence_requirements:
      provenance: true
      corroboration: true
      counter_evidence: true
    sufficiency_criteria: []`,
  structure:[["Purpose","Why research is needed"],["Questions","Derived from gaps"],["Sources","Authority/freshness"],["Evidence","Provenance/corroboration"],["Sufficiency","Stop conditions"],["Handoff","OSINT → ALINA"]]
 },
 competency:{
  label:"COMPETENCY",title:"Competency Model",eyebrow:"COMPETENCY ENGINEERING",version:"0.1.0",
  path:"intelligence/COMPETENCY_MODEL.yaml",
  content:`competencies:
  - id: COMP-001
    name:
    level_required:
    prerequisites: []
    knowledge: []
    skills: []
    tools: []
    decisions: []
    failure_modes: []
    tests: []`,
  structure:[["Competencies","Required abilities"],["Levels","Expected proficiency"],["Knowledge","Facts/rules/models"],["Skills","Procedures/decisions"],["Failures","Critical errors"],["Tests","Proof of competence"]]
 },
 graph:{
  label:"KNOWLEDGE GRAPH",title:"Knowledge Graph",eyebrow:"KNOWLEDGE MODEL",version:"0.1.0",
  path:"intelligence/KNOWLEDGE_MODEL.yaml",
  content:`nodes: []
edges: []
claims: []
sources: []
contradictions: []
confidence_rules: []
temporal_rules: []
jurisdiction_rules: []`,
  structure:[["Nodes","Entities/concepts"],["Edges","Relations"],["Claims","Evidence-backed assertions"],["Sources","Provenance"],["Conflicts","Contradictions"],["Context","Time/jurisdiction"]]
 },
 prompt:{
  label:"PROMPT",title:"Prompt Engineering",eyebrow:"PROMPT LAB",version:"0.2.0",
  path:"agents/alina/profiles/literary/PROMPT.md",
  content:`ROLE:
GOAL:
CONTEXT:
INPUT:
ALGORITHM:
DECISION_RULES:
TOOL_RULES:
RAG_RULES:
UNCERTAINTY_RULES:
SECURITY_RULES:
OUTPUT_CONTRACT:
FAIL_CONDITIONS:
ESCALATION:`,
  structure:[["Role","Agent identity"],["Goal","Target outcome"],["Algorithm","Reasoning procedure"],["Policies","Tools/RAG/security"],["Output","Contract"],["Failure","Escalation and hard fail"]]
 },
 rag:{
  label:"RAG",title:"RAG Engineering",eyebrow:"RAG LAB",version:"0.2.0",
  path:"agents/alina/profiles/literary/RAG_MANIFEST.yaml",
  content:`sources: []
ingestion:
normalization:
chunking:
metadata:
embedding:
index:
retrieval:
reranking:
context_assembly:
citation_policy:
metrics:
  recall_at_k:
  precision_at_k:
  mrr:
  faithfulness:`,
  structure:[["Sources","Authoritative inputs"],["Ingestion","Normalization"],["Chunking","Retrieval units"],["Retrieval","Search/reranking"],["Context","Assembly/citations"],["Metrics","Recall/precision/faithfulness"]]
 },
 kb:{
  label:"KNOWLEDGE BASE",title:"Knowledge Engineering",eyebrow:"KNOWLEDGE LAB",version:"0.2.0",
  path:"agents/alina/profiles/literary/KNOWLEDGE_BASE.md",
  content:`domains: []
concepts: []
rules: []
procedures: []
cases: []
exceptions: []
risks: []
tools: []
sources: []
decisions: []
competencies: []`,
  structure:[["Domains","Knowledge areas"],["Concepts","Vocabulary/models"],["Rules","Decision rules"],["Procedures","How work is done"],["Cases","Examples/exceptions"],["Sources","Evidence and authority"]]
 },
 training:{
  label:"TRAINING",title:"Training Program",eyebrow:"AGENT CURRICULUM",version:"0.1.0",
  path:"intelligence/TRAINING_PROGRAM.yaml",
  content:`levels:
  - level: 0
    objective: foundations
    materials: []
    exercises: []
    pass_threshold:
  - level: 1
    objective: typical_tasks
    materials: []
    exercises: []
    pass_threshold:
remediation:
graduation_criteria: []`,
  structure:[["Levels","Simple → complex"],["Materials","Training evidence"],["Cases","Exercises"],["Thresholds","Pass criteria"],["Remediation","Failure recovery"],["Graduation","Training complete"]]
 },
 ab:{
  label:"A/B & METRICS",title:"A/B Experiments & Metrics",eyebrow:"OPTIMIZATION",version:"0.1.0",
  path:"intelligence/AB_EXPERIMENT_PLAN.yaml",
  content:`experiments:
  - id: AB-001
    variable:
    baseline:
    candidate:
    fixed_conditions: []
    dataset:
    metrics: []
    hard_fails: []
    winner_rule:
metric_profile:
  accuracy:
  completeness:
  hallucination_rate:
  source_fidelity:
  uncertainty_calibration:
  latency:
  cost:`,
  structure:[["Variable","One main change"],["Controls","Fixed conditions"],["Dataset","Same cases"],["Metrics","Measured outcomes"],["Hard fail","Overrides score"],["Winner","Promotion rule"]]
 },
 acceptance:{
  label:"ACCEPTANCE",title:"Acceptance Program",eyebrow:"READINESS PROOF",version:"0.1.0",
  path:"intelligence/ACCEPTANCE_CRITERIA.yaml",
  content:`test_classes:
  - knowledge
  - tasks
  - edge_cases
  - adversarial
  - end_to_end
required_gates:
  - regression
  - security
  - model_substitution
  - rag_degradation
  - evidence
pass_criteria: []
hard_fail: []`,
  structure:[["Knowledge","What agent knows"],["Tasks","What agent can do"],["Edge cases","Abnormal conditions"],["Adversarial","Hostile inputs"],["E2E","Professional scenarios"],["Gates","Regression/security/evidence"]]
 },
 version:{
  label:"VERSIONING",title:"Versioning & Handoff",eyebrow:"CHANGE CONTROL",version:"0.1.0",
  path:"intelligence/HANDOFF.yaml",
  content:`artifact_id:
from_version:
to_version:
change_reason:
changed_by:
source_refs: []
tests: []
metrics: []
risks: []
evidence: []
gate_status: HOLD`,
  structure:[["Identity","Artifact/version"],["Reason","Why changed"],["Sources","Evidence"],["Tests","Verification"],["Metrics","Measured effect"],["Risks","Known issues"],["Gate","Promotion state"]]
 }
};

let activeKey=deepBlock && artifacts[deepBlock] ? deepBlock : "analysis";
let active=artifacts[activeKey];
const drafts={};
let currentEditor="current";
const stage=document.getElementById("editorStage");

function artifactDraft(key){
 if(!drafts[key]) drafts[key]={content:artifacts[key].content,state:"CURRENT"};
 return drafts[key];
}

function loadArtifact(key){
 if(!artifacts[key])return;
 activeKey=key;active=artifacts[key];
 document.getElementById("editingTarget").textContent=active.label;
 document.getElementById("editingPath").textContent=active.path.split("/").pop();
 document.getElementById("editorTitle").textContent=active.title;
 document.getElementById("editorEyebrow").textContent=active.eyebrow;
 document.getElementById("versionChip").textContent="v"+active.version;
 document.getElementById("currentVersion").textContent=active.version;
 document.querySelectorAll(".tool-nav").forEach(x=>x.classList.toggle("active",x.dataset.tool===key));
 currentEditor="current";
 document.querySelectorAll(".editor-tab").forEach(x=>x.classList.toggle("active",x.dataset.editor==="current"));
 setState(artifactDraft(key).state);
 renderEditor();
}

function renderEditor(){
 const d=artifactDraft(activeKey);
 if(currentEditor==="current"){
  stage.innerHTML='<textarea class="code-editor" id="mainEditor"></textarea>';
  const ed=document.getElementById("mainEditor");ed.value=d.content;
  ed.addEventListener("input",e=>{d.content=e.target.value;d.state="MODIFIED";setState("MODIFIED")});
 }else if(currentEditor==="structure"){
  stage.innerHTML='<div class="structure-grid">'+active.structure.map(x=>'<div class="structure-card"><h4>'+x[0]+'</h4><p>'+x[1]+'</p></div>').join("")+'</div>';
 }else if(currentEditor==="analysis"){
  stage.innerHTML='<div class="analysis-panel"><h3>Анализ ALINA Model Slot</h3><ul>'+
   '<li>Проверить связь с исходными требованиями и бизнес-процессом.</li>'+
   '<li>Проверить источники, gaps, противоречия и provenance.</li>'+
   '<li>Проверить влияние изменения на соседние артефакты.</li>'+
   '<li>Определить тесты, метрики и hard-fail для изменения.</li>'+
   '<li>Сформировать proposal, не изменяя CANON автоматически.</li>'+
   '</ul><p>Model: <b>'+alinaModel+'</b></p></div>';
 }else{
  stage.innerHTML='<div class="analysis-panel"><h3>PROPOSAL · '+active.title+'</h3><p>Предложение Алины отделено от текущей версии до прохождения eval/evidence.</p><textarea class="code-editor" id="proposalEditor"></textarea></div>';
  const pe=document.getElementById("proposalEditor");pe.value=d.content;
  pe.addEventListener("input",e=>{d.content=e.target.value;d.state="PROPOSAL";setState("PROPOSAL")});
 }
}

document.querySelectorAll(".editor-tab").forEach(b=>b.onclick=()=>{currentEditor=b.dataset.editor;document.querySelectorAll(".editor-tab").forEach(x=>x.classList.toggle("active",x===b));renderEditor()});
document.querySelectorAll(".tool-nav").forEach(b=>b.onclick=()=>loadArtifact(b.dataset.tool));
document.querySelectorAll("[data-action]").forEach(b=>b.onclick=()=>toolAction(b.dataset.action));

const modelSel=document.getElementById("alinaModelSelect");
alinaModels.forEach(m=>{const o=document.createElement("option");o.value=m.id;o.textContent=m.name+(m.status==="EXPERIMENTAL"?" · EXP":"");modelSel.appendChild(o)});
modelSel.value=alinaModel;
function renderModelMeta(){const m=alinaModels.find(x=>x.id===alinaModel);document.getElementById("alinaModelMeta").innerHTML='<b>'+m.id+'</b><br>ALINA_MODEL_SLOT · '+m.status}
modelSel.onchange=()=>{alinaModel=modelSel.value;renderModelMeta();toast("ALINA Model Slot: "+alinaModel)};renderModelMeta();

function toolAction(action){
 const messages={
  goal:"Цель изменения связана с активным артефактом.",
  claims:"Выделяются проверяемые claims.",
  sources:"Проверяется достаточность источников.",
  contradictions:"Ищутся противоречия между источниками и артефактами.",
  graph:"Обновляется граф зависимостей.",
  coverage:"Проверяется покрытие требований.",
  eval:"Формируется eval-план активного артефакта.",
  trace:"Строится traceability requirement → artifact → test → evidence."
 };
 document.getElementById("analysisReport").innerHTML='<p class="ok">'+(messages[action]||"Инструмент активирован.")+'</p>';
 toast(messages[action]||"Инструмент активирован");
}

document.getElementById("analyzeBtn").onclick=()=>{
 const d=artifactDraft(activeKey);d.state="ANALYZED";setState("ANALYZED");
 document.getElementById("analysisReport").innerHTML=
 '<p class="ok">✓ Активный артефакт: '+active.title+'</p>'+
 '<p class="ok">✓ Model Slot: '+alinaModel+'</p>'+
 '<p class="ok">✓ Проверяется traceability и source grounding</p>'+
 '<p class="warn">! Результат модели является PROPOSAL</p>'+
 '<p class="warn">! CANON требует eval/evidence/gate</p>';
};

document.getElementById("compareBtn").onclick=()=>{currentEditor="analysis";document.querySelectorAll(".editor-tab").forEach(x=>x.classList.toggle("active",x.dataset.editor==="analysis"));renderEditor();toast("Анализ изменений открыт")};

document.getElementById("saveVersionBtn").onclick=()=>{
 const d=artifactDraft(activeKey);
 const payload={
  schema:"ALINA_ENGINEERING_ARTIFACT_V1",
  artifact:activeKey,
  title:active.title,
  source_path:active.path,
  from_version:active.version,
  to_version:"NEXT",
  model_slot:"ALINA_MODEL_SLOT",
  model_id:alinaModel,
  content:d.content,
  status:"PROPOSAL",
  review:"PENDING",
  promotion_requires:["EVAL","EVIDENCE","APPROVAL"]
 };
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});
 const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="alina-"+activeKey+"-proposal.json";a.click();URL.revokeObjectURL(a.href);
 d.state="PROPOSAL";setState("PROPOSAL SAVED");toast("Артефакт сохранён как PROPOSAL");
};

function setState(v){document.getElementById("analysisState").textContent=v}
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__t);window.__t=setTimeout(()=>t.classList.remove("show"),2200)}

loadArtifact(activeKey);
