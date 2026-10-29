const blocks=[
 {id:"input",type:"INPUT",title:"Input Contract",desc:"Явный вход агента",x:55,y:120},
 {id:"role",type:"ROLE",title:"Role",desc:"Кто агент и за что отвечает",x:245,y:70},
 {id:"prompt",type:"PROMPT",title:"Prompt",desc:"Версионируемая инструкция",x:245,y:180},
 {id:"rag",type:"RAG",title:"RAG",desc:"Поиск релевантного знания",x:435,y:70},
 {id:"kb",type:"KB",title:"Knowledge Base",desc:"База знаний профиля",x:435,y:180},
 {id:"model",type:"MODEL_SLOT",title:"Model Slot",desc:"Сменная локальная LLM",x:625,y:125,cls:"model"},
 {id:"output",type:"OUTPUT",title:"Output Contract",desc:"Структурированный результат",x:815,y:70},
 {id:"eval",type:"EVAL",title:"Evals",desc:"Контракт + качество",x:815,y:180},
 {id:"evidence",type:"EVIDENCE",title:"Evidence",desc:"Кто / что / версия / PASS",x:1005,y:125,cls:"evidence"}
];
const edges=[["input","role"],["role","rag"],["role","prompt"],["prompt","model"],["rag","model"],["kb","model"],["model","output"],["output","eval"],["eval","evidence"]];
const palette=[
 ["ROLE","R","Роль","Ответственность агента"],["PROMPT","P","Prompt","Версия инструкций"],["RAG","G","RAG","Извлечение знаний"],["KB","K","Knowledge Base","Доменная база знаний"],["MODEL_SLOT","M","Model Slot","Сменная LLM"],["CONTRACT","C","Contract","Вход / выход"],["EVAL","E","Eval","Проверка качества"],["EVIDENCE","V","Evidence","Доказательства"]
];
const models=[
 {id:"MDL-GIGACHAT20-Q4",name:"GigaChat 20B A3B Q4_K_M",type:"TEXT_GENERATION",runtime:"llama.cpp",status:"ELIGIBLE"},
 {id:"MDL-GIGACHAT20-V15-Q4",name:"GigaChat 20B A3B v1.5 Q4_K_M",type:"TEXT_GENERATION",runtime:"llama.cpp",status:"ELIGIBLE"},
 {id:"MDL-GIGACHAT3-10B-Q4KS",name:"GigaChat3 10B A1.8B Q4_K_S",type:"TEXT_GENERATION",runtime:"llama.cpp",status:"ELIGIBLE"},
 {id:"MDL-QWEN25-14B-1M-Q4",name:"Qwen2.5 14B Instruct 1M Q4_K_M",type:"TEXT_GENERATION",runtime:"llama.cpp",status:"ELIGIBLE"},
 {id:"MDL-DEEPSEEK-CODER-V2-LITE-Q4",name:"DeepSeek Coder V2 Lite Q4_K_M",type:"TEXT_CODE_GENERATION",runtime:"llama.cpp",status:"EXPERIMENTAL"},
 {id:"MDL-DEEPSEEK-CODER-V2-LITE-Q5",name:"DeepSeek Coder V2 Lite Q5_K_M",type:"TEXT_CODE_GENERATION",runtime:"llama.cpp",status:"EXPERIMENTAL"},
 {id:"MDL-QWEN25-CODER-14B-Q4",name:"Qwen2.5 Coder 14B Q4_K_M",type:"TEXT_CODE_GENERATION",runtime:"llama.cpp",status:"EXPERIMENTAL"}
];
const config={
 agent_id:"AG-001",profile:"ALINA_LITERARY",capability:"STORY_CONTINUATION",
 role:"Литературный профиль ALINA. Продолжает рассказ, сохраняя канон, персонажей, POV и причинность.",
 prompt_version:"0.2.0",rag_version:"ALINA_LITERARY_RAG_V02",kb_version:"0.2.0",
 selected_model:"MDL-QWEN25-14B-1M-Q4"
};
const paletteEl=document.getElementById("palette");
palette.forEach(([type,icon,title,desc])=>{
 const b=document.createElement("button");b.className="palette-item";
 b.innerHTML='<span class="palette-icon">'+icon+'</span><span><b>'+title+'</b><small>'+desc+'</small></span>';
 b.onclick=()=>toast(type+" уже представлен на canvas");paletteEl.appendChild(b);
});
const nodes=document.getElementById("nodes"),canvas=document.getElementById("canvas"),svg=document.getElementById("wires");
function renderNodes(){
 nodes.innerHTML="";
 blocks.forEach(b=>{
  const n=document.createElement("article");n.className="node "+(b.cls||"");n.dataset.id=b.id;n.style.left=b.x+"px";n.style.top=b.y+"px";
  n.innerHTML='<div class="nhead"><span class="nid">'+b.type+'</span><span class="state"></span></div><h3>'+b.title+'</h3><p>'+b.desc+'</p>';
  n.onclick=()=>selectBlock(b.id);nodes.appendChild(n);
 });
 requestAnimationFrame(drawWires);
}
function drawWires(){
 svg.innerHTML="";
 edges.forEach(([a,b])=>{
  const A=document.querySelector('[data-id="'+a+'"]'),B=document.querySelector('[data-id="'+b+'"]');if(!A||!B)return;
  const x1=A.offsetLeft+A.offsetWidth,y1=A.offsetTop+A.offsetHeight/2,x2=B.offsetLeft,y2=B.offsetTop+B.offsetHeight/2;
  const mid=(x1+x2)/2;
  const p=document.createElementNS("http://www.w3.org/2000/svg","path");p.setAttribute("class","wire");p.setAttribute("d",`M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}`);svg.appendChild(p);
 });
}
function selectBlock(id){
 document.querySelectorAll(".node").forEach(n=>n.classList.toggle("selected",n.dataset.id===id));
 const b=blocks.find(x=>x.id===id);const ins=document.getElementById("inspector");document.getElementById("inspectorType").textContent=b.type;
 let html='<div class="info-box"><b>'+b.title+'</b><p>'+b.desc+'</p></div>';
 if(id==="role")html+=field("Agent ID",config.agent_id)+area("Role",config.role);
 else if(id==="prompt")html+=field("Prompt version",config.prompt_version)+area("Prompt","Продолжай исходный рассказ. Сохраняй канон, POV, время, персонажей и открытые сюжетные линии. Возвращай JSON по Output Contract.");
 else if(id==="rag")html+=field("RAG version",config.rag_version)+field("Mode","LOCAL_SIMPLE_RETRIEVAL");
 else if(id==="kb")html+=field("KB version",config.kb_version)+'<div class="info-box"><b>Sections</b><p><span class="tag">Canon</span><span class="tag">Continuity</span><span class="tag">Characters</span><span class="tag">Causality</span></p></div>';
 else if(id==="model")html+='<div class="info-box"><b>Replaceable engine</b><p>Модель меняется без изменения Role / Prompt / RAG / KB / Contracts.</p></div>'+field("Selected",config.selected_model);
 else if(id==="input")html+=area("Schema",'story_text: string\ntarget_length: integer\nconstraints: string[]');
 else if(id==="output")html+=area("Required",'continuation\ncontinuity\ncanon_delta\nproposals\nmodel_id');
 else if(id==="eval")html+='<div class="info-box"><b>Hard fail</b><p>contract invalid · canon contradiction · renamed character · rewrite instead of continuation</p></div>';
 else html+='<div class="info-box"><b>Provenance</b><p>model_id · agent_id · prompt/RAG/KB versions · latency · contract status · review status</p></div>';
 ins.innerHTML=html;
}
function field(label,value){return '<div class="field"><label>'+label+'</label><input value="'+String(value).replaceAll('"','&quot;')+'"></div>'}
function area(label,value){return '<div class="field"><label>'+label+'</label><textarea>'+value+'</textarea></div>'}
const sel=document.getElementById("modelSelect");
models.forEach(m=>{const o=document.createElement("option");o.value=m.id;o.textContent=m.name+(m.status==="EXPERIMENTAL"?" · EXP":"");sel.appendChild(o)});sel.value=config.selected_model;
function renderModel(){const m=models.find(x=>x.id===sel.value);config.selected_model=m.id;document.getElementById("modelMeta").innerHTML='<b>'+m.id+'</b><br>'+m.type+' · '+m.runtime+' · '+m.status;document.getElementById("modelStatus").textContent=models.length+" candidates";}
sel.onchange=()=>{renderModel();selectBlock("model")};renderModel();
const checks=["Role defined","Prompt versioned","RAG attached","Knowledge Base attached","Model Slot replaceable","Input contract","Output contract","Evals","Evidence"];
document.getElementById("checklist").innerHTML=checks.map(x=>'<div class="check"><span>'+x+'</span><b>READY</b></div>').join("");
document.getElementById("loadDemo").onclick=()=>{selectBlock("role");toast("ALINA Literary demo загружен")};
document.getElementById("validate").onclick=()=>{document.getElementById("gateStatus").textContent="DESIGN PASS";document.getElementById("gateStatus").className="";toast("Конструкция полная. Runtime proof ещё требуется.")};
document.getElementById("runDemo").onclick=()=>toast("Demo package готов: AG-001 + "+config.selected_model);
document.getElementById("exportBtn").onclick=()=>{
 const data={...config,model_candidates:models.map(x=>x.id),blocks:blocks.map(({id,type,title})=>({id,type,title})),edges};
 const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="father-agent-design.json";a.click();URL.revokeObjectURL(a.href);toast("Agent design JSON экспортирован");
};
function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(window.__toast);window.__toast=setTimeout(()=>t.classList.remove("show"),2200)}
window.addEventListener("resize",drawWires);renderNodes();selectBlock("role");