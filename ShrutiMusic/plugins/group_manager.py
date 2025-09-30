from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from ShrutiMusic import app, userbot
from ShrutiMusic.utils.database import add_afk, get_afk, remove_afk, set_welcome_message, get_welcome_message
from ShrutiMusic.utils.helpers import is_sudo
import asyncio

# Dictionary to store AFK users temporarily
AFK_USERS = {}
VC_LOGGER_STATUS = {}

# ====== /welcomehelp ======
@app.on_message(filters.command("welcomehelp") & filters.group)
async def welcome_help(client, message: Message):
    text = get_welcome_message(message.chat.id)
    if text:
        await message.reply_text(f"Current Welcome Message:\n\n{text}")
    else:
        await message.reply_text("No welcome message set yet. Use /setwelcome <text> to set one.")

# ====== /lock ======
@app.on_message(filters.command("lock") & filters.group)
async def lock_group(client, message: Message):
    # Only admins can lock
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not member.status in ("administrator", "creator"):
        await message.reply_text("You need to be an admin to lock the group!")
        return

    permissions = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False
    )
    await client.set_chat_permissions(message.chat.id, permissions)
    await message.reply_text("✅ Group locked successfully!")

# ====== /afk {reason} ======
@app.on_message(filters.command("afk"))
async def afk_mode(client, message: Message):
    reason = "No reason provided"
    if len(message.command) > 1:
        reason = " ".join(message.command[1:])
    AFK_USERS[message.from_user.id] = reason
    await add_afk(message.from_user.id, reason)
    await message.reply_text(f"AFK activated: {reason}")

@app.on_message(filters.text & ~filters.private)
async def afk_reply(client, message: Message):
    # Check if mentioned users are AFK
    if message.from_user.id in AFK_USERS:
        # Remove AFK if user sent message
        AFK_USERS.pop(message.from_user.id)
        await remove_afk(message.from_user.id)
        await message.reply_text("Welcome back! AFK removed.")

    for user_id in AFK_USERS.keys():
        if str(user_id) in message.text:
            reason = AFK_USERS[user_id]
            await message.reply_text(f"User is AFK: {reason}")

# ====== /autoapprove ======
@app.on_message(filters.command("autoapprove") & filters.group)
async def auto_approve(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not member.status in ("administrator", "creator"):
        await message.reply_text("You need to be an admin to toggle autoapprove!")
        return

    # Toggle autoapprove status in VC_LOGGER_STATUS for simplicity
    VC_LOGGER_STATUS[message.chat.id] = VC_LOGGER_STATUS.get(message.chat.id, {})
    VC_LOGGER_STATUS[message.chat.id]["autoapprove"] = not VC_LOGGER_STATUS[message.chat.id].get("autoapprove", False)
    status = "enabled" if VC_LOGGER_STATUS[message.chat.id]["autoapprove"] else "disabled"
    await message.reply_text(f"Auto approve join requests {status} ✅")

# ====== /pretender ======
@app.on_message(filters.command("pretender") & filters.group)
async def check_pretender(client, message: Message):
    # Example placeholder: return last 5 messages from user
    async for msg in client.iter_history(message.chat.id, limit=5):
        if msg.from_user and msg.from_user.id == message.from_user.id:
            await message.reply_text(f"Last messages:\n{msg.text or 'No text content'}")
            break

# ====== /edit ======
@app.on_message(filters.command("edit") & filters.group)
async def edit_guardian(client, message: Message):
    # Placeholder: just acknowledge
    await message.reply_text("Edit guardian activated. Future edits will be auto-deleted (placeholder).")

# ====== /vclogger on/off ======
@app.on_message(filters.command("vclogger") & filters.group)
async def vc_logger(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /vclogger on/off")
        return
    status = message.command[1].lower()
    VC_LOGGER_STATUS[message.chat.id] = VC_LOGGER_STATUS.get(message.chat.id, {})
    if status == "on":
        VC_LOGGER_STATUS[message.chat.id]["vclogger"] = True
        await message.reply_text("VC Logger enabled ✅")
    elif status == "off":
        VC_LOGGER_STATUS[message.chat.id]["vclogger"] = False
        await message.reply_text("VC Logger disabled ❌")
    else:
        await message.reply_text("Use 'on' or 'off' only.")

# ====== Update /help ======
@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = """
📌 *Available Group Commands:*
/welcomehelp - Set or view custom welcome
/lock - Lock group for members
/afk {reason} - Set AFK status
/autoapprove - Toggle auto approve join requests
/pretender - Check recent messages of user
/edit - Auto delete edits
/vclogger on/off - VC join/leave logs

Use /help to see full bot commands including music features.
"""
    await message.reply_text(help_text)