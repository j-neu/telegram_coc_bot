"""Main bot module for Telegram CoC Agreement Bot."""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.constants import ChatMemberStatus

import config
from config import (
    BOT_TOKEN,
    ADMIN_IDS,
    COC_VERSION,
    WELCOME_MESSAGE,
    AGREEMENT_SUCCESS_MESSAGE,
    ADMIN_ONLY_MESSAGE,
    DRY_RUN,
    STORAGE_TYPE,
)

# Import storage manager based on configuration
if STORAGE_TYPE == 'sqlite':
    from database_manager import DatabaseManager as StorageManager
else:
    from sheets_manager import SheetsManager as StorageManager

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Log configuration
logger.info(f"Storage type: {STORAGE_TYPE}")
if DRY_RUN:
    logger.warning("=" * 60)
    logger.warning("DRY RUN MODE ENABLED - No users will be restricted")
    logger.warning("All permission changes will only be logged")
    logger.warning("=" * 60)

# Initialize storage manager
storage_manager = StorageManager()


def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in ADMIN_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets the user and explains the bot's purpose in a private chat."""
    await update.message.reply_text(
        "Hello! I am the Code of Conduct bot for your group. "
        "You can agree to the CoC by clicking the 'Agree' button on the pinned message in your group."
    )


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new members joining the group."""
    if not update.chat_member:
        return

    new_member = update.chat_member.new_chat_member
    old_member = update.chat_member.old_chat_member

    if (old_member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and
        new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]):

        user = new_member.user
        chat = update.effective_chat

        if user.is_bot:
            return

        if storage_manager.has_agreed(user.id, chat.id, COC_VERSION):
            logger.info(f"Re-joining member {user.id} has already agreed.")
            return

        if not DRY_RUN:
            try:
                await context.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                logger.info(f"Restricted new member {user.id} in chat {chat.id}")
            except Exception as e:
                logger.error(f"Failed to restrict new member {user.id}: {e}")
        
        # Attempt to DM the user with instructions
        try:
            keyboard = [[InlineKeyboardButton("View Code of Conduct 📜", url=config.COC_LINK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=user.id,
                text="Welcome! Please find the pinned message in the group to agree to the Code of Conduct and start chatting.",
                reply_markup=reply_markup
            )
        except Exception:
            logger.warning(f"Could not DM new user {user.id}. They will need to see the pinned message.")


async def handle_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when a user clicks the 'Agree' button from any message."""
    query = update.callback_query
    user = query.from_user

    callback_data = query.data
    if not callback_data.startswith('agree_'):
        return

    try:
        group_id = int(callback_data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer("Invalid agreement data.", show_alert=True, cache_time=60)
        return

    if storage_manager.has_agreed(user.id, group_id, COC_VERSION):
        await query.answer("You have already agreed to the Code of Conduct!", show_alert=True, cache_time=60)
        return

    try:
        chat = await context.bot.get_chat(group_id)
        group_name = chat.title
    except Exception as e:
        logger.error(f"Failed to get chat info for {group_id}: {e}")
        group_name = "Unknown"

    success = storage_manager.record_agreement(
        user_id=user.id,
        username=user.username or '',
        full_name=user.full_name or '',
        group_id=group_id,
        group_name=group_name,
        version=COC_VERSION
    )

    if not success:
        await query.answer("Error: Could not record your agreement. Please try again.", show_alert=True)
        return

    if not DRY_RUN:
        try:
            await context.bot.restrict_chat_member(
                chat_id=group_id,
                user_id=user.id,
                permissions=ChatPermissions(
                    can_send_messages=True, can_send_audios=True, can_send_documents=True,
                    can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
                    can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
                    can_add_web_page_previews=True, can_change_info=True, can_invite_users=True,
                    can_pin_messages=True
                )
            )
            logger.info(f"Unrestricted user {user.id} in chat {group_id}")
        except Exception as e:
            logger.error(f"Failed to unrestrict user {user.id}: {e}")
            await query.answer("Agreement recorded, but failed to update permissions. Please contact an admin.", show_alert=True)
            return
    
    await query.answer(AGREEMENT_SUCCESS_MESSAGE, show_alert=True)
    # Don't edit the original message, as it might be pinned and we don't want to change it.
    # The query.answer is sufficient notification for the user.


async def who_agreed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: List users who have agreed."""
    user = update.effective_user
    chat = update.effective_chat
    if not is_admin(user.id): return

    agreed_users = storage_manager.get_all_agreed(chat.id, COC_VERSION)
    if not agreed_users:
        await update.message.reply_text("No users have agreed to the Code of Conduct yet.")
        return

    response = f"📊 Users who agreed to CoC v{COC_VERSION}: {len(agreed_users)} total\n\n"
    response += "\n".join([
        f"• @{u.get('username', '') or u.get('full_name', 'Unknown')}"
        for u in agreed_users[:50]
    ])
    if len(agreed_users) > 50:
        response += f"\n... and {len(agreed_users) - 50} more."
    await update.message.reply_text(response)


async def post_onboarding_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Posts the main persistent message for members to start the agreement process."""
    user = update.effective_user
    chat = update.effective_chat
    if not is_admin(user.id): return

    keyboard = [[
        InlineKeyboardButton("View & Agree to the Code of Conduct", callback_data=f"agree_{chat.id}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "**Action Required: Agree to the Code of Conduct**\n\n"
        "To participate in this group, all members must agree to our Code of Conduct. "
        "Please click the button below to view the CoC and agree to its terms.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def set_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: Update CoC version."""
    user = update.effective_user
    if not is_admin(user.id): return

    if not context.args:
        await update.message.reply_text(f"Current CoC version: {COC_VERSION}\nUsage: /setversion <new_version>")
        return

    await update.message.reply_text(
        "To change the CoC version, please update the `COC_VERSION` in your .env file and restart the bot."
    )


async def gatekeeper_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all messages to enforce CoC agreement."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message or chat.type not in ['group', 'supergroup'] or is_admin(user.id):
        return

    if not storage_manager.has_agreed(user.id, chat.id, COC_VERSION):
        logger.info(f"Gatekeeper: User {user.id} has not agreed. Deleting message.")
        try:
            if not DRY_RUN:
                await message.delete()
                await context.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
            
            try:
                await context.bot.send_message(
                    chat_id=user.id,
                    text=f"Your message in '{chat.title}' was removed because you have not yet agreed to the Code of Conduct. "
                         "Please find the pinned message in the group to agree and restore your chat permissions."
                )
            except Exception:
                logger.warning(f"Gatekeeper: Failed to send DM to user {user.id}. They are still restricted.")
        except Exception as e:
            logger.error(f"Error in gatekeeper for user {user.id}: {e}")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("whoagreed", who_agreed))
    application.add_handler(CommandHandler("post_onboarding", post_onboarding_message))
    application.add_handler(CommandHandler("setversion", set_version))
    
    application.add_handler(CallbackQueryHandler(handle_agreement, pattern="^agree_"))
    application.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gatekeeper_handler))

    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
