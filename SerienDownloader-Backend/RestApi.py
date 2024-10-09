import base64
import json
import os
import threading
import time

import requests
import re
import configparser
import yt_dlp
from bs4 import BeautifulSoup
from flask import Flask, jsonify, make_response, request, flash, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from queue import Queue
from enum import Enum, auto
from deprecated import deprecated

downloadQueue = Queue()
downloadSeriesQueue = Queue()

# downloadQueue = []
currentAnime = ""
currentSeason = ""
currentEpisode = ""
running = True
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.optionxform = str
path = os.path.dirname(__file__) + "/"
config.read(path + ".env", encoding='utf-8')
downloadPath = config.get("ENV", "downloadPath")
proxy_cfg = config.get("ENV", "proxy")
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, resources={r"/*": {"origins": "*"}})

proxy_header = dict(http=proxy_cfg, https=proxy_cfg) if proxy_cfg != "None" else None


class StreamProvider(Enum):
    AniWorld: int = 0
    SerienStream: int = 1


@app.route("/getStreamProvider", methods=['GET'])
def get_streaming_provider():
    stream_provider_list = []
    for stream in StreamProvider:
        stream_provider_list.append({"title": stream.name, "id": stream.value})
    return jsonify(stream_provider_list)


@app.route("/updateStreamList", methods=['GET'])
def update_stream_list():
    stream_provider = request.args.get('streamProvider')
    try:
        stream_provider_id = int(stream_provider)
        stream_provider_enum = StreamProvider(stream_provider_id)
    except:
        return jsonify({"Error": "Invalid Stream Provider"})

    return jsonify(create_stream_list_as_json(stream_provider_enum))


@app.route("/updateStreamThumbnailList", methods=['GET'])
def update_stream_thumbnail_list():
    stream_provider = request.args.get('streamProvider')
    try:
        stream_provider_id = int(stream_provider)
        stream_provider_enum = StreamProvider(stream_provider_id)
    except:
        return jsonify({"Error": "Invalid Stream Provider"})

    return jsonify(write_thumbnail_list(stream_provider_enum))


@app.route("/failedDownloads", methods=['GET'])
def get_failed_downloads():
    return jsonify(failed_downloads())


@deprecated(reason="There is a new and better funktion for this called get_stream_list")
@app.route('/animeList', methods=['GET'])
def get_anime_list():
    return jsonify(read_anime_list_json())


@app.route('/streamList', methods=['GET'])
def get_stream_list():
    stream_provider = request.args.get('streamProvider')
    if stream_provider is None:
        return jsonify({"Error": "No streaming provider set"})
    try:
        stream_provider_id = int(stream_provider)
        stream_provider = StreamProvider(stream_provider_id)
    except:
        return jsonify({"Error": "Invalid Stream Provider"})
    return jsonify(read_stream_list_json(stream_provider))


@app.route('/getSeasonsFromSeries', methods=['POST'])
def get_seasons_from_series_request():
    data = request.json
    stream_provider = data['streamProvider']
    series_name = data['series_name']
    try:
        stream_provider_id = int(stream_provider)
        stream_provider = StreamProvider(stream_provider_id)
    except:
        return jsonify({"Error": "Invalid Stream Provider"})
    return jsonify(get_seasons_from_series(series_name, stream_provider))


@deprecated(reason="There is a new and better funktion for this called get_seasons_from_series")
@app.route('/getSeasonsFromAnime', methods=['POST'])
def get_seasons_from_anime():
    data = request.json
    anime_name = data['anime_name']
    return jsonify(get_seasons(anime_name))


@app.route('/getEpisodesFromAnime', methods=['POST'])
def get_episodes_from_anime():
    data = request.json
    season_link = data['season_link']
    return jsonify(get_episodes(season_link))


@app.route('/getAllQueueSeries', methods=['GET'])
def get_all_queue_series():
    list = []
    for i in range(0, downloadSeriesQueue.qsize()):
        list.append(downloadSeriesQueue.queue[i])
    return list

@app.route('/getAllQueue', methods=['GET'])
def get_all_queue():
    list = []
    for i in range(0, downloadQueue.qsize()):
        list.append(downloadQueue.queue[i])
    return list


