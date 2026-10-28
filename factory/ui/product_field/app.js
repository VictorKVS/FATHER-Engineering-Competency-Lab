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
  const el=document.createElement("span");
  el.className="specialist "+(s.state==="active"?"active":s.state==="done"?"done":"");
  el.textContent=s.name;
  strip.appendChild(el);
});

function openDrawer(){drawer.classList.add("open");drawer.setAttribute("aria-hidden","false")}
function closeDrawer(){drawer.classList.remove("open");drawer.setAttribute("aria-hidden","true")}
card.addEventListener("click",openDrawer);
card.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" ")openDrawer()});
document.getElementById("closeDrawer").addEventListener("click",closeDrawer);

function renderTab(id){
  [...tabs.children].forEach(x=>x.classList.toggle("active",x.dataset.id===id));
  const data=p.dossier[id];
  body.innerHTML="";
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
  const sec=document.createElement("div");sec.className="section";
  const h=document.createElement("h4");h.textContent=p.tabs.find(t=>t.id===id)?.label||id;sec.appendChild(h);
  data.forEach(([k,v])=>{
    const row=document.createElement("div");row.className="item";
    row.innerHTML='<div class="k">'+k+'</div><div class="v">'+v+'</div>';
    sec.appendChild(row);
  });
  body.appendChild(sec);
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
