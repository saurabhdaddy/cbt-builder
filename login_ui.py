# login_ui.py - Login page: Saurabh Daddy Series

LOGIN_UI = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Login - Saurabh Daddy Test Series</title>
<style>
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:16px;
background:linear-gradient(160deg,#0f172a 0%,#1e1b4b 45%,#312e81 100%)}
.deco{position:fixed;inset:0;pointer-events:none;overflow:hidden}
.deco span{position:absolute;border-radius:50%;filter:blur(70px);opacity:.35}
.deco .a{width:380px;height:380px;background:#2563eb;top:-120px;left:-100px}
.deco .b{width:420px;height:420px;background:#9333ea;bottom:-140px;right:-120px}
.card{position:relative;background:rgba(15,23,42,.85);border:1px solid rgba(148,163,184,.25);border-radius:22px;padding:40px 34px;width:100%;max-width:430px;box-shadow:0 30px 80px rgba(0,0,0,.5);backdrop-filter:blur(8px)}
.brand{text-align:center;margin-bottom:26px}
.brand .logo{width:66px;height:66px;border-radius:18px;background:linear-gradient(135deg,#2563eb,#9333ea);display:flex;align-items:center;justify-content:center;margin:0 auto 14px;font-weight:900;font-size:24px;color:#fff;box-shadow:0 10px 30px rgba(37,99,235,.4)}
.brand h1{font-size:21px;margin:0;color:#fff;font-weight:800;letter-spacing:.3px}
.brand .tag{color:#a5b4fc;font-size:13px;margin-top:5px}
.brand .line{width:56px;height:3px;border-radius:2px;background:linear-gradient(90deg,#2563eb,#9333ea);margin:12px auto 0}
.fld{margin-bottom:16px}
.fld label{display:block;font-size:12.5px;color:#94a3b8;margin:0 0 6px;font-weight:700;letter-spacing:.6px}
.fld input{width:100%;padding:13px 14px;border-radius:12px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:15px;outline:none;transition:.2s}
.fld input:focus{border-color:#2563eb;box-shadow:0 0 0 3px rgba(37,99,235,.18)}
button{width:100%;padding:14px;border:none;border-radius:12px;background:linear-gradient(135deg,#2563eb,#4f46e5);color:#fff;font-size:15px;font-weight:800;cursor:pointer;letter-spacing:.5px;transition:.2s;box-shadow:0 12px 30px rgba(37,99,235,.35)}
button:hover{transform:translateY(-1px);box-shadow:0 16px 36px rgba(37,99,235,.45)}
button:disabled{opacity:.6;transform:none;cursor:wait}
.foot{text-align:center;color:#64748b;font-size:12px;margin-top:20px}
#err{color:#f87171;font-size:13.5px;margin-top:12px;text-align:center;min-height:20px;font-weight:600}
</style>
</head>
<body>
<div class="deco"><span class="a"></span><span class="b"></span></div>
<div class="card">
<div class="brand">
<div class="logo">SD</div>
<h1>Welcome to Saurabh Daddy Series</h1>
<div class="tag">Saurabh Daddy Test Series - Admin Panel</div>
<div class="line"></div>
</div>
<form id="loginForm">
<div class="fld"><label>USERNAME</label><input type="text" id="uname" autocomplete="username" placeholder="Enter username" required></div>
<div class="fld"><label>PASSWORD</label><input type="password" id="pw" autocomplete="current-password" placeholder="Enter password" required></div>
<button type="submit" id="btn">Login to Panel</button>
<div id="err"></div>
</form>
<div class="foot">Only for authorized admins</div>
</div>
<script>
localStorage.removeItem('cbt_admin_token');
localStorage.removeItem('cbt_admin_who');
document.getElementById('loginForm').addEventListener('submit', function(e){
  e.preventDefault();
  var err = document.getElementById('err');
  var btn = document.getElementById('btn');
  err.textContent = '';
  btn.disabled = true;
  btn.textContent = 'Logging in...';
  fetch('/api/admin/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      username: document.getElementById('uname').value.trim(),
      password: document.getElementById('pw').value
    })
  })
  .then(function(r){
    return r.json().then(function(j){
      if (!r.ok) throw new Error(j.detail || 'Login failed');
      return j;
    });
  })
  .then(function(j){
    localStorage.setItem('cbt_admin_token', j.token);
    localStorage.setItem('cbt_admin_who', j.name || j.username);
    window.location.href = '/admin/panel';
  })
  .catch(function(e){
    btn.disabled = false;
    btn.textContent = 'Login to Panel';
    err.textContent = e.message || 'Network error - server chal raha hai?';
  });
});
</script>
</body>
</html>
"""