import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import os

# Set a dummy bot token for testing
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

    def test_01_record_agreement(self):
        """Test that an agreement is recorded correctly."""
        user_id = 100
        group_id = -1001
        coc_version = "1.0"

        success = self.storage_manager.record_agreement(
            user_id=user_id,
            username='testuser',
            full_name='Test User',
            group_id=group_id,
            group_name='Test Group',
            version=coc_version
        )
        self.assertTrue(success)

        has_agreed = self.storage_manager.has_agreed(user_id, group_id, coc_version)
        self.assertTrue(has_agreed)

    @patch('bot.ContextTypes.DEFAULT_TYPE')
    @patch('bot.Update')
    def test_02_new_member_restriction(self, mock_update, mock_context):
        """Test that a new member is restricted and gets a DM."""
        
        # --- Mocking Telegram Objects ---
        mock_context.bot = AsyncMock()
        
        user_mock = MagicMock()
        user_mock.id = 200
        user_mock.is_bot = False
        user_mock.username = 'test_new_user'
        user_mock.full_name = 'Test New User'
        user_mock.mention_html.return_value = "Test New User"

        chat_mock = MagicMock()
        chat_mock.id = -1002
        chat_mock.title = 'Test Group'

        # This simulates a user joining
        new_chat_member_mock = MagicMock()
        new_chat_member_mock.user = user_mock
        new_chat_member_mock.status = bot.ChatMemberStatus.MEMBER
        
        old_chat_member_mock = MagicMock()
        old_chat_member_mock.status = bot.ChatMemberStatus.LEFT

        chat_member_update_mock = MagicMock()
        chat_member_update_mock.new_chat_member = new_chat_member_mock
        chat_member_update_mock.old_chat_member = old_chat_member_mock

        mock_update.chat_member = chat_member_update_mock
        mock_update.effective_chat = chat_mock
        
        # --- Run the function ---
        self.async_test(bot.handle_new_member(mock_update, mock_context))

        # --- Assertions ---
        # 1. Check if the bot tried to restrict the member
        mock_context.bot.restrict_chat_member.assert_called_once()
        args, kwargs = mock_context.bot.restrict_chat_member.call_args
        self.assertEqual(kwargs['chat_id'], chat_mock.id)
        self.assertEqual(kwargs['user_id'], user_mock.id)
        self.assertFalse(kwargs['permissions'].can_send_messages)

        # 2. Check if the bot tried to send a DM
        mock_context.bot.send_message.assert_called_once()
        args, kwargs = mock_context.bot.send_message.call_args
        self.assertEqual(kwargs['chat_id'], user_mock.id)
        self.assertIn("Welcome", kwargs['text'])

    @patch('bot.ContextTypes.DEFAULT_TYPE')
    @patch('bot.Update')
    def test_03_agreement_unrestricts(self, mock_update, mock_context):
        """Test that agreeing unrestricts a member."""

        # --- Setup ---
        user_id = 300
        group_id = -1003
        
        # --- Mocking Telegram Objects ---
        mock_context.bot = AsyncMock()
        # Mock the get_chat call to return a mock chat object with a title
        mock_context.bot.get_chat.return_value = MagicMock(title='Test Group')

        user_mock = MagicMock()
        user_mock.id = user_id
        user_mock.username = 'agree_user'
        user_mock.full_name = 'Agree User'

        query_mock = AsyncMock()
        query_mock.from_user = user_mock
        query_mock.data = f"agree_{group_id}"
        
        mock_update.callback_query = query_mock
        
        # --- Run the function ---
        self.async_test(bot.handle_agreement(mock_update, mock_context))

        # --- Assertions ---
        # 1. Check if agreement was recorded
        self.assertTrue(self.storage_manager.has_agreed(user_id, group_id, bot.COC_VERSION))

        # 2. Check if the bot tried to unrestrict the member
        mock_context.bot.restrict_chat_member.assert_called_once()
        args, kwargs = mock_context.bot.restrict_chat_member.call_args
        self.assertEqual(kwargs['chat_id'], group_id)
        self.assertEqual(kwargs['user_id'], user_id)
        self.assertTrue(kwargs['permissions'].can_send_messages)

        # 3. Check if the "success" message was sent
        query_mock.answer.assert_called_with(bot.AGREEMENT_SUCCESS_MESSAGE, show_alert=True)
        query_mock.edit_message_text.assert_called_once()


    @patch('bot.ContextTypes.DEFAULT_TYPE')
    @patch('bot.Update')
    def test_04_gatekeeper_restricts_unagreed_member(self, mock_update, mock_context):
        """Test that the gatekeeper deletes a message from and restricts an unagreed member."""

        # --- Setup ---
        user_id = 400
        group_id = -1004
        
        # --- Mocking Telegram Objects ---
        mock_context.bot = AsyncMock()
        
        user_mock = MagicMock()
        user_mock.id = user_id
        user_mock.is_bot = False

        chat_mock = MagicMock()
        chat_mock.id = group_id
        chat_mock.type = 'group'
        chat_mock.title = 'Gatekeeper Test Group'

        message_mock = AsyncMock()
        
        mock_update.effective_user = user_mock
        mock_update.effective_chat = chat_mock
        mock_update.effective_message = message_mock
        
        # --- Run the function ---
        self.async_test(bot.gatekeeper_handler(mock_update, mock_context))

        # --- Assertions ---
        # 1. Check if the message was deleted
        message_mock.delete.assert_called_once()

        # 2. Check if the member was restricted
        mock_context.bot.restrict_chat_member.assert_called_once()
        args, kwargs = mock_context.bot.restrict_chat_member.call_args
        self.assertEqual(kwargs['chat_id'], group_id)
        self.assertEqual(kwargs['user_id'], user_id)
        self.assertFalse(kwargs['permissions'].can_send_messages)

        # 3. Check if a DM was sent
        mock_context.bot.send_message.assert_called_once()
        args, kwargs = mock_context.bot.send_message.call_args
        self.assertEqual(kwargs['chat_id'], user_id)
        self.assertIn("Your message in", kwargs['text'])


if __name__ == '__main__':
    unittest.main()