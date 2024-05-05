import glob
# Selenium imports
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException
# Converting language to the "sound" (ie Chinese > Chinese Pinyin)
from pypinyin import lazy_pinyin, Style
import pykakasi
from hangul_romanize import Transliter
from hangul_romanize.rule import academic
import pythainlp
# other tools
import re
import sqlite3
# Output to EXCEL
import os
import datetime
import time
# PyTube instead of YouTube API, slower but not limited by API calls per day
from pytube import Search as ytSearch
from pytube import YouTube
from pytube.exceptions import PytubeError
# Custom modules
from mv_database import mv_database
from output import output_excel
from is_verified import channel_verified
from db_init import db_connect

transliter = Transliter(academic)
cid_list = []


def main(kpop_year):
    # Open kpopping
    driver.get(f"https://kpopping.com/musicalbums/year-{kpop_year}")

    # on webpage, find all artists and albums in the list
    artists = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/profiles/idol"]')
    albums = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/musicalbum"]')
    artist_group = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/profiles/group"]')
    # create artists and albums lists
    artists_list = []
    albums_list_raw = []

    # append lists with text from previous elements
    for artist in artists:
        artists_list.append(artist.text)
    for artist in artist_group:
        artists_list.append(artist.text)
    for album in albums:
        albums_list_raw.append(album.text)
        # edit list to match the formatting of kpopping links
        albums_list1 = [f"{kpop_year}-" + item.replace(" ", "-") for item in albums_list_raw]
        # does NOT remove - (hyphens)
        albums_list2 = [translate_symbol(item) for item in albums_list1]
        albums_list = [remove_special_characters(item) for item in albums_list2]
    # noinspection PyUnboundLocalVariable
    merged_list = list(zip(artists_list, albums_list))
    # convert to dictionary to make sorting easier later
    merged_dict = {}
    for artist, album in merged_list:
        if artist not in merged_dict:
            merged_dict[artist] = [album]
        else:
            merged_dict[artist].append(album)
    attempted_urls = []
    it_num = 1
    for artist, album in merged_dict.items():
        print(artist)
        kpopping_songs(album, attempted_urls, it_num, artist)


def kpopping_songs(album, attempted_urls, it_num, artist):
    for f in album:
        if f'https://kpopping.com/musicalbum/{f}'.lower() in attempted_urls:
            it_num += 1
            f = f'https://kpopping.com/musicalbum/{f}{it_num}'
        try:
            driver.get(f'https://kpopping.com/musicalbum/{f}')
            attempted_urls.append(f'https://kpopping.com/musicalbum/{f}'.lower())
            print(f'https://kpopping.com/musicalbum/{f}')
        except TimeoutException:
            attempt = 0
            while True:
                attempt += 1
                time.sleep(30)
                try:
                    driver.get(f'https://kpopping.com/musicalbum/{f}')
                    break
                except TimeoutException:
                    if attempt == 6:
                        print('TIMED OUT. 6 ATTEMPTS MADE OVER 3 MINUTES.')
                        driver.quit()
                        quit()
        try:
            try:
                driver.find_element(By.CSS_SELECTOR, '.fa-compact-disc')
            except InvalidSessionIdException:
                print('FireFox not responding.. Waiting 10 seconds..')
                time.sleep(10)
                driver.find_element(By.CSS_SELECTOR, '.fa-compact-disc')
            songs = grab_songs()
            # DATABASE IS IN FORMAT artist, album, songs, url, friendly_name
            # db_album used to format album name into a more readable format
            db_album = str(album[4:]).replace('-', '')
            for item in songs:
                # FNAME
                print(item)
                cur.execute(f"INSERT INTO y{chosen_year_q} (artist,album,songs) VALUES (?,?,?)",
                            (artist, db_album, item))
                kp_db.commit()
        except NoSuchElementException:
            no_album = 'N/A'
            no_song = 'N/A'
            cur.execute(f"INSERT INTO y{chosen_year_q} (artist,album,songs) VALUES (?,?,?)", (artist, no_album,
                                                                                              no_song))
            kp_db.commit()


