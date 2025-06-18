import json
import requests
import time
import os

from pyrogram import Client, filters
from pyrogram.types import Message

from YMusic.utils.formaters import progress
from config import PREFIX, RPREFIX

@Client.on_message(filters.command(["svn", "saavn"], prefixes=[PREFIX, RPREFIX]) & filters.me)
async def saavn(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage:</b> <code>{PREFIX}svn [song name]</code>"
        )
        return

    ms = await message.edit_text(f"<code>Searching for {query} on Saavn...</code>")
    try:
        response = requests.get(
            f"https://rsjiprivate-api.vercel.app/api/search/songs?query={query}"
        )
        result = json.loads(response.text)
    except Exception as e:
        await ms.edit_text(f"<code>Error: {str(e)}</code>")
        return

    if result.get("success") and result.get("data", {}).get("results"):
        song_details = result["data"]["results"][0]
        song_name = song_details["name"]
        thumb = song_details["image"][1]["url"]
        song_url = song_details["downloadUrl"][-1]["url"]

        await ms.edit_text(f"<code>Found: {song_name}</code>\nDownloading...")
        try:
            with open(f"{song_name}.jpg", "wb") as f:
                f.write(requests.get(thumb).content)

            song = requests.get(song_url)
            with open(f"{song_name}.mp3", "wb") as f:
                f.write(song.content)

            await ms.edit_text(f"<code>Uploading {song_name}...</code>")
            c_time = time.time()
            await client.send_audio(
                chat_id,
                f"{song_name}.mp3",
                caption=f"<b>🎵 Song:</b> {song_name}",
                progress=progress,
                progress_args=(ms, c_time, f"`Uploading {song_name}...`"),
                thumb=f"{song_name}.jpg",
            )
            await ms.delete()
        except Exception as e:
            await ms.edit_text(f"<code>Error: {str(e)}</code>")
        finally:
            if os.path.exists(f"{song_name}.jpg"):
                os.remove(f"{song_name}.jpg")
            if os.path.exists(f"{song_name}.mp3"):
                os.remove(f"{song_name}.mp3")
    else:
        await ms.edit_text(f"<code>No results found for {query}</code>")
