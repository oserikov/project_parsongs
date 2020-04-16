import requests
from pyquery import PyQuery as pq
import json
import csv
import os
import re
from urllib.parse import quote
from selenium import webdriver


PATH_TO_CSV = "PARSONGS/genius_songs.csv"
PATH_TO_SONGS_FOLDER = "PARSONGS/songs"
GENIUS_MAIN_PAGE = "https://genius.com"


#очищает строку от пунктуационных знаков
def clean_punc(string):
    punc = r'[!\"#$%&\'()*+,-./:;<=>?@\[\\\]^_`{|}~]'
    clean_string1 = re.sub(punc, '', string)
    clean_string2 = re.sub(r' – ', ' ', clean_string1)
    return clean_string2


#чистилка для крэйзи названий груп, чтобы винда не блочила названия папок, но при этом было более читабольно, чем названия файлов (например, для P!nk, Florence + The Machine)
def clean_for_dir(artist):
    ban = r'[\/:*?"<>|]'
    clean_name_for_dir = re.sub(ban,'',artist)
    return clean_name_for_dir


#Достаёт с сайта url исполнителя по запросу пользователя
def get_artist_url():
    artist_name_for_search = input('Hi! Write the artist whose songs you want to get: ').lower()
    artist_name_for_search_url = quote(artist_name_for_search)
    artist_search_url = f"{GENIUS_MAIN_PAGE}/search?q={artist_name_for_search_url}"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    wd = webdriver.Chrome('chromedriver', options=chrome_options)
    wd.get(artist_search_url)
    search_page = wd.page_source

    mini_cards = pq(search_page).find("mini-artist-card")
    if len(mini_cards) != 0:
        artist_url = pq(mini_cards[0]).find("a").attr("href")
    else:
        artist_url = "None"

    return artist_url


#вытаскивает тру имя исполнителя
def get_artist_name(artist_url):
    res_artist = requests.get(artist_url).text
    artist_all_names = pq(res_artist).find("div.profile_identity-text").text().splitlines()
    artist = artist_all_names[0]
    return artist


#создаёт директорию для дальнейшей работы программы, если такой ещё нет
def make_main_dir():
    try:
        os.makedirs(PATH_TO_SONGS_FOLDER)
        res = 'Work directory has been created'
    except FileExistsError:
        res = 'Work directory already exists'
    return res


#создаёт общий файл
def make_csv():
    with open(PATH_TO_CSV, "w", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(["Artist", "Song", "URL"])


#список всех песен со страницы автора
def list_of_all_songs(artist_url):
    res_artist = requests.get(str(artist_url)).text
    artist_number = pq(res_artist).find("meta[name='newrelic-resource-path']").attr("content")
    list_songs = []
    page = "1"
    while page != "None":
        res_list = requests.get(f"{GENIUS_MAIN_PAGE}/api{artist_number}/songs?page={page}&sort=popularity").text
        res_dic = json.loads(res_list)
        for dic_song in res_dic["response"]["songs"]:
            if dic_song["lyrics_state"] == "complete":
                list_songs.append([str(dic_song["primary_artist"]["name"]), str(dic_song["title"]),str(dic_song["url"])])
        page = str(res_dic["response"]["next_page"])
    return list_songs


#построчая запись в общий файл
def write_songs_in_csv(list_songs):
    with open(PATH_TO_CSV, "a", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in list_songs:
            writer.writerow(line)


#создание папки исполнителя
def make_artist_dir(artist):
    try:
        os.mkdir(f"{PATH_TO_SONGS_FOLDER}/{clean_for_dir(artist)}")
        res = f"{artist} folder ({clean_for_dir(artist)}) has been created"
    except FileExistsError:
        res = f"{artist} folder ({clean_for_dir(artist)}) already exists"
    return res


#Считает количество песен ИСПОЛНИТЕЛЯ (!= количеству записаных в файл с его страницы, так как там есть каверы)
def number_of_songs(artist):
    with open(PATH_TO_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        songs_num = 0
        for row in reader:
            if row["Artist"] == artist:
                songs_num += 1
    return songs_num


#чекает, сколько песен уже есть в директории исполнителя
def number_of_files_songs_in_dir(artist):
    list_of_files = os.listdir(f"{PATH_TO_SONGS_FOLDER}/{artist}")
    number_of_files = len(list_of_files)
    return number_of_files


#запись в папку исполнителя песен
def write_all_songs(artist, songs_num, number_of_files):
    how_many = int(input(f"{artist} has {songs_num} songs. There are already {number_of_files} in {artist} directory. How many do you want to download? Write a number (! including the number of songs which already exist): "))
    if how_many > songs_num or how_many <= 0:
        ans = "You can't download this number of songs."
    else:
        ans = "Songs have been downloaded!"
        with open(PATH_TO_CSV, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            counter = 0
            for row in reader:
                if row["Artist"] == artist:
                    res_link = requests.get(row["URL"]).text
                    lyrics = pq(res_link).find("div.lyrics").text()
                    file_name = clean_punc(row["Song"]).lower().replace(' ','_')
                    with open(f"{PATH_TO_SONGS_FOLDER}/{artist}/{file_name}.txt", "w", encoding="utf-8") as f:
                        f.write(artist + "\n" + row["Song"] + "\n" + lyrics)
                    counter += 1
                    if counter == how_many:
                        break
    return ans


#осталось главную написать...
def main():
    artist_url = get_artist_url()
    if artist_url == 'None':
        print('There is no such artist on Genius')
    else:
        res = make_main_dir()
        if res == 'Work directory already exists':
            pass
        else:
            make_csv()
        artist_name = get_artist_name(artist_url)
        songs_num = number_of_songs(artist_name)
        while songs_num == 0:
            what_do_you_want_1 = input(f"There is no songs of {artist_name} in the list yet. Print 'YES' to add this artist's songs to list and 'NO' to stop the program: ")
            if what_do_you_want_1 == 'NO':
                print("The program was stopped")
                break
            else:
                write_songs_in_csv(list_of_all_songs(artist_url))
                songs_num = number_of_songs(artist_name)
        if songs_num != 0:
            what_do_you_want_2 = input(f"There are songs of {artist_name} in the list. If this the right artist, do you want to download any of its songs? Print 'YES' or 'NO': ")
            if what_do_you_want_2 == 'NO':
                print("The program was stopped")
            else:
                make_artist_dir(artist_name)
                ans = write_all_songs(artist_name, songs_num, number_of_files_songs_in_dir(artist_name))
                print(ans)


if __name__ == '__main__':
    main()