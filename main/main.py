# functions to set up/initialise selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
# functions used within selenium
from selenium.webdriver.common.by import By
# selenium exceptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# other tools
import re
import time
import sqlite3
import sys
# YouTube API
import json
import googleapiclient.discovery


# API info
api_service_name = 'youtube'
api_version = 'v3'
with open('config.json') as f:
    config = json.load(f)
API_KEY = config['API_KEY']
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=API_KEY)


# Create a list for channel ID's
cid_list = []


def db_init(chosen_year):
    con = sqlite3.connect('kp_albums.db')
    cur = con.cursor()
    # try:
    #    cur.execute(f'DROP TABLE IF EXISTS y{chosen_year}')
    # except sqlite3.OperationalError:
    #    pass
    print(f'y{chosen_year}')
    # cur.execute(f"CREATE TABLE y{chosen_year}(artist, album, songs, url, mv, mvverified)")
    # con.commit()
    return con, cur


def main(kpop_year):
    # Open kpopping
    driver.get(f"https://kpopping.com/musicalbums/year-{kpop_year}")

    # on webpage, find all artists and albums in the list
    artists = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/profiles/idol"]')
    albums = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/musicalbum"]')

    # create artists and albums lists
    artists_list = []
    albums_list_raw = []

    # append lists with text from previous elements
    for artist in artists:
        artists_list.append(artist.text)

    for album in albums:
        albums_list_raw.append(album.text)
        # edit list to match the formatting of kpopping links
        albums_list1 = [f"{kpop_year}-" + item.replace(" ", "-") for item in albums_list_raw]
        # does NOT remove - (hyphens)
        albums_list = [remove_special_characters(item) for item in albums_list1]

        # error can be ignored
    merged_list = list(zip(artists_list, albums_list))
    # convert to dictionary to make sorting easier later
    merged_dict = {}
    for artist, album in merged_list:
        if artist not in merged_dict:
            merged_dict[artist] = [album]
        else:
            merged_dict[artist].append(album)

    for artist, album in merged_dict.items():
        print(artist)
        for f in album:
            try:
                driver.get(f'https://kpopping.com/musicalbum/{f}')
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
                            print('TIMEOUT. 6 ATTEMPTS MADE OVER 3 MINUTES.')
                            driver.quit()
                            quit()
            try:
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


def remove_special_characters(s):
    # Replace spaces with hyphens - this is to try to get around the issue with ' in album names
    # had to add more as some were coming out with -- and --- in the names, this has fixed all issues of this kind
    # SO FAR
    s = s.replace("'", " ")
    s = s.replace(" ", "-")
    s = s.replace(".", "-")
    s = s.replace("---", "-")
    s = s.replace("--", "-")
    # Use regular expression to remove special characters, excluding apostrophes in words
    return re.sub(r'[^a-zA-Z0-9\s-]|(?<=\w)\'(?=\w)', '', s)


def music_video():
    with open('json_response.txt', 'w+', encoding='utf-8'):
        # used to create fresh text file before continuing
        pass
    mv_searches = cur.execute(f"SELECT artist, songs FROM y{chosen_year_q}").fetchall()
    with open('raw_response.txt', 'w+', encoding='utf-8') as f:
        for mv_res in mv_searches:
            artist = mv_res[0]
            song = mv_res[1]
            print(f'{song} {artist}')
            request = youtube.search().list(
                part='snippet',
                q=f'{mv_res} {artist}',
                maxResults=5,
                order='relevance',
                type='video'
            )
            response = request.execute()
            f.write(f'{response}\n\n')
            format_response = convert_human_readable(response)
            with open('format_response.txt', 'a', encoding='utf-8') as jf:
                jf.write(f'{format_response}\n\n')
            mv_database(format_response, song, artist)


def convert_human_readable(data, indent=0):
    formatted_output = ""
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_output += "  " * indent + f"{key}:\n"
            formatted_output += convert_human_readable(value, indent + 1)
        elif isinstance(value, list):
            formatted_output += "  " * indent + f"{key}:\n"
            for item in value:
                if 'kind' in item and item['kind'] == 'youtube#searchResult':
                    formatted_output += "\n\n"
                formatted_output += convert_human_readable(item, indent + 1)
        else:
            formatted_output += "  " * indent + f"{key}: {value}\n"
    return formatted_output


