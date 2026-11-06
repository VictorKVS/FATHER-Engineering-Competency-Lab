function ensureBusinessPopover(){
  let p=document.getElementById("businessPopover");
  if(p) return p;
  p=document.createElement("div");
  p.id="businessPopover";
  p.className="business-popover";
  document.body.appendChild(p);
  return p;
}
function openBusinessPopover(node){
  const data=window.FATHER_BUSINESS_RICH.workshops[node.id] || {
    inputs:[{name:"Upstream package",form:"contract-defined",quality:"UNKNOWN until workshop design"}],
    algorithm:["Workshop algorithm not yet detailed"],
    outputs:[{name:node.output || "Workshop Package",form:"machine-readable + human-readable",quality:"gate-controlled"}],
    metrics:[{name:"Completeness",value:"to define"},{name:"Quality",value:"to define"}],
    tests:["Contract validation","Gate validation"],
    experiments:[]
  };
  const p=ensureBusinessPopover();
  p.innerHTML=`
    <button class="close" onclick="closeBusinessPopover()">✕</button>
    <h2>${node.name}</h2><div class="sub">${node.id} · ${node.status} · ${node.purpose}</div>
    <div class="popover-grid">
      <section class="pop-panel"><h3>Входящие данные</h3>${data.inputs.map(x=>mini(x)).join("")}</section>
      <section class="pop-panel"><h3>Исходящие данные</h3>${data.outputs.map(x=>mini(x)).join("")}</section>
      <section class="pop-panel wide"><h3>Алгоритм внутри цеха</h3><ol class="algorithm-list">${data.algorithm.map(x=>'<li>'+x+'</li>').join("")}</ol></section>
      <section class="pop-panel"><h3>Метрики</h3>${data.metrics.map(x=>'<div class="metric"><span>'+x.name+'</span><span>'+x.value+'</span></div>').join("")}</section>
      <section class="pop-panel"><h3>Тесты / Gate</h3><ul class="algorithm-list">${data.tests.map(x=>'<li>'+x+'</li>').join("")}</ul></section>
      <section class="pop-panel wide"><h3>A/B и эксперименты</h3>${data.experiments.length?data.experiments.map(x=>'<div class="ab-card"><div class="ab-title">'+x.name+'</div><div class="ab-vars">'+x.variants.join(" vs ")+' · metric: '+x.metric+'</div></div>').join(""):'<div class="mini-meta">Для этого цеха A/B пока не требуется.</div>'}</section>
    </div>`;
  p.classList.add("open");
}
function closeBusinessPopover(){const p=document.getElementById("businessPopover");if(p)p.classList.remove("open")}
function mini(x){return '<div class="mini-row"><div class="mini-name">'+x.name+'</div><div class="mini-meta">'+[x.form,x.quality,x.volume].filter(Boolean).join(" · ")+'</div></div>'}
