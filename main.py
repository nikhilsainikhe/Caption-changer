import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL")

app = Client("caption_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

delete_words = set()
replace_dict = {}

ADMIN_USERS = set()  # Will fill dynamically


def clean_caption(caption: str) -> str:
    if not caption:
        return caption
    for word in delete_words:
        caption = caption.replace(word, "")
    for old, new in replace_dict.items():
        caption = caption.replace(old, new)
    return caption.strip()


async def check_subscription(user_id):
    try:
        member = await app.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply("Bot is active. Admins can use /setdelete and /setreplace to configure word filters.")


@app.on_message(filters.command("setdelete") & filters.user(lambda _, __, msg: msg.from_user.id in ADMIN_USERS))
async def set_delete_words(_, message: Message):
    global delete_words
    words = message.text.split(None, 1)
    if len(words) < 2:
        await message.reply("Usage: /setdelete word1,word2,word3")
        return
    delete_words = set(w.strip() for w in words[1].split(","))
    await message.reply(f"Deleted words set to: {', '.join(delete_words)}")


@app.on_message(filters.command("setreplace") & filters.user(lambda _, __, msg: msg.from_user.id in ADMIN_USERS))
async def set_replace_words(_, message: Message):
    global replace_dict
    parts = message.text.split(None, 1)
    if len(parts) < 2:
        await message.reply("Usage: /setreplace old1:new1,old2:new2")
        return
    replace_dict.clear()
    entries = parts[1].split(",")
    for entry in entries:
        if ":" in entry:
            old, new = entry.split(":", 1)
            replace_dict[old.strip()] = new.strip()
    await message.reply(f"Replacement rules set: {replace_dict}")


@app.on_message(filters.media)
async def handle_media(_, message: Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        join_btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join Channel", url=f"https://t.me/+MnxII-5_qqY5ZjE1")]]
        )
        await message.reply("Please join the required channel to use this bot.", reply_markup=join_btn)
        return

    # Edit caption if present
    caption = message.caption
    new_caption = clean_caption(caption)

    if new_caption != caption:
        await message.copy(
            chat_id=message.chat.id,
            caption=new_caption,
            caption_entities=message.caption_entities
        )
        await message.delete()


@app.on_message(filters.command("id"))
async def get_id(_, message: Message):
    await message.reply(f"Your ID: `{message.from_user.id}`")
    ADMIN_USERS.add(message.from_user.id)


app.run()
print("Bot is running...")
