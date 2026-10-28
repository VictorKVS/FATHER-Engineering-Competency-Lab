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
  tabs:[
    {id:"overview",label:"Обзор"},
    {id:"documents",label:"Документы"},
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
