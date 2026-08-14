# jee_player.py - Saurabh Daddy Test Series (Offline CBT Player) v3.0
# Single-file HTML player: password gate, timer, +4/-1, palette, review,
# diagonal "Saurabh Daddy" watermark.
# IMPORTANT: JS template me KABHI backslash nahi hai - copy-paste me kabhi nahi tootega.
import hashlib
import json

DEFAULT_SECTIONS = [
    {"name": "Physics", "start": 1, "end": 45},
    {"name": "Chemistry", "start": 46, "end": 90},
    {"name": "Biology", "start": 91, "end": 180},
]

# Diagonal "SAURABH DADDY" watermark (tiled tile, text rotated -28 deg)
WATERMARK_CSS = """
#wm{position:fixed;inset:-10%;z-index:150;pointer-events:none;opacity:.055;
background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='520' height='380'%3E%3Ctext x='50%25' y='55%25' fill='%232563eb' font-size='38' font-weight='900' font-family='Arial,Helvetica,sans-serif' text-anchor='middle' transform='rotate(-28 260 190)'%3ES A U R A B H   D A D D Y%3C/text%3E%3C/svg%3E");
background-size:520px 380px}
"""

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:linear-gradient(135deg,#0f172a 0%,#1e293b 55%,#0f172a 100%);color:#e2e8f0;min-height:100vh}
.logo{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#fbbf24,#d97706);color:#1e293b;font-weight:900;font-size:18px;box-shadow:0 4px 12px rgba(251,191,36,.35)}
#gate{position:fixed;inset:0;z-index:300;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0f172a,#1e293b)}
.gbox{background:#1e293b;border:1px solid #334155;border-radius:18px;padding:36px;width:min(92vw,420px);text-align:center}
.gbox h2{margin-top:12px;font-size:20px;color:#fbbf24}
.gbox h3{margin:4px 0 14px;color:#94a3b8;font-weight:600}
.gmsg{color:#94a3b8;margin-bottom:16px;font-size:14px}
.gbox input{width:100%;padding:12px 14px;border-radius:10px;border:1px solid #475569;background:#0f172a;color:#e2e8f0;font-size:16px;outline:none;margin-bottom:12px}
.gbox input:focus{border-color:#fbbf24}
.gbox button{width:100%;padding:12px;border:none;border-radius:10px;background:linear-gradient(135deg,#fbbf24,#d97706);color:#1e293b;font-weight:800;font-size:15px;cursor:pointer}
.pwerr{color:#f87171;font-size:13px;margin-top:10px;min-height:18px}
.topbar{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:14px;padding:12px 20px;background:rgba(15,23,42,.92);backdrop-filter:blur(8px);border-bottom:1px solid #334155;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:12px;flex:1;min-width:220px}
.bname b{font-size:16px;color:#fbbf24}
.ttitle{display:block;font-size:12px;color:#94a3b8}
.timer{font-variant-numeric:tabular-nums;font-weight:800;font-size:22px;color:#fbbf24;background:#0f172a;border:1px solid #334155;padding:8px 16px;border-radius:10px}
.btn{border:none;border-radius:10px;padding:11px 18px;font-weight:800;font-size:14px;cursor:pointer}
.btn-submit{background:#dc2626;color:#fff;padding:10px 20px}
.welcome{padding:14px 20px;border-bottom:1px solid #334155}
.welcome h3{color:#fbbf24;font-size:18px}
.welcome p{color:#94a3b8;font-size:14px;margin-top:4px}
.main{display:flex;gap:18px;padding:18px 20px;max-width:1200px;margin:0 auto}
.qcol{flex:1;min-width:0}
.pcol{width:280px;flex-shrink:0}
.qmeta{color:#94a3b8;font-size:14px;margin-bottom:10px;font-weight:700}
#qcard{background:#1e293b;border:1px solid #334155;border-radius:16px;padding:20px}
.qhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.qno{font-weight:800;font-size:16px;color:#fbbf24}
.qsec{background:#312e81;color:#a5b4fc;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700}
.qimg{max-width:100%;height:auto;border-radius:10px;border:1px solid #334155;display:block;margin:0 auto}
.qtext{font-size:17px;line-height:1.7;white-space:pre-wrap}
.opts{display:grid;gap:12px;margin-top:18px}
.opt{display:flex;align-items:center;gap:14px;width:100%;padding:14px 16px;background:#0f172a;border:2px solid #334155;border-radius:12px;color:#e2e8f0;font-size:15px;cursor:pointer;text-align:left;transition:all .15s}
.opt:hover{border-color:#fbbf24}
.opt.sel{border-color:#fbbf24;background:rgba(251,191,36,.12)}
.ol{width:34px;height:34px;border-radius:50%;background:#334155;color:#e2e8f0;display:inline-flex;align-items:center;justify-content:center;font-weight:800}
.opt.sel .ol{background:#fbbf24;color:#1e293b}
.qacts{display:flex;gap:10px;margin-top:20px;flex-wrap:wrap}
.btn-ok{background:#2563eb;color:#fff}
.btn-mark{background:#7c3aed;color:#fff}
.btn-clear{background:#334155;color:#e2e8f0}
.pcol h4{margin-bottom:10px;color:#fbbf24}
.legend{display:flex;flex-wrap:wrap;gap:8px 14px;font-size:12px;color:#94a3b8;margin-bottom:12px}
.lg{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-1px}
.lg-ans{background:#16a34a}
.lg-mark{background:#7c3aed}
.lg-vis{background:#475569}
.lg-cur{background:#2563eb}
.lg-bad{background:#dc2626}
#palette{display:grid;grid-template-columns:repeat(auto-fill,minmax(38px,1fr));gap:8px}
.num{border:1px solid #475569;background:#0f172a;color:#94a3b8;border-radius:8px;height:38px;font-size:12px;font-weight:700;cursor:pointer}
.num.ans{background:#16a34a;color:#fff;border-color:#16a34a}
.num.mark{background:#7c3aed;color:#fff;border-color:#7c3aed}
.num.vis{background:#475569;color:#fff}
.num.cur{border-color:#fbbf24;color:#fbbf24;box-shadow:0 0 0 2px rgba(251,191,36,.4)}
.lgover{display:flex;justify-content:space-between;margin-top:14px;font-size:12px;color:#94a3b8}
#result{max-width:1000px;margin:0 auto;padding:24px 20px}
.res-head{text-align:center;margin-bottom:18px}
.res-head .logo{margin:0 auto}
.res-head h2{color:#fbbf24;margin-top:10px}
.res-head h3{color:#94a3b8}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin:18px 0}
.stat{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:18px;text-align:center}
.stat b{display:block;font-size:26px;color:#fbbf24}
.stat span{color:#94a3b8;font-size:13px}
.aklink{text-align:center;margin:6px 0 18px}
.aklink a{color:#2563eb;font-weight:700;text-decoration:none}
.rv-title{margin:20px 0 12px;color:#fbbf24}
.review{display:grid;gap:14px}
.rvitem{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:16px}
.rvhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;gap:8px}
.chip{padding:3px 12px;border-radius:20px;font-size:12px;font-weight:800;color:#fff}
.chip-ok{background:#16a34a}
.chip-bad{background:#dc2626}
.chip-skip{background:#475569}
.rvans{font-size:13px;color:#94a3b8;margin-top:10px}
.rvans b{color:#e2e8f0}
@media(max-width:900px){
.main{flex-direction:column}
.pcol{width:100%}
#palette{grid-template-columns:repeat(auto-fill,minmax(34px,1fr))}
.topbar{padding:10px 14px}
.timer{font-size:18px}
}
@media(max-width:600px){
.bname b{font-size:14px}
.logo{width:36px;height:36px;font-size:15px}
.qacts .btn{flex:1;min-width:130px}
}
"""

PAGE_CSS = BASE_CSS + WATERMARK_CSS

PAGE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
/*CSS*/
</style>
</head>
<body>
<div id="wm"></div>
"""

GATE_HTML = """
<div id="gate">
  <div class="gbox">
    <div class="logo">SD</div>
    <h2>Saurabh Daddy Test Series</h2>
    <h3>Protected Test</h3>
    <p class="gmsg">Test shuru karne ke liye paper password daalo.</p>
    <input type="password" id="pw" placeholder="Paper Password">
    <button type="button" id="unlockBtn">Unlock Test</button>
    <p id="pwmsg" class="pwerr"></p>
  </div>
</div>
"""

APP_HTML = """
<div id="app" style="display:none">
  <div class="topbar">
    <div class="brand"><span class="logo">SD</span><div class="bname"><b>Saurabh Daddy Test Series</b><span class="ttitle" id="ttitle"></span></div></div>
    <div class="timer" id="timer">03:00:00</div>
    <button type="button" class="btn btn-submit" id="submitBtn">Submit Test</button>
  </div>
  <div class="welcome"><h3 id="welcomet"></h3><p id="welcomem"></p></div>
  <div class="main">
    <div class="qcol">
      <div class="qmeta"><span id="qcount"></span></div>
      <div id="qcard"></div>
    </div>
    <div class="pcol">
      <h4>Question Palette</h4>
      <div class="legend">
        <span><i class="lg lg-ans"></i>Answered</span>
        <span><i class="lg lg-mark"></i>Marked</span>
        <span><i class="lg lg-vis"></i>Visited</span>
        <span><i class="lg lg-cur"></i>Current</span>
      </div>
      <div id="palette"></div>
      <div class="lgover">
        <span><i class="lg lg-ans"></i>Correct = +__POS__</span>
        <span><i class="lg lg-bad"></i>Wrong = -__NEG__</span>
      </div>
    </div>
  </div>
</div>
<div id="result" style="display:none"></div>
"""

PLAYER_JS = r"""
var QUESTIONS = __QUESTIONS_JSON__;
var ANSWERS = __ANSWERS_JSON__;
var SECTIONS = __SECTIONS_JSON__;
var POS = __POS__;
var NEG = __NEG__;
var TOTAL_MIN = __DURATION__;
var PASSWORD_HASH = "__PASSWORD_HASH__";
var ANSWER_KEY_URL = __ANSWER_KEY_URL__;
var WELCOME_TITLE = __WELCOME_TITLE__;
var WELCOME_MESSAGE = __WELCOME_MESSAGE__;

var userAnswers = {};
var marked = {};
var visited = {};
var current = 0;
var submitted = false;
var timeLeft = TOTAL_MIN * 60;
var timerId = null;

function esc(s){
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function sectionOf(no){
  for (var i = 0; i < SECTIONS.length; i++) {
    var s = SECTIONS[i];
    if (no >= s.start && no <= s.end) return s.name;
  }
  return SECTIONS.length ? SECTIONS[SECTIONS.length - 1].name : '';
}

function qBodyHtml(q){
  if (q.image_b64) {
    return '<img class="qimg" src="data:image/png;base64,' + q.image_b64 + '" alt="Q' + q.no + '">';
  }
  if (q.image_src) {
    return '<img class="qimg" src="' + esc(q.image_src) + '" alt="Q' + q.no + '">';
  }
  return '<div class="qtext">' + esc(q.text) + '</div>';
}

function renderQuestion(){
  var q = QUESTIONS[current];
  var ua = userAnswers[q.no] || '';
  var opts = 'ABCD'.split('').map(function(L){
    return '<button type="button" class="opt' + (ua === L ? ' sel' : '') + '" data-o="' + L + '">'
      + '<span class="ol">' + L + '</span>'
      + '<span class="ot">Option ' + L + '</span>'
      + '</button>';
  }).join('');
  document.getElementById('qcard').innerHTML =
    '<div class="qhead">'
    + '<span class="qno">Question ' + q.no + '</span>'
    + '<span class="qsec">' + esc(sectionOf(q.no)) + '</span>'
    + '</div>'
    + '<div class="qbody">' + qBodyHtml(q) + '</div>'
    + '<div class="opts">' + opts + '</div>'
    + '<div class="qacts">'
    + '<button type="button" class="btn btn-ok" onclick="saveNext()">Save &amp; Next</button>'
    + '<button type="button" class="btn btn-mark" onclick="markNext()">Mark for Review &amp; Next</button>'
    + '<button type="button" class="btn btn-clear" onclick="clearResp()">Clear Response</button>'
    + '</div>';
  document.getElementById('qcount').textContent = 'Question ' + (current + 1) + ' of ' + QUESTIONS.length;
  renderPalette();
}

function renderPalette(){
  var h = '';
  for (var i = 0; i < QUESTIONS.length; i++) {
    var q = QUESTIONS[i];
    var c = 'num';
    if (userAnswers[q.no]) c += ' ans';
    else if (marked[q.no]) c += ' mark';
    else if (visited[q.no]) c += ' vis';
    if (i === current) c += ' cur';
    h += '<button type="button" class="' + c + '" data-i="' + i + '">' + q.no + '</button>';
  }
  document.getElementById('palette').innerHTML = h;
}

function goTo(i){
  if (i < 0 || i >= QUESTIONS.length || submitted) return;
  current = i;
  visited[QUESTIONS[i].no] = 1;
  renderQuestion();
}

function pick(L){
  if (submitted) return;
  var q = QUESTIONS[current];
  userAnswers[q.no] = L;
  renderQuestion();
}

function saveNext(){
  if (submitted) return;
  var q = QUESTIONS[current];
  if (!userAnswers[q.no]) { alert('Pehle koi option select karo!'); return; }
  visited[q.no] = 1;
  if (current < QUESTIONS.length - 1) { current++; renderQuestion(); }
  else { submitTest(true); }
}

function markNext(){
  if (submitted) return;
  var q = QUESTIONS[current];
  marked[q.no] = 1;
  visited[q.no] = 1;
  if (current < QUESTIONS.length - 1) { current++; renderQuestion(); }
  else { renderPalette(); }
}

function clearResp(){
  if (submitted) return;
  var q = QUESTIONS[current];
  delete userAnswers[q.no];
  delete marked[q.no];
  renderQuestion();
}

function fmt(t){
  var h = Math.floor(t / 3600);
  var m = Math.floor((t % 3600) / 60);
  var s = t % 60;
  function p(x){ return (x < 10 ? '0' : '') + x; }
  return p(h) + ':' + p(m) + ':' + p(s);
}

function tick(){
  if (submitted) return;
  timeLeft--;
  document.getElementById('timer').textContent = fmt(timeLeft);
  if (timeLeft <= 0) {
    document.getElementById('timer').style.color = '#f87171';
    submitTest(false);
  }
}

function submitTest(manual){
  if (submitted) return;
  if (manual && !confirm('Kya aap test submit karna chahte hain?')) return;
  submitted = true;
  if (timerId) clearInterval(timerId);
  var correct = 0, wrong = 0, skipped = 0;
  for (var i = 0; i < QUESTIONS.length; i++) {
    var q = QUESTIONS[i];
    var ua = userAnswers[q.no];
    if (!ua) { skipped++; continue; }
    if (ua === ANSWERS[String(q.no)]) correct++; else wrong++;
  }
  var score = correct * POS - wrong * NEG;
  var pct = QUESTIONS.length ? Math.round(score / (QUESTIONS.length * POS) * 100) : 0;
  var review = buildReview();
  document.getElementById('app').style.display = 'none';
  var r = document.getElementById('result');
  r.style.display = 'block';
  r.innerHTML =
    '<div class="res-head"><div class="logo">SD</div><h2>Saurabh Daddy Test Series</h2><h3>Result</h3></div>'
    + '<div class="stats">'
    + '<div class="stat"><b>' + score + '</b><span>Score</span></div>'
    + '<div class="stat"><b>' + correct + '</b><span>Correct</span></div>'
    + '<div class="stat"><b>' + wrong + '</b><span>Wrong</span></div>'
    + '<div class="stat"><b>' + skipped + '</b><span>Skipped</span></div>'
    + '<div class="stat"><b>' + pct + '%</b><span>Percent</span></div>'
    + '</div>'
    + (ANSWER_KEY_URL ? '<p class="aklink"><a href="' + ANSWER_KEY_URL + '" target="_blank">Answer Key dekho</a></p>' : '')
    + '<h4 class="rv-title">Question-wise Review</h4>'
    + '<div class="review">' + review + '</div>';
  window.scrollTo(0, 0);
}

function reviewItemHtml(q, state, ua, ca){
  var chip = state === 'ok' ? '<span class="chip chip-ok">Correct</span>'
           : state === 'bad' ? '<span class="chip chip-bad">Wrong</span>'
           : '<span class="chip chip-skip">Skipped</span>';
  return '<div class="rvitem">'
    + '<div class="rvhead"><span class="qno">Question ' + q.no + '</span>' + chip + '</div>'
    + '<div class="qbody">' + qBodyHtml(q) + '</div>'
    + '<div class="rvans">Your answer: <b>' + (ua || 'Not attempted') + '</b> &nbsp;|&nbsp; Correct answer: <b>' + ca + '</b></div>'
    + '</div>';
}

function buildReview(){
  var h = '';
  for (var i = 0; i < QUESTIONS.length; i++) {
    var q = QUESTIONS[i];
    var ua = userAnswers[q.no] || '';
    var ca = ANSWERS[String(q.no)] || '-';
    var state = !ua ? 'skip' : (ua === ca ? 'ok' : 'bad');
    h += reviewItemHtml(q, state, ua, ca);
  }
  return h;
}

function unlock(){
  var inp = document.getElementById('pw');
  var v = inp.value;
  if (sha256(v) === PASSWORD_HASH) {
    document.getElementById('gate').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    document.getElementById('welcomet').textContent = WELCOME_TITLE;
    document.getElementById('welcomem').textContent = WELCOME_MESSAGE;
    document.getElementById('ttitle').textContent = WELCOME_TITLE;
    renderQuestion();
    timerId = setInterval(tick, 1000);
  } else {
    document.getElementById('pwmsg').textContent = 'Galat password! Dobara try karo.';
    inp.value = '';
    inp.focus();
  }
}

document.getElementById('unlockBtn').addEventListener('click', unlock);
document.getElementById('pw').addEventListener('keydown', function(e){
  if (e.key === 'Enter') unlock();
});
document.getElementById('submitBtn').addEventListener('click', function(){ submitTest(true); });

document.getElementById('qcard').addEventListener('click', function(e){
  var el = e.target;
  while (el && el !== this && !el.classList.contains('opt')) { el = el.parentNode; }
  if (el && el.classList.contains('opt')) { pick(el.getAttribute('data-o')); }
});

document.getElementById('palette').addEventListener('click', function(e){
  var el = e.target;
  while (el && el !== this && !el.classList.contains('num')) { el = el.parentNode; }
  if (el && el.classList.contains('num')) { goTo(parseInt(el.getAttribute('data-i'), 10)); }
});

document.addEventListener('keydown', function(e){
  if (submitted) return;
  var gate = document.getElementById('gate');
  if (gate && gate.style.display !== 'none') return;
  var k = e.key.toLowerCase();
  if (k === 'a') pick('A');
  else if (k === 'b') pick('B');
  else if (k === 'c') pick('C');
  else if (k === 'd') pick('D');
  else if (k === 'enter') saveNext();
});

/* Pure-JS SHA-256 (file:// offline me bhi kaam karta hai - crypto.subtle nahi chahiye) */
function sha256(ascii){
  function rightRotate(value, amount){ return (value >>> amount) | (value << (32 - amount)); }
  var mathPow = Math.pow;
  var maxWord = mathPow(2, 32);
  var result = '';
  var words = [];
  var asciiBitLength = ascii.length * 8;
  var hash = sha256.h = sha256.h || [];
  var k = sha256.k = sha256.k || [];
  var primeCounter = k.length;
  var isComposite = {};
  for (var candidate = 2; primeCounter < 64; candidate++) {
    if (!isComposite[candidate]) {
      for (var i = 0; i < 313; i += candidate) { isComposite[i] = candidate; }
      hash[primeCounter] = (mathPow(candidate, 0.5) * maxWord) | 0;
      k[primeCounter++] = (mathPow(candidate, 1 / 3) * maxWord) | 0;
    }
  }
  ascii += String.fromCharCode(128);
  while ((ascii.length % 64) !== 56) ascii += String.fromCharCode(0);
  for (i = 0; i < ascii.length; i++) {
    var j = ascii.charCodeAt(i);
    if (j >> 8) return '';
    words[i >> 2] |= j << (((3 - i) % 4) * 8);
  }
  words[words.length] = (asciiBitLength / maxWord) | 0;
  words[words.length] = asciiBitLength;
  for (j = 0; j < words.length;) {
    var w = words.slice(j, j += 16);
    var oldHash = hash;
    hash = hash.slice(0, 8);
    for (i = 0; i < 64; i++) {
      var w15 = w[i - 15], w2 = w[i - 2];
      var a = hash[0], e = hash[4];
      var temp1 = hash[7]
        + (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25))
        + ((e & hash[5]) ^ ((~e) & hash[6]))
        + k[i]
        + (w[i] = (i < 16) ? w[i] : (w[i - 16]
          + (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3))
          + w[i - 7]
          + (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10))) | 0);
      var temp2 = (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22))
        + ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]));
      hash = [(temp1 + temp2) | 0].concat(hash);
      hash[4] = (hash[4] + temp1) | 0;
    }
    for (i = 0; i < 8; i++) { hash[i] = (hash[i] + oldHash[i]) | 0; }
  }
  for (i = 0; i < 8; i++) {
    for (j = 3; j >= 0; j--) {
      var b = (hash[i] >> (j * 8)) & 255;
      result += ((b < 16) ? '0' : '') + b.toString(16);
    }
  }
  return result;
}
"""


def _esc(s):
    return (str(s).replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def build_sections(questions, sections=None):
    secs = [dict(s) for s in (sections or DEFAULT_SECTIONS)]
    if not secs:
        return secs
    max_no = max((int(q.get("no", 0)) for q in questions), default=0)
    if max_no:
        secs[-1]["end"] = max(secs[-1]["end"], max_no)
    return secs


def render_final_html(questions, answers, settings, welcome_title="",
                      welcome_message="", password="", answer_key_url="",
                      sections=None):
    settings = settings or {}
    try:
        pos = int(settings.get("positive", 4))
    except (TypeError, ValueError):
        pos = 4
    try:
        neg = int(settings.get("negative", 1))
    except (TypeError, ValueError):
        neg = 1
    try:
        dur = int(settings.get("duration", 180))
    except (TypeError, ValueError):
        dur = 180
    title = str(settings.get("title") or welcome_title or "Test")

    qs = []
    for idx, q in enumerate(questions or []):
        item = {"no": int(q.get("no", idx + 1))}
        if q.get("text") is not None:
            item["text"] = str(q["text"])
        if q.get("image_b64"):
            item["image_b64"] = str(q["image_b64"])
        if q.get("image_src"):
            item["image_src"] = str(q["image_src"])
        qs.append(item)

    secs = build_sections(qs, sections)
    pw_hash = hashlib.sha256(str(password or "").encode("utf-8")).hexdigest()
    answers_norm = {str(k): str(v).upper() for k, v in (answers or {}).items()}

    js = (PLAYER_JS
          .replace("__QUESTIONS_JSON__", json.dumps(qs).replace("</", "<\\/"))
          .replace("__ANSWERS_JSON__", json.dumps(answers_norm).replace("</", "<\\/"))
          .replace("__SECTIONS_JSON__", json.dumps(secs))
          .replace("__DURATION__", str(dur))
          .replace("__POS__", str(pos))
          .replace("__NEG__", str(neg))
          .replace("__PASSWORD_HASH__", pw_hash)
          .replace("__ANSWER_KEY_URL__", json.dumps(answer_key_url or "").replace("</", "<\\/"))
          .replace("__WELCOME_TITLE__", json.dumps(welcome_title or "").replace("</", "<\\/"))
          .replace("__WELCOME_MESSAGE__", json.dumps(welcome_message or "").replace("</", "<\\/")))

    app_html = APP_HTML.replace("__POS__", str(pos)).replace("__NEG__", str(neg))
    html = PAGE_HEAD.replace("__TITLE__", _esc(title)).replace("/*CSS*/", PAGE_CSS)
    html += GATE_HTML + app_html + "<script>\n" + js + "\n</script>\n</body>\n</html>"
    return html


if __name__ == "__main__":
    demo_qs = [
        {"no": 1, "text": "Which of the following is a vector quantity?\n(a) Speed (b) Distance (c) Velocity (d) Mass"},
        {"no": 2, "text": "SI unit of force is:\n(a) Joule (b) Newton (c) Watt (d) Pascal"},
    ]
    demo_ans = {"1": "C", "2": "B"}
    demo = render_final_html(
        demo_qs, demo_ans,
        {"title": "Demo Test", "duration": 180, "positive": 4, "negative": 1},
        "Saurabh Daddy Test Series",
        "Is demo me 2 questions hain. Paper password: 1234",
        "1234", "")
    with open("demo_test.html", "w", encoding="utf-8") as f:
        f.write(demo)
    print("demo_test.html ready - browser me kholo, password: saurabhpapaji")
    if "\\'" in demo:
        print("WARNING: JS me backslash-escape mila - kuch galat hai!")
    else:
        print("JS clean: koi backslash-escape nahi - OK")