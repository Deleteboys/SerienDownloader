import json
import time

import requests


def write_to_file():
    with open("animeslistNew.json", "w", encoding='utf-8') as w:
        w.write(json.dumps(anime_list, ensure_ascii=False))

def write_to_file2():
    with open("serienStreamListNew.json", "w", encoding='utf-8') as w:
        w.write(json.dumps(anime_list, ensure_ascii=False))


if __name__ == '__main__':
    anime_list = []
    with(open("serienStreamList.json", encoding='utf-8') as r):
        for anime in json.load(r):
            try:
                # r = requests.get(f"https://api.jikan.moe/v4/anime?q={anime['text']}")
                r = requests.get(f"https://api.themoviedb.org/3/search/tv?api_key=217cd958aac1d1d6fe9619cb1e8135b9&query={anime['text']}")
                content = json.loads(r.text)
                img = content['results'][0]['poster_path']
                anime["img"] = f'https://media.themoviedb.org/t/p/w300_and_h450_bestv2{img}'
                anime_list.append(anime)
                print(f"Added image for {anime['text']} the img url is https://media.themoviedb.org/t/p/w300_and_h450_bestv2{img}")
            except:
                print(r.status_code)
                print(r.text)
                anime_list.append(anime)
                print(f"Couldn't get image for {anime['text']}")
        write_to_file2()
        time.sleep(0.05)

# if __name__ == '__main__':
#     anime_list = []
#     with(open("animeslist.json", encoding='utf-8') as r):
#         for anime in json.load(r):
#             try:
#                 r = requests.get(f"https://api.jikan.moe/v4/anime?q={anime['text']}")
#                 content = json.loads(r.text)
#                 img = content['data'][0]['images']['webp']["image_url"]
#                 anime["img"] = img
#                 anime_list.append(anime)
#                 print(f"Added image for {anime['text']} the img url is {img}")
#             except:
#                 anime_list.append(anime)
#                 print(f"Couldn't get image for {anime['text']}")
#             write_to_file()
#             time.sleep(2)
