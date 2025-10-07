#!/usr/bin/env python3
"""Wait for the Postgres database to become available.

This script repeatedly attempts to connect using psycopg and exits when successful.
It reads DB connection settings from environment variables.
"""
import os
import time
import sys

try:
    import psycopg
except Exception:
    print("psycopg not installed; exiting")
    sys.exit(1)

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "db.postgres")
DB_USER = os.environ.get("DB_USER", "user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "mypassword")
TIMEOUT = int(os.environ.get("DB_WAIT_TIMEOUT", "60"))

start = time.time()
while True:
    try:
        conn = psycopg.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        conn.close()
        print("Database is available")
        break
    except Exception as exc:
        elapsed = time.time() - start
        if elapsed > TIMEOUT:
            print(f"Timed out after {TIMEOUT}s waiting for database: {exc}")
            raise
        print(f"Waiting for database ({int(elapsed)}s elapsed): {exc}")
        time.sleep(1)
