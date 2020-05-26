import csv
import os
import re
import collections
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()


PATH_TO_CSV = "PARSONGS/genius_songs.csv"
PATH_TO_RESEARCH_TXT = "RESEARCH/kinda_research.txt"
PATH_TO_SONGS_FOLDER = "PARSONGS/songs"
PATH_TO_RESEARCH_FOLDER = "RESEARCH"
PATH_TO_RESEARCH_WORK_FOLDER = "RESEARCH/work_files"
STOP_WORDS = set(stopwords.words("english")) #Он странный. Тут есть couldn't, но нет could, есть can, но нет can't. Но такие штуки решила сохранить.
my_set = {"n't", "'re", "'ve", "'s", "'ll", "'m"}  #Не поняла, какой обработки сокращений ждёт список стоп-слов, так что обработала по-своему, но пришлось добавить некоторые популярные сокращения в другом формате
STOP_WORDS.update(my_set)


#создаёт директорию для дальнейшей работы программы, если такой ещё нет
#и файл сводную табличку для результатов
def make_main_dir_and_csv():
    try:
        os.mkdir(PATH_TO_RESEARCH_FOLDER)
        with open(PATH_TO_RESEARCH_TXT, "w", encoding='utf-8') as txt_file:
            txt_file.write("Сводный файл по мини-исследованию\n\n")
            os.mkdir(f'{PATH_TO_RESEARCH_WORK_FOLDER}')
    except FileExistsError:
        return None


#Жарны исполнителя и их частота
def artists_genres(artist_from_the_table):
    artist_genres = []
    with open(PATH_TO_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Artist"] == artist_from_the_table:
                artist_genres.append(row["Genre"])
    count_genres_list = list(sorted(collections.Counter(artist_genres).items(),
                                    reverse=True, key=lambda kv_pair: kv_pair[1]))
    return count_genres_list


#Очистить от знаков препинания, но с сохранением ' в английском при сокращениях, их обработка будет дальше
def clean_punc_eng(string):
    punc = r'[!\"#$%&()*+,-./:;<=>?@\[\\\]^_`{|}~]'
    clean_string1 = re.sub(punc, '', string)
    clean_string2 = re.sub(r' – ', ' ', clean_string1)
    return clean_string2


#Получить сырой список ВСЕХ СЛОВ ОДНОЙ ПЕСНИ
def get_all_words_song(artist, file_song):
    with open(f"{PATH_TO_SONGS_FOLDER}/{artist}/{file_song}", encoding='utf-8') as s:
        text_lines = s.readlines()[2:]
    text_song = ''.join(text_lines)
    clean_song1 = re.sub(r'\[.+?\]', '', text_song) #Удалить теги в скобках
    clean_song2 = re.sub(r"([^a])(n't)", r'\1 \2', clean_song1) #Обработать сокращения not
    clean_song3 = re.sub(r"([^n])('.)", r'\1 \2', clean_song2) #Обработать другие сокращения
    clean_song4 = clean_punc_eng(clean_song3).lower().replace('\n',' ')
    all_words_song = clean_song4.split()
    return all_words_song


#Возвращает общее число слов ВСЕХ СЛОВ ВСЕХ ПЕСЕН исполнителя (включая стоп слова)
# и создаёт файл с леммантизированными словами ВСЕХ СЛОВ ВСЕХ ПЕСЕН (без стоп слов)
def count_all_words_and_write_meaning_words(artist):
    all_words_artist = 0
    list_of_files = os.listdir(f"{PATH_TO_SONGS_FOLDER}/{artist}")
    for file in list_of_files:
        all_words_song = get_all_words_song(artist, file)
        all_words_artist += len(all_words_song)
        without_stop_words_song = [word for word in all_words_song if not word in STOP_WORDS]
        with open(f'{PATH_TO_RESEARCH_WORK_FOLDER}/{artist}_meaning_words.txt', 'a', encoding='utf-8') as a:
            for word in without_stop_words_song:
                a.write(lemmatizer.lemmatize(word)+'\n')
    return all_words_artist


#Считает количество и частотный список ВСЕХ СЛОВ ВСЕХ ПЕСЕН (без стоп-слов)
def count_and_freq_meaning_words(artist):
    with open(f'{PATH_TO_RESEARCH_WORK_FOLDER}/{artist}_meaning_words.txt', encoding='utf-8') as r:
        words_line = r.read()
    words_list = words_line.splitlines()
    meaning_words = len(words_list)
    top_meaning_words = list(sorted(collections.Counter(words_list).items(),
                                    reverse=True, key=lambda kv_pair: kv_pair[1]))[:9]
    return meaning_words, top_meaning_words


#запись всего в сводный файл
def add_to_research_txt(artist, genres, all_words_artist, meaning_words, top_meaning_words):
    with open(PATH_TO_RESEARCH_TXT, "a", encoding='utf-8') as txt_file:
        txt_file.write(artist+'\n'+
                       'Genres: '+str(genres)+'\n'+
                       'Total number of words: '+str(all_words_artist)+'\n'+
                       "Number of 'meningful' words: "+str(meaning_words)+'\n'+
                       "Ratio: "+str(round(meaning_words/all_words_artist, 2))+'\n'+
                       "Top-10 'meaningful' words: "+str(top_meaning_words)+'\n\n')


#главная функция
def main():
    artist = str(input("Hi! Write the artist which you want to analyse (! In the same way, like in genius_songs.csv): "))
    genres = artists_genres(artist)
    if len(genres) == 0:
        print("You write your artist in a wrong way or there is no your artist's songs downloaded yet.")
    else:
        make_main_dir_and_csv()
        all_words_artist = count_all_words_and_write_meaning_words(artist)
        meaning_words, top_meaning_words = count_and_freq_meaning_words(artist)
        add_to_research_txt(artist, genres, all_words_artist, meaning_words, top_meaning_words)
        print("Done!")


if __name__ == '__main__':
    main()