@app.route('/downloadSeries', methods=['POST'])
def download_series():
    data = request.json
    season_link = data['season_link']
    season = data['season']
    series = data['series']
    stream_provider = data['streamProvider']
    try:
        stream_provider_id = int(stream_provider)
        stream_provider = StreamProvider(stream_provider_id)
    except:
        return jsonify({"Error": "Invalid Stream Provider"})
    for episode in get_episodes_from_series(season_link, stream_provider):
        downloadSeriesQueue.put({"series": series, "season": season, "episode": episode['text'], "plex_name": True,
                                 "episode_href": episode['href'], "stream_provider": stream_provider_id})
    return "Ok"


@app.route('/downloadAnime', methods=['POST'])
def download_anime():
    data = request.json
    season_link = data['season_link']
    season = data['season']
    anime = data['anime']
    for episode in get_episodes(season_link):
        downloadQueue.put({"anime": anime, "season": season, "episode": episode['text'], "plex_name": True,
                           "episode_href": episode['href']})
    return "Ok"


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@app.route('/retryFailedDownloadSeries', methods=['GET'])
def retry_failed_download_series():
    for f in failed_downloads():
        downloadSeriesQueue.put(f)
    clear_failed_downloads()
    update_download_queue_for_front_end()
    return "Ok"

@app.route('/retryFailedDownloads', methods=['GET'])
def retry_failed_downloads():
    for f in failed_downloads():
        downloadQueue.put(f)
    clear_failed_downloads()
    update_download_queue_for_front_end()
    return "Ok"


def clear_failed_downloads():
    with(open("backupFailedDownloads.json", "w", encoding="utf-8") as f):
        f.write(json.dumps(failed_downloads(), ensure_ascii=False))
    with(open("failedDownloads.json", "w", encoding="utf-8") as f):
        f.write("[]")


def add_failed_download(failed_download):
    currentFile = failed_downloads()
    if not currentFile.__contains__(failed_download):
        currentFile.append(failed_download)
        with(open("failedDownloads.json", "w", encoding="utf-8") as f):
            f.write(json.dumps(currentFile, ensure_ascii=False))
    else:
        print("Already added to failed list")


def failed_downloads():
    if os.path.exists("failedDownloads.json"):
        with(open("failedDownloads.json", encoding='utf-8') as r):
            return json.load(r)
    else:
        with(open("failedDownloads.json", "w", encoding="utf-8") as f):
            f.write("[]")
        return []


def redirect_to_vidoza(redirect_url: str):
    stream_url = requests.get(redirect_url, allow_redirects=True, proxies=proxy_header).url
    return stream_url

def extract_url_from_js(js_content):
    url_regex = r'window\.location\.href\s*=\s*[\'"]([^\'"]+)[\'"]'
    match = re.search(url_regex, js_content)
    if match:
        return match.group(1)
    return None

def get_m3u8_link(redirect_url: str):
    redirect_content = requests.get(redirect_url, allow_redirects=True).text
    redirect_url2 = extract_url_from_js(redirect_content)
    if redirect_url2 is not None:
        redirect_content = requests.get(redirect_url2, allow_redirects=True).text
    try:
        script_regex = r"'hls':\s*'([^']+?)'"
        match = re.search(script_regex, redirect_content)
        url = str(match.group(1))
        url = base64.b64decode(url).decode('utf-8')
        return url
    except:
        try:
            soup = BeautifulSoup(redirect_content.content, "html.parser")
            jsSource = soup.select("script")[-4].text.strip()
            slice_start = jsSource.find("'") + 1
            jsonText = jsSource[slice_start:jsSource.find("'", slice_start)]
            jsonText = base64.b64decode()
            source_json = json.loads(jsonText[::-1])  # parsing the JSON
            return source_json["file"]
        except:
            try:
                soup = BeautifulSoup(redirect_content.content, "html.parser")
                jsSource = soup.select("script")[-4].text.strip()
                slice_start = jsSource.find("'") + 1
                jsonText = jsSource[slice_start:jsSource.find("'", slice_start)]
                jsonText = base64.b64decode()
                source_json = json.loads(jsonText[::-1])  # parsing the JSON
                return source_json["file"]
            except:
                try:
                    script_regex = r"'hls':\s*'([^']+?)'"
                    match = re.search(script_regex, redirect_content)
                    return match.group(1)
                except:
                    return False
                    print("Nothing worked")