def grab_songs():
    songs_section = driver.find_element(By.CSS_SELECTOR, '.tracks')
    songs_section_list = songs_section.find_elements(By.CLASS_NAME, 'title-wr')
    songs_raw = []
    for song in songs_section_list:
        songs_raw.append(song.text)
    return songs_raw


# noinspection PyShadowingNames
def remove_special_characters(s):
    # Replace spaces with hyphens - this is to try to get around the issue with ' in album names
    # had to add more as some were coming out with -- and --- in the names, this has fixed all issues of this kind
    # SO FAR
    pattern = r'[\u2665\(),!]'
    s = re.sub(pattern, '', s)
    replace_list_space = ["'"]
    replace_list_dash = [' ', '.', '_', '+', '&', 'ː', '=', '÷', '/', '#', '?', '...', '’', '…', '---', '--']
    replace_list_empty = [':', '[', ']', '"']
    s = s.replace(':)', '2')
    s = s.replace('Ø', 'O')
    for i in replace_list_space:
        s = s.replace(i, ' ')
    for i in replace_list_empty:
        s = s.replace(i, '')
    for i in replace_list_dash:
        s = s.replace(i, '-')
    # Removes - if at the end of string
    s = re.sub(r'-\Z', '', s)
    s = s.replace('Ⅱ', 'II')
    s = s.replace('Ⅲ', 'III')
    s = s.replace('ᐸ', '<')
    s = s.replace('ᐳ', '>')
    s = s.replace('<', '%E1%90%B8')
    s = s.replace('>', '%E1%90%B3')
    # Exception due to inconsistency from kpopping
    if s == ('https://kpopping.com/musicalbum/2023-The-Seasons-VolII-10-%E1%90%B8AKMU-s-Long-Day-Long-'
             'Night%E1%90%B3-Re-Wake-x-Chuu'):
        s = s.replace('%E1%90%B8', '')
        s = s.replace('%E1%90%B3', '')
    return s


def translate_symbol(s):
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', s)
    for chinese_char in chinese_chars:
        pinyin_char = ''.join(lazy_pinyin(chinese_char, style=Style.NORMAL))
        s = s.replace(chinese_char, pinyin_char)
        s = s.replace('[', '-')
        s = s.replace(']', '')
    japanese_chars = re.findall(r'[\u3040-\u30FF\u31F0-\u31FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]+', s)
    for japanese_char in japanese_chars:
        kks = pykakasi.kakasi()
        result = kks.convert(japanese_char)
        for item in result:
            romaji_char = ''.join(item['hepburn'])
            s = s.replace(japanese_char, romaji_char)
        s = s.replace('[', '-')
        s = s.replace(']', '')
    korean_chars = re.findall(r'[\uac00-\ud7af\u1100-\u1112\u1161-\u1175\u11A8-\u11C2]+', s)
    for korean_char in korean_chars:
        romanized_char = ''.join(transliter.translit(korean_char))
        s = s.replace(korean_char, romanized_char)
        s = s.replace('[', '-')
        s = s.replace(']', '')
    thai_chars = re.findall(r'[\u0e00-\u0e7f]+', s)
    for thai_char in thai_chars:
        thairom_char = ''.join(pythainlp.romanize(thai_char))
        s = s.replace(thai_char, thairom_char)
        s = s.replace('[', '-')
        s = s.replace(']', '')
    return s


