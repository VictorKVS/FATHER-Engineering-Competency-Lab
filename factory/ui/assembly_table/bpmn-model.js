window.FATHER_BPMN = {
  id:"FATHER-FACTORY-BPMN-L1",
  version:"0.1.0",
  lanes:[
    {id:"customer",name:"Customer",steps:["Idea / Need","Submit Request","Clarify","Approve Intent","Accept Product"]},
    {id:"supervisor",name:"ALINA / Supervisor",steps:["Register Order","Route","Monitor Gates","Manage Rework","Freeze RC","Store Experience"]},
    {id:"business",name:"Business Analysis",steps:["Interpret Intent","SIPOC","BPMN","Roles","Flows","Rules","G1"]},
    {id:"system",name:"System Analysis",steps:["Requirements","Context","Interfaces","Events","Data Contracts","System Gate"]},
    {id:"architecture",name:"Architecture",steps:["Patterns","Components","Responsibilities","Topology","G2"]},
    {id:"data",name:"Data & Knowledge",steps:["Data Model","Sources","RAG","Graph","Provenance"]},
    {id:"ai",name:"AI / LLM",steps:["AI Tasks","Model Roles","Prompts","Context","Eval","Fallback"]},
    {id:"security",name:"Security",steps:["Trust Boundaries","Threat Model","Controls","Policy","Security Gate"]},
    {id:"development",name:"Development",steps:["Reuse","Build","Integrate","Build Artifact","G3"]},
    {id:"qa",name:"QA",steps:["Unit","Integration","Functional","AI Eval","Regression","G4"]},
    {id:"devsecops",name:"DevSecOps",steps:["Pipeline","Scans","SBOM","Package","Observability"]},
    {id:"optimization",name:"Optimization",steps:["Candidates","A/B","Compare","BKC"]},
    {id:"polygon",name:"Polygon",steps:["Adversarial","Failure","Load","Recovery","Verdict G5"]},
    {id:"release",name:"Release",steps:["Acceptance","Package","Deploy","Sale","Support"]}
  ]
};
