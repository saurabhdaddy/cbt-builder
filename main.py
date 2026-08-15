# main.py - Saurabh Daddy Test Series (Manual CBT Builder) v3.4
# v3.4 fixes (v3.3 ke upar):
#  - PDF ab database me save hota hai (pdf_data) => Render restart/OOM ke baad bhi
#    draft click karte hi pura resume (page images + crops + answers) milta hai
#  - PDF bytes memory cache => har request par DB hit nahi, fast rahta hai
# v3.3 fixes (yahi the):
#  1) Login ab: username = saurabh69 , password = saurabhpapa (har startup par force reset)
#  2) Data safety: PDF rendering serial (PDF_LOCK) => 70-80 crops par memory spike/505 nahi
#     SQLite WAL mode => crash par bhi last committed data safe
#     DATABASE_URL (Postgres) support => restart/redeploy par bhi kuch nahi udta
#  3) Har unexpected error ab clean JSON 500 deta hai, process nahi marta
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from threading import Lock
from uuid import uuid4

from fastapi import (FastAPI, UploadFile, File, Form, Body, Header,
                     HTTPException, BackgroundTasks, Request)
from fastapi.responses import HTMLResponse, Response, FileResponse, JSONResponse

import database as db
import jee_player as jp
from builder_ui import BUILDER_UI
from answers_ui import ANSWER_UI
from login_ui import LOGIN_UI
from admin_ui import ADMIN_UI

try:
    import pymupdf as fitz
except ImportError:
    import fitz

SECRET = os.environ.get("CBT_SECRET", "change-me-local-secret")
ZOOM = 2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FINAL_DIR = os.path.join(BASE_DIR, "final_html")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

app = FastAPI(title="Manual CBT Builder", version="3.4", docs_url=None, redoc_url=None)


# ================= SAFETY (505/OOM + data loss fix) =================

# PDF rendering ko serial karo => ek saath kai requests PDF na kholen,
# warna memory spike hoke Render container crash karta hai (505 + data udna)
PDF_LOCK = Lock()

# SQLite WAL mode => process beech me mar jaye tab bhi last committed data safe
if getattr(db, "engine", None) is not None:
    try:
        from sqlalchemy import event as sa_event
        if str(db.engine.url).startswith("sqlite"):
            @sa_event.listens_for(db.engine, "connect")
            def _sqlite_pragmas(dbapi_conn, connection_record):
                cur = dbapi_conn.cursor()
                cur.execute("PRAGMA journal_mode=WAL")
                cur.execute("PRAGMA synchronous=NORMAL")
                cur.execute("PRAGMA busy_timeout=15000")
                cur.close()
    except Exception:
        pass

# ============ PDF IN DATABASE (restart ke baad bhi resume) ============
# Render free ki disk ephemeral hai - isliye PDF bytes DB me rakhte hain.
# Memory cache => baar-baar DB query nahi karni padti.

_PDF_CACHE: dict = {}


def get_pdf_bytes(draft_id: int) -> bytes:
    cached = _PDF_CACHE.get(draft_id)
    if cached is not None:
        return cached
    s = db.SessionLocal()
    try:
        d = s.get(db.Draft, draft_id)
        if d is None:
            raise HTTPException(404, "Draft not found")
        data = d.pdf_data
    finally:
        s.close()
    if data is None:
        # Legacy draft (purana wala): PDF disk par pada hai
        d = get_draft(draft_id)
        if not d.pdf_path or not os.path.exists(d.pdf_path):
            raise HTTPException(410, "PDF file missing - draft dobara upload karo")
        with open(d.pdf_path, "rb") as f:
            data = f.read()
    if len(_PDF_CACHE) >= 6:  # sirf chhota cache rakho
        _PDF_CACHE.pop(next(iter(_PDF_CACHE)))
    _PDF_CACHE[draft_id] = data
    return data


def open_draft_pdf(draft_id: int):
    return fitz.open(stream=get_pdf_bytes(draft_id), filetype="pdf")


# ================= AUTH =================

def hash_password(password: str) -> str:
    return hashlib.sha256((password + SECRET).encode()).hexdigest()


