# import json
# import os
#
#
# def add_failed_download(failed_download):
#     currentFile = failed_downloads()
#     if not currentFile.__contains__(failed_download):
#         currentFile.append(failed_download)
#         with(open("failedDownloads.json", "w", encoding="utf-8") as f):
#             f.write(json.dumps(currentFile))
#     else:
#         print("Already added to failed list")
#
#
# def failed_downloads():
#     if os.path.exists("failedDownloads.json"):
#         with(open("failedDownloads.json", encoding='utf-8') as r):
#             return json.load(r)
#     else:
#         with(open("failedDownloads.json", "w", encoding="utf-8") as f):
#             f.write("[]")
#         return []
#
#
# add_failed_download({"test": "test123"})
from enum import Enum, auto


class StreamProvider(Enum):
    AniWorld: int = 0
    SerienStream: int = 1


if __name__ == '__main__':
    stream_provider_list = []
    for stream in StreamProvider:
        stream_provider_list.append({"title": stream.name, "id": stream.value})
    print(stream_provider_list)
    # print(StreamProvider.value)