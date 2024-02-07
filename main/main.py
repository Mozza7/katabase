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


def db_init(chosen_year):
    con = sqlite3.connect('kp_albums.db')
    cur = con.cursor()
    try:
        cur.execute(f'DROP TABLE IF EXISTS y{chosen_year}')
    except sqlite3.OperationalError:
        pass
    print(f'y{chosen_year}')
    cur.execute(f"CREATE TABLE y{chosen_year}(artist, album, songs, url)")
    con.commit()
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
                # DATABASE IS IN FORMAT artist, album, songs, url
                # db_album used to format album name into a more readable format
                db_album = str(album[4:]).replace('-', '')
                for item in songs:
                    cur.execute(f"INSERT INTO y{chosen_year_q} (artist,album,songs) VALUES (?,?,?)", (artist, db_album,
                                                                                                   item))
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
    # uses database created in main() to search for songs that have music videos / performance videos
    # data is then added to an excel in format:
    # ARTIST | ALBUM        | SONGS                     | MUSIC/PERFORMANCE VIDEO
    # YENA   | GOOD MORNING | GOOD MORNING              |   Y
    #                       | GOOD GIRLS IN THE DARK    |   N
    #                       | DAMN U                    |   N
    #                       | THE UGLY DUCKLING         |   N
    pass


if __name__ == '__main__':
    chosen_year_q = input('Year to get data for (format: YYYY e.g 2024): ')
    # chosen_year = int(site_year)

    kp_db, cur = db_init(chosen_year_q)
    kp_db.commit()
    # Setup geckodriver (Firefox)
    options = Options()
    options.headless = False
    geckodriver_path = 'drivers/geckodriver.exe'
    service = Service(executable_path=geckodriver_path)
    driver = webdriver.Firefox(options=options, service=service)
    main(chosen_year_q)
    # music_video()
    driver.quit()
