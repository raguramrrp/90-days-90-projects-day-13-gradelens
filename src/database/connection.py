"""
GradeLens Database Connection & Session Management Layer
Supports PostgreSQL production target with zero-setup SQLite fallback and full diagnostics.
"""

import os
import sqlite3
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_SQLITE_PATH = BASE_DIR / "data" / "gradelens.db"


def get_db_config() -> Dict[str, Any]:
    """Retrieves current database configuration from environment."""
    return {
        "engine_type": os.getenv("DATABASE_TYPE", "sqlite").lower(),
        "pg_host": os.getenv("PGHOST", "localhost"),
        "pg_port": int(os.getenv("PGPORT", "5432")),
        "pg_database": os.getenv("PGDATABASE", "gradelens_db"),
        "pg_user": os.getenv("PGUSER", "postgres"),
        "pg_password": os.getenv("PGPASSWORD", ""),
        "sqlite_path": os.getenv("SQLITE_DB_PATH", str(DEFAULT_SQLITE_PATH)),
    }


def get_postgres_uri() -> str:
    """Builds PostgreSQL SQLAlchemy / psycopg2 connection URI."""
    cfg = get_db_config()
    user = cfg["pg_user"]
    password = cfg["pg_password"]
    host = cfg["pg_host"]
    port = cfg["pg_port"]
    dbname = cfg["pg_database"]
    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    return f"postgresql://{user}@{host}:{port}/{dbname}"


def check_postgres_availability() -> Dict[str, Any]:
    """
    Checks if PostgreSQL server is reachable.
    Does not crash; returns actionable diagnostics.
    """
    cfg = get_db_config()
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=cfg["pg_host"],
            port=cfg["pg_port"],
            dbname=cfg["pg_database"],
            user=cfg["pg_user"],
            password=cfg["pg_password"],
            connect_timeout=3
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {
            "available": True,
            "version": version,
            "error": None,
            "host": cfg["pg_host"],
            "port": cfg["pg_port"],
            "database": cfg["pg_database"]
        }
    except Exception as exc:
        return {
            "available": False,
            "version": None,
            "error": str(exc),
            "host": cfg["pg_host"],
            "port": cfg["pg_port"],
            "database": cfg["pg_database"]
        }


class DatabaseManager:
    """Unified Database connection manager supporting SQLite and PostgreSQL."""

    def __init__(self, override_type: Optional[str] = None, sqlite_path: Optional[str] = None):
        cfg = get_db_config()
        self.engine_type = override_type or cfg["engine_type"]
        self.sqlite_path = Path(sqlite_path or cfg["sqlite_path"])
        if not self.sqlite_path.is_absolute():
            self.sqlite_path = BASE_DIR / self.sqlite_path

    def get_connection(self):
        """Returns an active raw DB-API connection."""
        if self.engine_type == "postgresql":
            import psycopg2
            cfg = get_db_config()
            return psycopg2.connect(
                host=cfg["pg_host"],
                port=cfg["pg_port"],
                dbname=cfg["pg_database"],
                user=cfg["pg_user"],
                password=cfg["pg_password"]
            )
        else:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.sqlite_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn

    def get_sqlalchemy_engine(self):
        """Returns a SQLAlchemy engine."""
        from sqlalchemy import create_engine
        if self.engine_type == "postgresql":
            return create_engine(get_postgres_uri(), pool_pre_ping=True)
        else:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            return create_engine(f"sqlite:///{self.sqlite_path}")

    def execute_script(self, sql_script: str):
        """Executes a multi-statement SQL script."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if self.engine_type == "postgresql":
                cursor.execute(sql_script)
            else:
                conn.executescript(sql_script)
            conn.commit()
        finally:
            conn.close()

    def get_status(self) -> Dict[str, Any]:
        """Provides runtime connection status and diagnostics."""
        if self.engine_type == "postgresql":
            pg_status = check_postgres_availability()
            return {
                "active_engine": "postgresql",
                "connected": pg_status["available"],
                "version": pg_status["version"],
                "details": f"PostgreSQL at {pg_status['host']}:{pg_status['port']}/{pg_status['database']}",
                "error": pg_status["error"],
                "fallback_available": True
            }
        else:
            exists = self.sqlite_path.exists()
            size_kb = round(self.sqlite_path.stat().st_size / 1024, 2) if exists else 0
            return {
                "active_engine": "sqlite",
                "connected": True,
                "version": f"SQLite {sqlite3.sqlite_version}",
                "details": f"Database file: {self.sqlite_path} ({size_kb} KB)",
                "error": None,
                "fallback_available": False
            }


# Default singleton manager instance
db_manager = DatabaseManager()
