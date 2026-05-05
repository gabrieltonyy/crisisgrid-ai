#!/usr/bin/env python3
"""Reset and seed the local CrisisGrid PostgreSQL database.

This command is intentionally destructive and intended for local development.
It starts the project PostgreSQL container, waits for readiness, resets the
backend tables, and seeds the current hackathon demo users/reports.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_DIR / "backend"
BACKEND_PYTHON = BACKEND_DIR / ".venv" / "bin" / "python"

DEMO_ACCOUNTS = [
    ("Citizen", "citizen.demo01@demo.crisisgrid.ai", "/citizen"),
    ("Authority", "authority.demo01@demo.crisisgrid.ai", "/admin/dashboard"),
    ("Admin", "admin.demo01@demo.crisisgrid.ai", "/admin/dashboard"),
]


def run(command: list[str], *, cwd: Path, display: str | None = None) -> None:
    print(f"$ {display or ' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def backend_python() -> str:
    if BACKEND_PYTHON.exists():
        return str(BACKEND_PYTHON)

    python = shutil.which("python3") or shutil.which("python")
    if python:
        return python

    raise RuntimeError("No Python executable found. Create the backend .venv first.")


def wait_for_postgres(timeout_seconds: int = 60) -> None:
    deadline = time.monotonic() + timeout_seconds
    command = [
        "docker",
        "compose",
        "exec",
        "-T",
        "postgres",
        "pg_isready",
        "-U",
        "crisisgrid",
        "-d",
        "crisisgrid",
    ]

    while time.monotonic() < deadline:
        result = subprocess.run(
            command,
            cwd=PROJECT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0:
            print("PostgreSQL is accepting connections.")
            return
        time.sleep(2)

    raise TimeoutError("PostgreSQL did not become ready within 60 seconds.")


def reset_tables(python: str) -> None:
    code = (
        "from app.db.init_db import init_database; "
        "from app.db.session import engine; "
        "engine.echo = False; "
        "raise SystemExit(0 if init_database(reset=True) else 1)"
    )
    run([python, "-c", code], cwd=BACKEND_DIR, display="backend init_db reset")


def seed_demo_data(python: str) -> None:
    # Import the current canonical seed helpers instead of invoking
    # scripts/seed_data.py directly, because that script prints demo passwords.
    code = r"""
import random
from scripts.seed_data import (
    SessionLocal,
    create_reports,
    create_users,
    ensure_auth_columns,
    engine,
    reset_demo_reports,
)

random.seed(20260503)
engine.echo = False

if not ensure_auth_columns():
    raise SystemExit(1)

db = SessionLocal()
try:
    users = create_users(db)
    reset_demo_reports(db, users)
    reports = create_reports(db, users)
    print(f"Seed complete: {len(users)} users and {len(reports)} reports.")
finally:
    db.close()
"""
    run([python, "-c", code], cwd=BACKEND_DIR, display="backend seed demo users/reports")


def main() -> int:
    os.environ.setdefault("PYTHONUNBUFFERED", "1")

    print("WARNING: this will delete and recreate local CrisisGrid database tables.")
    run(["docker", "compose", "up", "-d", "postgres"], cwd=PROJECT_DIR)
    wait_for_postgres()

    python = backend_python()
    reset_tables(python)
    seed_demo_data(python)

    print("\nDemo accounts seeded:")
    for role, email, redirect in DEMO_ACCOUNTS:
        print(f"- {role}: {email} -> {redirect}")

    print("\nDone. No tokens, API keys, or environment values were printed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}.", file=sys.stderr)
        raise SystemExit(exc.returncode)
