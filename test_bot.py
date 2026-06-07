import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import os

# Set dummy bot token for testing
os.environ['BOT_TOKEN'] = '12345:ABC-DEF'
os.environ['ADMIN_IDS'] = '1'

import bot
from database_manager import DatabaseManager

class TestBot(unittest.TestCase):

    def setUp(self):
        """Set up a clean database for each test."""
        self.db_path = 'test_agreements.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.storage_manager = DatabaseManager(db_path=self.db_path)
        bot.storage_manager = self.storage_manager

    def tearDown(self):
        """Clean up the database file after each test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def async_test(self, coro):
        """Helper to run async functions in tests."""
        return asyncio.run(coro)

    @patch('bot.ContextTypes.DEFAULT_TYPE')
    @patch('bot.Update')
    def test_gatekeeper_and_agreement_flow(self, mock_update, mock_context):
        """Test the full workflow: gatekeeper restricts, user agrees via pinned message, user is unrestricted."""
        
        # --- 1. An unagreed user sends a message ---
        user_id = 100
        group_id = -1001
        
        mock_bot = AsyncMock()
        mock_context.bot = mock_bot

        user_mock = MagicMock(id=user_id, is_bot=False, username='testuser', full_name='Test User')
        chat_mock = MagicMock(id=group_id, type='group', title="Test Group")
        message_mock = AsyncMock()
        
        mock_update.effective_user = user_mock
        mock_update.effective_chat = chat_mock
        mock_update.effective_message = message_mock

        # --- 2. The gatekeeper should fire ---
        self.async_test(bot.gatekeeper_handler(mock_update, mock_context))

        # Assert that the gatekeeper deleted the message and restricted the user
        message_mock.delete.assert_called_once()
        mock_bot.restrict_chat_member.assert_called_once_with(
            chat_id=group_id,
            user_id=user_id,
            permissions=unittest.mock.ANY
        )
        self.assertFalse(mock_bot.restrict_chat_member.call_args.kwargs['permissions'].can_send_messages)
        mock_bot.send_message.assert_called_once() # The DM attempt

        # --- 3. The user now clicks the "Agree" button on the pinned message ---
        mock_bot.restrict_chat_member.reset_mock() # Reset for the un-restriction call
        mock_bot.get_chat.return_value = MagicMock(title="Test Group") # Mock for handle_agreement

        query_mock = AsyncMock(data=f"agree_{group_id}", from_user=user_mock)
        mock_update.callback_query = query_mock
        
        self.async_test(bot.handle_agreement(mock_update, mock_context))

        # --- 4. Final Assertions ---
        # Assert the user's agreement is now recorded
        self.assertTrue(self.storage_manager.has_agreed(user_id, group_id, bot.COC_VERSION))
        
        # Assert the user was unrestricted
        mock_bot.restrict_chat_member.assert_called_once()
        args, kwargs = mock_bot.restrict_chat_member.call_args
        self.assertTrue(kwargs['permissions'].can_send_messages)

if __name__ == '__main__':
    unittest.main()