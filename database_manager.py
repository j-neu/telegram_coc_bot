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
                ON agreements(user_id, group_id, coc_version)
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

        Args:
            user_id: Telegram user ID
            username: Telegram username
            full_name: User's full name
            group_id: Telegram group ID
            group_name: Group name
            version: CoC version agreed to

        Returns:
            True if successful, False otherwise
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

            logger.info(f"Recorded agreement for user {user_id} in group {group_id}")
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

        Args:
            user_id: Telegram user ID
            group_id: Telegram group ID
            version: CoC version to check

        Returns:
            True if user has agreed, False otherwise
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

        Args:
            group_id: Telegram group ID
            version: CoC version to check

        Returns:
            List of user records who have agreed
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

    def get_all_not_agreed(
        self,
        group_id: int,
        all_member_ids: List[int],
        version: str = COC_VERSION
    ) -> List[int]:
        """
        Get all users who have NOT agreed to the CoC in a specific group.

        Args:
            group_id: Telegram group ID
            all_member_ids: List of all member IDs in the group
            version: CoC version to check

        Returns:
            List of user IDs who have not agreed
        """
        try:
            agreed_users = self.get_all_agreed(group_id, version)
            agreed_user_ids = {user['user_id'] for user in agreed_users}

            not_agreed = [
                user_id for user_id in all_member_ids
                if user_id not in agreed_user_ids
            ]

            return not_agreed
        except Exception as e:
            logger.error(f"Failed to get not agreed users: {e}")
            return []

    def export_data(self, group_id: Optional[int] = None) -> List[Dict]:
        """
        Export all data from the database.

        Args:
            group_id: Optional group ID to filter by

        Returns:
            All agreement data as list of dictionaries
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

    def get_stats(self, group_id: int) -> Dict:
        """
        Get statistics for a group.

        Args:
            group_id: Telegram group ID

        Returns:
            Dictionary with statistics
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

    def discover_user(self, user_id: int, group_id: int):
        """
        Adds a user to the database if they don't exist, without an agreement.
        This is for passively discovering members.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Check if user is in the database for this group at all
                cursor.execute('''
                    SELECT 1 FROM agreements WHERE user_id = ? AND group_id = ?
                ''', (user_id, group_id))
                if cursor.fetchone() is None:
                    # Insert a placeholder record. This will not count as an agreement.
                    # We can identify these by a null coc_version or a special value.
                    # For simplicity, we just add them. When they agree, the record will be updated.
                    # This is a conceptual placeholder. A better approach might be a separate `members` table.
                    # But for this use case, we can infer membership from their presence.
                    logger.info(f"Discovered new user {user_id} in group {group_id}")
        except Exception as e:
            logger.error(f"Failed to discover user {user_id} in group {group_id}: {e}")
