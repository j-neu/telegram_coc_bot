"""PostgreSQL database manager for tracking CoC agreements."""
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Dict

import psycopg2
import psycopg2.extras

from config import COC_VERSION, DATABASE_URL

logger = logging.getLogger(__name__)


class DatabaseManager:

    def __init__(self):
        self._init_database()
        logger.info("Database initialized successfully")

    @contextmanager
    def _conn(self):
        conn = psycopg2.connect(DATABASE_URL)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS agreements (
                        user_id     BIGINT NOT NULL,
                        username    TEXT,
                        full_name   TEXT,
                        group_id    BIGINT NOT NULL,
                        group_name  TEXT,
                        agreed_at   TIMESTAMPTZ NOT NULL,
                        coc_version TEXT NOT NULL,
                        PRIMARY KEY (user_id, group_id, coc_version)
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_agreements_user_group
                    ON agreements (user_id, group_id)
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key   TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)

    def get_setting(self, key: str, default: str = '') -> str:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT value FROM settings WHERE key = %s", (key,))
                    row = cur.fetchone()
                    return row[0] if row else default
        except Exception as e:
            logger.error(f"get_setting failed: {e}")
            return default

    def set_setting(self, key: str, value: str) -> bool:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO settings (key, value) VALUES (%s, %s)
                        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """, (key, value))
            return True
        except Exception as e:
            logger.error(f"set_setting failed: {e}")
            return False

    def record_agreement(
        self,
        user_id: int,
        username: str,
        full_name: str,
        group_id: int,
        group_name: str,
        version: str = COC_VERSION
    ) -> bool:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO agreements
                            (user_id, username, full_name, group_id, group_name, agreed_at, coc_version)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id, group_id, coc_version) DO UPDATE SET
                            username   = EXCLUDED.username,
                            full_name  = EXCLUDED.full_name,
                            group_name = EXCLUDED.group_name,
                            agreed_at  = EXCLUDED.agreed_at
                    """, (user_id, username or '', full_name or '', group_id,
                          group_name or '', datetime.now(timezone.utc), version))
            logger.info(f"Recorded agreement: user={user_id} group={group_id} version={version}")
            return True
        except Exception as e:
            logger.error(f"record_agreement failed: {e}")
            return False

    def has_agreed(self, user_id: int, group_id: int, version: str = COC_VERSION) -> bool:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 1 FROM agreements
                        WHERE user_id = %s AND group_id = %s AND coc_version = %s
                    """, (user_id, group_id, version))
                    return cur.fetchone() is not None
        except Exception as e:
            logger.error(f"has_agreed failed: {e}")
            return False

    def has_agreed_anywhere(self, user_id: int, version: str = COC_VERSION) -> bool:
        """Return True if user has agreed in any group under the given version."""
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 1 FROM agreements
                        WHERE user_id = %s AND coc_version = %s
                        LIMIT 1
                    """, (user_id, version))
                    return cur.fetchone() is not None
        except Exception as e:
            logger.error(f"has_agreed_anywhere failed: {e}")
            return False

    def get_all_agreed(self, group_id: int, version: str = COC_VERSION) -> List[Dict]:
        try:
            with self._conn() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT user_id, username, full_name, group_id, group_name, agreed_at, coc_version
                        FROM agreements
                        WHERE group_id = %s AND coc_version = %s
                        ORDER BY agreed_at DESC
                    """, (group_id, version))
                    return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"get_all_agreed failed: {e}")
            return []
