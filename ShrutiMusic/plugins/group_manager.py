from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from ShrutiMusic import app
from ShrutiMusic.utils.database import add_afk, remove_afk, get_welcome_message
import asyncio

# ====== Temporary storage ======
VC_LOGGER_STATUS = {}
MUTE_USERS = {}
ANTI_LINK_STATUS = {}

# ===================== /welcomehelp =====================
@app.on_message(filters.command("welcomehelp") & filters.group)
async def welcome_help(client, message: Message):
    text = get_welcome_message(message.chat.id)
    if text:
        await message.reply_text(f"Current Welcome Message:\n\n{text}")
    else:
        await message.reply_text("No welcome message set yet. Use /setwelcome <text> to set one.")

# ===================== /lock =====================
@app.on_message(filters.command("lock") & filters.group)
async def lock_group(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ("administrator", "creator"):
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

# ===================== /unlock =====================
@app.on_message(filters.command("unlock") & filters.group)
async def unlock_group(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ("administrator", "creator"):
        await message.reply_text("You need to be an admin to unlock the group!")
        return
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )
    await client.set_chat_permissions(message.chat.id, permissions=permissions)
    await message.reply_text("✅ Group unlocked successfully!")

# ===================== /mute /unmute =====================
@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to mute them!")
        return
    user = message.reply_to_message.from_user
    MUTE_USERS[user.id] = True
    permissions = ChatPermissions(can_send_messages=False)
    await client.restrict_chat_member(message.chat.id, user.id, permissions=permissions)
    await message.reply_text(f"🔇 Muted {user.first_name}")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to unmute them!")
        return
    user = message.reply_to_message.from_user
    MUTE_USERS.pop(user.id, None)
    permissions = ChatPermissions(can_send_messages=True)
    await client.restrict_chat_member(message.chat.id, user.id, permissions=permissions)
    await message.reply_text(f"🔊 Unmuted {user.first_name}")

# ===================== /kick /ban /unban =====================
@app.on_message(filters.command("kick") & filters.group)
async def kick_user(client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to kick them!")
        return
    user = message.reply_to_message.from_user
    await client.kick_chat_member(message.chat.id, user.id)
    await message.reply_text(f"👢 Kicked {user.first_name}")

@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to ban them!")
        return
    user = message.reply_to_message.from_user
    await client.ban_chat_member(message.chat.id, user.id)
    await message.reply_text(f"⛔ Banned {user.first_name}")

@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /unban <user_id>")
        return
    user_id = int(message.command[1])
    await client.unban_chat_member(message.chat.id, user_id)
    await message.reply_text(f"✅ Unbanned user {user_id}")

# ===================== /slowmode =====================
@app.on_message(filters.command("slowmode") & filters.group)
async def slowmode(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /slowmode <seconds>")
        return
    try:
        seconds = int(message.command[1])
        await client.set_chat_slow_mode_delay(message.chat.id, seconds)
        await message.reply_text(f"⏱ Slowmode set to {seconds} seconds")
    except:
        await message.reply_text("Invalid number!")

# ===================== /antilink on/off =====================
@app.on_message(filters.command("antilink") & filters.group)
async def anti_link(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /antilink on/off")
        return
    status = message.command[1].lower()
    ANTI_LINK_STATUS[message.chat.id] = True if status == "on" else False
    await message.reply_text(f"Anti-link is now {'enabled' if ANTI_LINK_STATUS[message.chat.id] else 'disabled'}")

@app.on_message(filters.text & ~filters.private)
async def delete_links(client, message: Message):
    if ANTI_LINK_STATUS.get(message.chat.id):
        if "t.me/" in message.text or "https://" in message.text:
            await message.delete()
            await message.reply_text(f"🚫 Link deleted!", quote=False)

# ===================== /vclogger on/off =====================
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

# ===================== /autoapprove =====================
@app.on_message(filters.command("autoapprove") & filters.group)
async def auto_approve(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ("administrator", "creator"):
        await message.reply_text("You need to be an admin to toggle autoapprove!")
        return
    VC_LOGGER_STATUS[message.chat.id] = VC_LOGGER_STATUS.get(message.chat.id, {})
    VC_LOGGER_STATUS[message.chat.id]["autoapprove"] = not VC_LOGGER_STATUS[message.chat.id].get("autoapprove", False)
    status = "enabled" if VC_LOGGER_STATUS[message.chat.id]["autoapprove"] else "disabled"
    await message.reply_text(f"Auto approve join requests {status} ✅")

# ===================== /edit =====================
@app.on_message(filters.command("edit") & filters.group)
async def edit_guardian(client, message: Message):
    await message.reply_text("Edit guardian activated. Future edits will be auto-deleted (placeholder).")

# ===================== /pretender =====================
@app.on_message(filters.command("pretender") & filters.group)
async def check_pretender(client, message: Message):
    async for msg in client.iter_history(message.chat.id, limit=5):
        if msg.from_user and msg.from_user.id == message.from_user.id:
            await message.reply_text(f"Last messages:\n{msg.text or 'No text content'}")
            break

# ===================== /ghelp =====================
@app.on_message(filters.command("ghelp"))
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
/vclogger on/off - VC logs
/autoapprove - Toggle auto approve join requests
/edit - Auto delete edits
/pretender - Last 5 messages of a user

Use /ghelp to see all security commands.
"""
    await message.reply_text(help_text)
