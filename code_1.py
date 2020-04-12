import requests
from pyquery import PyQuery as pq
import json
import csv
import os
import re
from urllib.parse import quote
from selenium import webdriver


#очищает строку от пунктуационных знаков
def clean_punc(string):
    punc = r'[!\"#$%&\'()*+,-./:;<=>?@\[\\\]^_`{|}~]'
    clean_string1 = re.sub(punc, '', string)
    clean_string2 = re.sub(r' – ', ' ', clean_string1)
    return clean_string2


#Достаёт с сайта url исполнителя по запросу пользователя
def search_link():
    art_s = input('Write the artist whose songs you want to get: ').lower()
    art_s_for_url = quote(art_s)
    art_s_url = "https://genius.com/search?q=" + art_s_for_url

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    wd = webdriver.Chrome('chromedriver', options=chrome_options)
    wd.get(art_s_url)
    search_page = wd.page_source

    mini_cards = pq(search_page).find("mini-artist-card")
    if len(mini_cards) != 0:
        artist_url = pq(mini_cards[0]).find("a").attr("href")
    else:
        artist_url = "None"

    return artist_url


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


#список всех песен со страницы автора
def get_all_data(artist_url):
    res_artist = requests.get(str(artist_url)).text
    artist_number = pq(res_artist).find("meta[name='newrelic-resource-path']").attr("content")
    data_artist = []
    page = "1"
    while page != "None":
        res_list = requests.get(f"https://genius.com/api{artist_number}/songs?page={page}&sort=popularity").text
        dic_res = json.loads(res_list)
        for dic_song in dic_res["response"]["songs"]:
            if dic_song["lyrics_state"] == "complete":
                data_artist.append([str(dic_song["primary_artist"]["name"]), str(dic_song["title"]),str(dic_song["url"])])
        page = str(dic_res["response"]["next_page"])
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

#Считает количество песен ИСПОЛНИТЕЛЯ (!= количеству записаных в файл с его страницы, так как там есть каверы)
def number_of_songs(artist):
    with open("PARSONGS/genius_songs.csv", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        songs_num = 0
        for row in reader:
            if row["Artist"] == artist:
                songs_num += 1
    return songs_num


#запись в папку исполнителя песен
def write_all_songs(artist, songs_num):
    how_many = int(input(f"{artist} has {songs_num} songs. How many do you want to download? Write a number: "))
    if how_many > songs_num or how_many <= 0:
        ans = "You can't download this number of songs."
    else:
        ans = "Songs have been downloaded!"
        with open("PARSONGS/genius_songs.csv", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            counter = 0
            for row in reader:
                if row["Artist"] == artist:
                    res_link = requests.get(row["URL"]).text
                    lyrics = pq(res_link).find("div.lyrics").text()
                    file_name = clean_punc(row["Song"]).lower().replace(' ','_')
                    with open(f"PARSONGS/songs/{artist}/{file_name}.txt", "w", encoding="utf-8") as f:
                        f.write(artist + "\n" + row["Song"] + "\n" + lyrics)
                    counter += 1
                    if counter == how_many:
                        break
    return ans

