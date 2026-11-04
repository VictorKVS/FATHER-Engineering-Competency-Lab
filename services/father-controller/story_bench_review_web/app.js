const criteria=["continuity","style_preservation","character_consistency","dialogue_quality","instruction_following","russian_language","narrative_coherence","creative_variation"];
let report=null,scores={},taskIndex=0;
const $=s=>document.querySelector(s);

function scoreKey(model,task,c){return model+"||"+task+"||"+c}
function renderCriteria(){
  $('#criteriaList').innerHTML=criteria.map(c=>'<div class="criterion"><label>'+c+'</label><div>1 — плохо · 5 — отлично</div></div>').join('');
}
function render(){
  if(!report||!report.results)return;
  const valid=report.results.filter(x=>x.status!=="MISSING");
  const tasks=(valid[0]?.tasks||[]);
  $('#summary').textContent=valid.length+' models · '+tasks.length+' tasks';
  $('#taskTabs').innerHTML=tasks.map((t,i)=>'<button class="tab '+(i===taskIndex?'active':'')+'" data-i="'+i+'">'+t.task_id+'</button>').join('');
  document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{taskIndex=Number(b.dataset.i);render()});
  const t=tasks[taskIndex];
  if(!t)return;
  $('#taskPrompt').className='prompt';
  $('#taskPrompt').textContent='TASK: '+t.task_id+' · '+t.mode;
  $('#models').className='modelGrid';
  $('#models').innerHTML=valid.map(m=>{
    const x=(m.tasks||[]).find(z=>z.task_id===t.task_id)||{};
    const rows=criteria.map(c=>{
      const k=scoreKey(m.model,t.task_id,c),v=scores[k]||3;
      return '<div class="scoreRow"><span>'+c+'</span><input type="number" min="1" max="5" step="1" value="'+v+'" data-key="'+k+'"></div>';
    }).join('');
    return '<div class="card" data-model="'+m.model+'"><h3>'+m.model+'</h3><div class="meta">'+(x.latency_ms||'—')+' ms · '+(x.chars||0)+' chars</div><div class="output">'+escapeHtml(x.output||x.error||'NO OUTPUT')+'</div>'+rows+'</div>'
  }).join('');
  document.querySelectorAll('input[data-key]').forEach(inp=>inp.onchange=()=>{scores[inp.dataset.key]=Number(inp.value);computeWinner()});
  computeWinner();
}
function escapeHtml(s){return String(s).replace(/[&<>"]/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[m]))}
function computeWinner(){
  if(!report)return;
  const totals={};
  for(const m of report.results.filter(x=>x.status!=="MISSING")){
    let sum=0,n=0;
    for(const task of (m.tasks||[])){
      for(const c of criteria){
        const k=scoreKey(m.model,task.task_id,c),v=Number(scores[k]||0);
        if(v){sum+=v;n++}
      }
    }
    totals[m.model]=n?sum/n:0;
  }
  const sorted=Object.entries(totals).sort((a,b)=>b[1]-a[1]);
  const winner=sorted[0];
  $('#winner').textContent=winner?'Лидер: '+winner[0]+' · '+winner[1].toFixed(2)+'/5':'';
  document.querySelectorAll('.card').forEach(c=>c.classList.toggle('best',winner&&c.dataset.model===winner[0]));
  return winner?winner[0]:null;
}
$('#save').onclick=async()=>{
  document.querySelectorAll('input[data-key]').forEach(inp=>scores[inp.dataset.key]=Number(inp.value));
  const winner=computeWinner();
  const r=await fetch('/api/scores',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scores,winner})});
  const j=await r.json();
  $('#save').textContent=j.ok?'Сохранено':'Ошибка';
};
(async()=>{
  renderCriteria();
  report=await (await fetch('/api/report')).json();
  const saved=await (await fetch('/api/scores')).json();
  scores=saved.scores||{};
  render();
})();