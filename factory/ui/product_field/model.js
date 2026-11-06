window.FATHER_STAGES = Array.from({length:101},(_,i)=>({
  id:String(i).padStart(3,"0"),
  name:i===0?"IDEA":i===1?"PRODUCT DISCOVERY":i===2?"ANALYSIS":i===3?"OSINT RESEARCH":i===4?"ARCHITECTURE":"STAGE "+String(i).padStart(3,"0"),
  state:i===0?"active":"locked",
  proofs:{reference:false,emulation:false,local:false,ab:false}
}));

window.FATHER_STAGES[0].proofs.reference=true;

window.FATHER_PRODUCT = {
  id:"PRODUCT-001",
  name:"OSINT Reference Product",
  status:"work",
  stage:"AG-000 Product Manager",
  gate:"DISCOVERY",
  progress:12,
  evidence:8,
  specialists:[
    {id:"AG-000",name:"Product",state:"active"},
    {id:"AG-001",name:"ALINA",state:"waiting"},
    {id:"AG-010",name:"OSINT",state:"waiting"},
    {id:"AG-005",name:"PIONEER",state:"waiting"},
    {id:"AG-002",name:"Security",state:"waiting"},
    {id:"AG-004",name:"CODEX",state:"waiting"},
    {id:"AG-006",name:"Test",state:"waiting"},
    {id:"AG-003",name:"TIMA",state:"waiting"},
    {id:"AG-009",name:"Polygon",state:"waiting"}
  ],
  specialistProfiles:{
    "AG-000":{
      title:"Product Manager",owner:"Product Discovery",maturity:"M2",
      role:"Проверяет проблему, пользователя, ценность и экономическую обоснованность до проектирования.",
      inputs:["Idea / Customer Intent","Stakeholders","Known Constraints"],
      algorithm:["Interviews & Surveys","Problem Discovery","Market / Alternatives","Economic Model","Doubts & Stop Conditions","Discovery Gate"],
      intelligence:["PROMPT.md","RAG_MANIFEST.yaml","KNOWLEDGE_BASE.md","EXPERIENCE/","EVALS/"],
      outputs:["PRODUCT_DISCOVERY_PACKAGE","ECONOMIC_MODEL","DOUBTS","SUCCESS_METRICS"],
      handoff:"AG-000 → AG-001 ALINA",
      tests:["PM-TEST-001","PM-TEST-002","PM-TEST-003"],
      gaps:["Research connectors","Accumulated discovery experience"]
    },
    "AG-001":{
      title:"ALINA Analyst",owner:"Analysis / Knowledge / Process",maturity:"M4",
      role:"Декомпозирует задачу, формирует исследовательские вопросы, claims, gaps и трассируемые выводы.",
      inputs:["Product Discovery Package","EvidencePackage","Prior ResearchGaps"],
      algorithm:["Objective","Research Questions","Hypotheses","ResearchRequest","Evidence Review","Claims","ResearchGap or Conclusion"],
      intelligence:["AGENTS.md","process_engine.py","docs/knowledge/","process-contract.v1.json","EXPERIENCE"],
      outputs:["ResearchRequest","AnalyticalAssessment","ResearchGap","EngineeringResearchPackage"],
      handoff:"AG-001 ↔ AG-010; AG-001 → AG-005",
      tests:["Process engine tests","Analyst↔OSINT protocol tests","Evidence traceability"],
      gaps:["Factory prompt wrapper","Explicit RAG manifest","Standard API wrapper"]
    },
    "AG-010":{
      title:"OSINT Expert",owner:"Search / Collection / Evidence",maturity:"M4",
      role:"Владелец стратегии поиска, сбора, provenance, coverage и EvidencePackage. Не делает финальный аналитический вывод.",
      inputs:["ResearchRequest","ResearchGap","Scope / Constraints","Required Sufficiency"],
      algorithm:["Parse Need","Source Classes","Search Plan","Collect RAW","Normalize / Deduplicate","Counter-evidence","Coverage / Sufficiency","EvidencePackage"],
      intelligence:["ROLE_MATRIX_ANALYST_OSINT_V1","ANALYST_OSINT_INTERACTION_PROTOCOL_V1","father_osint/","Search Intelligence KB","Development Journal"],
      outputs:["SearchPlanProposal","EvidencePackage","Coverage","Failed Attempts","Recommended Follow-up"],
      handoff:"AG-010 → AG-001 ALINA",
      tests:["21+ DEV baseline tests","Evidence quality","Counter-evidence","Sufficiency","TDLib / Telegram"],
      gaps:["Factory RAG wrapper","Standard API adapter","Three packaged regression cases"]
    },
    "AG-005":{
      title:"PIONEER",owner:"Infrastructure Architecture",maturity:"M4",
      role:"Строит инфраструктурную архитектуру, topology, dependency graph, BOM и GATE-1 пакет.",
      inputs:["Approved Requirements","Analytical Claims","Evidence Refs","Constraints","Security Inputs"],
      algorithm:["Validate Inputs","Logical Architecture","Topology","Dependencies","Network Plan","BOM","Threat Inputs","Acceptance Plan","GATE-1"],
      intelligence:["PIONEER-00/README.md","agent.yaml","topology.py","dependency_graph.py","security/","tests/"],
      outputs:["architecture.yaml","topology.json","bill-of-materials.yaml","test-plan.yaml","handoff-to-tima.json"],
      handoff:"AG-005 → AG-003 TIMA",
      tests:["Gate1 tests","Topology tests","Dependency graph tests","TIMA receiver tests"],
      gaps:["Canonical prompt","RAG manifest","Factory API adapter","Three packaged regression cases"]
    }
  },
  tabs:[
    {id:"overview",label:"Обзор"},
    {id:"documents",label:"Документы"},
    {id:"specialists",label:"Специалисты"},
    {id:"analysis",label:"Анализ"},
    {id:"tests",label:"Тесты"},
    {id:"evidence",label:"Evidence"},
    {id:"history",label:"История"}
  ],
  dossier:{
    overview:[
      ["Product ID","PRODUCT-001"],
      ["Current owner","AG-000 Product Manager"],
      ["Current gate","Product Discovery"],
      ["Recommendation","RESEARCH_MORE"],
      ["Confidence","0.68"],
      ["Next","ALINA after Discovery Gate"]
    ],
    documents:[
      {name:"PRODUCT_DISCOVERY_PACKAGE.yaml",type:"YAML",owner:"AG-000"},
      {name:"INTERVIEW_PLAN.md",type:"MD",owner:"AG-000"},
      {name:"SURVEY_PLAN.md",type:"MD",owner:"AG-000"},
      {name:"ECONOMIC_MODEL.yaml",type:"YAML",owner:"AG-000"},
      {name:"DOUBTS.md",type:"MD",owner:"AG-000"},
      {name:"EVIDENCE_INDEX.yaml",type:"YAML",owner:"AG-000"}
    ],
    analysis:[
      ["Facts / hypotheses","Separated"],
      ["Critical unknowns","3"],
      ["Economic model","In progress"],
      ["Reasons not to build","2"],
      ["Research gaps","Open"]
    ],
    tests:[
      ["PM-TEST-001","PASS"],
      ["PM-TEST-002","NOT RUN"],
      ["PM-TEST-003","NOT RUN"],
      ["Node tests","3"],
      ["Chain tests","0"]
    ],
    evidence:[
      ["Evidence items","8"],
      ["Provenance","Required"],
      ["Contradicting evidence","2"],
      ["Unverified items","3"]
    ],
    history:[
      ["v0.1","Idea registered"],
      ["v0.2","Product Manager assigned"],
      ["v0.3","Discovery started"]
    ]
  }
};
