const state={catalog:null,tab:'agents',nodes:[],edges:[],selected:null,selectedModel:null};
const $=s=>document.querySelector(s);
const canvas=$('#canvas'), list=$('#catalogList');

async function api(path,options){const r=await fetch(path,options);const j=await r.json();if(!r.ok)throw new Error(j.message||j.error||r.statusText);return j}
function csv(v){return v.split(',').map(x=>x.trim()).filter(Boolean)}
function escapeHtml(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}

function renderCatalog(){
  if(!state.catalog)return;
  const q=$('#search').value.toLowerCase();
  let rows=[];
  if(state.tab==='agents'){
    rows=state.catalog.agents.map(a=>({kind:'agent',id:a.agent_id,title:a.name,meta:a.role+' · '+a.status,data:a}));
  }else if(state.tab==='blocks'){
    rows=state.catalog.blocks.map(b=>({kind:'block',id:b.id,title:b.id,meta:b.type+' · '+b.status,data:b,block_type:b.type}));
  }else{
    rows=(state.catalog.models||[]).map(m=>({kind:'model',id:m.model_id,title:m.model_id,meta:m.admission_status+' · '+m.resource_class,data:m}));
  }
  list.innerHTML='';
  rows.filter(r=>(r.title+' '+r.meta).toLowerCase().includes(q)).forEach(r=>{
    const el=document.createElement('div');el.className='card';el.draggable=r.kind!=='model';
    el.innerHTML='<div class="cardTitle">'+escapeHtml(r.title)+'</div><div class="cardMeta">'+escapeHtml(r.meta)+'</div>';
    if(r.kind==='model'){
      (r.data.modalities||[]).slice(0,3).forEach(c=>el.innerHTML+='<span class="chip">'+escapeHtml(c)+'</span>');
      el.innerHTML+='<span class="chip">'+escapeHtml(r.data.verification?.bench_ready?'BENCH READY':'VERIFY')+'</span>';
      el.onclick=()=>showModelInInspector(r.data.model_id);
    }else{
      (r.data.capabilities||[]).slice(0,4).forEach(c=>el.innerHTML+='<span class="chip">'+escapeHtml(c)+'</span>');
      el.addEventListener('dragstart',e=>e.dataTransfer.setData('application/json',JSON.stringify(r)));
    }
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
    el.innerHTML='<span class="port in"></span><span class="port out"></span><div class="kind">'+(n.kind==='agent'?'AGENT':n.block_type.toUpperCase())+'</div><div class="title">'+escapeHtml(n.title||n.ref)+'</div><div class="ref">'+escapeHtml(n.ref)+'</div>';
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
  const obj=n.catalog||n;c.innerHTML='<dl>'+Object.entries(obj).filter(([k])=>!['catalog','position'].includes(k)).map(([k,v])=>'<dt>'+escapeHtml(k)+'</dt><dd>'+escapeHtml(typeof v==='object'?JSON.stringify(v):String(v))+'</dd>').join('')+'</dl>';
}

async function showModelInInspector(modelId){
  const m=await api('/api/models/'+encodeURIComponent(modelId));
  state.selectedModel=modelId;
  $('#inspectorEmpty').classList.add('hidden');const c=$('#inspectorContent');c.classList.remove('hidden');
  c.innerHTML='<dl>'+
    '<dt>model</dt><dd>'+escapeHtml(m.model_id)+'</dd>'+
    '<dt>runtime</dt><dd>'+escapeHtml(m.runtime_model)+'</dd>'+
    '<dt>admission</dt><dd>'+escapeHtml(m.admission_status)+'</dd>'+
    '<dt>deployment</dt><dd>'+escapeHtml(JSON.stringify(m.deployment))+'</dd>'+
    '<dt>commercial use</dt><dd>'+escapeHtml(m.commercial_use)+'</dd>'+
    '<dt>license</dt><dd>'+escapeHtml(JSON.stringify(m.license))+'</dd>'+
    '<dt>resource</dt><dd>'+escapeHtml(m.resource_class)+'</dd>'+
    '<dt>benchmark evidence</dt><dd>'+escapeHtml(JSON.stringify(m.benchmark_evidence))+'</dd>'+
    '<dt>claims</dt><dd>'+escapeHtml(String((m.claims||[]).length))+'</dd>'+
    '</dl>';
}

canvas.addEventListener('dragover',e=>e.preventDefault());
canvas.addEventListener('drop',e=>{
  e.preventDefault();const raw=e.dataTransfer.getData('application/json');if(!raw)return;
  const r=JSON.parse(raw);const rect=canvas.getBoundingClientRect();
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

async function refreshModels(){
  const r=await api('/api/models');
  state.catalog.models=r.models;
  renderCatalog();
  renderModelRegistry(r.models);
}

function renderModelRegistry(models){
  const root=$('#modelRegistryList');if(!root)return;root.innerHTML='';
  models.forEach(m=>{
    const el=document.createElement('div');el.className='modelRegistryRow';
    el.innerHTML='<div><strong>'+escapeHtml(m.model_id)+'</strong><div class="cardMeta">'+escapeHtml(m.provider+' · '+m.runtime_model)+'</div></div>'+
      '<div class="modelStatus '+(m.verification?.bench_ready?'ok':'warn')+'">'+escapeHtml(m.admission_status)+'</div>';
    el.onclick=()=>selectModelForIntel(m.model_id);
    root.appendChild(el);
  });
}

async function selectModelForIntel(modelId){
  state.selectedModel=modelId;$('#miSelectedModel').value=modelId;
  const m=await api('/api/models/'+encodeURIComponent(modelId));
  $('#miResult').textContent=JSON.stringify({
    admission_status:m.admission_status,
    commercial_use:m.commercial_use,
    license:m.license,
    deployment:m.deployment,
    benchmark_evidence:m.benchmark_evidence,
    claims:m.claims
  },null,2);
}

async function createModel(){
  const payload={
    model_id:$('#miModelId').value.trim(),
    provider:$('#miProvider').value.trim(),
    runtime_model:$('#miRuntime').value.trim(),
    version:$('#miVersion').value.trim(),
    modalities:['text']
  };
  const r=await api('/api/models/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  $('#miResult').textContent=JSON.stringify(r,null,2);
  await refreshModels();await selectModelForIntel(r.model_id);
}

async function addClaim(){
  const modelId=$('#miSelectedModel').value.trim();if(!modelId)throw new Error('Select a model first');
  let value=$('#miValue').value;
  if($('#miField').value.trim()==='context_window_tokens' && /^\d+$/.test(value))value=Number(value);
  const payload={
    field:$('#miField').value.trim(),
    value,
    source_url:$('#miSource').value.trim()||null,
    source_class:$('#miSourceClass').value,
    verification_status:$('#miVerify').value,
    confidence:$('#miConfidence').value
  };
  const r=await api('/api/models/'+encodeURIComponent(modelId)+'/claims',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  $('#miResult').textContent=JSON.stringify(r,null,2);
  await refreshModels();await selectModelForIntel(modelId);
}

document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('active'));b.classList.add('active');state.tab=b.dataset.tab;renderCatalog()});
$('#search').oninput=renderCatalog;$('#loadReference').onclick=loadReference;$('#validateBtn').onclick=validate;
$('#autoBtn').onclick=()=>$('#autoModal').classList.remove('hidden');$('#closeModal').onclick=()=>$('#autoModal').classList.add('hidden');$('#runAuto').onclick=runAuto;
$('#modelsBtn').onclick=async()=>{$('#modelsModal').classList.remove('hidden');await refreshModels()};
$('#closeModelsModal').onclick=()=>$('#modelsModal').classList.add('hidden');
$('#miCreateModel').onclick=()=>createModel().catch(e=>$('#miResult').textContent=e.message);
$('#miAddClaim').onclick=()=>addClaim().catch(e=>$('#miResult').textContent=e.message);

(async()=>{try{await api('/api/health');$('#healthBadge').textContent='ONLINE';$('#healthBadge').style.background='#16442e';state.catalog=await api('/api/catalog');renderCatalog();renderModelRegistry(state.catalog.models||[]);await loadReference()}catch(e){$('#healthBadge').textContent='OFFLINE';console.error(e)}})();
