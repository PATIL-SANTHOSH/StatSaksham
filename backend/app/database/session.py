import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

def normalize_database_url(url: str) -> str:
    url = url.strip().strip('"').strip("'")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    # Handle unencoded @ or special chars in password
    if "://" in url and not url.startswith("sqlite"):
        try:
            prefix, rest = url.split("://", 1)
            if "@" in rest:
                last_at = rest.rfind("@")
                creds, host_part = rest[:last_at], rest[last_at + 1:]
                if ":" in creds:
                    first_colon = creds.find(":")
                    user, pwd = creds[:first_colon], creds[first_colon + 1:]
                    # If password contains unencoded @ or symbols
                    if "@" in pwd:
                        pwd = urllib.parse.quote_plus(pwd)
                    url = f"{prefix}://{user}:{pwd}@{host_part}"
        except Exception:
            pass
    return url

# Normalize database URL
db_url = normalize_database_url(settings.DATABASE_URL)

# Configure engine arguments based on dialect
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args
else:
    # PostgreSQL / Supabase Connection Pool configuration
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 300  # Refresh connections every 5 mins for Supabase poolers
    # Enable SSL if connecting to Supabase and not already specified
    if "supabase" in db_url and "sslmode" not in db_url:
        connect_args["sslmode"] = "require"
    if connect_args:
        engine_kwargs["connect_args"] = connect_args

engine = create_engine(db_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
