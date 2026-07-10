"""
controllers/admin_controller.py
Beaply - Controller: Admin Panel

CRUD operations for admin to manage users, beasiswa, and feedback.
"""

import json
import os
from datetime import datetime

from models.database import get_connection
from models.beasiswa_model import ambil_semua_beasiswa, ambil_beasiswa_by_id
from models.feedback_model import FEEDBACK_FILE


# ════════════════════════════════════════════════════════════
# ADMIN EMAIL CHECK
# ════════════════════════════════════════════════════════════

# Hardcoded admin emails — nanti bisa diganti dengan tabel di DB
ADMIN_EMAILS = [
    "admin@beaply.com",
    "admin@gmail.com",
    "elang@gmail.com",
]


def is_admin(email: str) -> bool:
    """Check if email is a registered admin."""
    if not email:
        return False
    return email.strip().lower() in [e.lower() for e in ADMIN_EMAILS]


# ════════════════════════════════════════════════════════════
# USERS MANAGEMENT
# ════════════════════════════════════════════════════════════

def get_all_users() -> list[dict]:
    """Get all non-admin users with their profile info."""
    conn = get_connection()
    cur = conn.cursor()

    # Build placeholders for admin emails to exclude
    admin_lower = [e.strip().lower() for e in ADMIN_EMAILS]
    placeholders = ", ".join("?" for _ in admin_lower)

    cur.execute(f"""
        SELECT u.id, u.email, u.nama_lengkap, u.status, u.created_at,
               u.auth_provider, u.last_login_at,
               p.id as profil_id, p.nama as profil_nama, p.email as profil_email
        FROM users u
        LEFT JOIN profil p ON u.id = p.user_id
        WHERE LOWER(u.email) NOT IN ({placeholders})
        ORDER BY u.created_at DESC
    """, admin_lower)
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        # Use profil name if available, fallback to users.nama_lengkap
        if d.get("profil_nama"):
            d["nama_lengkap"] = d["profil_nama"]
        if d.get("profil_email"):
            d["email"] = d["profil_email"]
        results.append(d)
    return results


def delete_user(user_id: str) -> tuple[bool, str]:
    """Delete a user and all their data."""
    try:
        conn = get_connection()
        # Delete profiles first
        conn.execute("DELETE FROM profil WHERE user_id = ?", (user_id,))
        # Delete user
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True, "User deleted successfully."
    except Exception as e:
        return False, str(e)


def update_user(user_id: str, nama_lengkap: str, email: str) -> tuple[bool, str]:
    """Update user and profile data."""
    try:
        conn = get_connection()
        # Update users table
        conn.execute("UPDATE users SET nama_lengkap = ?, email = ? WHERE id = ?", (nama_lengkap, email, user_id))
        # Update profil table
        conn.execute("UPDATE profil SET nama = ?, email = ? WHERE user_id = ?", (nama_lengkap, email, user_id))
        conn.commit()
        conn.close()
        return True, "User updated successfully."
    except Exception as e:
        return False, str(e)


def get_user_count() -> int:
    """Get total user count."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0


# ════════════════════════════════════════════════════════════
# BEASISWA MANAGEMENT
# ════════════════════════════════════════════════════════════

def get_all_beasiswa_admin() -> list[dict]:
    """Get all scholarships for admin management."""
    return ambil_semua_beasiswa()


def delete_beasiswa(beasiswa_id: int) -> tuple[bool, str]:
    """Delete a scholarship and related bookmarks."""
    try:
        conn = get_connection()
        # Hapus bookmark terkait terlebih dahulu
        conn.execute("DELETE FROM bookmark_beasiswa WHERE beasiswa_id = ?", (beasiswa_id,))
        conn.execute("DELETE FROM beasiswa WHERE id = ?", (beasiswa_id,))
        conn.commit()
        conn.close()
        # Refresh cache rekomendasi agar data tetap sinkron
        try:
            from models.rekomendasi_model import refresh_cache
            refresh_cache()
        except Exception:
            pass
        return True, "Scholarship deleted successfully."
    except Exception as e:
        return False, str(e)


def get_beasiswa_count() -> int:
    """Get total scholarship count."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM beasiswa")
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0


# ════════════════════════════════════════════════════════════
# FEEDBACK MANAGEMENT
# ════════════════════════════════════════════════════════════

def get_all_feedback() -> list[dict]:
    """Get all feedback from JSON file."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        # Add index for identification
        for i, item in enumerate(data):
            item["_index"] = i
        return data
    except Exception:
        return []


def delete_feedback(index: int) -> tuple[bool, str]:
    """Delete a feedback entry by index."""
    try:
        if not os.path.exists(FEEDBACK_FILE):
            return False, "No feedback file found."
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list) or index < 0 or index >= len(data):
            return False, "Invalid feedback index."
        data.pop(index)
        with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True, "Feedback deleted."
    except Exception as e:
        return False, str(e)


def reply_to_feedback(index: int, reply_text: str) -> tuple[bool, str]:
    """Save admin reply to a feedback entry."""
    try:
        if not os.path.exists(FEEDBACK_FILE):
            return False, "No feedback file found."
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list) or index < 0 or index >= len(data):
            return False, "Invalid feedback index."
        data[index]["admin_reply"] = reply_text
        data[index]["replied_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True, "Reply saved successfully."
    except Exception as e:
        return False, str(e)


def get_feedback_count() -> int:
    """Get total feedback count."""
    return len(get_all_feedback())
