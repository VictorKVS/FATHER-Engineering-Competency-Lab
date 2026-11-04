let mode='CONTINUE';let history=[];
const $=s=>document.querySelector(s);
document.querySelectorAll('.mode').forEach(b=>b.onclick=()=>{document.querySelectorAll('.mode').forEach(x=>x.classList.remove('active'));b.classList.add('active');mode=b.dataset.mode});
$('#file').onchange=async e=>{const f=e.target.files[0];if(f)$('#source').value=await f.text()};
$('#run').onclick=async()=>{
  const text=$('#source').value.trim();if(!text)return;
  $('#status').textContent='Модель пишет...';$('#run').disabled=true;
  try{
    const payload={text,mode,instruction:$('#instruction').value,temperature:Number($('#temp').value),history};
    const r=await fetch('/api/story',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const j=await r.json();if(!r.ok)throw new Error(j.message||j.error);
    $('#result').value=j.content;
    history.push({role:'user',content:$('#instruction').value||mode},{role:'assistant',content:j.content});
    history=history.slice(-8);
    $('#status').textContent=j.runtime_model+' · '+j.mode;
  }catch(e){$('#status').textContent='Ошибка: '+e.message}
  finally{$('#run').disabled=false}
};
$('#useResult').onclick=()=>{$('#source').value=$('#result').value;$('#instruction').value='';window.scrollTo({top:0,behavior:'smooth'})};
$('#copy').onclick=async()=>{await navigator.clipboard.writeText($('#result').value);$('#status').textContent='Скопировано'};
