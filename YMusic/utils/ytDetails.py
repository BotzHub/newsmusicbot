import aiohttp
from pytubefix import Search, YouTube as pyYouTube, Playlist
from urllib.parse import urlparse, parse_qs

API_URL = "https://api.nekorinn.my.id/"


def searchYt(query, is_videoId=False):
    raise Exception("This request was detected as a bot")
    query = str(query)
    if is_videoId:
        video = pyYouTube(f"https://www.youtube.com/watch?v={query}")
        title = video.title
        duration = video.length
        link = video.watch_url
        return title, duration, link
    else:
        videosResult = Search(query)
        for Result in videosResult.videos:
            title = Result.title
            duration = Result.length
            link = Result.watch_url
            return title, duration, link
    return None, None, None


async def search_api(query, is_videoId=False, video=False):
    query = str(query)
    async with aiohttp.ClientSession() as session:
        if is_videoId:
            async with session.get(
                f"{API_URL}downloader/savetube?url=https://youtube.com/watch?v={query}&format={'720' if video else 'mp3'}"
            ) as response:
                data = await response.json()
                print(data)
                if data["status"] and data["statusCode"] == 200:
                    result = data["result"]
                    title = result["title"]
                    duration = result["duration"]
                    link = result["download"]
                    return title, duration, link
        else:
            async with session.get(
                f"{API_URL}downloader/spotifyplay?q={query}", ssl=False
            ) as response:
                data = await response.json()
                print(data)
                if data["status"] and data["statusCode"] == 200:
                    result = data["result"]
                    title = result["metadata"]["title"]
                    duration = result["metadata"]["duration"]
                    link = result["downloadUrl"]
                    return title, duration, link
                else:
                    async with session.get(
                        f"https://node01.dlapi.app/api/downloader/ytplay-savetube?q={query}"
                    ) as response:
                        data = await response.json()
                        print(data)
                        if data["status"] and data["statusCode"] == 200:
                            result = data["result"]
                            title = result["metadata"]["title"]
                            duration = result["metadata"]["duration"]
                            link = result["downloadUrl"]
                            return title, duration, link

    return None, None, None


def searchPlaylist(query):
    query = str(query)
    playlistResult = Playlist(query)
    title = playlistResult.title
    duration = playlistResult.length
    return title, duration


def extract_playlist_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    playlist_id = query_params.get("list", [None])[0]
    return playlist_id


def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        video_id = parsed_url.path[1:]
    else:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v", [None])[0]
    return video_id
