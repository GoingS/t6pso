import requests
import json
import re

base_url = "https://myanimelist.net/anime/"
base_url_search = "https://myanimelist.net/anime.php?q="
base_api_url = "https://jikan.me/api/anime/"
regex = r'\"https://myanimelist.net/anime/[0-9]+.*/'

class AnimeInfo:
    def __init__(self):
        self.id = 0
        self.title = ""
        self.score = 0
        self.episodes = 0
        self.type = ""
        self.status = ""
        self.source = ""
        self.aired = ""

    def print(self):
        print("Title: " + self.title)
        print("Score: " + str(self.score))
        print("Episodes: " + str(self.episodes))
        print("Type: " + str(self.type))
        print("Status: " + str(self.status))
        print("Source: " + str(self.source))
        print("Aired: " + str(self.aired))
        print("Link: " + base_url + str(self.id))

    def parse_json(self, data):
        self.title = data.get("title")
        self.score = data.get("score")[0]
        self.episodes = data.get("episodes")
        self.type = data.get("type")
        self.status = data.get("status")
        self.source = data.get("source")
        self.aired = data.get("aired")

    @staticmethod
    def get_infos (ids):
        anime_infos = []
        for id in ids:
            j = Website.get_json(id)
            a = AnimeInfo()
            a.id = id
            a.parse_json(j)
            anime_infos.append(a)
        return anime_infos


class RequestInfo:
    type_ = []
    source = []

    def __init__(self):
        self.query = None
        self.min_score = -1
        self.max_score = -1
        self.min_episodes = -1
        self.max_episodes = -1
        self.type_ = []
        self.status = []
        self.source = []

    def print(self):
        if self.query:
            print("\nQuery: " + self.query)
        print("Score: " + str(self.min_score) + " ~ " + str(self.max_score))
        print("Episodes: " + str(self.min_episodes) + " ~ " + str(self.max_episodes))
        if self.type_:
            print("Type: ")
            print(self.type_)
        if self.source:
            print("Source: ")
            print(self.source)

    def parse_request(self, req):
        if req.__contains__('@'):
            self.query = req.split('@')[0]
            specs = req.split('@')[1].split(' ')
            self.parse_specs(specs)
        else:
            self.query = req

    def parse_specs(self, specs):
        for s in specs:
            spec = s.split(':')[0]
            filter = s.split(':')[1]
            if spec == "score":
                minimum = filter.split('-')[0]
                maximum = filter.split('-')[1]
                if minimum is not None:
                    self.min_score = float(minimum)
                if maximum is not None:
                    self.max_score = float(maximum)
            elif spec == "episodes":
                minimum = filter.split('-')[0]
                maximum = filter.split('-')[1]
                if minimum is not None:
                    self.min_episodes = int(minimum)
                if maximum is not None:
                    self.max_episodes = int(maximum)
            elif spec == "type":
                filters = filter.split(',')
                self.type_ += filters
            elif spec == "status":
                filters = filter.split(',')
                self.status += filters
            elif spec == "source":
                filters = filter.split(',')
                self.source += filters


    def filter_animes(self, animes):
        if self.min_score != -1:
            animes = [x for x in animes if self.min_score < x.score]
        if self.max_score != -1:
            animes = [x for x in animes if self.max_score > x.score]
        if self.min_episodes != -1:
            animes = [x for x in animes if self.min_episodes < x.episodes]
        if self.max_episodes != -1:
            animes = [x for x in animes if self.max_episodes > x.episodes]
        if self.type_ != []:
            animes = [x for x in animes if x.type in self.type_]
        if self.status != []:
            animes = [x for x in animes if x.status in self.status]
        if self.source != []:
            animes = [x for x in animes if x.source in self.source]
        return animes


class Website:

    @staticmethod
    def prepare_url(query):
        query = query.replace(' ', '%20')
        return base_url_search + query

    @staticmethod
    def get_ids(page, query):
        result = []
        links = re.findall(regex, page)
        keywords = query.split(' ')
        for i in range(0, links.__len__()):
            links[i] = links[i].split('\"')[1]
            for k in keywords:
                if links[i].__contains__(k):
                    result.append(re.findall(r'[0-9]+', links[i])[0])
        if result.__contains__(''):
            result.remove('')
        return list(set(result))

    def get_json(id):
        return json.loads(requests.get(base_api_url + str(id)).text)

"""
a1 = AnimeInfo()
a1.type = "TV"
a1.score = 9
a1.aired = "aa"
a1.episodes = 24
a1.source = "Original"
a1.status = "Finished Airing"
a1.title = "Oregairu"

a2 = AnimeInfo()
a2.type = "TV"
a2.score = 6
a2.aired = "aa"
a2.episodes = 12
a2.source = "Original"
a2.status = "Manga"
a2.title = "Sakura Trick"

a3 = AnimeInfo()
a3.type = "TV"
a3.score = 7
a3.aired = "aa"
a3.episodes = 12
a3.source = "Light Novel"
a3.status = "Finished Airing"
a3.title = "Oreimo"

a4 = AnimeInfo()
a4.type = "TV"
a4.score = 5
a4.aired = "aa"
a4.episodes = 6
a4.source = "Original"
a4.status = "Finished Airing"
a4.title = "Black rock shooter"

anime_infos = [a1, a2, a3, a4]
search = "@score:4-10 type:TV"
request_info = RequestInfo()
request_info.parse_request(search)
request_info.print()
anime_infos = request_info.filter_animes(anime_infos)
print ("\nanimes left:")
for a in anime_infos:
    print(a.title)
"""


while True:
    search = input("Type the query search, then a '@' and then the filters:\n")
    request_info = RequestInfo()
    request_info.parse_request(search)
    request_info.print()
    url = Website.prepare_url(request_info.query)
    req = requests.get(url).text
    ids = Website.get_ids(req, request_info.query)
    anime_infos = AnimeInfo.get_infos(ids[:5])
    anime_infos = request_info.filter_animes(anime_infos)
    print("\nFound " + str(anime_infos.__len__()) + " results:\n")
    for a in anime_infos:
        a.print()
        print("")

