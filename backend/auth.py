"""Authentication helpers for Campus Customs.

Password storage: PBKDF2-HMAC-SHA256 with a random 16-byte per-user salt and
600,000 iterations (OWASP's 2024 floor for PBKDF2-SHA256). We store only the
derived hash in the form:

    pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>

The plaintext password is never stored, logged, or returned. Verification uses a
constant-time compare so timing can't leak how much of a hash matched. Even with
full read access to the users table, an attacker (human or AI) only sees salted,
stretched hashes — not the passwords.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
import time
from pathlib import Path

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000
SALT_BYTES = 16

BACKEND_DIR = Path(__file__).resolve().parent
# Signing key for session cookies. Kept out of git; regenerated if missing,
# which just invalidates existing sessions (users log in again).
_SECRET_FILE = BACKEND_DIR / ".session_secret"
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60  # one week


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Constant-time check of a password against a stored hash.

    Only the 4-part format we write is verifiable; legacy seed rows in a
    different format simply fail to verify.
    """
    try:
        algorithm, iterations_s, salt_hex, hash_hex = stored.split("$")
        if algorithm != ALGORITHM:
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except ValueError:
        return False
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations_s))
    return hmac.compare_digest(derived, expected)


# ---- Session tokens (signed, stateless) ----


def _secret() -> bytes:
    if not _SECRET_FILE.exists():
        _SECRET_FILE.write_text(secrets.token_hex(32))
        _SECRET_FILE.chmod(0o600)
    return _SECRET_FILE.read_text().strip().encode("utf-8")


def issue_session(user_id: int) -> str:
    """Return a tamper-proof token: <user_id>.<expiry>.<hmac>."""
    expiry = int(time.time()) + SESSION_TTL_SECONDS
    payload = f"{user_id}.{expiry}"
    signature = hmac.new(_secret(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def read_session(token: str | None) -> int | None:
    """Return the user id if the token is valid and unexpired, else None."""
    if not token:
        return None
    try:
        user_id_s, expiry_s, signature = token.rsplit(".", 2)
    except ValueError:
        return None
    payload = f"{user_id_s}.{expiry_s}"
    expected = hmac.new(_secret(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    if int(expiry_s) < time.time():
        return None
    return int(user_id_s)


def connect_rw(db_path: Path) -> sqlite3.Connection:
    """Writable connection for the users table. Foreign keys on."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
