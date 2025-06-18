import json
import requests
import time
import os

from pyrogram import Client, filters
from pyrogram.types import Message

from YMusic.utils.formaters import progress
from config import PREFIX, RPREFIX
from YMusic.misc import SUDOERS

PLAY_COMMAND = ["svn", "saavn"]

@Client.on_message(filters.command(PLAY_COMMAND, [PREFIX, RPREFIX]) & filters.me)
async def saavn(client: Client, message: Message):
    start_time = time.time()
    chat_id = message.chat.id
    
    # Extract query
    if len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage:</b> <code>{PREFIX}{PLAY_COMMAND[0]} [song name]</code>"
        )
        return

    ms = await message.edit_text(f"<code>Searching for {query} on Saavn...</code>")
    
    try:
        response = requests.get(
            f"https://rsjiprivate-api.vercel.app/api/search/songs?query={query}",
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        await ms.edit_text(f"<code>Error searching Saavn: {str(e)}</code>")
        return

    if result.get("success") and result.get("data", {}).get("results"):
        try:
            song_details = result["data"]["results"][0]
            song_name = song_details["name"]
            thumb = song_details["image"][1]["url"]
            song_url = song_details["downloadUrl"][-1]["url"]

            await ms.edit_text(f"<code>Found: {song_name}</code>\nDownloading...")
            
            # Download thumbnail
            with open(f"{song_name}.jpg", "wb") as f:
                f.write(requests.get(thumb).content)

            # Download song
            with open(f"{song_name}.mp3", "wb") as f:
                f.write(requests.get(song_url).content)

            await ms.edit_text(f"<code>Uploading {song_name}...</code>")
            c_time = time.time()
            
            # Upload with progress
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
            await ms.edit_text(f"<code>Error processing song: {str(e)}</code>")
        finally:
            # Cleanup files
            if os.path.exists(f"{song_name}.jpg"):
                os.remove(f"{song_name}.jpg")
            if os.path.exists(f"{song_name}.mp3"):
                os.remove(f"{song_name}.mp3")
    else:
        await ms.edit_text(f"<code>No results found for {query}</code>")


@Client.on_message(filters.command(PLAY_COMMAND, [PREFIX, RPREFIX]) & SUDOERS)
async def _raPlay(_, message):
    start_time = time.time()
    if (message.reply_to_message) is not None:
        await message.reply_text("Currently this is not supported")
    elif (len(message.command)) < 3:
        await message.reply_text("You Forgot To Pass An Argument")
    else:
        m = await message.reply_text("Searching Your Query...")
        query = message.text.split(" ", 2)[2]
        msg_id = message.text.split(" ", 2)[1]
        
        try:
            response = requests.get(
                f"https://rsjiprivate-api.vercel.app/api/search/songs?query={query}",
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            await m.edit_text(f"<code>Error searching Saavn: {str(e)}</code>")
            return

        if result.get("success") and result.get("data", {}).get("results"):
            song_details = result["data"]["results"][0]
            song_name = song_details["name"]
            song_url = song_details["downloadUrl"][-1]["url"]

            await m.edit_text("Downloading...")
            with open(f"{song_name}.mp3", "wb") as f:
                f.write(requests.get(song_url).content)

            Status, Text = await userbot.playAudio(msg_id, f"{song_name}.mp3")
            if Status == False:
                await m.edit(Text)
            
            finish_time = time.time()
            total_time_taken = str(int(finish_time - start_time)) + "s"
            await m.edit(
                f"Playing your song\n\nSongName:- {song_name}\nTime taken to play:- {total_time_taken}\n\n Powered by: @astrousersbot"
            )
            
            if os.path.exists(f"{song_name}.mp3"):
                os.remove(f"{song_name}.mp3")
        else:
            await m.edit_text(f"<code>No results found for {query}</code>")
