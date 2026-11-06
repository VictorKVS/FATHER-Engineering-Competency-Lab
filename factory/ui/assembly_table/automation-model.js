window.FATHER_AUTOMATION = {
  id:"FATHER-AUTOMATION-CANVAS",
  version:"0.1.0",
  zones:[
    {
      id:"sources",
      name:"Inputs / Sources",
      nodes:[
        {id:"SRC_FORM",name:"Forms",kind:"channel"},
        {id:"SRC_TELEGRAM",name:"Telegram",kind:"channel"},
        {id:"SRC_EMAIL",name:"Email",kind:"channel"},
        {id:"SRC_API",name:"External API",kind:"channel"},
        {id:"SRC_FILES",name:"Files",kind:"channel"}
      ]
    },
    {
      id:"workflows",
      name:"Workflow Automation",
      nodes:[
        {id:"WF_TRIGGER",name:"Trigger",kind:"workflow"},
        {id:"WF_FILTER",name:"Filter / Validate",kind:"workflow"},
        {id:"WF_TRANSFORM",name:"Transform",kind:"workflow"},
        {id:"WF_ROUTE",name:"Route",kind:"workflow"},
        {id:"WF_ACTION",name:"Action",kind:"workflow"}
      ]
    },
    {
      id:"agents",
      name:"Agents / Multi-Agent",
      nodes:[
        {id:"AG_RESEARCH",name:"Research Agent",kind:"agent"},
        {id:"AG_ANALYST",name:"Analyst Agent",kind:"agent"},
        {id:"AG_MANAGER",name:"Manager Agent",kind:"agent"},
        {id:"AG_WRITER",name:"Writer Agent",kind:"agent"},
        {id:"AG_SECURITY",name:"Security Agent",kind:"agent"}
      ]
    },
    {
      id:"systems",
      name:"Systems / Stores",
      nodes:[
        {id:"SYS_CRM",name:"CRM",kind:"system"},
        {id:"SYS_DB",name:"Database",kind:"store"},
        {id:"SYS_RAG",name:"RAG / Knowledge",kind:"store"},
        {id:"SYS_GITHUB",name:"GitHub",kind:"system"},
        {id:"SYS_MAIL",name:"Mail",kind:"system"}
      ]
    },
    {
      id:"outputs",
      name:"Outputs",
      nodes:[
        {id:"OUT_TELEGRAM",name:"Telegram Reply",kind:"output"},
        {id:"OUT_EMAIL",name:"Email",kind:"output"},
        {id:"OUT_REPORT",name:"Report",kind:"output"},
        {id:"OUT_TASK",name:"Task / Ticket",kind:"output"},
        {id:"OUT_API",name:"API Response",kind:"output"}
      ]
    }
  ],
  templates:[
    {
      id:"TPL_AUTOMATE_REPETITIVE",
      name:"Automate Repetitive Work",
      graph:["SRC_FORM","WF_VALIDATE","WF_ROUTE","AG_ANALYST","SYS_DB","OUT_EMAIL"]
    },
    {
      id:"TPL_LEAD_MANAGEMENT",
      name:"Lead Management",
      graph:["SRC_FORM","WF_FILTER","AG_ANALYST","SYS_CRM","OUT_TASK"]
    },
    {
      id:"TPL_CLIENT_ONBOARDING",
      name:"Client Onboarding",
      graph:["SRC_FORM","WF_VALIDATE","AG_MANAGER","SYS_GITHUB","OUT_EMAIL"]
    },
    {
      id:"TPL_RESEARCH_PIPELINE",
      name:"Research Pipeline",
      graph:["SRC_API","AG_RESEARCH","SYS_RAG","AG_ANALYST","AG_WRITER","OUT_REPORT"]
    }
  ]
};