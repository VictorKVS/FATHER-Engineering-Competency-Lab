const state={catalog:null,tab:'agents',nodes:[],edges:[],selected:null};
const $=s=>document.querySelector(s);
const canvas=$('#canvas'), list=$('#catalogList');

async function api(path,options){const r=await fetch(path,options);const j=await r.json();if(!r.ok)throw new Error(j.message||j.error||r.statusText);return j}
function csv(v){return v.split(',').map(x=>x.trim()).filter(Boolean)}

function renderCatalog(){
  if(!state.catalog)return;
  const q=$('#search').value.toLowerCase();
  let rows=[];
  if(state.tab==='agents'){
    rows=state.catalog.agents.map(a=>({kind:'agent',id:a.agent_id,title:a.name,meta:a.role+' · '+a.status,data:a}));
  }else{
    rows=state.catalog.blocks.map(b=>({kind:'block',id:b.id,title:b.id,meta:b.type+' · '+b.status,data:b,block_type:b.type}));
  }
  list.innerHTML='';
  rows.filter(r=>(r.title+' '+r.meta).toLowerCase().includes(q)).forEach(r=>{
    const el=document.createElement('div');el.className='card';el.draggable=true;
    el.innerHTML='<div class="cardTitle">'+r.title+'</div><div class="cardMeta">'+r.meta+'</div>';
    (r.data.capabilities||[]).slice(0,4).forEach(c=>el.innerHTML+='<span class="chip">'+c+'</span>');
    el.addEventListener('dragstart',e=>e.dataTransfer.setData('application/json',JSON.stringify(r)));
    list.appendChild(el);
  });
}

function render(){
  canvas.querySelectorAll('.node').forEach(n=>n.remove());
  state.nodes.forEach(n=>{
    const el=document.createElement('div');
    el.className='node'+(state.selected===n.node_id?' selected':'');
    el.style.left=(n.position?.x||100)+'px';el.style.top=(n.position?.y||100)+'px';
    el.dataset.id=n.node_id;
    el.innerHTML='<span class="port in"></span><span class="port out"></span><div class="kind">'+(n.kind==='agent'?'AGENT':n.block_type.toUpperCase())+'</div><div class="title">'+(n.title||n.ref)+'</div><div class="ref">'+n.ref+'</div>';
    el.onclick=()=>{state.selected=n.node_id;render();showInspector(n)};
    canvas.appendChild(el);
  });
  drawEdges();
  $('#summary').textContent=state.nodes.length+' nodes · '+state.edges.length+' edges';
}
function drawEdges(){
  const svg=$('#edges');svg.innerHTML='';
  const map=Object.fromEntries(state.nodes.map(n=>[n.node_id,n]));
  state.edges.forEach(e=>{
    const a=map[e.from],b=map[e.to];if(!a||!b)return;
    const x1=(a.position?.x||0)+170,y1=(a.position?.y||0)+34,x2=(b.position?.x||0),y2=(b.position?.y||0)+34;
    const p=document.createElementNS('http://www.w3.org/2000/svg','path');
    const mx=(x1+x2)/2;p.setAttribute('d',`M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`);p.setAttribute('class','edgeLine');svg.appendChild(p);
  });
}
function showInspector(n){
  $('#inspectorEmpty').classList.add('hidden');const c=$('#inspectorContent');c.classList.remove('hidden');
  const obj=n.catalog||n;c.innerHTML='<dl>'+Object.entries(obj).filter(([k])=>!['catalog','position'].includes(k)).map(([k,v])=>'<dt>'+k+'</dt><dd>'+escapeHtml(typeof v==='object'?JSON.stringify(v):String(v))+'</dd>').join('')+'</dl>';
}
function escapeHtml(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}

