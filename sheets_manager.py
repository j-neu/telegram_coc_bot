"""Google Sheets integration for tracking CoC agreements."""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import List, Dict, Optional
import logging

from config import SHEET_ID, COC_VERSION
from get_credentials import get_google_credentials_path

logger = logging.getLogger(__name__)


class SheetsManager:
    """Manages Google Sheets operations for CoC agreements."""

    def __init__(self):
        """Initialize connection to Google Sheets."""
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = None
        self.sheet = None
        self.worksheet = None
        self._connect()

    def _connect(self):
        """Establish connection to Google Sheets."""
        try:
            credentials_path = get_google_credentials_path()
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                credentials_path, self.scope
            )
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(SHEET_ID)

            # Get or create the Agreements worksheet
            try:
                self.worksheet = self.sheet.worksheet('Agreements')
            except gspread.exceptions.WorksheetNotFound:
                self.worksheet = self.sheet.add_worksheet(
                    title='Agreements',
                    rows=1000,
                    cols=7
                )
                # Add headers
                self.worksheet.append_row([
                    'user_id', 'username', 'full_name', 'group_id',
                    'group_name', 'agreed_at', 'coc_version'
                ])

            logger.info("Successfully connected to Google Sheets")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise

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
            row = [
                user_id,
                username or '',
                full_name or '',
                group_id,
                group_name or '',
                agreed_at,
                version
            ]
            self.worksheet.append_row(row)
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
            all_records = self.worksheet.get_all_records()
            for record in all_records:
                if (str(record.get('user_id')) == str(user_id) and
                    str(record.get('group_id')) == str(group_id) and
                    record.get('coc_version') == version):
                    return True
            return False
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
            all_records = self.worksheet.get_all_records()
            agreed_users = []
            seen_users = set()

            for record in all_records:
                user_id = str(record.get('user_id'))
                if (str(record.get('group_id')) == str(group_id) and
                    record.get('coc_version') == version and
                    user_id not in seen_users):
                    agreed_users.append(record)
                    seen_users.add(user_id)

            return agreed_users
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
            agreed_user_ids = {str(record.get('user_id')) for record in agreed_users}

            not_agreed = [
                user_id for user_id in all_member_ids
                if str(user_id) not in agreed_user_ids
            ]

            return not_agreed
        except Exception as e:
            logger.error(f"Failed to get not agreed users: {e}")
            return []

    def export_data(self) -> List[List]:
        """
        Export all data from the worksheet.

        Returns:
            All worksheet data as a list of lists
        """
        try:
            return self.worksheet.get_all_values()
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return []
