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
    COC_VERSION as _DEFAULT_COC_VERSION,
    DRY_RUN,
    WEBHOOK_URL,
    PORT,
)
from database_manager import DatabaseManager as StorageManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if DRY_RUN:
    logger.warning("=" * 60)
    logger.warning("DRY RUN MODE ENABLED - No users will be restricted")
    logger.warning("All permission changes will only be logged")
    logger.warning("=" * 60)

storage_manager = StorageManager()

# Active CoC version: DB value takes precedence over env var so /setversion persists across restarts.
_active_coc_version: str = storage_manager.get_setting('coc_version', _DEFAULT_COC_VERSION)
logger.info(f"Active CoC version: {_active_coc_version}")


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def _coc_agree_keyboard(group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("CoC (EN) 📜", url=config.COC_LINK),
            InlineKeyboardButton("CoC (DE) 📜", url=config.COC_LINK_DE),
        ],
        [InlineKeyboardButton("Agree / Zustimmen ✅", callback_data=f"agree_{group_id}")]
    ])


def _coc_confirm_keyboard(group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Confirm / Bestätigen ✅", callback_data=f"confirm_{group_id}")
    ]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I am the Code of Conduct bot for your group. "
        "You can agree to the CoC by clicking the 'Agree' button on the pinned message in your group.\n\n"
        "🇩🇪 Hallo! Ich bin der Verhaltenskodex-Bot für diese Gruppe. "
        "Du kannst dem Verhaltenskodex zustimmen, indem du in der Gruppe auf den 'Zustimmen'-Button klickst."
    )


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

        if storage_manager.has_agreed(user.id, chat.id, _active_coc_version):
            logger.info(f"Re-joining member {user.id} has already agreed.")
            return

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would restrict new member {user.id} in chat {chat.id}")
            return

        try:
            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            logger.info(f"Restricted new member {user.id} in chat {chat.id}")
        except Exception as e:
            logger.error(f"Failed to restrict new member {user.id}: {e}")

        if storage_manager.has_agreed_anywhere(user.id, _active_coc_version):
            reply_markup = _coc_confirm_keyboard(chat.id)
            dm_text = (
                f"Welcome to '{chat.title}'! 👋\n\n"
                f"You've already agreed to the CoC in another group. "
                f"Tap below to confirm it applies here too.\n\n"
                f"🇩🇪 Willkommen bei '{chat.title}'! 👋\n\n"
                f"Du hast dem Verhaltenskodex bereits in einer anderen Gruppe zugestimmt. "
                f"Tippe unten, um zu bestätigen, dass er auch hier gilt."
            )
            group_text = (
                f"Welcome {user.mention_html()}! 👋 "
                f"Tap below to confirm your CoC agreement for this group (you've agreed before).\n"
                f"🇩🇪 Tippe unten, um deine Zustimmung zum Verhaltenskodex für diese Gruppe zu bestätigen."
            )
        else:
            reply_markup = _coc_agree_keyboard(chat.id)
            dm_text = (
                f"Welcome to '{chat.title}'! 👋\n\n"
                f"Before you can post, please read the Code of Conduct and click Agree.\n\n"
                f"🇩🇪 Willkommen bei '{chat.title}'! 👋\n\n"
                f"Bevor du schreiben kannst, lies bitte den Verhaltenskodex und klicke auf Zustimmen."
            )
            group_text = (
                f"Welcome {user.mention_html()}! 👋 "
                f"Please read the Code of Conduct and click Agree before posting.\n"
                f"🇩🇪 Bitte lies den Verhaltenskodex und klicke auf Zustimmen, bevor du schreibst."
            )

        dm_sent = False
        try:
            await context.bot.send_message(chat_id=user.id, text=dm_text, reply_markup=reply_markup)
            dm_sent = True
            logger.info(f"Sent CoC DM to new member {user.id}")
        except Exception:
            pass

        if not dm_sent:
            logger.warning(f"Could not DM new member {user.id}, posting group fallback")
            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=group_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Failed to send group fallback for new member {user.id}: {e}")


async def handle_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user

    callback_data = query.data
    if not (callback_data.startswith('agree_') or callback_data.startswith('confirm_')):
        return

    try:
        group_id = int(callback_data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer(
            "Invalid agreement data. / Ungültige Zustimmungsdaten.",
            show_alert=True, cache_time=60
        )
        return

    if storage_manager.has_agreed(user.id, group_id, _active_coc_version):
        await query.answer(
            "You have already agreed! / Du hast bereits zugestimmt!",
            show_alert=True, cache_time=60
        )
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
        version=_active_coc_version
    )

    if not success:
        await query.answer(
            "Error: Could not save your agreement. Please try again. / "
            "Fehler: Zustimmung konnte nicht gespeichert werden. Bitte erneut versuchen.",
            show_alert=True
        )
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
            await query.answer(
                "Agreement recorded, but failed to update permissions. Please contact an admin. / "
                "Zustimmung gespeichert, aber Berechtigungen konnten nicht aktualisiert werden. "
                "Bitte Admin kontaktieren.",
                show_alert=True
            )
            return

    await query.answer(
        f"You're all set! You can now post in '{group_name}'. 🎉\n"
        f"🇩🇪 Alles klar! Du kannst jetzt in '{group_name}' schreiben. 🎉",
        show_alert=True
    )


