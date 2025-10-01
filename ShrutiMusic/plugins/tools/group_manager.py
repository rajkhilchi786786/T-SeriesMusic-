from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from ShrutiMusic import app
from ShrutiMusic.utils.database import get_welcome_message
import asyncio
import re

# ====== Temporary Storage ======
VC_LOGGER_STATUS = {}
MUTE_USERS = {}
ANTI_LINK_STATUS = {}

LINK_PATTERN = re.compile(r"(https?://\S+|t.me/\S+)")

# ===================== /welcomehelp =====================
@app.on_message(filters.command("welcomehelp") & filters.group)
async def welcome_help(client, message: Message):
    text = get_welcome_message(message.chat.id)
    if text:
        await message.reply_text(f"📌 Current Welcome Message:\n\n{text}", quote=True)
    else:
        await message.reply_text("No welcome message set yet. Use /setwelcome <text> to set one.", quote=True)

# ===================== /lock =====================
@app.on_message(filters.command("lock") & filters.group)
async def lock_group(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ("administrator", "creator"):
        return await message.reply_text("❌ You need to be an admin to lock the group!", quote=True)
    permissions = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
    )
    await client.set_chat_permissions(message.chat.id, permissions)
    await message.reply_text("✅ Group locked successfully!", quote=True)

# ===================== /unlock =====================
@app.on_message(filters.command("unlock") & filters.group)
async def unlock_group(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ("administrator", "creator"):
        return await message.reply_text("❌ You need to be an admin to unlock the group!", quote=True)
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
    )
    await client.set_chat_permissions(message.chat.id, permissions=permissions)
    await message.reply_text("✅ Group unlocked successfully!", quote=True)

# ===================== /mute /unmute =====================
@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a user's message to mute them!", quote=True)
    user = message.reply_to_message.from_user
    MUTE_USERS[user.id] = True
    permissions = ChatPermissions(can_send_messages=False)
    await client.restrict_chat_member(message.chat.id, user.id, permissions=permissions)
    await message.reply_text(f"🔇 Muted {user.mention}", quote=True)

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a user's message to unmute them!", quote=True)
    user = message.reply_to_message.from_user
    MUTE_USERS.pop(user.id, None)
    permissions = ChatPermissions(can_send_messages=True)
    await client.restrict_chat_member(message.chat.id, user.id, permissions=permissions)
    await message.reply_text(f"🔊 Unmuted {user.mention}", quote=True)

# ===================== /kick /ban /unban =====================
@app.on_message(filters.command("kick") & filters.group)
async def kick_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a user's message to kick them!", quote=True)
    user = message.reply_to_message.from_user
    await client.kick_chat_member(message.chat.id, user.id)
    await message.reply_text(f"👢 Kicked {user.mention}", quote=True)

@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a user's message to ban them!", quote=True)
    user = message.reply_to_message.from_user
    await client.ban_chat_member(message.chat.id, user.id)
    await message.reply_text(f"⛔ Banned {user.mention}", quote=True)

@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /unban <user_id>", quote=True)
    try:
        user_id = int(message.command[1])
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"✅ Unbanned user {user_id}", quote=True)
    except ValueError:
        await message.reply_text("❌ Invalid user_id!", quote=True)

