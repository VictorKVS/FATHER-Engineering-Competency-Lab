window.WORKSHOP01 = {
  id:"W01-BUSINESS-ANALYSIS",
  version:"0.1.0",
  name:"Business Analysis Workshop",
  stages:[
    {id:"BA01",name:"Intent Analysis",output:"customer_intent",status:"READY"},
    {id:"BA02",name:"Ambiguity Analysis",output:"terminology_register",status:"READY"},
    {id:"BA03",name:"Scope",output:"scope_non_scope",status:"DRAFT"},
    {id:"BA04",name:"SIPOC",output:"sipoc",status:"DRAFT"},
    {id:"BA05",name:"BPMN L0/L1",output:"process_model",status:"DRAFT"},
    {id:"BA06",name:"Roles / RACI",output:"role_catalog",status:"DRAFT"},
    {id:"BA07",name:"Activities",output:"activity_catalog",status:"DRAFT"},
    {id:"BA08",name:"Information Flows",output:"information_flow_catalog",status:"DRAFT"},
    {id:"BA09",name:"Artifacts",output:"artifact_catalog",status:"DRAFT"},
    {id:"BA10",name:"Business Rules",output:"business_rules",status:"DRAFT"},
    {id:"BA11",name:"Quality / Volume / SLA",output:"quality_matrix",status:"DRAFT"},
    {id:"BA12",name:"Exceptions / Risks",output:"risk_exception_catalog",status:"DRAFT"},
    {id:"BA13",name:"Acceptance Criteria",output:"acceptance_criteria",status:"DRAFT"},
    {id:"BA14",name:"Quality Gate G1",output:"business_design_package",status:"DRAFT"}
  ],
  gate:{
    id:"G1",
    conditions:[
      "critical_ambiguities == 0",
      "every_input_has_source",
      "every_output_has_consumer",
      "every_flow_has_producer_and_consumer",
      "traceability_pass",
      "reality_check_pass"
    ]
  }
};