async def who_agreed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: List users who have agreed."""
    user = update.effective_user
    chat = update.effective_chat
    if not is_admin(user.id): return

    agreed_users = storage_manager.get_all_agreed(chat.id, _active_coc_version)
    if not agreed_users:
        await update.message.reply_text("No users have agreed to the Code of Conduct yet.")
        return

    response = f"📊 Users who agreed to CoC v{_active_coc_version}: {len(agreed_users)} total\n\n"
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

    await update.message.reply_text(
        "*Action Required: Agree to the Code of Conduct*\n\n"
        "To participate in this group, all members must agree to our Code of Conduct. "
        "Please read it and click the button below to agree.\n\n"
        "🇩🇪 *Aktion erforderlich: Verhaltenskodex zustimmen*\n\n"
        "Um in dieser Gruppe mitzumachen, müssen alle Mitglieder dem Verhaltenskodex zustimmen. "
        "Bitte lies ihn und klicke unten auf Zustimmen.",
        reply_markup=_coc_agree_keyboard(chat.id),
        parse_mode='Markdown'
    )


async def set_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command: Update CoC version."""
    global _active_coc_version
    user = update.effective_user
    if not is_admin(user.id): return

    if not context.args:
        await update.message.reply_text(
            f"Current CoC version: {_active_coc_version}\nUsage: /setversion <new_version>"
        )
        return

    new_version = context.args[0]
    if new_version == _active_coc_version:
        await update.message.reply_text(f"CoC version is already {_active_coc_version}. No change made.")
        return

    old_version = _active_coc_version
    if not storage_manager.set_setting('coc_version', new_version):
        await update.message.reply_text("❌ Failed to save new version to database. No change made.")
        return

    _active_coc_version = new_version
    logger.info(f"CoC version changed {old_version} → {new_version} by admin {user.id}")
    await update.message.reply_text(
        f"✅ CoC version updated: {old_version} → {new_version}\n"
        f"All users must now re-agree to the Code of Conduct."
    )


async def gatekeeper_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete messages and restrict users who haven't agreed to the CoC."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return
    if chat.type not in ['group', 'supergroup']:
        return
    if user.is_bot or is_admin(user.id):
        return
    if storage_manager.has_agreed(user.id, chat.id, _active_coc_version):
        return

    logger.info(f"Gatekeeper: blocking user={user.id} in chat={chat.id}")

    if DRY_RUN:
        logger.info(f"[DRY RUN] Would delete message and restrict user {user.id} in {chat.id}")
        return

    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Failed to delete message from user {user.id}: {e}")

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
    except Exception as e:
        logger.error(f"Failed to restrict user {user.id}: {e}")

    if storage_manager.has_agreed_anywhere(user.id, _active_coc_version):
        reply_markup = _coc_confirm_keyboard(chat.id)
        dm_text = (
            f"You've already agreed to the CoC in another group. "
            f"Tap below to confirm it applies in '{chat.title}' too.\n\n"
            f"🇩🇪 Du hast dem Verhaltenskodex bereits in einer anderen Gruppe zugestimmt. "
            f"Tippe unten, um zu bestätigen, dass er auch für '{chat.title}' gilt."
        )
        group_text = (
            f"{user.mention_html()}, tap below to confirm your CoC agreement for this group "
            f"(you've already agreed in another group).\n"
            f"🇩🇪 Tippe unten, um deine Zustimmung zum Verhaltenskodex für diese Gruppe zu bestätigen."
        )
    else:
        reply_markup = _coc_agree_keyboard(chat.id)
        dm_text = (
            f"Your message in '{chat.title}' was removed because you haven't agreed to the "
            f"Code of Conduct yet.\n\nPlease read the CoC and click Agree to restore your access.\n\n"
            f"🇩🇪 Deine Nachricht in '{chat.title}' wurde entfernt, weil du dem Verhaltenskodex "
            f"noch nicht zugestimmt hast.\n\nBitte lies ihn und klicke auf Zustimmen, "
            f"um wieder schreiben zu können."
        )
        group_text = (
            f"{user.mention_html()}, your message was removed — you haven't agreed to the "
            f"Code of Conduct yet. Please read it and click Agree to restore your access.\n"
            f"🇩🇪 Deine Nachricht wurde entfernt — du hast dem Verhaltenskodex noch nicht zugestimmt. "
            f"Bitte lies ihn und klicke auf Zustimmen."
        )

    dm_sent = False
    try:
        await context.bot.send_message(chat_id=user.id, text=dm_text, reply_markup=reply_markup)
        dm_sent = True
        logger.info(f"Sent CoC DM to user {user.id}")
    except Exception:
        pass

    if not dm_sent:
        logger.warning(f"Could not DM user {user.id}, posting group fallback")
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=group_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to send group fallback for user {user.id}: {e}")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("whoagreed", who_agreed))
    application.add_handler(CommandHandler("post_onboarding", post_onboarding_message))
    application.add_handler(CommandHandler("setversion", set_version))

    application.add_handler(CallbackQueryHandler(handle_agreement, pattern="^(agree|confirm)_"))
    application.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, gatekeeper_handler))

    if WEBHOOK_URL:
        url_path = BOT_TOKEN  # token as URL path provides basic request authentication
        logger.info(f"Starting webhook on port {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=url_path,
            webhook_url=f"{WEBHOOK_URL}/{url_path}",
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        logger.info("No WEBHOOK_URL set, using polling")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
