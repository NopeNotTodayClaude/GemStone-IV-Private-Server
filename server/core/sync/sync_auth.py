"""
sync_auth.py
------------
Token generation and validation for the real-time sync channel.

Uses db._get_conn() directly - the same pattern as every other method
in server/core/database.py.  No db.execute() or db.fetchall() - those
don't exist on the Database class.
"""

import os
import logging
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

TOKEN_TTL_HOURS = 24


def _hex_token():
    return os.urandom(32).hex()


def generate_token(db, character_id):
    """Upsert a fresh sync token. Returns token string (always, even on DB error)."""
    token   = _hex_token()
    expires = (datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    conn = db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO sync_tokens (character_id, token, expires_at)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE
                   token = VALUES(token),
                   expires_at = VALUES(expires_at),
                   created_at = CURRENT_TIMESTAMP""",
            (character_id, token, expires)
        )
        conn.commit()
        log.debug("sync_auth: token generated for character_id=%d", character_id)
    except Exception as e:
        log.error("sync_auth: generate_token DB write failed for character_id=%d: %s", character_id, e)
        # Token is still returned - cache_token() covers auth even without DB write
    finally:
        conn.close()
    return token


def validate_token(db, token):
    """Returns character_id if valid and unexpired, else None."""
    if not token or len(token) != 64:
        return None
    try:
        int(token, 16)
    except ValueError:
        return None
    conn = db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT character_id, expires_at FROM sync_tokens WHERE token = %s LIMIT 1",
            (token,)
        )
        row = cur.fetchone()
        if not row:
            return None
        expires_at = row["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
        if expires_at < datetime.utcnow():
            revoke_by_token(db, token)
            return None
        return int(row["character_id"])
    except Exception as e:
        log.error("sync_auth: validate_token error: %s", e)
        return None
    finally:
        conn.close()


def revoke_token(db, character_id):
    conn = db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM sync_tokens WHERE character_id = %s", (character_id,))
        conn.commit()
    except Exception as e:
        log.warning("sync_auth: revoke_token failed: %s", e)
    finally:
        conn.close()


def revoke_by_token(db, token):
    conn = db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM sync_tokens WHERE token = %s", (token,))
        conn.commit()
    except Exception as e:
        log.warning("sync_auth: revoke_by_token failed: %s", e)
    finally:
        conn.close()


def cleanup_expired(db):
    conn = db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM sync_tokens WHERE expires_at < NOW()")
        conn.commit()
    except Exception as e:
        log.warning("sync_auth: cleanup_expired failed: %s", e)
    finally:
        conn.close()
