from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL")

app = Client("caption-changer-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

words_to_delete = []
words_to_replace = {}

async def is_admin(client, message: Message):
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return chat_member.status in ["administrator", "creator"]
    except:
        return False

@app.on_message(filters.command("setdelete"))
async def set_delete_words(client, message: Message):
    global words_to_delete
    if message.from_user and await is_admin(client, message):
        words_to_delete = message.text.split()[1:]
        await message.reply(f"Words to delete set: {words_to_delete}")
    else:
        await message.reply("Only admins can use this command.")

@app.on_message(filters.command("setreplace"))
async def set_replace_words(client, message: Message):
    global words_to_replace
    if message.from_user and await is_admin(client, message):
        try:
            parts = message.text.split(None, 2)[1].split("|")
            key, val = parts[0].strip(), parts[1].strip()
            words_to_replace[key] = val
            await message.reply(f"Replacement set: '{key}' -> '{val}'")
        except:
            await message.reply("Format: /setreplace old|new")
    else:
        await message.reply("Only admins can use this command.")

@app.on_message(filters.command("reset"))
async def reset_filters(client, message: Message):
    global words_to_delete, words_to_replace
    if message.from_user and await is_admin(client, message):
        words_to_delete = []
        words_to_replace = {}
        await message.reply("Filters have been reset.")
    else:
        await message.reply("Only admins can use this command.")

@app.on_message(filters.media)
async def handle_media(client, message: Message):
    user_id = message.from_user.id if message.from_user else (
        message.sender_chat.id if message.sender_chat else None
    )
    if not user_id:
        return

    if FORCE_SUB_CHANNEL and not await is_subscribed(client, user_id):
        await message.reply(f"Please join our channel first: {FORCE_SUB_CHANNEL}")
        return

    caption = message.caption or ""
    for word in words_to_delete:
        caption = caption.replace(word, "")
    for old, new in words_to_replace.items():
        caption = caption.replace(old, new)

    try:
        await message.copy(chat_id=message.chat.id, caption=caption)
        await message.delete()
    except:
        pass

async def is_subscribed(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

print("Bot is running...")
app.run()