def get_third_stream_of_episode(episode_url: str):
    anime = requests.get(episode_url, proxies=proxy_header)
    soup = BeautifulSoup(anime.content, "html.parser")
    visible_li = soup.select("ul.row li:not([style*='display: none'])")
    return visible_li[2].get("data-link-target")


def get_fist_stream_of_episode(episode_url: str):
    anime = requests.get(episode_url, proxies=proxy_header)
    soup = BeautifulSoup(anime.content, "html.parser")
    first_visible_li = soup.select_one("ul.row li:not([style*='display: none'])")
    return first_visible_li.get("data-link-target")

def get_all_streams_of_episode(episode_url: str):
    anime = requests.get(episode_url, proxies=proxy_header)
    soup = BeautifulSoup(anime.content, "html.parser")
    visible_li = soup.select_one("ul.row li:not([style*='display: none'])")
    result = []
    for stream_button in visible_li:
        result.append(stream_button.get("data-link-target"))
    return result


def progress_hook(d):
    if d['status'] == 'downloading':
        percentage = d['_percent_str']
        download_speed = d['_speed_str']
        estimated_time = d['_eta_str']
        socketio.emit('broadcast_message', {
            'percentage': int(str(percentage).split(".")[0]), "download_speed": str(download_speed),
            "estimated_time": str(estimated_time), "animeTitle": currentAnime, "season": currentSeason,
            "episode": currentEpisode})


def update_download_queue_for_front_end():
    socketio.emit('broadcast_message', {'update': "now"})


def get_download_link(url_header:str, episode_href: str, episode_url: str):
    for redirect_link in get_all_streams_of_episode(episode_url):
        download_link = get_m3u8_link(f"{url_header}{redirect_link}")
        if not download_link:
            download_link = redirect_to_vidoza(f"{url_header}{redirect_link}")
        return download_link

def download_series_loop():
    while running:
        if not downloadSeriesQueue.empty():
            e = downloadSeriesQueue.get()
            try:
                series = e['series']
                episode_href = e['episode_href']
                season = e['season']
                episode = e['episode']
                plex_name = e['plex_name']
                stream_provider = e['stream_provider']
                try:
                    stream_provider_id = int(stream_provider)
                    stream_provider = StreamProvider(stream_provider_id)
                except:
                    return jsonify({"Error": "Invalid Stream Provider"})
                download_link = ""
                if stream_provider == StreamProvider.AniWorld:
                    aniword_redirect_link = get_fist_stream_of_episode(f"https://aniworld.to{episode_href}")
                    download_link = get_m3u8_link(f"https://aniworld.to{aniword_redirect_link}")
                    if not download_link:
                        print("Failed to download from Voe")
                        aniword_redirect_link = get_third_stream_of_episode(f"https://aniworld.to{episode_href}")
                        download_link = redirect_to_vidoza(f"https://aniworld.to{aniword_redirect_link}")
                    print(aniword_redirect_link)
                if stream_provider == StreamProvider.SerienStream:
                    serien_stream_redirect_link = get_fist_stream_of_episode(f"https://s.to{episode_href}")
                    download_link = get_m3u8_link(f"https://s.to{serien_stream_redirect_link}")
                    if not download_link:
                        print("Failed to download from Voe")
                        serien_stream_redirect_link = get_third_stream_of_episode(f"https://s.to{episode_href}")
                        download_link = redirect_to_vidoza(f"https://s.to{serien_stream_redirect_link}")
                    print(serien_stream_redirect_link)
                if not os.path.exists(f'{downloadPath}{series}'):
                    os.mkdir(f'{downloadPath}{series}')
                if not os.path.exists(f'{downloadPath}{series}/Season {season}'):
                    os.mkdir(f'{downloadPath}{series}/Season {season}')
                file_name = f'{downloadPath}{series}/Season {season}/{series} - s{season}e{episode}.mp4' if plex_name else f'{series} - Season {season} - Episode {episode}.mp4'
                if not os.path.isfile(file_name):
                    yt_opts = {
                        'verbose': True,
                        'color': "never",
                        'force_keyframes_at_cuts': True,
                        'outtmpl': file_name,
                        "progress_hooks": [progress_hook]
                    }

                    with yt_dlp.YoutubeDL(yt_opts) as ydl:
                        global currentAnime
                        global currentSeason
                        global currentEpisode
                        currentAnime = series
                        currentSeason = season
                        currentEpisode = episode
                        ydl.download(download_link)
                downloadSeriesQueue.task_done()
                update_download_queue_for_front_end()
            except Exception as a:
                print(a)
                add_failed_download(e)
                downloadSeriesQueue.task_done()
                print("Something went wrong")
                update_download_queue_for_front_end()