# noinspection PyShadowingNames
def music_video():
    if not os.path.isdir('response_files'):
        os.mkdir('response_files')
    mv_searches = cur.execute(f"SELECT artist, songs FROM y{chosen_year_q}").fetchall()
    iteration = 0
    batch_execute = 1
    for mv_res in mv_searches:
        print(batch_execute)
        if batch_execute == 1:
            jf = open(f'response_files/format_response{iteration}.txt', 'w+', encoding='utf-8')
            artist = mv_res[0]
            song = mv_res[1]
            print(f'{song} {artist}')
            search_term = f'{mv_res} {artist}'
            search_result = ytSearch(search_term).results
            x = 0
            for i in search_result:
                i = str(i)
                if x < 11:
                    start_index = i.find("videoId=") + len("videoId=")
                    end_index = i.find(">", start_index)
                    video_id = i[start_index:end_index]
                    search_id = f'https://www.youtube.com/watch?v={video_id}'
                    youtube_return = YouTube(search_id)
                    cid_line = youtube_return.channel_id
                    channel_user = youtube_return.channel_url
                    start_index = channel_user.find("@") + len("@")
                    channel_name = channel_user[start_index:]
                    upload_date = youtube_return.publish_date.year
                    vname_line = youtube_return.title
                    print(video_id)
                    jf.write(f'video_id:{video_id}\nchannel_id:{cid_line}\nvideo_name:{vname_line}\nchannel_'
                             f'name:{channel_name}\nupload_year:{upload_date}\n[debug]search_term:{search_term}\n'
                             f'\n')
                    x += 1
        else:
            artist = mv_res[0]
            song = mv_res[1]
            print(f'{song} {artist}')
            search_term = f'{mv_res} {artist}'
            search_result = ytSearch(search_term).results
            x = 0
            for i in search_result:
                i = str(i)
                if x < 11:
                    start_index = i.find("videoId=") + len("videoId=")
                    end_index = i.find(">", start_index)
                    video_id = i[start_index:end_index]
                    search_id = f'https://www.youtube.com/watch?v={video_id}'
                    youtube_return = YouTube(search_id)
                    cid_line = youtube_return.channel_id
                    channel_user = youtube_return.channel_url
                    start_index = channel_user.find("@") + len("@")
                    channel_name = channel_user[start_index:]
                    upload_date = youtube_return.publish_date.year
                    try:
                        vname_line = youtube_return.title
                    except PytubeError:
                        time.sleep(1)
                        try:
                            vname_line = youtube_return.title
                        except PytubeError:
                            vname_line = 'ERROR_RETURNING_VIDEO_TITLE'
                    print(video_id)
                    # noinspection PyUnboundLocalVariable
                    jf.write(f'video_id:{video_id}\nchannel_id:{cid_line}\nvideo_name:{vname_line}\nchannel_'
                             f'name:{channel_name}\nupload_year:{upload_date}\n[debug]search_term:{search_term}\n'
                             f'\n')
                    x += 1
        batch_execute += 1
        if batch_execute == 10:
            batch_execute = 1
            jf.close()
            mv_database(filename=f'response_files/format_response{iteration}.txt', song=song, artist=artist, os=os,
                        cur=cur, cid_list=cid_list, chosen_year_q=chosen_year_q, kp_db=kp_db, re=re)
            iteration += 1


if __name__ == '__main__':
    import timeit
    start = timeit.default_timer()
    print('Cleaning files..')
    clean_files = glob.glob('response_files/*')
    for i in clean_files:
        os.remove(i)
    chosen_year_q = input('Year to get data for (format: YYYY e.g 2024): ')
    print('Loading database..')
    #kp_db, cur = db_connect(chosen_year_q, is_main=1)
    kp_db, cur = db_connect(chosen_year_q, is_main=0)
    kp_db.commit()
    try:
        cur.execute(f"CREATE TABLE mv(video, vname, song, artist, channel, cid, verified)")
        kp_db.commit()
    except sqlite3.OperationalError:
        pass
    cur.execute("DROP TABLE IF EXISTS video_type")
    cur.execute(f"CREATE TABLE video_type(name, vid_id, vid_type)")
    kp_db.commit()
    # Setup geckodriver (Firefox)
    print('Launching Firefox via Geckodriver in HEADLESS mode..')
    options = Options()
    options.add_argument("-headless")
    geckodriver_path = 'geckodriver.exe'
    service = Service(executable_path=geckodriver_path)
    driver = webdriver.Firefox(options=options, service=service)
    print(f'Checking kpopping list for year {chosen_year_q}..')
    #main(chosen_year_q)
    print('List created. Checking music videos..')
    music_video()
    print('Data grab complete. Checking channel verification status.. (May take a while.. '
          'Approx. 6-7 seconds per video)')
    #channel_verified(cid_list, cur, kp_db, driver)
    driver.quit()
    output_excel(os, datetime, chosen_year_q, cur, re)
    stop = timeit.default_timer()
    print(f'Total runtime: {stop - start}')