def user_token(username: str, password_hash: str) -> str:
    return hashlib.sha256(f"{username}:{password_hash}:{SECRET}".encode()).hexdigest()


def seed_users():
    """Har startup par force: saurabh69 / saurabhpapa main admin.
    Purana 'admin' user auto-delete => sirf saurabh69 hi main login."""
    s = db.SessionLocal()
    try:
        u = s.query(db.User).filter(db.User.username == "saurabh69").first()
        if u is None:
            s.add(db.User(name="Saurabh", username="saurabh69",
                          password_hash=hash_password("saurabhpapa")))
        else:
            u.name = "Saurabh"
            u.password_hash = hash_password("saurabhpapa")
        old = s.query(db.User).filter(db.User.username == "admin").first()
        if old is not None:
            s.delete(old)
        s.commit()
    finally:
        s.close()


def require_admin(authorization: str | None = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid admin token")
    tok = authorization[7:]
    s = db.SessionLocal()
    try:
        for u in s.query(db.User).all():
            if user_token(u.username, u.password_hash) == tok:
                return u.username
    finally:
        s.close()
    raise HTTPException(401, "Invalid admin token")


def require_admin_or_token(authorization: str | None, token: str = "") -> str:
    """Download link me header nahi jata (browser <a> tag), isliye ?token= bhi chalega."""
    if not authorization and not token:
        raise HTTPException(401, "Invalid admin token")
    tok = authorization[7:] if authorization and authorization.startswith("Bearer ") else token
    s = db.SessionLocal()
    try:
        for u in s.query(db.User).all():
            if user_token(u.username, u.password_hash) == tok:
                return u.username
    finally:
        s.close()
    raise HTTPException(401, "Invalid admin token")


def get_draft(draft_id: int):
    s = db.SessionLocal()
    d = s.get(db.Draft, draft_id)
    s.close()
    if d is None:
        raise HTTPException(404, "Draft not found")
    return d


def qlist(d) -> list:
    return json.loads(d.questions or "[]")


def save_questions(draft_id: int, questions: list):
    s = db.SessionLocal()
    try:
        d = s.get(db.Draft, draft_id)
        d.questions = json.dumps(questions)
        s.commit()
    finally:
        s.close()


def pix_png(pix):
    try:
        return pix.tobytes("png")
    except AttributeError:
        return pix.getPNGData()


# ================= STORAGE CLEANUP (free tier ke liye) =================

def cleanup_orphan_files():
    """Jo files ka koi DB record nahi hai, unhe disk se delete kar do.
    Ye safety net hai - draft/final delete ke baad bhi koi file reh jaye to yahan hat jayegi."""
    import glob
    try:
        s = db.SessionLocal()
        known_uploads = {d.pdf_path for d in s.query(db.Draft).all() if d.pdf_path}
        s.close()
    except Exception:
        known_uploads = set()
    for f in glob.glob(os.path.join(UPLOAD_DIR, "*.pdf")):
        if f not in known_uploads:
            try:
                os.remove(f)
            except OSError:
                pass
    try:
        s = db.SessionLocal()
        known_final = {os.path.join(FINAL_DIR, fp.html_filename)
                       for fp in s.query(db.FinalPaper).all() if fp.html_filename}
        s.close()
    except Exception:
        known_final = set()
    for f in glob.glob(os.path.join(FINAL_DIR, "*.html")):
        if f not in known_final:
            try:
                os.remove(f)
            except OSError:
                pass


def remove_final_paper(final_id: int, path: str):
    """Download ke baad final HTML + record server se delete - free storage nahi bharega."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
    s = db.SessionLocal()
    try:
        f = s.get(db.FinalPaper, final_id)
        if f:
            s.delete(f)
        s.commit()
    finally:
        s.close()


seed_users()
cleanup_orphan_files()  # startup par purani orphan files hata do


# ================= GLOBAL ERROR HANDLER =================
# Koi bhi unexpected error => clean JSON 500, server crash nahi, data safe

@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500,
                        content={"detail": f"Internal error: {exc}"})


# ================= PUBLIC =================

@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return LANDING


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/t/{draft_id}", response_class=HTMLResponse)
def serve_test(draft_id: int):
    d = get_draft(draft_id)
    if d.status != "published":
        raise HTTPException(403, "Test not published yet")
    questions = json.loads(d.final_questions or "[]")
    answers = json.loads(d.answers or "{}")
    settings = json.loads(d.settings or "{}")
    settings["title"] = d.title
    return jp.render_final_html(questions, answers, settings,
                                d.title, "Read instructions carefully.", "test123", "")


@app.get("/api/drafts/published")
def published_drafts():
    s = db.SessionLocal()
    rows = s.query(db.Draft).filter(db.Draft.status == "published").order_by(db.Draft.id.desc()).all()
    s.close()
    return [{"id": d.id, "title": d.title,
             "created_at": d.created_at.strftime("%Y-%m-%d") if d.created_at else ""}
            for d in rows]


# ================= ADMIN: LOGIN + USERS =================

@app.post("/api/admin/login")
def admin_login(body: dict = Body(...)):
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    s = db.SessionLocal()
    u = s.query(db.User).filter(db.User.username == username).first()
    s.close()
    if u is None or u.password_hash != hash_password(password):
        raise HTTPException(401, "Wrong username or password")
    return {"token": user_token(u.username, u.password_hash),
            "username": u.username, "name": u.name}


@app.get("/api/admin/me")
def admin_me(authorization: str | None = Header(None)):
    username = require_admin(authorization)
    s = db.SessionLocal()
    u = s.query(db.User).filter(db.User.username == username).first()
    s.close()
    return {"username": u.username, "name": u.name or u.username}


@app.get("/api/admin/users")
def user_list(authorization: str | None = Header(None)):
    require_admin(authorization)
    s = db.SessionLocal()
    rows = s.query(db.User).order_by(db.User.id).all()
    s.close()
    return [{"id": u.id, "name": u.name, "username": u.username,
             "created_at": u.created_at.strftime("%Y-%m-%d") if u.created_at else ""}
            for u in rows]


@app.post("/api/admin/users")
def user_add(body: dict = Body(...), authorization: str | None = Header(None)):
    require_admin(authorization)
    name = str(body.get("name") or "").strip()
    username = str(body.get("username") or "").strip()
    password = str(body.get("password") or "")
    if not username or not password:
        raise HTTPException(400, "Username and password are required")
    s = db.SessionLocal()
    try:
        if s.query(db.User).filter(db.User.username == username).first():
            raise HTTPException(400, "Username already exists")
        u = db.User(name=name or username, username=username,
                    password_hash=hash_password(password))
        s.add(u)
        s.commit()
    finally:
        s.close()
    return {"ok": True, "username": username}


@app.delete("/api/admin/users/{user_id}")
def user_delete(user_id: int, authorization: str | None = Header(None)):
    me = require_admin(authorization)
    s = db.SessionLocal()
    try:
        u = s.get(db.User, user_id)
        if u is None:
            raise HTTPException(404, "User not found")
        if u.username == me:
            raise HTTPException(400, "Apna account delete nahi kar sakte")
        if u.username == "saurabh69":
            raise HTTPException(400, "Main admin delete nahi kar sakte")
        s.delete(u)
        s.commit()
    finally:
        s.close()
    return {"ok": True}


# ================= ADMIN: DRAFTS =================

@app.get("/api/admin/drafts")
def admin_drafts(authorization: str | None = Header(None)):
    require_admin(authorization)
    s = db.SessionLocal()
    rows = s.query(db.Draft).order_by(db.Draft.id.desc()).all()
    s.close()
    return [{"id": d.id, "title": d.title, "status": d.status,
             "count": len(qlist(d)),
             "updated": d.updated_at.strftime("%Y-%m-%d %H:%M") if d.updated_at else ""}
            for d in rows]


@app.post("/api/admin/draft/new")
async def new_draft(question_pdf: UploadFile = File(...),
                    title: str = Form(""),
                    duration: int = Form(180),
                    positive: int = Form(4),
                    negative: int = Form(1),
                    authorization: str | None = Header(None)):
    require_admin(authorization)
    data = await question_pdf.read()
    if not data:
        raise HTTPException(400, "Empty PDF")
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        page_count = doc.page_count
        doc.close()
    except Exception:
        raise HTTPException(400, "Not a valid PDF")
    t = title.strip() or (question_pdf.filename or "Untitled Test").replace(".pdf", "")
    s = db.SessionLocal()
    try:
        d = db.Draft(title=t, pdf_data=data, page_count=page_count,
                     settings=json.dumps({"duration": duration, "positive": positive,
                                          "negative": negative}))
        s.add(d)
        s.commit()
        s.refresh(d)
        _PDF_CACHE[d.id] = data   # PDF DB me => restart ke baad bhi resume
    finally:
        s.close()
    return {"draft_id": d.id, "page_count": page_count,
            "builder_url": f"/admin/builder/{d.id}"}


@app.delete("/api/admin/draft/{draft_id}")
def delete_draft(draft_id: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    d = get_draft(draft_id)
    try:
        if d.pdf_path and os.path.exists(d.pdf_path):
            os.remove(d.pdf_path)
    except OSError:
        pass
    _PDF_CACHE.pop(draft_id, None)
    s = db.SessionLocal()
    try:
        d = s.get(db.Draft, draft_id)
        s.delete(d)
        s.commit()
    finally:
        s.close()
    return {"ok": True}


@app.get("/api/admin/draft/{draft_id}")
def draft_detail(draft_id: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    d = get_draft(draft_id)
    return {"id": d.id, "title": d.title, "status": d.status,
            "page_count": d.page_count,
            "questions": qlist(d),
            "answers": json.loads(d.answers or "{}"),
            "settings": json.loads(d.settings or "{}"),
            "url": f"/t/{draft_id}" if d.status == "published" else None}


# ================= IMAGES (public - <img> header nahi bhej sakta) =================

@app.get("/api/admin/draft/{draft_id}/page/{page}")
def page_image(draft_id: int, page: int):
    d = get_draft(draft_id)
    if not (1 <= page <= d.page_count):
        raise HTTPException(404, "Page out of range")
    with PDF_LOCK:
        doc = open_draft_pdf(draft_id)
        try:
            pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM))
        finally:
            doc.close()
    return Response(content=pix_png(pix), media_type="image/png")


@app.post("/api/admin/draft/{draft_id}/preview")
def preview_crop(draft_id: int, body: dict = Body(...),
                 authorization: str | None = Header(None)):
    require_admin(authorization)
    d = get_draft(draft_id)
    page = int(body["page"])
    rect = [int(x) for x in body["rect"]]
    with PDF_LOCK:
        doc = open_draft_pdf(draft_id)
        try:
            pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM),
                                           clip=fitz.Rect(rect[0] / ZOOM, rect[1] / ZOOM,
                                                          rect[2] / ZOOM, rect[3] / ZOOM))
        finally:
            doc.close()
    return Response(content=pix_png(pix), media_type="image/png")


@app.get("/api/admin/draft/{draft_id}/question/{no}/img")
def question_image(draft_id: int, no: int):
    d = get_draft(draft_id)
    q = next((q for q in qlist(d) if q["no"] == no), None)
    if q is None or q["type"] != "image":
        raise HTTPException(404, "Question not found")
    with PDF_LOCK:
        doc = open_draft_pdf(draft_id)
        try:
            pix = doc[q["page"] - 1].get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM),
                                                clip=fitz.Rect(*(x / ZOOM for x in q["rect"])))
        finally:
            doc.close()
    return Response(content=pix_png(pix), media_type="image/png")


# ================= QUESTIONS =================

@app.post("/api/admin/draft/{draft_id}/question")
def add_question(draft_id: int, body: dict = Body(...),
                 authorization: str | None = Header(None)):
    require_admin(authorization)
    d = get_draft(draft_id)
    qs = qlist(d)
    no = max([q["no"] for q in qs], default=0) + 1
    if body.get("type") == "text":
        q = {"no": no, "type": "text", "text": body.get("text", "")}
    else:
        q = {"no": no, "type": "image", "page": int(body["page"]),
             "rect": [int(x) for x in body["rect"]]}
    qs.append(q)
    save_questions(draft_id, qs)
    return {"no": no, "total": len(qs)}


@app.put("/api/admin/draft/{draft_id}/question/{no}")
def update_question(draft_id: int, no: int, body: dict = Body(...),
                    authorization: str | None = Header(None)):
    require_admin(authorization)
    qs = qlist(get_draft(draft_id))
    q = next((q for q in qs if q["no"] == no), None)
    if q is None:
        raise HTTPException(404, "Question not found")
    if body.get("type") == "text":
        q.update({"type": "text", "text": body.get("text", "")})
        q.pop("page", None)
        q.pop("rect", None)
    else:
        q.update({"type": "image", "page": int(body["page"]),
                  "rect": [int(x) for x in body["rect"]]})
        q.pop("text", None)
    save_questions(draft_id, qs)
    return {"ok": True}


@app.post("/api/admin/draft/{draft_id}/question/insert")
def insert_question(draft_id: int, body: dict = Body(...),
                    authorization: str | None = Header(None)):
    """Beech me question miss ho gaya? after=Q no ke baad insert karo.
    Baaki questions + answers auto-shift ho jaate hain. after=0 => TOP me."""
    require_admin(authorization)
    d = get_draft(draft_id)
    qs = qlist(d)
    after = int(body.get("after", 0))
    if after < 0 or after > len(qs):
        raise HTTPException(400, "Invalid insert position")
    new_no = after + 1
    if body.get("type") == "text":
        q = {"no": new_no, "type": "text", "text": body.get("text", "")}
    else:
        q = {"no": new_no, "type": "image", "page": int(body["page"]),
             "rect": [int(x) for x in body["rect"]]}
    out = []
    inserted = False
    for old in qs:
        if old["no"] == new_no and not inserted:
            out.append(q)
            inserted = True
        if old["no"] >= new_no:
            old = dict(old)
            old["no"] = old["no"] + 1
        out.append(old)
    if not inserted:
        out.append(q)
    for i, old in enumerate(out, 1):
        old["no"] = i
    old_ans = json.loads(d.answers or "{}")
    new_ans = {}
    for k, v in old_ans.items():
        ki = int(k)
        if ki < new_no:
            new_ans[str(ki)] = v
        else:
            new_ans[str(ki + 1)] = v
    s = db.SessionLocal()
    try:
        dd = s.get(db.Draft, draft_id)
        dd.questions = json.dumps(out)
        dd.answers = json.dumps(new_ans)
        s.commit()
    finally:
        s.close()
    return {"ok": True, "no": new_no, "total": len(out)}


@app.delete("/api/admin/draft/{draft_id}/question/{no}")
def delete_question(draft_id: int, no: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    d = get_draft(draft_id)
    qs = [q for q in qlist(d) if q["no"] != no]
    for i, q in enumerate(qs, 1):
        q["no"] = i
    old_ans = json.loads(d.answers or "{}")
    new_ans = {}
    for k, v in old_ans.items():
        ki = int(k)
        if ki < no:
            new_ans[k] = v
        elif ki > no:
            new_ans[str(ki - 1)] = v
    s = db.SessionLocal()
    try:
        d = s.get(db.Draft, draft_id)
        d.questions = json.dumps(qs)
        d.answers = json.dumps(new_ans)
        s.commit()
    finally:
        s.close()
    return {"ok": True}


# ================= ANSWERS + PUBLISH =================

@app.post("/api/admin/draft/{draft_id}/answer")
def save_answer(draft_id: int, body: dict = Body(...),
                authorization: str | None = Header(None)):
    require_admin(authorization)
    d = get_draft(draft_id)
    no = int(body["no"])
    ans = body["answer"].upper()
    answers = json.loads(d.answers or "{}")
    answers[str(no)] = ans
    s = db.SessionLocal()
    try:
        d = s.get(db.Draft, draft_id)
        d.answers = json.dumps(answers)
        s.commit()
    finally:
        s.close()
    return {"ok": True}


@app.post("/api/admin/draft/{draft_id}/to_answers")
def to_answers(draft_id: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    d = get_draft(draft_id)
    if not qlist(d):
        raise HTTPException(400, "Add at least one question first")
    s = db.SessionLocal()
    try:
        d = s.get(db.Draft, draft_id)
        d.status = "answers_pending"
        s.commit()
    finally:
        s.close()
    return {"ok": True}


@app.post("/api/admin/draft/{draft_id}/reopen")
def reopen(draft_id: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    s = db.SessionLocal()
    try:
        d = s.get(db.Draft, draft_id)
        d.status = "building"
        s.commit()
    finally:
        s.close()
    return {"ok": True}


@app.post("/api/admin/draft/{draft_id}/publish")
def publish(draft_id: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    d = get_draft(draft_id)
    qs = qlist(d)
    answers = json.loads(d.answers or "{}")
    if len(answers) < len(qs):
        raise HTTPException(400, f"Mark answers for {len(qs) - len(answers)} more question(s)")
    final = []
    with PDF_LOCK:
        doc = open_draft_pdf(draft_id)
        try:
            for q in qs:
                if q["type"] == "text":
                    final.append({"no": q["no"], "text": q.get("text", "")})
                else:
                    pix = doc[q["page"] - 1].get_pixmap(
                        matrix=fitz.Matrix(ZOOM, ZOOM),
                        clip=fitz.Rect(*(x / ZOOM for x in q["rect"])))
                    final.append({"no": q["no"],
                                  "image_b64": base64.b64encode(pix_png(pix)).decode()})
        finally:
            doc.close()
    s = db.SessionLocal()
    try:
        d = s.get(db.Draft, draft_id)
        d.final_questions = json.dumps(final)
        d.status = "published"
        s.commit()
    finally:
        s.close()
    return {"draft_id": draft_id, "status": "published", "url": f"/t/{draft_id}"}


# ================= FINALIZE (single self-contained HTML) =================

@app.post("/api/admin/draft/{draft_id}/finalize")
def finalize_draft(draft_id: int, body: dict = Body(...),
                   authorization: str | None = Header(None)):
    user = require_admin(authorization)
    d = get_draft(draft_id)
    draft_title = d.title
    qs = qlist(d)
    answers = json.loads(d.answers or "{}")
    if len(answers) < len(qs):
        raise HTTPException(400, f"Mark answers for {len(qs) - len(answers)} more question(s) first")
    paper_password = str(body.get("paper_password") or "").strip()
    if not paper_password:
        raise HTTPException(400, "Paper password is required")
    welcome_title = str(body.get("welcome_title") or draft_title).strip()
    welcome_message = str(body.get("welcome_message") or
                          "Read all instructions carefully before starting the test.").strip()
    answer_key_url = str(body.get("answer_key_url") or "").strip()

    settings = json.loads(d.settings or "{}")
    settings["title"] = draft_title

    final = []
    with PDF_LOCK:
        doc = open_draft_pdf(draft_id)
        try:
            for q in qs:
                if q["type"] == "text":
                    final.append({"no": q["no"], "text": q.get("text", "")})
                else:
                    pix = doc[q["page"] - 1].get_pixmap(
                        matrix=fitz.Matrix(ZOOM, ZOOM),
                        clip=fitz.Rect(*(x / ZOOM for x in q["rect"])))
                    final.append({"no": q["no"],
                                  "image_b64": base64.b64encode(pix_png(pix)).decode()})
        finally:
            doc.close()

    try:
        html = jp.render_final_html(final, answers, settings,
                                    welcome_title, welcome_message,
                                    paper_password, answer_key_url)
    except Exception as e:
        raise HTTPException(500, f"HTML generation failed: {e}")

    os.makedirs(FINAL_DIR, exist_ok=True)
    fname = f"paper_{draft_id}_{int(time.time())}.html"
    fpath = os.path.join(FINAL_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(fpath)

    s = db.SessionLocal()
    try:
        fp = db.FinalPaper(title=draft_title, html_filename=fname, size=size,
                           created_by=user, answer_key_url=answer_key_url)
        s.add(fp)
        d2 = s.get(db.Draft, draft_id)
        if d2:
            s.delete(d2)
        s.commit()
        final_id = fp.id
    finally:
        s.close()
    _PDF_CACHE.pop(draft_id, None)  # draft delete ho gaya, cache bhi saaf

    # Legacy disk PDF (agar purane draft se aaya ho) bhi hata do
    try:
        if d.pdf_path and os.path.exists(d.pdf_path):
            os.remove(d.pdf_path)
    except OSError:
        pass

    return {"final_id": final_id, "filename": fname, "title": draft_title,
            "size": size, "download_url": f"/api/admin/final/{final_id}/download"}


@app.get("/api/admin/final")
def final_list(authorization: str | None = Header(None)):
    require_admin(authorization)
    s = db.SessionLocal()
    rows = s.query(db.FinalPaper).order_by(db.FinalPaper.id.desc()).all()
    s.close()
    return [{"id": f.id, "title": f.title, "filename": f.html_filename,
             "size": f.size, "created_by": f.created_by,
             "answer_key_url": f.answer_key_url or "",
             "created_at": f.created_at.strftime("%Y-%m-%d %H:%M") if f.created_at else ""}
            for f in rows]


@app.get("/api/admin/final/{final_id}/download")
def final_download(final_id: int, background_tasks: BackgroundTasks,
                   token: str = "", authorization: str | None = Header(None)):
    require_admin_or_token(authorization, token)
    s = db.SessionLocal()
    f = s.get(db.FinalPaper, final_id)
    s.close()
    if f is None:
        raise HTTPException(404, "File not found")
    path = os.path.join(FINAL_DIR, f.html_filename)
    if not os.path.exists(path):
        raise HTTPException(404, "File missing on disk")
    # Download complete hote hi server se file + record delete (HTML aapke paas aa gaya)
    background_tasks.add_task(remove_final_paper, final_id, path)
    return FileResponse(path, media_type="text/html", filename=f.html_filename)


@app.delete("/api/admin/final/{final_id}")
def final_delete(final_id: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    s = db.SessionLocal()
    try:
        f = s.get(db.FinalPaper, final_id)
        if f:
            try:
                os.remove(os.path.join(FINAL_DIR, f.html_filename))
            except OSError:
                pass
            s.delete(f)
            s.commit()
    finally:
        s.close()
    return {"ok": True}


@app.post("/api/admin/cleanup")
def admin_cleanup(authorization: str | None = Header(None)):
    """Manually bhi chala sakte ho - orphan files (bina record wali) delete ho jayengi."""
    require_admin(authorization)
    cleanup_orphan_files()
    return {"ok": True}


# ================= PAGES =================

@app.get("/admin", response_class=HTMLResponse)
def admin_login_page() -> str:
    return LOGIN_UI


@app.get("/admin/panel", response_class=HTMLResponse)
def admin_panel_page() -> str:
    return ADMIN_UI


@app.get("/admin/builder/{draft_id}", response_class=HTMLResponse)
def builder_page(draft_id: int) -> str:
    return BUILDER_UI


@app.get("/admin/answers/{draft_id}", response_class=HTMLResponse)
def answers_page(draft_id: int) -> str:
    return ANSWER_UI


# ================= LANDING =================

LANDING = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Online Exam Platform</title>
<style>
body{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.card{background:#1e293b;border:1px solid #334155;border-radius:16px;padding:40px;text-align:center;max-width:420px}
h1{margin:0 0 10px}
p{color:#94a3b8;line-height:1.6}
a{display:inline-block;margin-top:16px;padding:12px 24px;background:#2563eb;color:#fff;border-radius:10px;text-decoration:none;font-weight:700}
</style>
</head>
<body>
<div class="card">
<h1>Online Exam Platform</h1>
<p>Tests yahan banaye aur distribute kiye jaate hain. Students ko final HTML files bheji jaati hain.</p>
<a href="/admin">Admin Login</a>
</div>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0",
                port=int(os.environ.get("PORT", "8000")),
                reload=os.environ.get("DEBUG") == "1")