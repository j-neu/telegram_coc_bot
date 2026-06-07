"""SQLite database manager for tracking CoC agreements."""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging
from contextlib import contextmanager

from config import COC_VERSION

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for CoC agreements."""

    def __init__(self, db_path: str = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        # Use DATABASE_PATH env var if available (for Railway persistent storage)
        # Otherwise use local file
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'coc_agreements.db')

        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.db_path = db_path
        logger.info(f"Using database at: {self.db_path}")
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create agreements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agreements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    full_name TEXT,
                    group_id INTEGER NOT NULL,
                    group_name TEXT,
                    agreed_at TEXT NOT NULL,
                    coc_version TEXT NOT NULL,
                    UNIQUE(user_id, group_id, coc_version)
                )
            ''')

            # Create index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_group
                ON agreements(user_id, group_id)
            ''')

            logger.info("Database initialized successfully")

    def record_agreement(
        self,
        user_id: int,
        username: str,
        full_name: str,
        group_id: int,
        group_name: str,
        version: str = COC_VERSION
    ) -> bool:
        """
        Record a user's agreement to the CoC.
        """
        try:
            agreed_at = datetime.utcnow().isoformat()

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO agreements
                    (user_id, username, full_name, group_id, group_name, agreed_at, coc_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, username or '', full_name or '', group_id,
                      group_name or '', agreed_at, version))

            logger.info(f"Recorded agreement for user {user_id} in group {group_id} with version {version}")
            return True
        except Exception as e:
            logger.error(f"Failed to record agreement: {e}")
            return False

    def has_agreed(
        self,
        user_id: int,
        group_id: int,
        version: str = COC_VERSION
    ) -> bool:
        """
        Check if a user has agreed to the CoC for a specific group and version.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 1 FROM agreements
                    WHERE user_id = ? AND group_id = ? AND coc_version = ?
                ''', (user_id, group_id, version))

                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Failed to check agreement status: {e}")
            return False

    def get_all_agreed(
        self,
        group_id: int,
        version: str = COC_VERSION
    ) -> List[Dict]:
        """
        Get all users who have agreed to the CoC in a specific group.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, full_name, group_id,
                           group_name, agreed_at, coc_version
                    FROM agreements
                    WHERE group_id = ? AND coc_version = ?
                    ORDER BY agreed_at DESC
                ''', (group_id, version))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get agreed users: {e}")
            return []

    def get_unagreed_members(self, group_id: int, version: str = COC_VERSION) -> List[int]:
        """
        Get all user IDs in a group that have NOT agreed to the specified version.
        This includes users who have agreed to a previous version and newly discovered users.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Get IDs of everyone who HAS agreed to the current version
                cursor.execute('''
                    SELECT user_id FROM agreements WHERE group_id = ? AND coc_version = ?
                ''', (group_id, version))
                agreed_user_ids = {row['user_id'] for row in cursor.fetchall()}

                # Get IDs of ALL users known in that group
                cursor.execute('''
                    SELECT DISTINCT user_id FROM agreements WHERE group_id = ?
                ''', (group_id,))
                all_known_user_ids = {row['user_id'] for row in cursor.fetchall()}

                # Return the difference
                return list(all_known_user_ids - agreed_user_ids)
        except Exception as e:
            logger.error(f"Failed to get unagreed members: {e}")
            return []

    def export_data(self, group_id: Optional[int] = None) -> List[Dict]:
        """
        Export all data from the database.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if group_id:
                    cursor.execute('''
                        SELECT * FROM agreements WHERE group_id = ?
                        ORDER BY agreed_at DESC
                    ''', (group_id,))
                else:
                    cursor.execute('''
                        SELECT * FROM agreements ORDER BY agreed_at DESC
                    ''')

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return []
    
    def discover_user(self, user_id: int, username: str, full_name: str, group_id: int, group_name: str) -> None:
        """
        Ensures a user exists in the database for a given group.
        If they don't, a placeholder 'discovered' record is created.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Use a more specific check to see if this user/group combo is known at all
                cursor.execute(
                    "SELECT 1 FROM agreements WHERE user_id = ? AND group_id = ?",
                    (user_id, group_id)
                )
                if cursor.fetchone() is None:
                    # User is not known in this group, add a 'discovered' record
                    agreed_at = datetime.utcnow().isoformat()
                    # Use INSERT OR IGNORE to be safe against race conditions, though less likely in this flow
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO agreements (user_id, username, full_name, group_id, group_name, agreed_at, coc_version)
                        VALUES (?, ?, ?, ?, ?, ?, 'discovered')
                        """,
                        (user_id, username, full_name, group_id, group_name, agreed_at)
                    )
                    logger.info(f"Discovered and recorded new user {user_id} in group {group_id}")
        except Exception as e:
            logger.error(f"Failed to discover/record user {user_id}: {e}")


    def get_stats(self, group_id: int) -> Dict:
        """
        Get statistics for a group.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Total agreements
                cursor.execute('''
                    SELECT COUNT(*) as total FROM agreements WHERE group_id = ?
                ''', (group_id,))
                total = cursor.fetchone()['total']

                # Agreements by version
                cursor.execute('''
                    SELECT coc_version, COUNT(*) as count
                    FROM agreements
                    WHERE group_id = ?
                    GROUP BY coc_version
                ''', (group_id,))
                by_version = {row['coc_version']: row['count'] for row in cursor.fetchall()}

                return {
                    'total_agreements': total,
                    'by_version': by_version
                }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'total_agreements': 0, 'by_version': {}}
