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

def process_caption_command(command, caption_text):
    """
    Process the /caption command to delete and replace words in the caption.

    Args:
        command (str): The /caption command string containing delete and replace instructions.
        caption_text (str): The original caption text to process.

    Returns:
        str: The modified caption text after processing.
    """
    if not command.startswith("/caption"):
        raise ValueError("Invalid command format. Command must start with '/caption'.")

    # Extract delete and replace parts
    try:
        command_parts = command[len("/caption "):].split(" replace|")
        delete_part = command_parts[0].replace("delete:", "").strip()
        replace_part = command_parts[1] if len(command_parts) > 1 else ""

        # Process delete
        if delete_part:
            words_to_delete = delete_part.split(",")
            for word in words_to_delete:
                caption_text = caption_text.replace(word, "")

        # Process replace
        if replace_part:
            replace_pairs = replace_part.split(",")
            for pair in replace_pairs:
                word, replacement = pair.split(":")
                caption_text = caption_text.replace(word, replacement)

        # Return the processed caption
        return caption_text.strip()

    except Exception as e:
        raise ValueError(f"Error processing command: {e}")


# Example usage
command = "/caption delete:word1,word2 replace|word1:replace1,word3:replace3"
caption_text = "word1 is here, word2 is there, and word3 is everywhere."

result = process_caption_command(command, caption_text)
print(result)

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