# ===================== /slowmode =====================
@app.on_message(filters.command("slowmode") & filters.group)
async def slowmode(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /slowmode <seconds>", quote=True)
    try:
        seconds = int(message.command[1])
        if seconds < 0 or seconds > 3600:
            raise ValueError
        await client.set_chat_slow_mode_delay(message.chat.id, seconds)
        await message.reply_text(f"⏱ Slowmode set to {seconds} seconds", quote=True)
    except ValueError:
        await message.reply_text("❌ Invalid number! Use 0-3600", quote=True)

# ===================== /antilink on/off =====================
@app.on_message(filters.command("antilink") & filters.group)
async def anti_link(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /antilink on/off", quote=True)
    status = message.command[1].lower()
    ANTI_LINK_STATUS[message.chat.id] = True if status == "on" else False
    await message.reply_text(f"🚫 Anti-link is now {'enabled' if ANTI_LINK_STATUS[message.chat.id] else 'disabled'}", quote=True)

@app.on_message(filters.text & ~filters.private)
async def delete_links(client, message: Message):
    if ANTI_LINK_STATUS.get(message.chat.id) and message.text:
        if LINK_PATTERN.search(message.text):
            await message.delete()
            await message.reply_text(f"🚫 Link deleted!", quote=False)

# ===================== /vclogger on/off =====================
@app.on_message(filters.command("vclogger") & filters.group)
async def vc_logger(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /vclogger on/off", quote=True)
    status = message.command[1].lower()
    VC_LOGGER_STATUS[message.chat.id] = VC_LOGGER_STATUS.get(message.chat.id, {})
    if status == "on":
        VC_LOGGER_STATUS[message.chat.id]["vclogger"] = True
        await message.reply_text("🎙 VC Logger enabled ✅", quote=True)
    elif status == "off":
        VC_LOGGER_STATUS[message.chat.id]["vclogger"] = False
        await message.reply_text("❌ VC Logger disabled", quote=True)
    else:
        await message.reply_text("Use 'on' or 'off' only.", quote=True)

# 🎙 Notify when users join/leave livestream or VC
@app.on_chat_member_updated()
async def vc_notify(client, chat_member_update):
    chat_id = chat_member_update.chat.id
    if not VC_LOGGER_STATUS.get(chat_id, {}).get("vclogger"):
        return
    user = chat_member_update.new_chat_member.user
    if chat_member_update.new_chat_member.is_member and chat_member_update.old_chat_member and not chat_member_update.old_chat_member.is_member:
        await app.send_message(chat_id, f"🎥 {user.mention} joined the livestream/VC ✅")
    elif chat_member_update.old_chat_member and chat_member_update.old_chat_member.is_member and not chat_member_update.new_chat_member.is_member:
        await app.send_message(chat_id, f"👋 {user.mention} left the livestream/VC ❌")

# ===================== /autoapprove =====================
@app.on_message(filters.command("autoapprove") & filters.group)
async def auto_approve(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ("administrator", "creator"):
        return await message.reply_text("❌ You need to be an admin to toggle autoapprove!", quote=True)
    VC_LOGGER_STATUS[message.chat.id] = VC_LOGGER_STATUS.get(message.chat.id, {})
    VC_LOGGER_STATUS[message.chat.id]["autoapprove"] = not VC_LOGGER_STATUS[message.chat.id].get("autoapprove", False)
    status = "enabled" if VC_LOGGER_STATUS[message.chat.id]["autoapprove"] else "disabled"
    await message.reply_text(f"✅ Auto approve join requests {status}", quote=True)

# ===================== /edit =====================
@app.on_message(filters.command("edit") & filters.group)
async def edit_guardian(client, message: Message):
    await message.reply_text("✍️ Edit guardian activated. Future edits will be auto-deleted.", quote=True)

@app.on_message(filters.edited & filters.group)
async def delete_edits(client, message: Message):
    await message.delete()

# ===================== /pretender =====================
@app.on_message(filters.command("pretender") & filters.group)
async def check_pretender(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a user's message to check their last 5 messages.", quote=True)
    user = message.reply_to_message.from_user
    text = f"🕵️ Last 5 messages from {user.first_name}:\n\n"
    async for msg in client.iter_history(message.chat.id, limit=50):
        if msg.from_user and msg.from_user.id == user.id:
            text += f"- {msg.text or '📎 Media/Other'}\n"
    await message.reply_text(text, quote=True)

# ===================== /ghelp =====================
@app.on_message(filters.command("ghelp") & filters.group)
async def ghelp_command(client, message: Message):
    help_text = """
📌 Group Security Commands:
/welcomehelp - View welcome message
/lock - Lock group
/unlock - Unlock group
/mute - Mute user (reply)
/unmute - Unmute user (reply)
/kick - Kick user (reply)
/ban - Ban user (reply)
/unban <user_id> - Unban user
/slowmode <seconds> - Set slowmode
/antilink on/off - Enable/disable anti-link
/vclogger on/off - VC logs (join/leave notify)
/autoapprove - Toggle auto approve join requests
/edit - Auto delete edits
/pretender - Last 5 messages of a user
"""
    await message.reply_text(help_text, quote=True)