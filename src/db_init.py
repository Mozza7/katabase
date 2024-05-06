import sqlite3


def db_connect(chosen_year, is_main):
    con = sqlite3.connect('kp_albums.db')
    cur = con.cursor()
    if is_main == 1:
        try:
            cur.execute(f'DROP TABLE IF EXISTS y{chosen_year}')
        except sqlite3.OperationalError:
            pass
        try:
            cur.execute('DROP TABLE IF EXISTS mv')
            cur.execute('CREATE TABLE mv(video, vname, song, artist, channel, cid, verified)')
        except sqlite3.OperationalError:
            pass
        cur.execute(f"CREATE TABLE y{chosen_year}(artist, album, songs, url, mv, mvverified)")
        con.commit()
    return con, cur

