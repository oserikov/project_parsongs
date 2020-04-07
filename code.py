import requests
from pyquery import PyQuery as pq
import json
import csv
import os

#создаёт директорию для дальнейшей работы программы, если такой ещё нет
def make_main_dir():
    try:
        os.makedirs('PARSONGS/songs')
        res = 'Work directory has been created'
    except FileExistsError:
        res = 'Work directory already exists'
    return res

#создаёт общий файл
def make_csv():
    with open("PARSONGS/genius_songs.csv", "w", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(["Artist", "Song", "URL"])
    pass

#словарь всех песен со страницы автора
def get_all_data(artist_url):
    res_artist = requests.get(str(artist_url)).text
    artist_number = pq(res_artist).find("meta[name='newrelic-resource-path']").attr("content")
    data_artist = []
    i = "1"
    while i != "None":
        res_list = requests.get(f"https://genius.com/api{artist_number}/songs?page={i}&sort=popularity").text
        dic_res = json.loads(res_list)
        for dic_song in dic_res["response"]["songs"]:
            if dic_song["lyrics_state"] == "complete":
                data_artist.append([str(dic_song["primary_artist"]["name"]), str(dic_song["title"]),str(dic_song["url"])])
        i = str(dic_res["response"]["next_page"])
    return data_artist

#построчая запись в общий файл
def write_data(data_artist):
    with open("PARSONGS/genius_songs.csv", "a", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data_artist:
            writer.writerow(line)
    pass

#оздание папки исполнителя
def make_art_dir(artist):
    try:
        os.mkdir(f"PARSONGS/songs/{artist}")
        res = f"{artist} folder has been created"
    except FileExistsError:
        res = f"{artist} folder already exists"
    return res


#запись в папку исполнителя песен
def write_all_songs(artist):
    with open("PARSONGS/genius_songs.csv", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Artist"] == artist:
                res_link = requests.get(row["URL"]).text
                title = pq(res_link).find("h1.header_with_cover_art-primary_info-title").text() #Мб не искать по сайту, а из колонки цсв
                artist_name = pq(res_link).find("a.header_with_cover_art-primary_info-primary_artist").text() #То же самое
                lyrics = pq(res_link).find("div.lyrics").text()
                file_name = title.lower().replace(',','').replace('.','').replace('!','').replace('?','').replace('...','').replace('/','').replace('"','').replace(';','').replace('(','').replace(')','').replace('—',' ').replace(' ','_')
                with open(f"PARSONGS/songs/{artist}/{file_name}.txt", "w", encoding="utf-8") as f:
                    f.write(artist_name + "\n" + title + "\n" + lyrics)
    pass

