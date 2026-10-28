const p=window.FATHER_PRODUCT;
const card=document.getElementById("productCard");
const drawer=document.getElementById("drawer");
const tabs=document.getElementById("tabs");
const body=document.getElementById("drawerBody");
document.getElementById("productName").textContent=p.name;
document.getElementById("drawerTitle").textContent=p.name;
document.getElementById("stageLabel").textContent=p.stage;
document.getElementById("gateLabel").textContent=p.gate;
document.getElementById("evidenceCount").textContent=p.evidence;
document.getElementById("progressFill").style.width=p.progress+"%";

const statusMap={idea:"IDEA",work:"IN WORK",hold:"HOLD",pass:"PASS",fail:"FAIL"};
document.getElementById("statusPill").textContent=statusMap[p.status]||p.status;

const strip=document.getElementById("specialistStrip");
p.specialists.forEach(s=>{
  const el=document.createElement("button");
  el.className="specialist "+(s.state==="active"?"active":s.state==="done"?"done":"");
  el.textContent=s.name;
  el.title=s.id;
  el.addEventListener("click",e=>{e.stopPropagation();openDrawer();renderSpecialist(s.id)});
  strip.appendChild(el);
});

function openDrawer(){drawer.classList.add("open");drawer.setAttribute("aria-hidden","false")}
function closeDrawer(){drawer.classList.remove("open");drawer.setAttribute("aria-hidden","true")}
card.addEventListener("click",openDrawer);
card.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" ")openDrawer()});
document.getElementById("closeDrawer").addEventListener("click",closeDrawer);

function section(title,items){
  const sec=document.createElement("div");sec.className="section";
  const h=document.createElement("h4");h.textContent=title;sec.appendChild(h);
  items.forEach(([k,v])=>{
    const row=document.createElement("div");row.className="item";
    row.innerHTML='<div class="k">'+k+'</div><div class="v">'+v+'</div>';
    sec.appendChild(row);
  });
  return sec;
}

function chips(items){
  const wrap=document.createElement("div");wrap.className="chip-wrap";
  items.forEach(x=>{const c=document.createElement("span");c.className="chip";c.textContent=x;wrap.appendChild(c)});
  return wrap;
}

function renderSpecialist(id){
  [...tabs.children].forEach(x=>x.classList.remove("active"));
  body.innerHTML="";
  const s=p.specialistProfiles[id]||{
    title:p.specialists.find(x=>x.id===id)?.name||id,
    owner:"Factory role",maturity:"M1",
    role:"Типовой профиль специалиста. Полный пакет ещё формируется.",
    inputs:["Standard Handoff"],algorithm:["Receive","Validate","Execute","Evaluate","Handoff"],
    intelligence:["ROLE","PROMPT","ALGORITHM","RAG","KB"],outputs:["Versioned Artifact"],
    handoff:"Standard API Handoff",tests:["Package tests"],gaps:["Full standard package"]
  };
  const back=document.createElement("button");back.className="back-btn";back.textContent="← К досье продукта";
  back.addEventListener("click",()=>renderTab("overview"));body.appendChild(back);

  const hero=document.createElement("div");hero.className="specialist-hero";
  hero.innerHTML='<div><div class="eyebrow">'+id+' • '+s.maturity+'</div><h3>'+s.title+'</h3><p>'+s.role+'</p></div><span class="owner-badge">'+s.owner+'</span>';
  body.appendChild(hero);

  body.appendChild(section("Контракт",[
    ["Owner",s.owner],
    ["Maturity",s.maturity],
    ["API handoff",s.handoff]
  ]));

  const blocks=[
    ["Входы",s.inputs],["Алгоритм",s.algorithm],["Prompt / RAG / KB",s.intelligence],
    ["Выходы",s.outputs],["Тесты",s.tests],["Gaps",s.gaps]
  ];
  blocks.forEach(([title,items])=>{
    const sec=document.createElement("div");sec.className="section";
    const h=document.createElement("h4");h.textContent=title;sec.appendChild(h);
    sec.appendChild(chips(items));body.appendChild(sec);
  });
}

function renderSpecialistList(){
  body.innerHTML="";
  const sec=document.createElement("div");sec.className="section";
  const h=document.createElement("h4");h.textContent="Маршрут специалистов";sec.appendChild(h);
  p.specialists.forEach(s=>{
    const row=document.createElement("button");row.className="agent-row";
    const profile=p.specialistProfiles[s.id];
    row.innerHTML='<span><b>'+s.id+' • '+s.name+'</b><small>'+(profile?.owner||"Factory role")+'</small></span><span class="badge">'+s.state.toUpperCase()+'</span>';
    row.addEventListener("click",()=>renderSpecialist(s.id));
    sec.appendChild(row);
  });
  body.appendChild(sec);
}

function renderTab(id){
  [...tabs.children].forEach(x=>x.classList.toggle("active",x.dataset.id===id));
  const data=p.dossier[id];
  body.innerHTML="";
  if(id==="specialists"){renderSpecialistList();return}
  if(id==="documents"){
    const sec=document.createElement("div");sec.className="section";
    const h=document.createElement("h4");h.textContent="Документы продукта";sec.appendChild(h);
    data.forEach(d=>{
      const el=document.createElement("div");el.className="file";
      el.innerHTML='<div><b>'+d.name+'</b><br><small>'+d.owner+'</small></div><span class="badge">'+d.type+'</span>';
      sec.appendChild(el);
    });
    body.appendChild(sec);return;
  }
  body.appendChild(section(p.tabs.find(t=>t.id===id)?.label||id,data));
}

p.tabs.forEach((t,i)=>{
  const b=document.createElement("button");b.className="tab"+(i===0?" active":"");b.dataset.id=t.id;b.textContent=t.label;
  b.addEventListener("click",()=>renderTab(t.id));tabs.appendChild(b);
});
renderTab("overview");

window.setFatherProductState=function(state,stage,gate,progress){
  p.status=state;p.stage=stage||p.stage;p.gate=gate||p.gate;p.progress=progress??p.progress;
  card.className="product-card status-"+state;
  document.getElementById("statusPill").textContent=statusMap[state]||state;
  document.getElementById("stageLabel").textContent=p.stage;
  document.getElementById("gateLabel").textContent=p.gate;
  document.getElementById("progressFill").style.width=p.progress+"%";
};
