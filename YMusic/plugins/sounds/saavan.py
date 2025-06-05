import json
import requests
import time
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from YMusic.core import userbot
from YMusic.misc import SUDOERS

PREFIX = "!"  # Replace with your actual prefix

@Client.on_message(filters.command(["svn", "saavn"], PREFIX) & filters.me)
async def saavn(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage: </b><code>{PREFIX}svn [song name to search & download|upload]</code>"
        )
        return
    
    ms = await message.edit_text(f"<code>Searching for {query} on saavn</code>")
    response = requests.get(
        f"https://rsjiprivate-api.vercel.app/api/search/songs?query={query}"
    )

    result = json.loads(response.text)

    if result["success"] and result["data"]["results"]:
        song_details = result["data"]["results"][0]
        song_name = song_details["name"]
        thumb = song_details["image"][1]["url"]
        song_url = song_details["downloadUrl"][-1]["url"]

        await ms.edit_text(f"<code>Found: {song_name} </code>\n Downloading...")
        
        # Download the song
        song = requests.get(song_url)
        with open(f"{song_name}.mp3", "wb") as f:
            f.write(song.content)

        await ms.edit_text(f"<code>Uploading {song_name}... </code>")
        
        # Play the song using your userbot
        Status, Text = await userbot.playAudio(chat_id, f"{song_name}.mp3")
        if Status == False:
            await ms.edit(Text)
        else:
            await ms.edit(
                f"Playing your song\n\nSongName:- {song_name}\n\n Powered by: @astrousersbot",
                disable_web_page_preview=True,
            )
        
        # Clean up
        if os.path.exists(f"{song_name}.mp3"):
            os.remove(f"{song_name}.mp3")
    else:
        await ms.edit_text(f"<code>No results found for {query}</code>")
