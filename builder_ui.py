# builder_ui.py - Saurabh Daddy Test Series (Question Builder UI) v2.3
# Fix: JS me koi backslash escape nahi - 'none' SyntaxError khatam
# Page viewer PDF jaisa fit + scale-aware crop + recrop/insert modes

BUILDER_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Builder - Saurabh Daddy Test Series</title>
<style>
:root{--navy:#0f172a;--navy2:#1e293b;--line:#334155;--gold:#fbbf24;--gold2:#d97706;--txt:#e2e8f0;--mut:#94a3b8}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:linear-gradient(135deg,#0f172a,#1e293b 55%,#0f172a);color:var(--txt);min-height:100vh}
button{font-family:inherit}
.topbar{display:flex;align-items:center;gap:12px;padding:12px 18px;background:rgba(15,23,42,.95);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:60;flex-wrap:wrap}
.logo{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#fbbf24,#d97706);color:#1e293b;font-weight:900;font-size:16px;box-shadow:0 4px 12px rgba(251,191,36,.3)}
.brand{display:flex;align-items:center;gap:12px;flex:1;min-width:200px}
.bname b{font-size:15px;color:var(--gold)}
.bname span{display:block;font-size:12px;color:var(--mut)}
.tbtn{border:1px solid var(--line);background:var(--navy2);color:var(--txt);border-radius:10px;padding:9px 14px;font-size:13px;font-weight:700;cursor:pointer}
.tbtn:hover{border-color:var(--gold);color:var(--gold)}
.tbtn.primary{background:linear-gradient(135deg,#fbbf24,#d97706);color:#1e293b;border:none}
.tbtn.danger{background:#dc2626;color:#fff;border:none}
.modebar{display:flex;align-items:center;gap:10px;padding:8px 18px;background:rgba(30,41,59,.7);border-bottom:1px solid var(--line);font-size:13px;flex-wrap:wrap}
.modechip{background:#312e81;color:#a5b4fc;padding:4px 12px;border-radius:20px;font-weight:800;font-size:12px}
.modeinfo{color:var(--mut);font-weight:600}
.layout{display:grid;grid-template-columns:150px minmax(0,1fr) 380px;gap:14px;padding:14px 18px;align-items:start}
.panel{background:var(--navy2);border:1px solid var(--line);border-radius:14px;padding:12px}
.panel h4{font-size:13px;color:var(--gold);margin-bottom:10px;letter-spacing:.5px}
.pages{display:flex;flex-direction:column;gap:6px;max-height:calc(100vh - 170px);overflow:auto}
.pg{border:1px solid var(--line);background:#0f172a;color:var(--mut);border-radius:8px;padding:8px 10px;font-size:12px;font-weight:700;cursor:pointer;text-align:center}
.pg:hover{border-color:var(--gold);color:var(--gold)}
.pg.on{background:var(--gold);color:#1e293b;border-color:var(--gold)}
.pg.top{border-style:dashed;color:#a5b4fc}
.pg.top.on{background:#7c3aed;color:#fff;border-color:#7c3aed}
.viewer{display:flex;flex-direction:column;gap:10px;min-width:0}
.vtool{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.vtool span{color:var(--mut);font-size:12px;font-weight:700}
.pvw{position:relative;display:inline-block;line-height:0;align-self:center;max-width:100%;touch-action:none}
.pvw img{max-width:100%;max-height:calc(100vh - 215px);width:auto;height:auto;display:block;background:#fff;border-radius:8px;box-shadow:0 8px 30px rgba(0,0,0,.5);cursor:crosshair;touch-action:none;user-select:none;-webkit-user-select:none}
.sel{position:absolute;border:2px dashed var(--gold);background:rgba(251,191,36,.18);pointer-events:none;display:none;z-index:5}
.oldsel{position:absolute;border:2px dashed #f87171;background:rgba(248,113,113,.10);pointer-events:none;display:none;z-index:4}
.qpanel{display:flex;flex-direction:column;gap:8px;max-height:calc(100vh - 170px);overflow:auto}
.qitem{background:#0f172a;border:1px solid var(--line);border-radius:10px;padding:10px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.qno{background:var(--navy2);border:1px solid var(--line);color:var(--gold);min-width:34px;height:34px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:13px}
.qthumb{max-height:64px;max-width:90px;border-radius:6px;border:1px solid var(--line);background:#fff}
.qmeta{flex:1;min-width:120px}
.qmeta b{font-size:13px;display:block}
.qmeta span{font-size:11px;color:var(--mut)}
.qacts{display:flex;gap:6px;flex-wrap:wrap}
.qacts .tbtn{padding:6px 10px;font-size:11px;border-radius:8px}
.texter{display:flex;flex-direction:column;gap:8px;margin-top:12px}
.texter textarea{width:100%;min-height:70px;background:#0f172a;border:1px solid var(--line);border-radius:10px;color:var(--txt);padding:10px;font-size:14px;resize:vertical;outline:none}
.texter textarea:focus{border-color:var(--gold)}
.toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:#16a34a;color:#fff;padding:10px 18px;border-radius:10px;font-weight:700;font-size:13px;z-index:200;opacity:0;transition:opacity .3s;pointer-events:none}
.toast.show{opacity:1}
.modal{position:fixed;inset:0;background:rgba(2,6,23,.85);display:none;align-items:center;justify-content:center;z-index:150;padding:18px}
.mbox{background:var(--navy2);border:1px solid var(--line);border-radius:16px;padding:18px;max-width:min(92vw,760px);max-height:88vh;overflow:auto}
.mbox img{max-width:100%;border-radius:8px;background:#fff}
.empty{color:var(--mut);font-size:13px;text-align:center;padding:16px}
@media(max-width:1100px){
.layout{grid-template-columns:minmax(0,1fr) 340px}
.pages{flex-direction:row;flex-wrap:wrap;max-height:none}
.panel.pgpanel{grid-column:1/-1}
}
@media(max-width:780px){
.layout{grid-template-columns:1fr}
.panel.pgpanel{grid-column:auto}
.pvw img{max-height:calc(100vh - 270px)}
}
</style>
</head>
<body>
<div class="topbar">
  <div class="brand"><span class="logo">SD</span><div class="bname"><b>Saurabh Daddy Test Series</b><span id="dtitle">Builder</span></div></div>
  <button class="tbtn" onclick="location.href='/admin/panel'">&larr; Panel</button>
  <button class="tbtn primary" onclick="goAnswers()">Answers likho &rarr;</button>
</div>
<div class="modebar">
  <span class="modechip" id="modechip">ADD</span>
  <span class="modeinfo" id="modeinfo">Naya question add karne ke liye page par drag karke crop karo</span>
  <button class="tbtn" style="display:none" id="btnCancel" onclick="cancelMode()">Cancel</button>
</div>
<div class="layout">
  <div class="panel pgpanel">
    <h4>Pages</h4>
    <div class="pages" id="pages"></div>
  </div>
  <div class="viewer">
    <div class="vtool">
      <button class="tbtn" onclick="pageNav(-1)">&#9664;</button>
      <span id="pginfo">Page 1 / 1</span>
      <button class="tbtn" onclick="pageNav(1)">&#9654;</button>
      <button class="tbtn" onclick="previewCrop()">Preview Crop</button>
      <button class="tbtn primary" id="btnCrop" onclick="cropQuestion()">Crop Question</button>
      <span style="font-size:11px;color:#94a3b8">Drag karke area select karo</span>
    </div>
    <div class="pvw" id="pvw">
      <img id="pageimg" alt="page">
      <div class="oldsel" id="oldsel"></div>
      <div class="sel" id="sel"></div>
    </div>
    <div class="texter">
      <textarea id="qtext" placeholder="Text question likho (agar image crop nahi karna)..."></textarea>
      <button class="tbtn" id="btnText" onclick="saveText()">Add Text Question</button>
    </div>
  </div>
  <div class="panel">
    <h4>Questions (<span id="qcount">0</span>)</h4>
    <div class="qpanel" id="qpanel"></div>
  </div>
</div>
<div class="modal" id="modal" onclick="if(event.target===this)closeModal()"><div class="mbox" id="mbox"></div></div>
<div class="toast" id="toast"></div>
<script>
var DRAFT_ID=parseInt((location.pathname.split('/').pop())||'0');
var TOKEN=localStorage.getItem('cbt_admin_token')||'';
function authHeaders(){return {'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json'};}
function api(u,o){return fetch(u,o).then(function(r){return r.json().catch(function(){return {};}).then(function(j){if(!r.ok)throw new Error(j.detail||('HTTP '+r.status));return j;});});}

var st={mode:'add',refNo:null,page:1,pageCount:1,questions:[],sel:null,drag:null,title:'',oldRect:null};
var toastTimer=null;
function toast(msg){var t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(function(){t.classList.remove('show');},2200);}

async function load(){
  var d=await api('/api/admin/draft/'+DRAFT_ID,{headers:authHeaders()});
  st.questions=d.questions||[];
  st.pageCount=d.page_count||1;
  st.title=d.title||'';
  document.getElementById('dtitle').textContent=st.title;
  if(st.page<1||st.page>st.pageCount)st.page=1;
  renderPages();renderQuestions();renderPage();renderModeBar();
}

function renderPages(){
  var h='';
  h+='<button class="pg top'+(st.mode==='insert'&&st.refNo===0?' on':'')+'" onclick="insertTop()">+ TOP</button>';
  for(var p=1;p<=st.pageCount;p++){
    h+='<button class="pg'+(p===st.page?' on':'')+'" onclick="setPage('+p+')">P'+p+'</button>';
  }
  document.getElementById('pages').innerHTML=h;
}
function insertTop(){setMode('insert',0);selClear();}

function setPage(p){
  st.page=p;st.sel=null;st.oldRect=null;
  selEl.style.display='none';oldEl.style.display='none';
  renderPage();renderPages();
}
function pageNav(d){var p=st.page+d;if(p>=1&&p<=st.pageCount)setPage(p);}

function renderPage(){
  document.getElementById('pginfo').textContent='Page '+st.page+' / '+st.pageCount;
  imgEl.onload=function(){
    oldEl.style.display='none';st.oldRect=null;
    if(st.mode==='edit'&&st.refNo!=null){
      var q=null;
      for(var i=0;i<st.questions.length;i++){if(st.questions[i].no===st.refNo){q=st.questions[i];break;}}
      if(q&&q.type==='image'&&q.page===st.page){
        var s=imgEl.clientWidth/imgEl.naturalWidth;
        st.oldRect={x:q.rect[0]*s,y:q.rect[1]*s,w:(q.rect[2]-q.rect[0])*s,h:(q.rect[3]-q.rect[1])*s};
        oldEl.style.display='block';
        oldEl.style.left=st.oldRect.x+'px';oldEl.style.top=st.oldRect.y+'px';
        oldEl.style.width=st.oldRect.w+'px';oldEl.style.height=st.oldRect.h+'px';
      }
    }
  };
  imgEl.src='/api/admin/draft/'+DRAFT_ID+'/page/'+st.page+'?t='+Date.now();
}

var pvw=document.getElementById('pvw');
var imgEl=document.getElementById('pageimg');
var selEl=document.getElementById('sel');
var oldEl=document.getElementById('oldsel');

pvw.addEventListener('pointerdown',function(e){
  if(!imgEl.src)return;
  e.preventDefault();
  var r=pvw.getBoundingClientRect();
  st.drag={x0:e.clientX-r.left,y0:e.clientY-r.top};
  st.sel={x:st.drag.x0,y:st.drag.y0,w:0,h:0};
  try{pvw.setPointerCapture(e.pointerId);}catch(err){}
  renderSel();
});
pvw.addEventListener('pointermove',function(e){
  if(!st.drag)return;
  var r=pvw.getBoundingClientRect();
  var cw=imgEl.clientWidth,ch=imgEl.clientHeight;
  var x=Math.max(0,Math.min(cw,e.clientX-r.left));
  var y=Math.max(0,Math.min(ch,e.clientY-r.top));
  var x0=st.drag.x0,y0=st.drag.y0;
  st.sel={x:Math.min(x0,x),y:Math.min(y0,y),w:Math.abs(x-x0),h:Math.abs(y-y0)};
  renderSel();
});
['pointerup','pointercancel'].forEach(function(ev){
  pvw.addEventListener(ev,function(){st.drag=null;});
});

function renderSel(){
  if(!st.sel||st.sel.w<1||st.sel.h<1){selEl.style.display='none';return;}
  selEl.style.display='block';
  selEl.style.left=st.sel.x+'px';selEl.style.top=st.sel.y+'px';
  selEl.style.width=st.sel.w+'px';selEl.style.height=st.sel.h+'px';
}

function toImgRect(){
  if(!st.sel||st.sel.w<4||st.sel.h<4)return null;
  var s=imgEl.naturalWidth/imgEl.clientWidth;
  return [Math.round(st.sel.x*s),Math.round(st.sel.y*s),
          Math.round((st.sel.x+st.sel.w)*s),Math.round((st.sel.y+st.sel.h)*s)];
}
function selClear(){st.sel=null;st.oldRect=null;renderSel();oldEl.style.display='none';}

async function cropQuestion(){
  var rect=toImgRect();
  if(!rect){toast('Pehle page par drag karke area select karo');return;}
  var body={type:'image',page:st.page,rect:rect};
  try{
    if(st.mode==='edit'&&st.refNo!=null){
      await api('/api/admin/draft/'+DRAFT_ID+'/question/'+st.refNo,{method:'PUT',headers:authHeaders(),body:JSON.stringify(body)});
      toast('Q'+st.refNo+' update ho gaya');
    }else if(st.mode==='insert'){
      await api('/api/admin/draft/'+DRAFT_ID+'/question/insert',{method:'POST',headers:authHeaders(),body:JSON.stringify(Object.assign({after:st.refNo},body))});
      toast('Naya question insert ho gaya');
    }else{
      await api('/api/admin/draft/'+DRAFT_ID+'/question',{method:'POST',headers:authHeaders(),body:JSON.stringify(body)});
      toast('Question add ho gaya');
    }
    resetMode();selClear();await load();
  }catch(e){alert(e.message);}
}

async function saveText(){
  var txt=document.getElementById('qtext').value.trim();
  if(!txt){toast('Text khali hai - pehle likho');return;}
  var body={type:'text',text:txt};
  try{
    if(st.mode==='edit'&&st.refNo!=null){
      await api('/api/admin/draft/'+DRAFT_ID+'/question/'+st.refNo,{method:'PUT',headers:authHeaders(),body:JSON.stringify(body)});
      toast('Text update ho gaya');
    }else if(st.mode==='insert'){
      await api('/api/admin/draft/'+DRAFT_ID+'/question/insert',{method:'POST',headers:authHeaders(),body:JSON.stringify(Object.assign({after:st.refNo},body))});
      toast('Text question insert ho gaya');
    }else{
      await api('/api/admin/draft/'+DRAFT_ID+'/question',{method:'POST',headers:authHeaders(),body:JSON.stringify(body)});
      toast('Text question add ho gaya');
    }
    document.getElementById('qtext').value='';
    resetMode();await load();
  }catch(e){alert(e.message);}
}

function thumbErr(el){el.style.display='none';}

function renderQuestions(){
  var box=document.getElementById('qpanel');
  document.getElementById('qcount').textContent=st.questions.length;
  if(!st.questions.length){
    box.innerHTML='<div class="empty">Abhi koi question nahi. Left side se page select karo aur crop karo.</div>';
    return;
  }
  var h='';
  for(var i=0;i<st.questions.length;i++){
    var q=st.questions[i];
    var prev='';
    if(q.type==='image'){
      prev='<img class="qthumb" src="/api/admin/draft/'+DRAFT_ID+'/question/'+q.no+'/img" onerror="thumbErr(this)">';
    }else{
      prev='<span class="qthumb" style="display:inline-flex;align-items:center;justify-content:center;color:#94a3b8;font-size:10px;width:90px">TEXT</span>';
    }
    h+='<div class="qitem">';
    h+='<span class="qno">'+q.no+'</span>';
    h+=prev;
    h+='<div class="qmeta"><b>Q'+q.no+'</b><span>'+(q.type==='image'?'Image crop (Page '+q.page+')':'Text question')+'</span></div>';
    h+='<div class="qacts">';
    if(q.type==='image'){
      h+='<button class="tbtn" onclick="recrop('+q.no+')">Recrop</button>';
    }else{
      h+='<button class="tbtn" onclick="editText('+q.no+')">Edit</button>';
    }
    h+='<button class="tbtn" onclick="insertAfter('+q.no+')">+ After</button>';
    h+='<button class="tbtn danger" onclick="delQ('+q.no+')">Del</button>';
    h+='</div></div>';
  }
  box.innerHTML=h;
}

function recrop(no){
  setMode('edit',no);selClear();
  for(var i=0;i<st.questions.length;i++){if(st.questions[i].no===no){setPage(st.questions[i].page);break;}}
}
function insertAfter(no){setMode('insert',no);selClear();toast('Q'+no+' ke baad insert hoga - ab crop karo ya text likho');}
function delQ(no){
  if(!confirm('Q'+no+' delete karna hai?'))return;
  api('/api/admin/draft/'+DRAFT_ID+'/question/'+no,{method:'DELETE',headers:authHeaders()})
    .then(function(){toast('Q'+no+' delete ho gaya');return load();})
    .catch(function(e){alert(e.message);});
}

function setMode(m,refNo){st.mode=m;st.refNo=refNo;renderModeBar();renderPages();}
function resetMode(){st.mode='add';st.refNo=null;renderModeBar();renderPages();}
function cancelMode(){resetMode();selClear();}

function renderModeBar(){
  var chip=document.getElementById('modechip');
  var info=document.getElementById('modeinfo');
  var cancel=document.getElementById('btnCancel');
  var btnT=document.getElementById('btnText');
  var btnC=document.getElementById('btnCrop');
  if(st.mode==='edit'){
    chip.textContent='EDIT Q'+st.refNo;
    chip.style.background='#7c3aed';chip.style.color='#fff';
    info.textContent='Is question ka naya crop select karo (ya text update karo)';
    cancel.style.display='inline-block';
    btnT.textContent='Update Text';btnC.textContent='Update Crop';
  }else if(st.mode==='insert'){
    chip.textContent=st.refNo===0?'INSERT TOP':'INSERT AFTER Q'+st.refNo;
    chip.style.background='#2563eb';chip.style.color='#fff';
    info.textContent=st.refNo===0?'Top pe naya question add hoga - crop karo ya text likho':'Q'+st.refNo+' ke baad naya question add hoga - crop karo ya text likho';
    cancel.style.display='inline-block';
    btnT.textContent='Insert Text';btnC.textContent='Insert Crop';
  }else{
    chip.textContent='ADD';
    chip.style.background='#312e81';chip.style.color='#a5b4fc';
    info.textContent='Naya question add karne ke liye page par drag karke crop karo';
    cancel.style.display='none';
    btnT.textContent='Add Text Question';btnC.textContent='Crop Question';
  }
}

function editText(no){
  setMode('edit',no);
  var q=null;
  for(var i=0;i<st.questions.length;i++){if(st.questions[i].no===no){q=st.questions[i];break;}}
  document.getElementById('qtext').value=(q&&q.text)||'';
  document.getElementById('qtext').scrollIntoView({behavior:'smooth'});
}

function previewCrop(){
  var rect=toImgRect();
  if(!rect){toast('Pehle selection karo');return;}
  fetch('/api/admin/draft/'+DRAFT_ID+'/preview',{method:'POST',headers:authHeaders(),body:JSON.stringify({page:st.page,rect:rect})})
    .then(function(r){if(!r.ok)throw new Error('HTTP '+r.status);return r.blob();})
    .then(function(b){
      var u=URL.createObjectURL(b);
      document.getElementById('mbox').innerHTML='<img src="'+u+'"><p style="text-align:center;margin-top:10px"><button class="tbtn" onclick="closeModal()">Band karo</button></p>';
      document.getElementById('modal').style.display='flex';
    })
    .catch(function(e){alert(e.message);});
}
function closeModal(){document.getElementById('modal').style.display='none';}

async function goAnswers(){
  if(!st.questions.length){toast('Pehle koi question add karo');return;}
  try{
    await api('/api/admin/draft/'+DRAFT_ID+'/to_answers',{method:'POST',headers:authHeaders()});
    location.href='/admin/answers/'+DRAFT_ID;
  }catch(e){alert(e.message);}
}

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