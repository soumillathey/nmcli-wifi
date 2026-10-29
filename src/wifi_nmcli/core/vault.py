"""vault.py — Persistent SQLite storage for known Wi-Fi networks."""
from __future__ import annotations

import sqlite3
from typing import Any

from wifi_nmcli.core.constants import VAULT_DB_PATH


def _get_connection() -> sqlite3.Connection:
    VAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(VAULT_DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS wifi_networks ("
        "ssid TEXT PRIMARY KEY, password TEXT NOT NULL, saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    return conn


def save_network(ssid: str, password: str) -> None:
    """Store or update Wi-Fi credentials."""
    with _get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO wifi_networks (ssid, password) VALUES (?, ?)",
            (ssid.strip(), password),
        )


def get_password(ssid: str) -> str | None:
    """Retrieve password for given SSID."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT password FROM wifi_networks WHERE ssid = ?", (ssid.strip(),)
        ).fetchone()
        return str(row[0]) if row else None


def list_saved_networks() -> list[dict[str, Any]]:
    """List all saved network SSIDs."""
    with _get_connection() as conn:
        cur = conn.execute("SELECT ssid, saved_at FROM wifi_networks ORDER BY saved_at DESC")
        return [{"ssid": r[0], "saved_at": r[1]} for r in cur.fetchall()]


def delete_network(ssid: str) -> bool:
    """Delete a saved network profile."""
    with _get_connection() as conn:
        cur = conn.execute("DELETE FROM wifi_networks WHERE ssid = ?", (ssid.strip(),))
        return cur.rowcount > 0