def download_loop():
    while running:
        if not downloadQueue.empty():
            e = downloadQueue.get()
            try:
                anime = e['anime']
                episode_href = e['episode_href']
                season = e['season']
                episode = e['episode']
                aniword_redirect_link = get_fist_stream_of_episode(f"https://aniworld.to{episode_href}")
                download_link = get_m3u8_link(f"https://aniworld.to{aniword_redirect_link}")
                if not download_link:
                    print("Failed to download from Voe")
                    aniword_redirect_link = get_third_stream_of_episode(f"https://aniworld.to{episode_href}")
                    download_link = redirect_to_vidoza(f"https://aniworld.to{aniword_redirect_link}")
                print(aniword_redirect_link)
                if not os.path.exists(f'{downloadPath}{anime}'):
                    os.mkdir(f'{downloadPath}{anime}')
                if not os.path.exists(f'{downloadPath}{anime}/Season {season}'):
                    os.mkdir(f'{downloadPath}{anime}/Season {season}')
                file_name = f'{downloadPath}{anime}/Season {season}/{anime} - s{season}e{episode}.mp4' if plex_name else f'{anime} - Season {season} - Episode {episode}.mp4'
                if not os.path.isfile(file_name):
                    yt_opts = {
                        'verbose': True,
                        'color': "never",
                        'force_keyframes_at_cuts': True,
                        'outtmpl': file_name,
                        "progress_hooks": [progress_hook]
                    }

                    with yt_dlp.YoutubeDL(yt_opts) as ydl:
                        global currentAnime
                        global currentSeason
                        global currentEpisode
                        currentAnime = anime
                        currentSeason = season
                        currentEpisode = episode
                        ydl.download(download_link)
                downloadQueue.task_done()
                update_download_queue_for_front_end()
            except Exception as a:
                print(a)
                add_failed_download(e)
                downloadQueue.task_done()
                print("Something went wrong")
                update_download_queue_for_front_end()


def get_episodes_from_aniworld(anime_season_url: str):
    anime = requests.get(f"https://aniworld.to{anime_season_url}", proxies=proxy_header)
    soup = BeautifulSoup(anime.content, "html.parser")
    all_uls = soup.select("div.hosterSiteDirectNav#stream ul")
    seasons = all_uls[1]
    alist = []
    for li in seasons.find_all("li")[1:]:
        a_tag = li.find("a")
        if a_tag:
            item = {
                "text": a_tag.text.strip(),
                "href": a_tag.get("href", None),
            }
            alist.append(item)

    return alist


def get_episodes_from_serien_stream(series_season_url: str):
    series = requests.get(f"https://s.to{series_season_url}", proxies=proxy_header)
    soup = BeautifulSoup(series.content, "html.parser")
    all_uls = soup.select("div.hosterSiteDirectNav#stream ul")
    seasons = all_uls[1]
    alist = []
    for li in seasons.find_all("li")[1:]:
        a_tag = li.find("a")
        if a_tag:
            item = {
                "text": a_tag.text.strip(),
                "href": a_tag.get("href", None),
            }
            alist.append(item)

    return alist


def get_episodes_from_series(series_season_url: str, provider: StreamProvider):
    if provider == StreamProvider.AniWorld:
        return get_episodes_from_aniworld(series_season_url)
    if provider == StreamProvider.SerienStream:
        return get_episodes_from_serien_stream(series_season_url)
    else:
        return {"Error": "Invalid StreamProvider!"}


@deprecated(reason="There is a new and better funktion for this called get_seasons_from_series")
def get_episodes(anime_season_url: str):
    anime = requests.get(f"https://aniworld.to{anime_season_url}", proxies=proxy_header)
    soup = BeautifulSoup(anime.content, "html.parser")
    all_uls = soup.select("div.hosterSiteDirectNav#stream ul")
    seasons = all_uls[1]
    alist = []
    for li in seasons.find_all("li")[1:]:
        a_tag = li.find("a")
        if a_tag:
            item = {
                "text": a_tag.text.strip(),
                "href": a_tag.get("href", None),
            }
            alist.append(item)

    return alist