canvas.addEventListener('dragover',e=>e.preventDefault());
canvas.addEventListener('drop',e=>{
  e.preventDefault();const r=JSON.parse(e.dataTransfer.getData('application/json'));const rect=canvas.getBoundingClientRect();
  const id=(r.kind==='agent'?'agent':'block')+'-'+Date.now();
  const n={node_id:id,kind:r.kind,ref:r.id,title:r.title,position:{x:e.clientX-rect.left+canvas.scrollLeft-85,y:e.clientY-rect.top+canvas.scrollTop-30},catalog:r.data};
  if(r.kind==='agent')n.manifest=r.data.manifest;else n.block_type=r.block_type;
  state.nodes.push(n);render();
});

async function loadReference(){
  const p=await api('/api/project/reference');state.nodes=p.nodes.map(n=>({...n,title:n.ref}));state.edges=p.edges;$('#projectName').textContent=p.name;$('#chassisLabel').textContent=p.chassis;render();
}
async function validate(){
  const project={project_id:'ui-'+Date.now(),name:$('#projectName').textContent,chassis:$('#chassisLabel').textContent,nodes:state.nodes.map(({catalog,title,...n})=>n),edges:state.edges,product:{product_id:'father-ui-draft-v1',agent_manifest:'config/agents/father_general.json',brain_id:'qwen-analysis',competency_id:'generic',inputs:['api'],outputs:['json'],knowledge:{adapter:'folder'},retrieval:{top_k:5},tools:'default',context_bus:true}};
  try{
    const r=await api('/api/validate-design',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(project)});
    $('#gate').textContent=r.ok?'VALID':'BLOCKED';$('#gate').className='gate '+(r.ok?'ready':'blocked');
    $('#canvasStatus').textContent=r.ok?'Graph and registry references valid':'Validation failed';
    $('#compatibility').innerHTML=r.ok?'<div class="compatRow ok">✓ graph valid</div><div class="compatRow ok">✓ registry references valid</div><div class="compatRow ok">✓ Product Spec compiled</div>':r.problems.map(p=>'<div class="compatRow bad">✕ '+escapeHtml(JSON.stringify(p))+'</div>').join('');
  }catch(e){$('#canvasStatus').textContent=e.message}
}

async function runAuto(){
  const req={requirement_id:'ui-auto',product_id:'father-ui-auto-v1',task:$('#reqTask').value,modality:'text',specialization:$('#reqSpec').value,complexity:Number($('#reqComplexity').value),capabilities:csv($('#reqCaps').value),competency_id:'generic',inputs:csv($('#reqInputs').value),outputs:['json','file'],knowledge:'folder',tools:'default',top_k:5};
  const r=await api('/api/auto-assemble',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(req)});
  $('#autoResult').textContent=JSON.stringify({ok:r.ok,agent:r.agent_choice?.agent_id,brain:r.model_choice?.brain_id,reuse:r.gaps.reuse,adapt:r.gaps.adapt,build:r.gaps.build},null,2);
  $('#compatibility').innerHTML='<div class="compatRow '+(r.ok?'ok':'warn')+'">'+(r.ok?'✓ AUTO ASSEMBLY READY':'⚠ GAPS DETECTED')+'</div>'+
    r.gaps.reuse.map(x=>'<div class="compatRow ok">REUSE · '+x.kind+' · '+x.id+'</div>').join('')+
    r.gaps.adapt.map(x=>'<div class="compatRow warn">ADAPT · '+x.kind+' · '+x.id+'</div>').join('')+
    r.gaps.build.map(x=>'<div class="compatRow bad">BUILD · '+x.kind+' · '+x.id+'</div>').join('');
}

document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('active'));b.classList.add('active');state.tab=b.dataset.tab;renderCatalog()});
$('#search').oninput=renderCatalog;$('#loadReference').onclick=loadReference;$('#validateBtn').onclick=validate;
$('#autoBtn').onclick=()=>$('#autoModal').classList.remove('hidden');$('#closeModal').onclick=()=>$('#autoModal').classList.add('hidden');$('#runAuto').onclick=runAuto;

(async()=>{try{await api('/api/health');$('#healthBadge').textContent='ONLINE';$('#healthBadge').style.background='#16442e';state.catalog=await api('/api/catalog');renderCatalog();await loadReference()}catch(e){$('#healthBadge').textContent='OFFLINE';console.error(e)}})();
