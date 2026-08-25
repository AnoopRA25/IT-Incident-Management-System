import sqlite3
from datetime import datetime


DB_NAME = "incidents.db"


def get_connection():
    """
    Create and return a database connection.
    """
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def create_table():
    """
    Create the incidents table if it does not already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            impact TEXT,
            urgency TEXT,
            priority TEXT,
            status TEXT,
            assigned_team TEXT,
            created_at TEXT,
            sla_deadline TEXT,
            root_cause TEXT,
            resolution TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_incident(
    title,
    description,
    category,
    impact,
    urgency,
    priority,
    assigned_team,
    sla_deadline
):
    """
    Create and save a new incident.
    """

    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO incidents (
            incident_id,
            title,
            description,
            category,
            impact,
            urgency,
            priority,
            status,
            assigned_team,
            created_at,
            sla_deadline,
            root_cause,
            resolution
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "TEMP",
        title,
        description,
        category,
        impact,
        urgency,
        priority,
        "Open",
        assigned_team,
        created_at,
        sla_deadline.isoformat(),
        "",
        ""
    ))

    db_id = cursor.lastrowid

    incident_id = f"INC{db_id:04d}"

    cursor.execute("""
        UPDATE incidents
        SET incident_id = ?
        WHERE id = ?
    """, (incident_id, db_id))

    conn.commit()
    conn.close()

    return incident_id


def get_all_incidents():
    """
    Return all incidents.
    """

    conn = get_connection()

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM incidents
        ORDER BY id DESC
    """)

    incidents = cursor.fetchall()

    conn.close()

    return [dict(incident) for incident in incidents]


def get_incident_by_id(incident_id):
    """
    Return one incident using its incident ID.
    """

    conn = get_connection()

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM incidents
        WHERE incident_id = ?
    """, (incident_id,))

    incident = cursor.fetchone()

    conn.close()

    if incident:
        return dict(incident)

    return None


def update_incident(
    incident_id,
    status,
    root_cause,
    resolution
):
    """
    Update incident status, root cause and resolution.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE incidents
        SET
            status = ?,
            root_cause = ?,
            resolution = ?
        WHERE incident_id = ?
    """, (
        status,
        root_cause,
        resolution,
        incident_id
    ))

    conn.commit()
    conn.close()