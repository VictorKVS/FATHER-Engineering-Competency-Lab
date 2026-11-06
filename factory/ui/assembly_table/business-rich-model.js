window.FATHER_BUSINESS_RICH = {
  id:"FATHER-BUSINESS-MODEL-RICH",
  version:"0.2.0",
  workshops:{
    W01:{
      inputs:[
        {name:"Customer Intent",form:"YAML/JSON + human text",quality:"clarified",volume:"per order"},
        {name:"Constraints",form:"structured fields",quality:"explicit/UNKNOWN",volume:"small"}
      ],
      algorithm:[
        "Interpret intent",
        "Resolve ambiguities",
        "Define scope/non-scope",
        "Build SIPOC",
        "Build BPMN L0/L1",
        "Define roles and RACI",
        "Define activities",
        "Define information flows",
        "Define artifacts and rules",
        "Define quality/SLA/risks",
        "Create acceptance criteria",
        "Run G1 quality gate"
      ],
      outputs:[
        {name:"Business Design Package",form:"GitHub artifacts + machine-readable model",quality:"G1 PASS"},
        {name:"Security Handoff",form:"YAML",quality:"identified trust/data concerns"}
      ],
      metrics:[
        {name:"Process completeness",value:"target ≥ 95%"},
        {name:"Flow completeness",value:"target ≥ 95%"},
        {name:"Traceability",value:"target ≥ 90%"},
        {name:"Critical ambiguities",value:"target = 0"}
      ],
      tests:[
        "Every input has source",
        "Every output has consumer",
        "Every flow has producer and consumer",
        "Every decision has rule",
        "Acceptance criteria are testable",
        "Reality check passes"
      ],
      experiments:[
        {id:"AB-BA-PROMPT",name:"Prompt A/B",variants:["PROMPT-v0.1","PROMPT-v0.2"],metric:"business_model_score"},
        {id:"AB-BA-RAG",name:"RAG strategy A/B",variants:["hybrid","hybrid+rerank"],metric:"traceability+completeness"}
      ]
    },
    W05:{
      inputs:[
        {name:"Architecture Package",form:"structured artifacts",quality:"G2-ready"},
        {name:"Data & Knowledge Package",form:"schemas/RAG/graph",quality:"validated"}
      ],
      algorithm:["Identify AI tasks","Map capabilities","Select model roles","Design prompts","Design context","Design routing/fallback","Define evals"],
      outputs:[{name:"AI Configuration Package",form:"YAML/JSON",quality:"validated"}],
      metrics:[{name:"Quality",value:"task-specific"},{name:"Latency",value:"profiled"},{name:"Cost",value:"profiled"},{name:"Confidence",value:"measured"}],
      tests:["Structured output","Fallback","Context limits","Hallucination eval","Model compatibility"],
      experiments:[{id:"AB-MODEL",name:"Model A/B",variants:["local-primary","strong-fallback"],metric:"quality/cost/latency"}]
    },
    W08:{
      inputs:[{name:"Build Artifact",form:"artifact/container/config",quality:"G3 PASS"}],
      algorithm:["Unit","Integration","Functional","AI eval","Regression","Evidence completeness"],
      outputs:[{name:"Test Evidence",form:"reports + metrics",quality:"G4 PASS"}],
      metrics:[{name:"Pass rate",value:"target 100% critical"},{name:"Regression rate",value:"target 0 critical"}],
      tests:["Unit","Integration","Functional","Regression","Eval"],
      experiments:[]
    },
    W10:{
      inputs:[{name:"Verified Candidate",form:"config bundle",quality:"G4 PASS"}],
      algorithm:["Generate variants","Run A/B","Compare metrics","Apply hard constraints","Select Pareto/BKC","Regression recheck"],
      outputs:[{name:"Best Known Configuration",form:"immutable config manifest",quality:"winner verified"}],
      metrics:[{name:"Quality",value:"maximize"},{name:"Latency",value:"minimize"},{name:"Cost",value:"minimize"},{name:"Risk",value:"hard constraint"}],
      tests:["Statistical sanity","Regression","Security hard gates"],
      experiments:[{id:"AB-CONFIG",name:"Configuration A/B/C",variants:["A","B","C"],metric:"multi-objective utility"}]
    },
    W12:{
      inputs:[{name:"Frozen RC",form:"immutable package",quality:"hash/config fixed"}],
      algorithm:["Adversarial","Failure","Load","Chaos","Recovery","Security exercise","Verdict"],
      outputs:[{name:"Polygon Report",form:"signed evidence",quality:"PASS/FAIL"}],
      metrics:[{name:"Security failures",value:"0 critical"},{name:"Recovery",value:"within profile"}],
      tests:["Adversarial","Failure","Load","Recovery","Lifecycle"],
      experiments:[]
    }
  }
};