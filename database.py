from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///cbt.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class Draft(Base):
    __tablename__ = "drafts"
    id = Column(Integer, primary_key=True)
    title = Column(String, default="Untitled Test")
    pdf_path = Column(String)
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
    import sqlite3
    con = sqlite3.connect("cbt.db")
    cur = con.cursor()
    tables = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "users" in tables:
        cols = {r[1] for r in cur.execute("PRAGMA table_info(users)")}
        if "name" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN name VARCHAR DEFAULT ''")
        if "password_hash" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR")
    if "final_papers" in tables:
        cols = {r[1] for r in cur.execute("PRAGMA table_info(final_papers)")}
        if "answer_key_url" not in cols:
            cur.execute("ALTER TABLE final_papers ADD COLUMN answer_key_url TEXT DEFAULT ''")
    else:
        cur.execute("""CREATE TABLE final_papers (id INTEGER PRIMARY KEY,
            title VARCHAR DEFAULT 'Untitled Test', html_filename VARCHAR,
            size INTEGER DEFAULT 0, created_by VARCHAR DEFAULT '',
            answer_key_url TEXT DEFAULT '', created_at DATETIME)""")
    con.commit()
    con.close()


ensure_schema()