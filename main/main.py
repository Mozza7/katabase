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

# Setup geckodriver (Firefox)
options = Options()
options.headless = False
geckodriver_path = 'drivers/geckodriver.exe'
service = Service(executable_path=geckodriver_path)
driver = webdriver.Firefox(options=options, service=service)


def main():
    # Open kpopping
    # kpop_year = input("Type the year you are looking for data on: ")
    # driver.get(f"https://kpopping.com/musicalbums/year-{kpop_year}")
    # MAKE CUSTOMISABLE, USING 2022 FOR TESTING PURPOSES
    driver.get("https://kpopping.com/musicalbums/year-2022")

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
        # CHANGE "2022-" TO BE CUSTOMISABLE
        # edit list to match the formatting of kpopping links
        albums_list1 = ["2022-" + item.replace(" ", "-") for item in albums_list_raw]
        # does NOT remove - (hyphens)
        albums_list = [remove_special_characters(item) for item in albums_list1]

        # error can be ignored, albums_list can NOT be undefined
    merged_list = list(zip(artists_list, albums_list))
    # convert to dictionary to make sorting easier later
    merged_dict = {}
    for artist, album in merged_list:
        if artist not in merged_dict:
            merged_dict[artist] = [album]
        else:
            merged_dict[artist].append(album)

    # overwrite existing list
    with open('songlist.txt', 'w+', encoding='utf-8') as f:
        f.write('ARTIST - ALBUM - SONGS\n\n')

    # open list for appending within for loop
    song_list = open('songlist.txt', 'w', encoding='utf-8')
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
                            song_list.write('TIMEOUT. 6 ATTEMPTS MADE OVER 3 MINUTES.')
                            driver.quit()
                            quit()
            try:
                driver.find_element(By.CSS_SELECTOR, '.fa-compact-disc')
                song_list.write(f'{artist} - {f} - SONGS: \n')
                songs = grab_songs()
                for item in songs:
                    song_list.write(f'{item}\n')
                song_list.write('\n')
            except NoSuchElementException:
                song_list.write(f'{artist} - {f} - !> NO SONGS FOUND <!\n\n')
    driver.quit()


def grab_songs():
    songs_section = driver.find_element(By.CSS_SELECTOR, '.tracks')
    songs_section_list = songs_section.find_elements(By.CLASS_NAME, 'title-wr')
    songs_raw = []
    for song in songs_section_list:
        songs_raw.append(song.text)
    return songs_raw


def remove_special_characters(s):
    # remove all special characters except for hyphens
    return re.sub(r'[^a-zA-Z0-9\s-]', '', s)


if __name__ == '__main__':
    main()
