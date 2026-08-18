from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Handling postgres vs sqlite differences
if settings.DATABASE_URL.startswith("postgres://"):
    # SQLAlchemy 1.4+ requires postgresql:// instead of postgres://
    url = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    url = settings.DATABASE_URL

connect_args = {}
if url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
