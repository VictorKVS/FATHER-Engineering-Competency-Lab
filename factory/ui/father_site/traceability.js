const nodes=[
{id:"REQ-001",type:"REQUIREMENT",label:"Requirement",x:30,y:230,owner:"ROLE-101"},
{id:"PROC-001",type:"BUSINESS_PROCESS",label:"Process",x:185,y:120,owner:"ROLE-102"},
{id:"DEC-001",type:"DECISION",label:"Decision",x:340,y:230,owner:"ROLE-102"},
{id:"COMP-001",type:"COMPETENCY",label:"Competency",x:495,y:120,owner:"ROLE-105"},
{id:"SKILL-001",type:"SKILL",label:"Skill",x:650,y:230,owner:"ROLE-105"},
{id:"KN-001",type:"KNOWLEDGE_NODE",label:"Knowledge",x:495,y:360,owner:"ROLE-001"},
{id:"SRC-001",type:"SOURCE",label:"Source",x:340,y:460,owner:"ROLE-001"},
{id:"EVAL-001",type:"EVAL_CASE",label:"Eval",x:805,y:120,owner:"ROLE-001"},
{id:"EVD-001",type:"EVIDENCE",label:"Evidence",x:805,y:360,owner:"ROLE-001"}];
const edges=[["REQ-001","PROC-001"],["PROC-001","DEC-001"],["DEC-001","COMP-001"],["COMP-001","SKILL-001"],["SKILL-001","KN-001"],["KN-001","SRC-001"],["SKILL-001","EVAL-001"],["EVAL-001","EVD-001"]];
let tab="graph",selected=null;
document.getElementById("nodeTypes").innerHTML=[...new Set(nodes.map(n=>n.type))].map(x=>'<span>'+x+'</span>').join("");
function render(){
 const s=document.getElementById("traceStage");
 if(tab==="graph"){
   const paths=edges.map(([a,b])=>{const A=nodes.find(n=>n.id===a),B=nodes.find(n=>n.id===b);return '<path d="M '+(A.x+135)+' '+(A.y+25)+' C '+(A.x+165)+' '+(A.y+25)+', '+(B.x-30)+' '+(B.y+25)+', '+B.x+' '+(B.y+25)+'"/>'}).join("");
   s.innerHTML='<div class="trace-board"><svg>'+paths+'</svg>'+nodes.map(n=>'<div class="trace-node '+(selected===n.id?'selected':'')+'" data-id="'+n.id+'" style="left:'+n.x+'px;top:'+n.y+'px"><small>'+n.type+'</small><b>'+n.id+' · '+n.label+'</b></div>').join("")+'</div>';
   document.querySelectorAll(".trace-node").forEach(e=>e.onclick=()=>selectNode(e.dataset.id));
 } else if(tab==="matrix"){
   s.innerHTML='<table class="matrix"><thead><tr><th>From</th><th>To</th><th>Relation</th><th>Status</th></tr></thead><tbody>'+edges.map((e,i)=>'<tr><td>'+e[0]+'</td><td>'+e[1]+'</td><td>'+(i===5?'DERIVED_FROM':i===6?'TESTS':i===7?'PRODUCES':'REQUIRES')+'</td><td>ACTIVE</td></tr>').join("")+'</tbody></table>';
 } else {
   s.innerHTML='<div class="okbox">Minimal project has trace paths for requirement, skill and knowledge source. Release node is not yet present, so release evidence rule is not evaluated in this demo.</div>';
 }
}
function selectNode(id){selected=id;const n=nodes.find(x=>x.id===id);render();document.getElementById("traceInspector").innerHTML='<b>'+n.id+'</b><p>Type: '+n.type+'<br>Owner: '+n.owner+'</p><p>Incoming: '+edges.filter(e=>e[1]===id).length+' · Outgoing: '+edges.filter(e=>e[0]===id).length+'</p>'}
document.querySelectorAll(".trace-tab").forEach(b=>b.onclick=()=>{tab=b.dataset.tab;document.querySelectorAll(".trace-tab").forEach(x=>x.classList.toggle("active",x===b));render()});
document.getElementById("validateGraph").onclick=()=>{document.getElementById("traceGate").textContent="VALIDATED";document.getElementById("traceValidation").innerHTML='<p class="okbox">Traceability checks complete for demo graph.</p>';toast("Canonical graph validated")};
document.getElementById("exportGraph").onclick=()=>{const blob=new Blob([JSON.stringify({project:"PRJ-001",nodes,edges},null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="traceability-evidence-map.json";a.click();URL.revokeObjectURL(a.href);toast("Evidence Map exported")};
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__t);window.__t=setTimeout(()=>t.classList.remove("show"),2200)}render();