# database.py - Saurabh Daddy Test Series v3.4
# FIX: Render free ki disk ephemeral hai => ab data Postgres (DATABASE_URL) me save hota hai.
#      Restart / OOM / crash ke baad bhi kuch nahi udta.
#      Locally bina env ke chalao to SQLite fallback (cbt.db) use hota hai.
import os

from sqlalchemy import (create_engine, Column, Integer, String, Text, DateTime,
                        LargeBinary, func)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///cbt.db")
_is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {"pool_pre_ping": True}   # Neon/Supabase scale-to-zero ke baad connection reset
if _is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


class Draft(Base):
    __tablename__ = "drafts"
    id = Column(Integer, primary_key=True)
    title = Column(String, default="Untitled Test")
    pdf_path = Column(String)                      # legacy (purane disk wale drafts ke liye)
    pdf_data = Column(LargeBinary, nullable=True)  # NEW: PDF bytes Postgres me => restart ke baad bhi resume
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
    """Sirf purane SQLite cbt.db ke liye missing columns add karta hai.
       Naya Postgres DB to create_all() ne khud bana diya hota hai."""
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