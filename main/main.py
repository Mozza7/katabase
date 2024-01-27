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
                song_list.write(f'ARTIST: {artist} > ALBUM: {f} > SONGS: \n')
                songs = grab_songs()
                for item in songs:
                    song_list.write(f'{item}\n')
                song_list.write('\n')
            except NoSuchElementException:
                song_list.write(f'ARTIST: {artist} > ALBUM: {f} > ! NO SONGS FOUND !\n\n')


def grab_songs():
    songs_section = driver.find_element(By.CSS_SELECTOR, '.tracks')
    songs_section_list = songs_section.find_elements(By.CLASS_NAME, 'title-wr')
    songs_raw = []
    for song in songs_section_list:
        songs_raw.append(song.text)
    return songs_raw


def remove_special_characters(s):
    # Replace spaces with hyphens - this is to try to get around the issue with ' in album names
    s = s.replace("'", " ")
    s = s.replace(" ", "-")
    s = s.replace(".", "-")
    s = s.replace("---", "-")
    s = s.replace("--", "-")
    # Use regular expression to remove special characters, excluding apostrophes in words
    return re.sub(r'[^a-zA-Z0-9\s-]|(?<=\w)\'(?=\w)', '', s)


def music_video():
    # Open the text file for reading
    with open("songlist.txt", 'r', encoding='utf-8') as file:
        # Initialize variables to store current artist, album, and songs
        current_artist = None
        current_album = None
        current_songs = []

        # Iterate over the lines in the file
        for line in file:
            # Clean up the line by stripping leading and trailing whitespaces
            line = line.strip()

            # Debug print to check each line
            print(f"DEBUG: {line}")

            # Check if the line contains ">"
            if ">" in line:
                # Split the line at ">" and extract words between them
                parts = line.split(">")

                # Clean up parts by stripping leading and trailing whitespaces
                parts = [part.strip() for part in parts]

                # Debug print to check key and parts
                print(f"DEBUG: Key: {parts[0]}, Parts: {parts[1:]}")

                # If the key is "ARTIST", update the current artist
                if parts[0] == "ARTIST":
                    # If this is not the first iteration, print the accumulated information
                    if current_artist:
                        print(f"ARTIST: {current_artist}, ALBUM: {current_album}, SONGS: {'; '.join(current_songs)};\n")
                    # Reset variables for the new artist
                    current_artist = parts[1]
                    current_album = None
                    current_songs = []

                # If the key is "ALBUM", update the current album
                elif parts[0] == "ALBUM":
                    current_album = parts[1]

                # If the key is "SONGS", read and store all songs until the next artist
                elif parts[0] == "SONGS":
                    # Split songs using ";" and strip each song
                    current_songs = [song.strip() for song in parts[1].split(';')]

        # Print the last artist information after the loop
        if current_artist:
            print(f"ARTIST: {current_artist}, ALBUM: {current_album}, SONGS: {'; '.join(current_songs)};")


if __name__ == '__main__':
    # main() # commented out as this is working now. need to get the next section working
    music_video()
    driver.quit()
