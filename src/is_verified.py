from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import time
import sys


def channel_verified(cid_list, cur, kp_db, driver):
    run_number = 0
    for i in cid_list:
        is_verified = cur.execute("""SELECT verified FROM mv WHERE cid=?""", (i,)).fetchone()
        if is_verified == 'tbc':
            run_number += 1
            format_url = f'https://www.youtube.com/channel/{i}'
            if verify_element_exist(format_url, run_number, driver):
                print(f'{format_url} IS VERIFIED')
                cur.execute("""UPDATE mv SET verified = 1 WHERE cid=?""", (i,))
            else:
                print(f'{format_url} IS NOT VERIFIED')
                cur.execute("""UPDATE mv SET verified = 0 WHERE cid=?""", (i,))
        else:
            continue
    kp_db.commit()
    for i in cid_list:
        ver_value = cur.execute("""SELECT verified FROM mv WHERE cid=?""", (i,)).fetchone()
        if ver_value == 2:
            manual_verify(i, cur, driver)
        else:
            pass


def verify_element_exist(url, run_number, driver):
    verified_badge = ('ytd-channel-name.ytd-c4-tabbed-header-renderer > ytd-badge-supported-renderer:nth-child(2) '
                      '> div:nth-child(1) > yt-icon:nth-child(1) > yt-icon-shape:nth-child(1) > icon-shape:nth-child(1)'
                      ' > div:nth-child(1)')
    artist_badge = ('ytd-channel-name.ytd-c4-tabbed-header-renderer > ytd-badge-supported-renderer:nth-child(2) '
                    '> div:nth-child(1) > yt-icon:nth-child(1) > yt-icon-shape:nth-child(1) > icon-shape:nth-child(1) '
                    '> div:nth-child(1) > svg:nth-child(1)')
    cookie_accept_2 = ('.KZ9vpc > form:nth-child(3) > div:nth-child(1) > div:nth-child(1) > '
                       'button:nth-child(1) > span:nth-child(4)')
    driver.get(url)
    if run_number == 1:
        try:
            WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, cookie_accept_2)))
            driver.find_element(By.CSS_SELECTOR, cookie_accept_2).click()
        except NoSuchElementException:
            try:
                driver.find_element(By.CSS_SELECTOR, 'input.ytd-searchbox').click()
            except NoSuchElementException:
                print('Failed to load page. Exiting..')
                driver.quit()
                sys.exit()
    else:
        pass
    if driver.find_elements(By.CSS_SELECTOR, artist_badge) or driver.find_elements(By.CSS_SELECTOR, verified_badge):
        print('VERIFIED')
        return True
    else:
        time.sleep(5)
        if driver.find_elements(By.CSS_SELECTOR, artist_badge) or driver.find_elements(By.CSS_SELECTOR, verified_badge):
            print('VERIFIED')
            return True
        else:
            print('NOT VERIFIED')
            return False


def manual_verify(cid, cur, driver):
    do_manual_verify = ('The script has complete. There are some videos uploaded by channels without a \n'
                        'verification tick. Would you like to iterate through the list to manually verify these \n'
                        'channels? NOTE: This is used to help pick out a channel that would upload the correct \n'
                        'video and not a fan made video. (Y/N): ')
    if do_manual_verify.casefold() == 'y':
        print('Please answer questions with either a Y for yes or an N for no: ')
        for i in cid:
            channel_name = cur.execute("""SELECT cname FROM mv WHERE cid=?""", (i,)).fetchone()
            yes_channel = input(f'Should {channel_name} (www.youtube.com/channel/{cid}) be verified (Y/N)?:')
            if yes_channel.casefold() == 'y':
                cur.execute("""UPDATE mv SET verified=1 WHERE cid=?""", (cid,))
            elif yes_channel.casefold() == 'n':
                cur.execute("""UPDATE mv SET verified=0 WHERE cid=?""", (cid,))
            else:
                print('Input invalid. You will need to manually change this in the database or re-run script.')
                cur.execute("""UPDATE mv SET verified=2 WHERE cid=?""", (cid,))
    elif do_manual_verify.casefold() == 'n':
        print('No problem, if you change your mind you can manually open the "kp_albums.db" database and open the\n'
              '"mv" table and change the value in the "verified" column to a 1 for verified, 0 for not. Or run '
              '"alter_verification.bat" to use a script to do this.')
        time.sleep(1)
        print('Cleaning up..')
        time.sleep(2)
        print('Exiting script..')
        time.sleep(1)
        driver.quit()
        sys.exit()
    else:
        print('Input not recognised. Expected result either: Y or N\nPlease try again..\n\n')
        manual_verify(cid, cur, driver)


if __name__ == '__main__':
    print('is_verified.py is currently not designedto be ran standalone. This is in development')
