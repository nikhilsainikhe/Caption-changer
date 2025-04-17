from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from logs import logging
import os
import asyncio
from aiohttp import ClientSession, web

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("caption-changer-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Define aiohttp routes
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("https://text-leech-bot-for-render.onrender.com/")

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def start_bot():
    await bot.start()
    print("Bot is up and running")

async def stop_bot():
    await bot.stop()

async def main():
    if WEBHOOK:
        # Start the web server
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        site = web.TCPSite(app_runner, "0.0.0.0", PORT)
        await site.start()
        print(f"Web server started on port {PORT}")

    # Start the bot
    await start_bot()

    # Keep the program running
    try:
        while True:
            await bot.polling()  # Run forever, or until interrupted
    except (KeyboardInterrupt, SystemExit):
        await stop_bot()
    

async def start_bot():
    await bot.start()
    print("Bot is up and running")

async def stop_bot():
    await bot.stop()
    
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
if __name__ == "__main__":
    asyncio.run(main())
