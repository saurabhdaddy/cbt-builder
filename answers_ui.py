# answers_ui.py - Saurabh Daddy Test Series (Answers + Publish UI) v2.2
# Fix: JS me koi backslash escape nahi
# Cropped images /api/admin/draft/{id}/question/{no}/img se load hoti hain

ANSWER_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Answers - Saurabh Daddy Test Series</title>
<style>
:root{--navy:#0f172a;--navy2:#1e293b;--line:#334155;--gold:#fbbf24;--txt:#e2e8f0;--mut:#94a3b8}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:linear-gradient(135deg,#0f172a,#1e293b 55%,#0f172a);color:var(--txt);min-height:100vh}
button{font-family:inherit}
.topbar{display:flex;align-items:center;gap:12px;padding:12px 18px;background:rgba(15,23,42,.95);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:60;flex-wrap:wrap}
.logo{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#fbbf24,#d97706);color:#1e293b;font-weight:900;font-size:16px;box-shadow:0 4px 12px rgba(251,191,36,.3)}
.brand{display:flex;align-items:center;gap:12px;flex:1;min-width:200px}
.bname b{font-size:15px;color:var(--gold)}
.bname span{display:block;font-size:12px;color:var(--mut)}
.status{background:#475569;color:#fff;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:800}
.status.pub{background:#16a34a}
.tbtn{border:1px solid var(--line);background:var(--navy2);color:var(--txt);border-radius:10px;padding:9px 14px;font-size:13px;font-weight:700;cursor:pointer}
.tbtn:hover{border-color:var(--gold);color:var(--gold)}
.tbtn.primary{background:linear-gradient(135deg,#fbbf24,#d97706);color:#1e293b;border:none}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:14px;padding:14px 18px;align-items:start}
.qarea{min-width:0}
#qcard{background:var(--navy2);border:1px solid var(--line);border-radius:16px;padding:20px}
.qhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.qno{font-weight:800;font-size:16px;color:var(--gold)}
.qsec{background:#312e81;color:#a5b4fc;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700}
.qimg{max-width:100%;max-height:calc(100vh - 300px);width:auto;height:auto;display:block;margin:0 auto;border-radius:10px;border:1px solid var(--line);background:#fff}
.qtext{font-size:17px;line-height:1.7;white-space:pre-wrap}
.opts{display:grid;gap:12px;margin-top:18px}
.opt{display:flex;align-items:center;gap:14px;width:100%;padding:14px 16px;background:#0f172a;border:2px solid var(--line);border-radius:12px;color:var(--txt);font-size:15px;cursor:pointer;text-align:left}
.opt:hover{border-color:var(--gold)}
.opt.sel{border-color:var(--gold);background:rgba(251,191,36,.12)}
.ol{width:34px;height:34px;border-radius:50%;background:#334155;color:var(--txt);display:inline-flex;align-items:center;justify-content:center;font-weight:800}
.opt.sel .ol{background:var(--gold);color:#1e293b}
.saved{margin-left:auto;color:#16a34a;font-size:12px;font-weight:800}
.qacts{display:flex;gap:10px;margin-top:16px}
.navrow{display:flex;align-items:center;gap:10px;margin-top:14px;flex-wrap:wrap}
.navrow span{color:var(--mut);font-weight:700;font-size:14px;flex:1;text-align:center}
.pcol{background:var(--navy2);border:1px solid var(--line);border-radius:14px;padding:14px}
.pcol h4{font-size:13px;color:var(--gold);margin-bottom:10px}
.prog{background:#0f172a;border:1px solid var(--line);border-radius:8px;height:12px;overflow:hidden;margin-bottom:6px}
.bar{height:100%;background:linear-gradient(90deg,#16a34a,#4ade80);width:0%;transition:width .3s}
.ptext{color:var(--mut);font-size:12px;font-weight:700;margin-bottom:12px}
#palette{display:grid;grid-template-columns:repeat(auto-fill,minmax(36px,1fr));gap:7px}
.num{border:1px solid var(--line);background:#0f172a;color:var(--mut);border-radius:8px;height:36px;font-size:12px;font-weight:700;cursor:pointer}
.num.ans{background:#16a34a;color:#fff;border-color:#16a34a}
.num.cur{border-color:var(--gold);color:var(--gold);box-shadow:0 0 0 2px rgba(251,191,36,.4)}
.empty{color:var(--mut);font-size:13px;text-align:center;padding:16px}
.imgerr{color:#f87171;font-size:13px;text-align:center;padding:10px}
.modal{position:fixed;inset:0;background:rgba(2,6,23,.85);display:none;align-items:center;justify-content:center;z-index:150;padding:18px}
.mbox{background:var(--navy2);border:1px solid var(--line);border-radius:16px;padding:20px;max-width:min(92vw,560px);width:100%}
.toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:#16a34a;color:#fff;padding:10px 18px;border-radius:10px;font-weight:700;font-size:13px;z-index:200;opacity:0;transition:opacity .3s;pointer-events:none}
.toast.show{opacity:1}
@media(max-width:900px){
.layout{grid-template-columns:1fr}
#palette{grid-template-columns:repeat(auto-fill,minmax(34px,1fr))}
.qimg{max-height:40vh}
}
</style>
</head>
<body>
<div class="topbar">
  <div class="brand"><span class="logo">SD</span><div class="bname"><b>Saurabh Daddy Test Series</b><span id="dtitle">Answers</span></div></div>
  <span class="status" id="status">Building</span>
  <button class="tbtn" onclick="reopenDraft()">&larr; Builder me</button>
  <button class="tbtn primary" onclick="publishTest()">Publish Test</button>
</div>
<div class="layout">
  <div class="qarea">
    <div id="qcard"></div>
    <div class="navrow">
      <button class="tbtn" onclick="nav(-1)">&#9664; Prev</button>
      <span id="qpos">1 / 1</span>
      <button class="tbtn" onclick="nav(1)">Next &#9654;</button>
      <button class="tbtn primary" onclick="saveNext()">Save &amp; Next</button>
    </div>
  </div>
  <div class="pcol">
    <h4>Progress</h4>
    <div class="prog"><div class="bar" id="bar"></div></div>
    <p class="ptext" id="ptext">0 answered</p>
    <div id="palette"></div>
  </div>
</div>
<div class="modal" id="modal" onclick="if(event.target===this)closeModal()"><div class="mbox" id="mbox"></div></div>
<div class="toast" id="toast"></div>
<script>
var DRAFT_ID=parseInt((location.pathname.split('/').pop())||'0');
var TOKEN=localStorage.getItem('cbt_admin_token')||'';
var qs=[],ans={},cur=0,status='building';
function authHeaders(){return {'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json'};}
function api(u,o){return fetch(u,o).then(function(r){return r.json().catch(function(){return {};}).then(function(j){if(!r.ok)throw new Error(j.detail||('HTTP '+r.status));return j;});});}
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function sectionOf(no){if(no<=45)return 'Physics';if(no<=90)return 'Chemistry';return 'Biology';}

var toastTimer=null;
function toast(msg){
  var t=document.getElementById('toast');
  t.textContent=msg;t.classList.add('show');
  clearTimeout(toastTimer);toastTimer=setTimeout(function(){t.classList.remove('show');},2200);
}

async function load(){
  var d=await api('/api/admin/draft/'+DRAFT_ID,{headers:authHeaders()});
  qs=d.questions||[];
  ans=d.answers||{};
  status=d.status||'building';
  document.getElementById('dtitle').textContent=d.title||'';
  var st=document.getElementById('status');
  if(status==='published'){st.textContent='Published';st.classList.add('pub');}
  if(cur>=qs.length)cur=qs.length-1;
  if(cur<0)cur=0;
  render();
}

function render(){renderQ();renderPalette();}

function renderQ(){
  var card=document.getElementById('qcard');
  if(!qs.length){
    card.innerHTML='<div class="empty">Koi question nahi - pehle Builder me questions add karo.</div>';
    return;
  }
  var q=qs[cur];
  var body='';
  if(q.type==='image'){
    body='<img class="qimg" src="/api/admin/draft/'+DRAFT_ID+'/question/'+q.no+'/img" alt="Q'+q.no+'" onerror="imgErr(this)">';
  }else{
    body='<div class="qtext">'+esc(q.text)+'</div>';
  }
  var sel=ans[String(q.no)]||'';
  var opts='ABCD'.split('').map(function(L){
    return '<button class="opt'+(sel===L?' sel':'')+'" onclick="pick(&quot;'+L+'&quot;)"><span class="ol">'+L+'</span><span class="ot">Option '+L+'</span>'+(sel===L?'<span class="saved">&#10003; Saved</span>':'')+'</button>';
  }).join('');
  card.innerHTML='<div class="qhead"><span class="qno">Question '+q.no+'</span><span class="qsec">'+sectionOf(q.no)+'</span></div>'
    +body
    +'<div class="opts">'+opts+'</div>'
    +'<div class="qacts"><button class="tbtn" onclick="clearResp()">Clear Response</button></div>';
  document.getElementById('qpos').textContent=(cur+1)+' / '+qs.length;
}
function imgErr(el){el.outerHTML='<p class="imgerr">Image load nahi hui - Builder me is question ka Recrop karo</p>';}

async function pick(L){
  if(status==='published'){toast('Test published hai - wapas Builder mode me lao');return;}
  try{
    await api('/api/admin/draft/'+DRAFT_ID+'/answer',{method:'POST',headers:authHeaders(),body:JSON.stringify({no:qs[cur].no,answer:L})});
    ans[String(qs[cur].no)]=L;
    render();
  }catch(e){alert(e.message);}
}

async function clearResp(){
  if(status==='published')return;
  try{
    await api('/api/admin/draft/'+DRAFT_ID+'/answer',{method:'POST',headers:authHeaders(),body:JSON.stringify({no:qs[cur].no,answer:''})});
    ans[String(qs[cur].no)]='';
    render();
  }catch(e){alert(e.message);}
}

function nav(d){var n=cur+d;if(n>=0&&n<qs.length){cur=n;render();}}
function goQ(i){cur=i;render();}

function saveNext(){
  if(!qs.length)return;
  if(!ans[String(qs[cur].no)]){toast('Pehle koi option select karo');return;}
  if(cur<qs.length-1){cur++;render();}
}

function renderPalette(){
  var h='';
  for(var i=0;i<qs.length;i++){
    var q=qs[i];
    var v=ans[String(q.no)];
    var c='num'+(v?' ans':'')+(i===cur?' cur':'');
    h+='<button class="'+c+'" onclick="goQ('+i+')">'+q.no+'</button>';
  }
  document.getElementById('palette').innerHTML=h;
  var n=0;
  for(var k in ans){if(ans[k])n++;}
  document.getElementById('ptext').textContent=n+' / '+qs.length+' answered';
  document.getElementById('bar').style.width=(qs.length?Math.round(n/qs.length*100):0)+'%';
}

async function publishTest(){
  if(!qs.length){toast('Pehle questions add karo');return;}
  if(!confirm('Publish karne par students /t/'+DRAFT_ID+' se test de sakenge. Continue?'))return;
  try{
    var d=await api('/api/admin/draft/'+DRAFT_ID+'/publish',{method:'POST',headers:authHeaders()});
    status='published';
    var st=document.getElementById('status');
    st.textContent='Published';st.classList.add('pub');
    var link=location.origin+'/t/'+DRAFT_ID;
    document.getElementById('mbox').innerHTML=
      '<h3 style="color:#fbbf24;margin-bottom:8px">&#10004; Test Published</h3>'
      +'<p style="color:#94a3b8;font-size:14px;margin-bottom:12px">Student link neeche hai - copy karke students ko bhejo.</p>'
      +'<div style="background:#0f172a;border:1px solid #334155;border-radius:10px;padding:10px 12px;font-size:13px;word-break:break-all;margin-bottom:12px" id="linkbox">'+link+'</div>'
      +'<button class="tbtn primary" style="width:100%" onclick="copyLink()">Copy Link</button>'
      +'<p style="color:#64748b;font-size:12px;margin-top:10px">Final offline HTML file ke liye Panel &rarr; Final Papers &rarr; Finalize karo.</p>';
    document.getElementById('modal').style.display='flex';
  }catch(e){alert(e.message);}
}
function closeModal(){document.getElementById('modal').style.display='none';}

function copyLink(){
  var t=document.getElementById('linkbox').textContent;
  navigator.clipboard.writeText(t).then(function(){toast('Link copy ho gaya');}).catch(function(){toast('Manually copy karo');});
}

async function reopenDraft(){
  if(!confirm('Builder mode me wapas jana hai? Answers ka data safe rahega.'))return;
  try{
    await api('/api/admin/draft/'+DRAFT_ID+'/reopen',{method:'POST',headers:authHeaders()});
    location.href='/admin/builder/'+DRAFT_ID;
  }catch(e){alert(e.message);}
}

document.addEventListener('keydown',function(e){
  var m=document.getElementById('modal');
  if(m&&m.style.display==='flex')return;
  var k=e.key.toLowerCase();
  if(k==='a')pick('A');
  else if(k==='b')pick('B');
  else if(k==='c')pick('C');
  else if(k==='d')pick('D');
  else if(k==='arrowleft')nav(-1);
  else if(k==='arrowright')nav(1);
  else if(k==='enter')saveNext();
});

document.addEventListener('DOMContentLoaded',function(){
  if(!TOKEN){location.href='/admin';return;}
  load().catch(function(e){
    if(String(e.message).indexOf('token')>-1||String(e.message).indexOf('401')>-1){location.href='/admin';}
    else{alert(e.message);}
  });
});
</script>
</body>
</html>"""