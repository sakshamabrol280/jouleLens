"""
JouleLens — Database module.
SQLite-based storage for profiling runs and CRUD operations.
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "joulelens.db")


def get_connection():
    """Get a database connection with row_factory set for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the profiling_runs table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiling_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            code_snippet TEXT NOT NULL,
            language TEXT DEFAULT 'Python',
            workload_type TEXT,
            total_joules REAL,
            total_wh REAL,
            cost_usd REAL,
            co2_grams REAL,
            joule_score TEXT,
            region TEXT,
            carbon_intensity REAL,
            function_breakdown TEXT,
            ai_refactor_available INTEGER DEFAULT 0,
            ai_summary TEXT,
            ai_refactored_code TEXT,
            ai_energy_reduction_percent INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    try:
        cursor.execute("ALTER TABLE profiling_runs ADD COLUMN language TEXT DEFAULT 'Python'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def insert_run(run_dict):
    """Insert a profiling run record. Returns the new row ID."""
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure function_breakdown is JSON-encoded
    fb = run_dict.get("function_breakdown", [])
    if isinstance(fb, (list, dict)):
        fb = json.dumps(fb)

    cursor.execute("""
        INSERT INTO profiling_runs 
        (timestamp, code_snippet, language, workload_type, total_joules, total_wh,
         cost_usd, co2_grams, joule_score, region, carbon_intensity,
         function_breakdown, ai_refactor_available, ai_summary,
         ai_refactored_code, ai_energy_reduction_percent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_dict.get("timestamp", ""),
        run_dict.get("code_snippet", ""),
        run_dict.get("language", "Python"),
        run_dict.get("workload_type", "CPU-Bound"),
        run_dict.get("total_joules", 0.0),
        run_dict.get("total_wh", 0.0),
        run_dict.get("cost_usd", 0.0),
        run_dict.get("co2_grams", 0.0),
        run_dict.get("joule_score", "C"),
        run_dict.get("region", "US-CAL"),
        run_dict.get("carbon_intensity", 300.0),
        fb,
        run_dict.get("ai_refactor_available", 0),
        run_dict.get("ai_summary", None),
        run_dict.get("ai_refactored_code", None),
        run_dict.get("ai_energy_reduction_percent", None),
    ))
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id


def get_all_runs():
    """Return all runs as a list of dicts, ordered by created_at DESC."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiling_runs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_run_by_id(run_id):
    """Return a single run dict by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiling_runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_run_with_refactor(run_id, ai_summary, ai_refactored_code, ai_energy_reduction_percent):
    """Update an existing run with AI refactor data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE profiling_runs 
        SET ai_refactor_available = 1,
            ai_summary = ?,
            ai_refactored_code = ?,
            ai_energy_reduction_percent = ?
        WHERE id = ?
    """, (ai_summary, ai_refactored_code, ai_energy_reduction_percent, run_id))
    conn.commit()
    conn.close()


def clear_all_runs():
    """Delete all records from the profiling_runs table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profiling_runs")
    conn.commit()
    conn.close()


def get_aggregate_stats():
    """Return aggregate stats dict: total_runs, total_joules, total_co2, total_cost."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as total_runs,
            COALESCE(SUM(total_joules), 0) as total_joules,
            COALESCE(SUM(co2_grams), 0) as total_co2,
            COALESCE(SUM(cost_usd), 0) as total_cost
        FROM profiling_runs
    """)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {
        "total_runs": 0, "total_joules": 0, "total_co2": 0, "total_cost": 0
    }
