# admin_ui.py - sirf admin panel (customize easy)

ADMIN_UI = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admin Panel - CBT Builder</title>
<style>
body{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;max-width:1000px;margin:30px auto;padding:0 20px}
h2{margin:0 0 16px}
input,textarea{padding:10px;border-radius:8px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;font-size:15px;box-sizing:border-box;width:100%}
button{padding:10px 16px;border-radius:8px;border:none;background:#2563eb;color:#fff;font-weight:700;cursor:pointer;font-size:14px}
button:disabled{background:#475569;cursor:wait}
button.gray{background:#475569}
button.red{background:#dc2626}
button.green{background:#16a34a}
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:18px;margin:16px 0}
h3{margin:0 0 10px;font-size:15px;color:#94a3b8}
.tabs{display:flex;gap:8px;align-items:center;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:8px;margin:16px 0;flex-wrap:wrap}
.tabbtn{background:transparent;color:#94a3b8;border:1px solid transparent}
.tabbtn.active{background:#2563eb;color:#fff}
.row{display:flex;justify-content:space-between;gap:10px;align-items:center;border:1px solid #334155;border-radius:10px;padding:12px;margin-top:8px;font-size:14px;flex-wrap:wrap}
.row a{color:#60a5fa;text-decoration:none;font-weight:600}
.row small{color:#64748b}
.row .actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.fld{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin:8px 0}
.hint{color:#94a3b8;font-size:13px}
#upmsg,#uerr,#fm-msg{color:#f87171;font-size:14px}
#fm-dl a{color:#4ade80;font-weight:700}
#finalModal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:20;align-items:center;justify-content:center}
#finalModal .box{background:#1e293b;border-radius:12px;padding:20px;max-width:560px;width:92%;max-height:88vh;overflow:auto}
#finalModal label{font-size:13px;color:#94a3b8;display:block;margin:10px 0 4px}
#finalModal h3{margin:0}
</style>
</head>
<body>
<h2>Admin Panel - CBT Builder</h2>
<div id="panel">
<div class="tabs">
<button class="tabbtn active" id="tab-work" onclick="tab('work')">Current Paper</button>
<button class="tabbtn" id="tab-final" onclick="tab('final')">Final HTML</button>
<button class="tabbtn" id="tab-users" onclick="tab('users')">Admins</button>
<span style="flex:1"></span>
<span class="hint" id="who"></span>
<button class="gray" onclick="logout()">Logout</button>
</div>

<div id="view-work">
<div class="card">
<h3>Upload PDF - naya paper</h3>
<input type="file" id="qp" accept="application/pdf">
<div class="fld">
<input type="text" id="title" placeholder="Test title (optional)">
<input type="number" id="dur" value="180" title="Duration (minutes)">
<input type="number" id="pos" value="4" title="Correct marks">
<input type="number" id="neg" value="1" title="Negative marks">
</div>
<button onclick="upload()">Upload PDF</button>
<div id="upmsg"></div>
</div>
<div class="card">
<h3>Current paper workspace - sab admins ko dikhta hai, jahan tak save hua wahan se continue karo</h3>
<div id="list"><p style="color:#64748b">Loading...</p></div>
</div>
</div>

<div id="view-final" style="display:none">
<div class="card">
<h3>Generated final HTML files - single file, offline, password protected</h3>
<div id="flist"><p style="color:#64748b">Loading...</p></div>
</div>
</div>

<div id="view-users" style="display:none">
<div class="card">
<h3>Add admin (5-6 members team)</h3>
<div class="fld" style="grid-template-columns:1fr 1fr 1fr 1fr">
<input type="text" id="nname" placeholder="Name">
<input type="text" id="nuname" placeholder="Username">
<input type="password" id="npw" placeholder="Password">
<button onclick="addUser()">Add</button>
</div>
<div id="uerr"></div>
</div>
<div class="card"><h3>All admins</h3><div id="ulist"></div></div>
</div>
</div>

<div id="finalModal"><div class="box">
<h3>Finalize and Generate HTML</h3>
<div class="hint" style="margin-top:6px">Paper: <b id="fm-title"></b></div>
<label>Welcome screen title</label>
<input type="text" id="fm-wt">
<label>Welcome message (Accept and Continue se pehle dikhega)</label>
<textarea id="fm-wm" rows="4"></textarea>
<label>Password for the HTML file (students ko alag se bhejna)</label>
<input type="text" id="fm-pw">
<label>Answer key link (optional - result page par dikhega aur admin panel me bhi)</label>
<input type="text" id="fm-ak" placeholder="https://... (optional)">
<div id="fm-msg"></div>
<div id="fm-dl"></div>
<button onclick="doFinalize()" style="margin-top:12px;width:100%">Generate Final HTML</button>
<button class="gray" onclick="closeModal()" style="margin-top:8px;width:100%">Cancel</button>
</div></div>

<script>
var token = localStorage.getItem('cbt_admin_token') || '';
if (!token) { window.location.href = '/admin'; }
var finId = 0;
var DRAFTS = {};

function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); }
function kb(n){ return n>1048576 ? (n/1048576).toFixed(1)+' MB' : Math.max(1,Math.round(n/1024))+' KB'; }

function errText(j){
  if (j && typeof j.detail === 'string') return j.detail;
  if (j && Array.isArray(j.detail) && j.detail.length){
    return j.detail.map(function(d){
      return ((d.loc && d.loc.length ? d.loc.join('.') + ': ' : '') + (d.msg || 'Invalid input'));
    }).join('; ');
  }
  return 'Request failed - server response check karo';
}

function api(path, opts){
  opts = opts || {};
  opts.headers = Object.assign({}, opts.headers, {'Authorization':'Bearer '+token});
  if (opts.body && typeof opts.body !== 'string') opts.body = JSON.stringify(opts.body);
  if (opts.body) opts.headers['Content-Type'] = 'application/json';
  return fetch(path, opts).then(function(r){
    if (r.status === 401){ window.location.href = '/admin'; throw new Error('Session expired - login again'); }
    return r.json().then(function(j){
      if (!r.ok) throw new Error(errText(j));
      return j;
    });
  });
}

function logout(){
  localStorage.removeItem('cbt_admin_token');
  localStorage.removeItem('cbt_admin_who');
  window.location.href = '/admin';
}

function tab(name){
  ['work','final','users'].forEach(function(t){
    document.getElementById('tab-'+t).classList.toggle('active', t===name);
    document.getElementById('view-'+t).style.display = (t===name)?'block':'none';
  });
}

function statusLabel(st){
  return st==='published' ? 'Published' : (st==='answers_pending' ? 'Answers pending' : 'Building');
}

function loadDrafts(){
  api('/api/admin/drafts').then(function(list){
    DRAFTS = {};
    list.forEach(function(d){ DRAFTS[d.id] = d; });
    var h = '';
    list.forEach(function(d){
      var links = '<a href="/admin/builder/'+d.id+'">Builder</a>'
        + ' <a href="/admin/answers/'+d.id+'">Answers</a>';
      if (d.status === 'answers_pending'){
        links += ' <button onclick="pub('+d.id+')">Publish</button>';
      } else if (d.status === 'published'){
        links += ' <a href="/t/'+d.id+'">Test link</a>';
      }
      links += ' <button class="green" onclick="fin('+d.id+')">Finalize HTML</button>'
        + ' <button class="red" onclick="delDraft('+d.id+')">Delete</button>';
      h += '<div class="row"><div><b>'+esc(d.title)+'</b><br><small>'+statusLabel(d.status)+' | '+d.count+' questions | updated '+esc(d.updated)+'</small></div>'
        + '<div class="actions">'+links+'</div></div>';
    });
    document.getElementById('list').innerHTML = h || '<p style="color:#64748b">No drafts yet - upar PDF upload karo.</p>';
  }).catch(function(){});
}

function upload(){
  var f = document.getElementById('qp').files[0];
  if(!f){ document.getElementById('upmsg').textContent = 'Pehle PDF select karo.'; return; }
  var fd = new FormData();
  fd.append('question_pdf', f);
  fd.append('title', document.getElementById('title').value);
  fd.append('duration', document.getElementById('dur').value);
  fd.append('positive', document.getElementById('pos').value);
  fd.append('negative', document.getElementById('neg').value);
  document.getElementById('upmsg').textContent = 'Uploading...';
  fetch('/api/admin/draft/new', {method:'POST', headers:{'Authorization':'Bearer '+token}, body:fd})
    .then(function(r){ return r.json().then(function(j){ if(!r.ok) throw new Error(errText(j)); return j; }); })
    .then(function(j){
      document.getElementById('upmsg').textContent = 'Uploaded - ' + j.page_count + ' pages';
      window.location.href = j.builder_url;
    })
    .catch(function(e){ document.getElementById('upmsg').textContent = e.message; });
}

function pub(id){
  if(!confirm('Publish online test? (finalize ke baad ye link delete ho jayega)')) return;
  api('/api/admin/draft/'+id+'/publish', {method:'POST'})
    .then(loadDrafts).catch(function(e){ alert(e.message); });
}

function delDraft(id){
  if(!confirm('Draft delete karna hai? PDF + saved progress remove hoga.')) return;
  api('/api/admin/draft/'+id, {method:'DELETE'})
    .then(loadDrafts).catch(function(e){ alert(e.message); });
}

function fin(id){
  var d = DRAFTS[id] || {};
  finId = id;
  document.getElementById('fm-title').textContent = d.title || ('Draft #' + id);
  document.getElementById('fm-wt').value = d.title || '';
  document.getElementById('fm-wm').value = "Welcome to the test.\\n\\nRead all instructions carefully before starting.\\nTimer start hoga jaise hi aap Continue dabayenge.";
  document.getElementById('fm-pw').value = '';
  document.getElementById('fm-ak').value = '';
  document.getElementById('fm-msg').textContent = '';
  document.getElementById('fm-dl').innerHTML = '';
  document.getElementById('finalModal').style.display = 'flex';
}

function closeModal(){ document.getElementById('finalModal').style.display = 'none'; }

function doFinalize(){
  var pw = document.getElementById('fm-pw').value;
  var msg = document.getElementById('fm-msg');
  if(!pw){ msg.textContent = 'Paper password required hai.'; return; }
  msg.textContent = 'Generating...';
  api('/api/admin/draft/'+finId+'/finalize', {method:'POST', body:{
    welcome_title: document.getElementById('fm-wt').value,
    welcome_message: document.getElementById('fm-wm').value,
    paper_password: pw,
    answer_key_url: document.getElementById('fm-ak').value
  }}).then(function(j){
    msg.textContent = '';
    document.getElementById('fm-dl').innerHTML = '<a href="'+j.download_url+'?token='+encodeURIComponent(token)+'">Download: '+esc(j.filename)+' ('+kb(j.size)+')</a>';
    loadDrafts(); loadFinal();
  }).catch(function(e){ msg.textContent = e.message; });
}

function loadFinal(){
  api('/api/admin/final').then(function(list){
    var h = '';
    list.forEach(function(f){
      var ak = f.answer_key_url ? ' | <a href="'+esc(f.answer_key_url)+'" target="_blank">Answer key</a>' : '';
      h += '<div class="row"><div><b>'+esc(f.title)+'</b><br><small>'+esc(f.filename)+' | '+kb(f.size)+' | by '+esc(f.created_by)+' | '+esc(f.created_at)+ak+'</small></div>'
        + '<div class="actions"><button class="green" onclick="dlF('+f.id+')">Download</button>'
        + '<button class="red" onclick="delF('+f.id+')">Delete</button></div></div>';
    });
    document.getElementById('flist').innerHTML = h || '<p style="color:#64748b">Abhi koi final HTML nahi bana.</p>';
  }).catch(function(){});
}

function dlF(id){ window.location.href = '/api/admin/final/'+id+'/download?token='+encodeURIComponent(token); }

function delF(id){
  if(!confirm('Final HTML delete karna hai?')) return;
  api('/api/admin/final/'+id, {method:'DELETE'})
    .then(loadFinal).catch(function(e){ alert(e.message); });
}

function loadUsers(){
  api('/api/admin/users').then(function(list){
    var h = '';
    list.forEach(function(u){
      h += '<div class="row"><div><b>'+esc(u.name||u.username)+'</b> <small>@'+esc(u.username)+' | joined '+esc(u.created_at)+'</small></div>'
        + '<button class="red" onclick="delU('+u.id+')">Remove</button></div>';
    });
    document.getElementById('ulist').innerHTML = h || '<p style="color:#64748b">Koi admin nahi.</p>';
  }).catch(function(){});
}

function addUser(){
  var name = document.getElementById('nname').value;
  var username = document.getElementById('nuname').value;
  var pw = document.getElementById('npw').value;
  document.getElementById('uerr').textContent = '';
  api('/api/admin/users', {method:'POST', body:{name:name, username:username, password:pw}})
    .then(function(){ document.getElementById('npw').value=''; loadUsers(); })
    .catch(function(e){ document.getElementById('uerr').textContent = e.message; });
}

function delU(id){
  if(!confirm('Is admin ko remove karna hai?')) return;
  api('/api/admin/users/'+id, {method:'DELETE'})
    .then(loadUsers).catch(function(e){ alert(e.message); });
}

api('/api/admin/me').then(function(me){
  document.getElementById('who').textContent = 'Logged in: ' + (me.name || me.username);
  loadDrafts(); loadFinal(); loadUsers();
}).catch(function(){ window.location.href = '/admin'; });
</script>
</body>
</html>
"""