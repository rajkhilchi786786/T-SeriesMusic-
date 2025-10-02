# © 2025 Nand Yaduwanshi (@NoxxOP)
# VC Logger Plugin for ShrutiMusic

from pyrogram import filters
from pyrogram.types import Message
from ShrutiMusic import app

# Dictionary to track VC logger status per chat
VC_LOGGER_STATUS = {}

# ===================== /vclogger =====================
@app.on_message(filters.command("vclogger") & filters.group)
async def toggle_vclogger(client, message: Message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        status = VC_LOGGER_STATUS.get(chat_id, False)
        return await message.reply_text(
            f"🔎 Current VC Logger status: `{status}`\n\nUsage:\n`/vclogger on` or `/vclogger off`"
        )

    arg = message.command[1].lower()
    if arg in ["on", "yes", "true"]:
        VC_LOGGER_STATUS[chat_id] = True
        await message.reply_text("✅ VC logging ENABLED (Current State: `True`)")
    elif arg in ["off", "no", "false"]:
        VC_LOGGER_STATUS[chat_id] = False
        await message.reply_text("❌ VC logging DISABLED (Current State: `False`)")
    else:
        await message.reply_text("⚠️ Invalid argument! Use `/vclogger on` or `/vclogger off`")

# ===================== VC Join Event =====================
@app.on_chat_member_updated()
async def vc_join_leave(client, update):
    try:
        chat_id = update.chat.id
        if not VC_LOGGER_STATUS.get(chat_id, False):
            return

        old = update.old_chat_member
        new = update.new_chat_member

        user = new.user.mention

        # User joined VC
        if old and old.is_member and old.status != "left" and new.status == "member":
            if new.is_member and new.can_manage_voice_chats:
                await client.send_message(chat_id, f"🎵 {user} has joined – let's rock this vibe! 🔥")

        # User left VC
        if old and old.is_member and new.status == "left":
            await client.send_message(chat_id, f"👋 {user} left the VC – hope to see you back soon! 🌟")

    except Exception as e:
        print(f"[VCLOGGER ERROR] {e}")