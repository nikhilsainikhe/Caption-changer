from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("caption-changer-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

words_to_delete = []
words_to_replace = {}

@app.on_message(filters.command("setdelete"))
async def set_delete_words(client, message: Message):
    global words_to_delete
    words_to_delete = message.text.split()[1:]
    await message.reply(f"Words to delete set: {words_to_delete}")

@app.on_message(filters.command("setreplace"))
async def set_replace_words(client, message: Message):
    global words_to_replace
    try:
        parts = message.text.split(None, 2)[1].split("|")
        key, val = parts[0].strip(), parts[1].strip()
        words_to_replace[key] = val
        await message.reply(f"Replacement set: '{key}' -> '{val}'")
    except:
        await message.reply("Format: /setreplace old|new")

@app.on_message(filters.command("reset"))
async def reset_filters(client, message: Message):
    global words_to_delete, words_to_replace
    words_to_delete = []
    words_to_replace = {}
    await message.reply("Filters have been reset.")

@app.on_message(filters.media)
async def handle_media(client, message: Message):
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

print("Bot is running...")
app.run()
