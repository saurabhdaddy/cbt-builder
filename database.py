# database.py - v3.7 (LOCAL-FIRST + .env support)
# - Bina DATABASE_URL ke => SQLite (cbt.db) => LOCAL par sab save, kuch nahi udta
# - .env file banaoge => wo khud padh lega (DATABASE_URL + CBT_SECRET)
# - Cloud par deploy karte waqt galti se SQLite chala ke data loss na ho,
#   uske liye REQUIRE_POSTGRES=1 env set karna hoga (tabhi guard active hota hai)
import os
from pathlib import Path

# ---- .env file automatically load (agar hai to) ----
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # python-dotenv nahi hai to .env skip (local SQLite fir bhi chalega)

from sqlalchemy import (create_engine, Column, Integer, String, Text, DateTime,
                        LargeBinary, func)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///cbt.db")

# ---- Cloud guard (sirf tab active jab REQUIRE_POSTGRES=1 ho) ----
if os.environ.get("REQUIRE_POSTGRES") and not os.environ.get("DATABASE_URL"):
    raise RuntimeError(
        "DATABASE_URL not set! Cloud deploy kar rahe ho to connection string "
        "env me daalo. Local chalana hai to ye variable MAT daalo."
    )

# ---- Postgres driver check (sirf jab postgres URL ho) ----
if DATABASE_URL.startswith("postgres"):
    try:
        import psycopg2  # noqa: F401
    except ImportError:
        raise RuntimeError(
            "psycopg2-binary install nahi hai. Command: pip install psycopg2-binary"
        )
    print("DB: PostgreSQL -> " + str(DATABASE_URL).split("@")[-1].split("/")[0])
else:
    print("DB: SQLITE (local) -> cbt.db file me save hota hai")

_is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {"pool_pre_ping": True}
if _is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


class Draft(Base):
    __tablename__ = "drafts"
    id = Column(Integer, primary_key=True)
    title = Column(String, default="Untitled Test")
    pdf_path = Column(String)                       # legacy (purane disk drafts)
    pdf_data = Column(LargeBinary, nullable=True)   # PDF bytes DB me => crash/restart ke baad bhi resume
    page_count = Column(Integer, default=0)
    status = Column(String, default="building")
    questions = Column(Text, default="[]")
    answers = Column(Text, default="{}")
    final_questions = Column(Text, nullable=True)
    settings = Column(Text, default="{}")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class FinalPaper(Base):
    __tablename__ = "final_papers"
    id = Column(Integer, primary_key=True)
    title = Column(String, default="Untitled Test")
    html_filename = Column(String)
    size = Column(Integer, default=0)
    created_by = Column(String, default="")
    answer_key_url = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())


Base.metadata.create_all(engine)


def ensure_schema():
    """Purane SQLite cbt.db me missing columns add karne ke liye."""
    if not _is_sqlite:
        return
    from sqlalchemy import inspect as sa_inspect, text
    insp = sa_inspect(engine)
    with engine.begin() as con:
        if insp.has_table("users"):
            cols = {c["name"] for c in insp.get_columns("users")}
            if "name" not in cols:
                con.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR DEFAULT ''"))
            if "password_hash" not in cols:
                con.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR"))
        if insp.has_table("drafts"):
            cols = {c["name"] for c in insp.get_columns("drafts")}
            if "pdf_data" not in cols:
                con.execute(text("ALTER TABLE drafts ADD COLUMN pdf_data BLOB"))
        if insp.has_table("final_papers"):
            cols = {c["name"] for c in insp.get_columns("final_papers")}
            if "answer_key_url" not in cols:
                con.execute(text("ALTER TABLE final_papers ADD COLUMN answer_key_url TEXT DEFAULT ''"))


ensure_schema()