def mv_database(api_response, song, artist):

    # parse api_response into variables
    lines = api_response.split('\n')
    # vid_lines=video, vname_lines=vname, song=song, artist=artist, cname_lines=channel, cid_lines=cid
    vid_lines = [line.split(':')[1].strip() for line in lines if 'videoId' in line]
    cid_lines = [line.split(':')[1].strip() for line in lines if 'channelId' in line]
    vname_lines = [line.split(':')[1].strip() for line in lines if 'title' in line]
    cname_lines = [line.split(':')[1].strip() for line in lines if 'channelTitle' in line]
    # check if video is already in database using video id
    for vid, cid, vname, cname in zip(vid_lines, cid_lines, vname_lines, cname_lines):
        mv_exist = cur.execute("""SELECT video FROM mv WHERE video=?""", (vid,)).fetchone()
        cid_list.append(cid)
        if mv_exist:
            print(f'Video with ID {vid} already exists in database. Skipping {song} by {artist}')
        else:
            cur.execute("""INSERT INTO mv (video, title, song, artist, channel_title, channel_id, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (vid, vname, song, artist, cname, cid, 'tbc',))
            print(f'Video with ID {vid} and name {vname} added to database')


def channel_verified():
    for i in cid_list:
        driver.get(f'www.youtube.com/channel/{i}')
        try:
            driver.find_element(By.CSS_SELECTOR, 'ytd-channel-name.ytd-c4-tabbed-header-renderer > '
                                                 'ytd-badge-supported-renderer:nth-child(2) > '
                                                 'div:nth-child(1) > '
                                                 'yt-icon:nth-child(1) > yt-icon-shape:nth-child(1)')
            return 1
        except NoSuchElementException:
            return 2
    for i in cid_list:
        # Check if manual verification is required
        ver_value = cur.execute("""SELECT verified FROM mv WHERE cid=?""", (i,)).fetchone()
        if ver_value == 2:
            manual_verify(i)
        else:
            pass


def manual_verify(cid):
    do_manual_verify = ('The script has complete. There are some videos uploaded by channels without a \n'
                        'verification tick. Would you like to iterate through the list to manually verify these \n'
                        'channels? NOTE: This is used to help pick out a channel that would upload the correct \n'
                        'video and not a fan made video. (Y/N): ')
    if do_manual_verify.casefold() == 'y':
        for i in cid:
            pass
    elif do_manual_verify.casefold() == 'n':
        print('No problem, if you change your mind you can manually open the "kp_albums.db" database and open the\n'
              '"mv" table and change the value in the "verified" column to a 1 for verified, 0 for not.')
        time.sleep(1)
        print('Cleaning up..')
        time.sleep(2)
        print('Exiting script..')
        time.sleep(1)
        driver.quit()
        sys.exit()
    else:
        print('Input not recognised. Expected result either: Y or N\nPlease try again..\n\n')
        manual_verify(cid)

# add function to verify channel is legit. if it is not found in verified_channels.db then ask if it should be
# verified or not. This will add a 0 (no) or 1 (yes) tag to a "mvverified" column in the original database


if __name__ == '__main__':
    chosen_year_q = input('Year to get data for (format: YYYY e.g 2024): ')
    # # PROBABLY NOT NEEDED: # chosen_year = int(site_year)
    #
    kp_db, cur = db_init(chosen_year_q)
    kp_db.commit()
    try:
        # vname = video name, cid = channel id
        cur.execute(f"CREATE TABLE mv(video, vname, song, artist, channel, cid, verified)")
        kp_db.commit()
    except sqlite3.OperationalError:
        pass
    # # Setup geckodriver (Firefox)
    # options = Options()
    # options.headless = False
    # geckodriver_path = 'geckodriver.exe'
    # service = Service(executable_path=geckodriver_path)
    # driver = webdriver.Firefox(options=options, service=service)
    print(f'Checking kpopping list for year {chosen_year_q}..')
    # main(chosen_year_q)
    print('List created. Checking music videos..')
    music_video()
    print('Data grab complete. Checking channel verification status..')
    channel_verified()
    # driver.quit()
