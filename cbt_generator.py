from __future__ import annotations

import html
import json

PLAYER_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#eef1f6;--card:#fff;--text:#17212b;--muted:#64748b;--accent:#2563eb;
--border:#dbe2ec;--ok:#16a34a;--bad:#dc2626;--mark:#9333ea;--unseen:#94a3b8}
body.dark{--bg:#0f172a;--card:#1e293b;--text:#e2e8f0;--muted:#94a3b8;--border:#334155}
body{background:var(--bg);color:var(--text);font-family:system-ui,Segoe UI,Roboto,sans-serif}
header{display:flex;align-items:center;gap:16px;padding:12px 20px;background:var(--card);
border-bottom:1px solid var(--border);position:sticky;top:0;z-index:5}
.brand{font-weight:700;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.timer{font-variant-numeric:tabular-nums;font-weight:700;background:var(--accent);color:#fff;
padding:6px 14px;border-radius:8px;min-width:110px;text-align:center}
#themeBtn{cursor:pointer;border:1px solid var(--border);background:var(--card);color:var(--text);border-radius:8px;padding:6px 10px}
main{display:flex;gap:20px;padding:20px;max-width:1100px;margin:0 auto}
.qwrap{flex:1}
#qArea{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px;min-height:380px}
.qno{font-weight:700;color:var(--accent);margin-bottom:10px}
.qtext{font-size:16px;line-height:1.65;margin:8px 0;white-space:pre-wrap;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:14px}
#qArea img{max-width:100%;border-radius:8px;border:1px solid var(--border)}
.opts{display:grid;gap:10px;margin-top:16px}
.opt{display:flex;gap:12px;align-items:center;padding:12px 14px;cursor:pointer;
border:1px solid var(--border);border-radius:10px;background:var(--card);color:var(--text);font-size:16px}
.opt:hover{border-color:var(--accent)}
.opt.selected{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 8%,var(--card))}
.opt-label{font-weight:700;min-width:24px;height:24px;border:1px solid var(--border);border-radius:50%;
display:inline-flex;align-items:center;justify-content:center;font-size:13px}
.opt.selected .opt-label{background:var(--accent);color:#fff;border-color:var(--accent)}
.controls{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}
.controls button,.palette button{cursor:pointer;border:1px solid var(--border);background:var(--card);
color:var(--text);padding:10px 16px;border-radius:10px;font-weight:600;font-size:14px}
aside.palette{width:240px;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;height:fit-content}
.legend{display:grid;gap:6px;font-size:12px;color:var(--muted);margin-bottom:12px}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}
#paletteGrid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:14px}
.pcell{width:100%;aspect-ratio:1;border-radius:8px;border:1px solid var(--border);background:var(--unseen);
color:#fff;font-size:12px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center}
.pcell.v{background:#ef4444}.pcell.a{background:var(--ok)}.pcell.m{background:var(--mark)}
.pcell.am{background:var(--mark);box-shadow:inset 0 0 0 3px var(--ok)}
#submitBtn{width:100%;background:var(--accent);color:#fff;border:none!important}
#modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:10;align-items:center;justify-content:center}
#modal .box{background:var(--card);border-radius:14px;padding:28px;max-width:640px;width:92%;max-height:82vh;overflow:auto}
.stat{display:flex;gap:20px;margin:18px 0;flex-wrap:wrap}
.stat div{flex:1;min-width:110px;background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center}
.stat b{display:block;font-size:24px}
#reviewArea{margin-top:14px;display:grid;gap:10px}
.rq{border:1px solid var(--border);border-radius:10px;padding:12px;font-size:14px}
.rq.ok{border-left:4px solid var(--ok)}.rq.bad{border-left:4px solid var(--bad)}
"""

PLAYER_JS = r"""
const DATA = __DATA__;
const N = DATA.questions.length;
const LETTERS = ['A','B','C','D'];
const ST = {none:0, seen:1, ans:2, mark:3, ansmark:4};
const state = new Array(N).fill(ST.none);
const sel   = new Array(N).fill(null);
let idx = 0, submitted = false;
let remaining = DATA.settings.duration * 60;
let timerId;

const $ = id => document.getElementById(id);
function cls(i){return state[i]===ST.ans?'a':state[i]===ST.mark?'m':
  state[i]===ST.ansmark?'am':state[i]===ST.seen?'v':''}

function renderQuestion(){
  const q = DATA.questions[idx], area = $('qArea');
  area.innerHTML = '';
  const qno = document.createElement('div'); qno.className='qno';
  qno.textContent = 'Question ' + q.no; area.append(qno);
  if (q.text) {
    const td = document.createElement('div'); td.className='qtext';
    td.textContent = q.text; area.append(td);
  } else {
    const img = document.createElement('img');
    img.src = 'data:image/png;base64,' + q.image_b64; area.append(img);
  }
  const opts = document.createElement('div'); opts.className='opts';
  LETTERS.forEach(L => {
    const b = document.createElement('button');
    b.className = 'opt' + (sel[idx]===L ? ' selected' : '');
    b.innerHTML = '<span class="opt-label">'+L+'</span><span>Option '+L+'</span>';
    b.onclick = () => { if(submitted) return;
      sel[idx] = L;
      state[idx] = state[idx]>=ST.mark ? ST.ansmark : ST.ans;
      renderQuestion(); renderPalette(); };
    opts.append(b);
  });
  area.append(opts);
  renderPalette();
}
function renderPalette(){
  const g = $('paletteGrid'); g.innerHTML='';
  for(let i=0;i<N;i++){
    const c=document.createElement('button'); c.className='pcell '+cls(i);
    c.textContent=i+1; c.onclick=()=>{idx=i;renderQuestion()}; g.append(c);
  }
}
function saveState(){ state[idx] = sel[idx] ? (state[idx]>=ST.mark?ST.ansmark:ST.ans) : (state[idx]?state[idx]:ST.seen); }
$('nextBtn').onclick = ()=>{ saveState(); if(idx<N-1){idx++;renderQuestion()} };
$('prevBtn').onclick = ()=>{ saveState(); if(idx>0){idx--;renderQuestion()} };
$('markBtn').onclick = ()=>{ state[idx]=sel[idx]?ST.ansmark:ST.mark; if(idx<N-1){idx++;renderQuestion()} else renderPalette(); };
$('clearBtn').onclick = ()=>{ sel[idx]=null; state[idx]=state[idx]>=ST.mark?ST.mark:ST.seen; renderQuestion(); };
$('themeBtn').onclick = ()=>document.body.classList.toggle('dark');
$('submitBtn').onclick = ()=>{ if(!submitted && confirm('Submit the test?')) submitTest(false); };
function fmt(s){s=Math.max(0,s);const h=String(Math.floor(s/3600)).padStart(2,'0'),
  m=String(Math.floor(s%3600/60)).padStart(2,'0'),ss=String(s%60).padStart(2,'0');
  return h+':'+m+':'+ss;}
function tick(){ $('timer').textContent = fmt(--remaining);
  if(remaining<=0){ clearInterval(timerId); submitTest(true); } }
function submitTest(auto){
  submitted = true; clearInterval(timerId);
  let correct=0, wrong=0, skipped=0, score=0;
  const details = [];
  for(let i=0;i<N;i++){
    const q=DATA.questions[i], right=DATA.answers[q.no];
    if(sel[i]==null){skipped++; details.push({i,ok:null,right});}
    else if(sel[i]===right){correct++; score+=DATA.settings.positive; details.push({i,ok:true,right});}
    else {wrong++; score-=DATA.settings.negative; details.push({i,ok:false,right});}
  }
  $('modal').style.display='flex';
  $('modalTitle').textContent = auto ? 'Time up - auto-submitted' : 'Test submitted';
  $('stats').innerHTML =
    '<div><b>'+score+'</b>Score</div><div><b>'+correct+'</b>Correct</div>'+
    '<div><b>'+wrong+'</b>Wrong</div><div><b>'+skipped+'</b>Skipped</div>';
  $('reviewArea').innerHTML = details.map(d=>{
    const q=DATA.questions[d.i];
    const status = d.ok===null?'- skipped':d.ok?'Correct':'Wrong';
    const line = 'Your answer: '+(sel[d.i]||'-')+' - Correct: '+d.right;
    return '<div class="rq '+(d.ok===true?'ok':d.ok===false?'bad':'')+'">'+
      '<b>Q'+(d.i+1)+'</b> - '+status+'<br>'+line+'</div>';
  }).join('');
}
renderQuestion();
$('timer').textContent = fmt(remaining);
timerId = setInterval(tick, 1000);
window.onbeforeunload = () => submitted ? null : 'Test in progress';
"""


def render_cbt(questions: list, answers: dict, settings: dict) -> str:
    data = {"questions": questions, "answers": answers, "settings": settings}
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    js = PLAYER_JS.replace("__DATA__", payload)
    title = html.escape(settings.get("title", "CBT"))
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - CBT</title><style>{PLAYER_CSS}</style></head>
<body>
<header><div class="brand">{title}</div>
<div class="timer" id="timer">00:00:00</div>
<button id="themeBtn">Theme</button></header>
<main><div class="qwrap"><div id="qArea"></div>
<div class="controls">
<button id="prevBtn">Previous</button><button id="clearBtn">Clear Response</button>
<button id="markBtn">Mark for Review &amp; Next</button><button id="nextBtn">Save &amp; Next</button>
</div></div>
<aside class="palette">
<div class="legend">
<span><span class="dot" style="background:#94a3b8"></span>Not visited</span>
<span><span class="dot" style="background:#ef4444"></span>Visited / not answered</span>
<span><span class="dot" style="background:#16a34a"></span>Answered</span>
<span><span class="dot" style="background:#9333ea"></span>Marked for review</span>
</div>
<div id="paletteGrid"></div>
<button id="submitBtn">Submit Test</button>
</aside></main>
<div id="modal"><div class="box"><h2 id="modalTitle"></h2>
<div class="stat" id="stats"></div>
<div id="reviewArea"></div>
<button onclick="document.getElementById('modal').style.display='none'" style="margin-top:14px">Close</button>
</div></div>
<script>{js}</script>
</body></html>"""