def get_seasons_from_anime_on_aniworld(anime_name: str):
    anime_json = {}
    for anime in read_stream_list_json(StreamProvider.AniWorld):
        if anime['text'] == anime_name:
            anime_json = anime
    anime = requests.get(f"https://aniworld.to{anime_json['href']}", proxies=proxy_header)
    soup = BeautifulSoup(anime.content, "html.parser")
    all_uls = soup.select("div.hosterSiteDirectNav#stream ul")
    seasons = all_uls[0]
    alist = []
    for li in seasons.find_all("li")[1:]:
        a_tag = li.find("a")
        if a_tag:
            item = {
                "text": a_tag.text.strip(),
                "href": a_tag.get("href", None),
            }
            alist.append(item)

    return alist


def get_seasons_from_series_on_serien_stream(series_name: str):
    anime_json = {}
    for anime in read_stream_list_json(StreamProvider.SerienStream):
        if anime['text'] == series_name:
            anime_json = anime
    serie = requests.get(f"https://s.to{anime_json['href']}", proxies=proxy_header)
    soup = BeautifulSoup(serie.content, "html.parser")
    all_uls = soup.select("div.hosterSiteDirectNav#stream ul")
    seasons = all_uls[0]
    alist = []
    for li in seasons.find_all("li")[1:]:
        a_tag = li.find("a")
        if a_tag:
            item = {
                "text": a_tag.text.strip(),
                "href": a_tag.get("href", None),
            }
            alist.append(item)

    return alist


def get_seasons_from_series(series_name: str, provider: StreamProvider):
    if provider == StreamProvider.AniWorld:
        return get_seasons_from_anime_on_aniworld(series_name)
    if provider == StreamProvider.SerienStream:
        return get_seasons_from_series_on_serien_stream(series_name)
    else:
        return {"Error": "Invalid StreamProvider!"}


@deprecated(reason="There is a new and better funktion for this called get_seasons_from_series")
def get_seasons(anime_name: str):
    anime_json = {}
    for anime in read_anime_list_json():
        if anime['text'] == anime_name:
            anime_json = anime
    anime = requests.get(f"https://aniworld.to{anime_json['href']}", proxies=proxy_header)
    soup = BeautifulSoup(anime.content, "html.parser")
    all_uls = soup.select("div.hosterSiteDirectNav#stream ul")
    seasons = all_uls[0]
    alist = []
    for li in seasons.find_all("li")[1:]:
        a_tag = li.find("a")
        if a_tag:
            item = {
                "text": a_tag.text.strip(),
                "href": a_tag.get("href", None),
            }
            alist.append(item)

    return alist


def write_thumbnail_list(provider: StreamProvider):
    if provider == StreamProvider.AniWorld:
        new_img_list = update_anime_thumbnail_list()
        anime_list = read_stream_list_json(StreamProvider.AniWorld)
        for new_anime in new_img_list:
            anime_list.append(new_anime)
        with open("animeslistNew.json", "w", encoding='utf-8') as r:
            r.write(json.dumps(anime_list, ensure_ascii=False))
    elif provider == StreamProvider.SerienStream:
        new_img_list = update_serien_stream_thumbnail_list()
        series_list = read_stream_list_json(StreamProvider.SerienStream)
        for new_series in new_img_list:
            series_list.append(new_series)
        with open("serienStreamListNew.json", "w", encoding='utf-8') as r:
            r.write(json.dumps(series_list, ensure_ascii=False))
    else:
        return {"Error": "Invalid StreamProvider!"}
    return {"status": "success"}

def update_serien_stream_thumbnail_list():
    series_list = []
    for series in remove_duplicates_from_list(StreamProvider.SerienStream):
        try:
            r = requests.get(
                f"https://api.themoviedb.org/3/search/tv?api_key=217cd958aac1d1d6fe9619cb1e8135b9&query={series['text']}")
            content = json.loads(r.text)
            img = content['results'][0]['poster_path']
            series["img"] = f'https://media.themoviedb.org/t/p/w300_and_h450_bestv2{img}'
            series_list.append(series)
            print(
                f"Added image for {series['text']} the img url is https://media.themoviedb.org/t/p/w300_and_h450_bestv2{img}")
        except:
            series_list.append(series)
            print(f"Couldn't get image for {series['text']}")
        time.sleep(0.05)
    return series_list


