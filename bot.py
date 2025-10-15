"""Main bot module for Telegram CoC Agreement Bot."""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    ContextTypes,
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
    """Handle /start command - send CoC agreement message."""
    user = update.effective_user
    chat = update.effective_chat

    keyboard = [
        [
            InlineKeyboardButton("View Code of Conduct 📜", url=config.COC_LINK),
            InlineKeyboardButton("Agree ✅", callback_data=f"agree_{chat.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new members joining the group."""
    if not update.chat_member:
        return

    new_member = update.chat_member.new_chat_member
    old_member = update.chat_member.old_chat_member

    # Check if this is a new member joining
    if (old_member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and
        new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]):

        user = new_member.user
        chat = update.effective_chat

        # Skip bots
        if user.is_bot:
            return

        # Record the user's presence. This is crucial for /restrict_existing to find them.
        storage_manager.record_agreement(
            user_id=user.id,
            username=user.username or '',
            full_name=user.full_name or '',
            group_id=chat.id,
            group_name=chat.title or '',
            version='joined' # Special version to indicate they are known but haven't agreed
        )

        # Check if user has already agreed to the current version
        if storage_manager.has_agreed(user.id, chat.id, COC_VERSION):
            logger.info(f"User {user.id} has already agreed, skipping restriction")
            return

        # Restrict the user (remove all permissions)
        if DRY_RUN:
            logger.info(f"[DRY RUN] Would restrict user {user.id} in chat {chat.id}")
        else:
            try:
                await context.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_send_audios=False,
                        can_send_documents=False,
                        can_send_photos=False,
                        can_send_videos=False,
                        can_send_video_notes=False,
                        can_send_voice_notes=False,
                        can_send_polls=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                        can_change_info=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                    )
                )
                logger.info(f"Restricted user {user.id} in chat {chat.id}")
            except Exception as e:
                logger.error(f"Failed to restrict user {user.id}: {e}")
                return

        # Prepare agreement message
        keyboard = [
            [
                InlineKeyboardButton("View Code of Conduct 📜", url=config.COC_LINK),
                InlineKeyboardButton("Agree ✅", callback_data=f"agree_{chat.id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Try to send DM first
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=WELCOME_MESSAGE,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            logger.info(f"Sent DM to user {user.id}")
        except Exception as e:
            # If DM fails, send message in group
            logger.warning(f"Failed to send DM to user {user.id}: {e}")
            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=f"Welcome {user.mention_html()}!\n\n{WELCOME_MESSAGE}",
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Failed to send group message: {e}")


async def handle_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when user clicks the Agree button."""
    query = update.callback_query
    user = query.from_user

    # Parse callback data to get group_id
    callback_data = query.data
    if not callback_data.startswith('agree_'):
        return

    try:
        group_id = int(callback_data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer("Invalid agreement data.", show_alert=True)
        return

    # Check if already agreed
    if storage_manager.has_agreed(user.id, group_id, COC_VERSION):
        await query.answer("You have already agreed to the Code of Conduct!", show_alert=True)
        return

    # Get group info
    try:
        chat = await context.bot.get_chat(group_id)
        group_name = chat.title
    except Exception as e:
        logger.error(f"Failed to get chat info for {group_id}: {e}")
        group_name = "Unknown"

    # Record agreement
    success = storage_manager.record_agreement(
        user_id=user.id,
        username=user.username or '',
        full_name=user.full_name or '',
        group_id=group_id,
        group_name=group_name,
        version=COC_VERSION
    )

    if not success:
        await query.answer("Failed to record agreement. Please try again.", show_alert=True)
        return

    # Unrestrict user in the group
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would unrestrict user {user.id} in chat {group_id}")
    else:
        try:
            await context.bot.restrict_chat_member(
                chat_id=group_id,
                user_id=user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_audios=True,
                    can_send_documents=True,
                    can_send_photos=True,
                    can_send_videos=True,
                    can_send_video_notes=True,
                    can_send_voice_notes=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                )
            )
            logger.info(f"Unrestricted user {user.id} in chat {group_id}")
        except Exception as e:
            logger.error(f"Failed to unrestrict user {user.id}: {e}")
            await query.answer("Agreement recorded, but failed to update permissions. Please contact an admin.", show_alert=True)
            return

    await query.answer(AGREEMENT_SUCCESS_MESSAGE, show_alert=True)
    await query.edit_message_text(
        f"✅ {AGREEMENT_SUCCESS_MESSAGE}"
    )


async def who_agreed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: List users who have agreed."""
    user = update.effective_user
    chat = update.effective_chat

    if not is_admin(user.id):
        await update.message.reply_text(ADMIN_ONLY_MESSAGE)
        return

    # Get agreed users for this group
    agreed_users = storage_manager.get_all_agreed(chat.id, COC_VERSION)

    if not agreed_users:
        await update.message.reply_text("No users have agreed to the Code of Conduct yet.")
        return

    # Format response
    response = f"📊 Users who agreed to CoC (v{COC_VERSION}):\n\n"
    response += f"Total: {len(agreed_users)} users\n\n"

    for idx, user_record in enumerate(agreed_users[:50], 1):  # Limit to 50 for message length
        username = user_record.get('username', '')
        full_name = user_record.get('full_name', 'Unknown')
        agreed_at = user_record.get('agreed_at', '')[:10]  # Just the date

        user_display = f"@{username}" if username else full_name
        response += f"{idx}. {user_display} - {agreed_at}\n"

    if len(agreed_users) > 50:
        response += f"\n... and {len(agreed_users) - 50} more users."

    await update.message.reply_text(response)


async def scan_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: Informs the admin about the member onboarding process."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text(ADMIN_ONLY_MESSAGE)
        return

    await update.message.reply_text(
        "ℹ️ Onboarding Existing Members\n\n"
        "This bot automatically handles NEW members when they join.\n\n"
        "To onboard an EXISTING group, you must make the bot aware of members:\n"
        "1. Use `/sendcode_group` to post a public message. When users click 'Agree', the bot learns they exist.\n"
        "2. After a while, use `/restrict_existing` to restrict anyone the bot knows about who hasn't agreed.\n"
        "3. Use `/sendcode_dm` to send reminders to those who are now restricted."
    )


async def send_code_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: Send CoC agreement request to the group chat."""
    user = update.effective_user
    chat = update.effective_chat

    if not is_admin(user.id):
        await update.message.reply_text(ADMIN_ONLY_MESSAGE)
        return

    keyboard = [
        [
            InlineKeyboardButton("View Code of Conduct 📜", url=config.COC_LINK),
            InlineKeyboardButton("Agree ✅", callback_data=f"agree_{chat.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📢 Attention all members!\n\n{WELCOME_MESSAGE}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    await update.message.reply_text(
        "✅ Code of Conduct agreement request has been sent to the group!"
    )


async def send_code_dm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: Send a DM to all known unagreed members."""
    user = update.effective_user
    chat = update.effective_chat

    if not is_admin(user.id):
        await update.message.reply_text(ADMIN_ONLY_MESSAGE)
        return

    await update.message.reply_text("Processing... Sending DMs to unagreed members.")

    unagreed_member_ids = storage_manager.get_unagreed_members(chat.id, COC_VERSION)

    if not unagreed_member_ids:
        await update.message.reply_text("No unagreed members found to DM. They may have all agreed already.")
        return

    sent_count = 0
    failed_count = 0

    for user_id in unagreed_member_ids:
        try:
            keyboard = [[
                InlineKeyboardButton("View Code of Conduct 📜", url=config.COC_LINK),
                InlineKeyboardButton("Agree ✅", callback_data=f"agree_{chat.id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=user_id,
                text=WELCOME_MESSAGE,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to DM user {user_id}: {e}")
            failed_count += 1

    await update.message.reply_text(
        f"DM process complete.\n\n"
        f"✅ DMs sent successfully: {sent_count}\n"
        f"❌ Failed to reach: {failed_count}"
    )


async def restrict_existing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: Restrict all known members who have not agreed."""
    user = update.effective_user
    chat = update.effective_chat

    if not is_admin(user.id):
        await update.message.reply_text(ADMIN_ONLY_MESSAGE)
        return

    await update.message.reply_text("Processing... Restricting all known, unagreed members.")

    unagreed_member_ids = storage_manager.get_unagreed_members(chat.id, COC_VERSION)

    if not unagreed_member_ids:
        await update.message.reply_text("No unagreed members found to restrict. They may have all agreed already.")
        return

    restricted_count = 0
    for user_id in unagreed_member_ids:
        try:
            member = await context.bot.get_chat_member(chat.id, user_id)
            if member.user.is_bot or member.status != ChatMemberStatus.MEMBER:
                continue

            if DRY_RUN:
                logger.info(f"[DRY RUN] Would restrict user {user_id} via /restrict_existing")
            else:
                await context.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                logger.info(f"Restricted user {user_id} via /restrict_existing")
            restricted_count += 1
        except Exception as e:
            logger.error(f"Failed to restrict user {user_id} via /restrict_existing: {e}")

    await update.message.reply_text(
        f"Restriction process complete.\n\n"
        f"✅ Members newly restricted: {restricted_count}"
    )


async def set_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: Update CoC version."""
    user = update.effective_user

    if not is_admin(user.id):
        await update.message.reply_text(ADMIN_ONLY_MESSAGE)
        return

    if not context.args:
        await update.message.reply_text(
            f"Current CoC version: {COC_VERSION}\n\n"
            "Usage: /setversion <new_version>\n"
            "Example: /setversion 2.0"
        )
        return

    new_version = context.args[0]
    await update.message.reply_text(
        f"⚠️ To change the CoC version to {new_version}, please update the COC_VERSION "
        "in your .env file and restart the bot.\n\n"
        "This will require all users to re-agree to the new version."
    )


async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: Export agreement data."""
    user = update.effective_user
    chat = update.effective_chat

    if not is_admin(user.id):
        await update.message.reply_text(ADMIN_ONLY_MESSAGE)
        return

    if STORAGE_TYPE == 'sheets':
        await update.message.reply_text(
            "You can access the full agreement data directly in your Google Sheet:\n"
            f"https://docs.google.com/spreadsheets/d/{config.SHEET_ID}"
        )
    else:
        # Export from database
        data = storage_manager.export_data(chat.id)
        stats = storage_manager.get_stats(chat.id)

        response = f"📊 Agreement Data Export\n\n"
        response += f"Total agreements: {stats['total_agreements']}\n"
        response += f"Current version ({COC_VERSION}): {stats['by_version'].get(COC_VERSION, 0)}\n\n"

        if data:
            response += "Recent agreements:\n"
            for record in data[:10]:  # Show last 10
                username = record.get('username', '')
                full_name = record.get('full_name', 'Unknown')
                agreed_at = record.get('agreed_at', '')[:10]
                user_display = f"@{username}" if username else full_name
                response += f"• {user_display} - {agreed_at}\n"

            if len(data) > 10:
                response += f"\n... and {len(data) - 10} more records"

        await update.message.reply_text(response)


async def check_group_members_on_startup(application: Application) -> None:
    """
    Check all groups for members who haven't agreed after startup.
    This handles the case where the bot was offline and missed new joins.
    """
    logger.info("Running startup check for unagreed members...")

    try:
        all_agreements = storage_manager.export_data()
        group_ids = {agreement.get('group_id') for agreement in all_agreements if agreement.get('group_id')}
        logger.info(f"Found {len(group_ids)} groups to check")

        for group_id in group_ids:
            try:
                unagreed_user_ids = storage_manager.get_unagreed_members(group_id, COC_VERSION)
                logger.info(f"Checking group {group_id} for {len(unagreed_user_ids)} unagreed members")

                for user_id in unagreed_user_ids:
                    try:
                        member = await application.bot.get_chat_member(group_id, user_id)
                        user = member.user

                        if user.is_bot:
                            continue

                        logger.info(f"Found unagreed member {user.id} in group {group_id} on startup")

                        if DRY_RUN:
                            logger.info(f"[DRY RUN] Would restrict user {user.id} in group {group_id}")
                        else:
                            await application.bot.restrict_chat_member(
                                chat_id=group_id,
                                user_id=user_id,
                                permissions=ChatPermissions(can_send_messages=False)
                            )
                            logger.info(f"Restricted user {user.id} in group {group_id} on startup")

                        keyboard = [[
                            InlineKeyboardButton("View Code of Conduct 📜", url=config.COC_LINK),
                            InlineKeyboardButton("Agree ✅", callback_data=f"agree_{group_id}")
                        ]]
                        reply_markup = InlineKeyboardMarkup(keyboard)

                        try:
                            await application.bot.send_message(
                                chat_id=user.id,
                                text=f"⚠️ Recovery Notice: The bot was offline or restarted.\n\n{WELCOME_MESSAGE}",
                                reply_markup=reply_markup,
                                parse_mode='Markdown'
                            )
                            logger.info(f"Sent recovery DM to user {user.id}")
                        except Exception as e:
                            logger.warning(f"Failed to send recovery DM to user {user.id}: {e}")
                    except Exception as e:
                        logger.error(f"Failed to process user {user_id} in group {group_id}: {e}")

            except Exception as e:
                logger.error(f"Failed to check group {group_id}: {e}")
                continue

        logger.info("Startup member check completed")

    except Exception as e:
        logger.error(f"Failed during startup check: {e}")


async def post_init(application: Application) -> None:
    """Called after bot initialization but before polling starts."""
    logger.info("Bot initialized, running post-startup tasks...")
    await check_group_members_on_startup(application)
    logger.info("Post-startup tasks completed")


async def gatekeeper_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all messages to enforce CoC agreement."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message or chat.type not in ['group', 'supergroup']:
        return
        
    # Ignore admins
    if is_admin(user.id):
        return

    # If user has not agreed, delete message, restrict, and notify.
    if not storage_manager.has_agreed(user.id, chat.id, COC_VERSION):
        logger.info(f"User {user.id} has not agreed. Deleting message and restricting.")

        try:
            # 1. Delete the message
            await message.delete()

            # 2. Restrict the user
            if not DRY_RUN:
                await context.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
            
            # 3. Notify the user via DM
            keyboard = [[
                InlineKeyboardButton("View Code of Conduct 📜", url=config.COC_LINK),
                InlineKeyboardButton("Agree ✅", callback_data=f"agree_{chat.id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=user.id,
                text=f"Your message in '{chat.title}' was removed because you have not yet agreed to the Code of Conduct.\n\n{WELCOME_MESSAGE}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in gatekeeper for user {user.id}: {e}")


def main() -> None:
    """Start the bot."""
    from telegram.ext import MessageHandler, filters
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("whoagreed", who_agreed))
    application.add_handler(CommandHandler("scan", scan_members))
    application.add_handler(CommandHandler("sendcode_group", send_code_group))
    application.add_handler(CommandHandler("sendcode_dm", send_code_dm))
    application.add_handler(CommandHandler("restrict_existing", restrict_existing))
    application.add_handler(CommandHandler("setversion", set_version))
    application.add_handler(CommandHandler("export", export_data))

    application.add_handler(CallbackQueryHandler(handle_agreement, pattern="^agree_"))
    application.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))
    
    # Add the gatekeeper handler to check all messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gatekeeper_handler))


    # Add post-init callback for startup checks
    application.post_init = post_init

    # Start bot
    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
