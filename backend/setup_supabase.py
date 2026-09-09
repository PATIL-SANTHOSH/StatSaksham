"""
STATSAKSHAM — Supabase PostgreSQL Setup, Migration & Seeding Tool
SIH 2026 | SIH26101 | MoSPI / DIID

Usage:
  python setup_supabase.py --test-only    (Check connection to Supabase)
  python setup_supabase.py --seed         (Create schema and seed full MoSPI dataset)
  python setup_supabase.py --verify       (Verify table counts and row statistics)
"""

import os
import sys
import time
import argparse
from sqlalchemy import text, inspect

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.database.session import engine, SessionLocal, Base
from seed_data import seed_database

def check_connection():
    print("\n" + "=" * 60)
    print("STATSAKSHAM — Database Connection Check")
    print("=" * 60)
    
    url = settings.DATABASE_URL
    # Mask password for display
    masked_url = url
    if "@" in url and "://" in url:
        prefix, rest = url.split("://", 1)
        creds, host_part = rest.split("@", 1)
        if ":" in creds:
            user, _ = creds.split(":", 1)
            masked_url = f"{prefix}://{user}:******@{host_part}"

    print(f"Target Database URL: {masked_url}")
    is_supabase = "supabase" in url.lower() or "pooler.supabase.com" in url.lower()
    print(f"Provider: {'Supabase Cloud PostgreSQL' if is_supabase else ('PostgreSQL' if 'postgres' in url.lower() else 'SQLite Local')}")

    t0 = time.time()
    try:
        with engine.connect() as conn:
            latency = (time.time() - t0) * 1000
            result = conn.execute(text("SELECT 1")).scalar()
            
            # Check version
            try:
                version_str = conn.execute(text("SELECT version()")).scalar()
            except Exception:
                version_str = "SQLite / Compatible"
            
            print(f"[OK] Connection Successful! (Latency: {latency:.1f}ms)")
            print(f"Server Engine: {version_str[:80]}")
            return True
    except Exception as e:
        print(f"[ERROR] Could not connect to database: {e}")
        if is_supabase:
            print("\nTroubleshooting Supabase Connection:")
            print("1. Ensure your Supabase project is active and not paused.")
            print("2. Check if you used the Session Pooler (port 6543) or Transaction Pooler (port 5432).")
            print("3. Verify that your password does not contain unescaped special characters (e.g. #, %, @).")
            print("4. Verify ?sslmode=require is appended to the connection string.")
        return False

def verify_tables():
    print("\n" + "=" * 60)
    print("STATSAKSHAM — Database Table Verification")
    print("=" * 60)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("[!] No tables found in database. Please run with --seed to initialize schema.")
        return False

    print(f"Found {len(tables)} tables:\n")
    print(f"{'Table Name':<30} {'Row Count':<15}")
    print("-" * 45)
    
    with engine.connect() as conn:
        for t in sorted(tables):
            try:
                cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
                print(f"{t:<30} {cnt:<15}")
            except Exception as e:
                print(f"{t:<30} Error: {e}")
    print("-" * 45)
    return True

def main():
    parser = argparse.ArgumentParser(description="StatSaksham Supabase Migration Tool")
    parser.add_argument("--test-only", action="store_true", help="Test database connection only")
    parser.add_argument("--seed", action="store_true", help="Create tables and seed complete dataset")
    parser.add_argument("--verify", action="store_true", help="Verify tables and row counts")
    
    args = parser.parse_args()

    if args.test_only:
        check_connection()
        return

    if args.verify:
        if check_connection():
            verify_tables()
        return

    # Default action: Test, Seed & Verify
    print("Connecting and initializing StatSaksham database schema on Supabase...")
    if check_connection():
        print("\nStarting full migration & seeding...")
        seed_database()
        verify_tables()
        print("\n[SUCCESS] StatSaksham is fully initialized and operational on Supabase PostgreSQL!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