def update_anime_thumbnail_list():
    anime_list = []
    for anime in remove_duplicates_from_list(StreamProvider.AniWorld):
        try:
            r = requests.get(f"https://api.jikan.moe/v4/anime?q={anime['text']}")
            content = json.loads(r.text)
            img = content['data'][0]['images']['webp']["image_url"]
            anime["img"] = img
            anime_list.append(anime)
            print(f"Added image for {anime['text']} the img url is {img}")
        except:
            anime_list.append(anime)
            print(f"Couldn't get image for {anime['text']}")
        time.sleep(2)
    return anime_list


def remove_duplicates_from_list(provider: StreamProvider):
    final_list = []
    if provider == StreamProvider.AniWorld:
        with open('animeslist.json', encoding='utf-8', mode='r') as base_file:
            base_json = json.load(base_file)
            with open('animeslistNew.json', encoding='utf-8', mode='r') as old_file:
                old_json = json.load(old_file)
                for item in base_json:
                    is_in = False
                    for old_item in old_json:
                        if item['text'] == old_item['text']:
                            is_in = True
                    if not is_in:
                        final_list.append(item)
    elif provider == StreamProvider.SerienStream:
        with open('serienStreamList.json', encoding='utf-8', mode='r') as base_file:
            base_json = json.load(base_file)
            with open('serienStreamListNew.json', encoding='utf-8', mode='r') as old_file:
                old_json = json.load(old_file)
                for item in base_json:
                    is_in = False
                    for old_item in old_json:
                        if item['text'] == old_item['text']:
                            is_in = True
                    if not is_in:
                        final_list.append(item)
    else:
        return {"Error": "Invalid StreamProvider!"}

    return final_list


def read_anime_list_json():
    with(open("animeslistNew.json", encoding='utf-8') as r):
        return json.load(r)


def read_stream_list_json(provider: StreamProvider):
    if provider == StreamProvider.AniWorld:
        with(open("animeslistNew.json", encoding='utf-8') as r):
            return json.load(r)
    if provider == StreamProvider.SerienStream:
        with(open("serienStreamListNew.json", encoding='utf-8') as r):
            return json.load(r)
    else:
        return {"Error": "Invalid StreamProvider!"}


def create_stream_list_as_json(provider: StreamProvider):
    if provider == StreamProvider.AniWorld:
        anime_list = requests.get("https://aniworld.to/animes")

        soup = BeautifulSoup(anime_list.content, "html.parser")

        alist = []
        for ul in soup.find_all("ul"):
            for li in ul.find_all("li"):
                a_tag = li.find("a")
                if a_tag and a_tag.get('data-alternative-title') is not None:
                    item = {
                        "text": a_tag.text.strip(),
                        "href": a_tag.get("href", None),
                        "searchParm": a_tag.get('data-alternative-title')
                    }
                    alist.append(item)

        with open("animeslist.json", "w", encoding='utf-8') as r:
            r.write(json.dumps(alist, ensure_ascii=False))
    elif provider == StreamProvider.SerienStream:
        anime_list = requests.get("https://s.to/serien")

        soup = BeautifulSoup(anime_list.content, "html.parser")

        alist = []
        for ul in soup.find_all("ul"):
            for li in ul.find_all("li"):
                a_tag = li.find("a")
                if a_tag and a_tag.get('data-alternative-title') is not None:
                    item = {
                        "text": a_tag.text.strip(),
                        "href": a_tag.get("href", None),
                        "searchParm": a_tag.get('data-alternative-title')
                    }
                    alist.append(item)

        with open("serienStreamList.json", "w", encoding='utf-8') as r:
            r.write(json.dumps(alist, ensure_ascii=False))
    else:
        return {"Error": "Invalid StreamProvider!"}
    return {"status": "success"}


if __name__ == '__main__':
    download_loop = threading.Thread(target=download_loop)
    download_loop.start()
    download_loop_series = threading.Thread(target=download_series_loop)
    download_loop_series.start()
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True, port=9090)
    running = False
    download_loop.join()
    download_loop_series.join()
    print("Server Stopped")
