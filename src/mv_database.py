def mv_database(filename, song, artist, os, cur, cid_list, chosen_year_q, kp_db, re):
    with open(filename, 'r', encoding='utf-8') as input_file:
        lines = input_file.readlines()
    vid_lines = [line.split(':')[1].strip() for line in lines if 'video_id' in line]
    cid_lines = [line.split(':')[1].strip() for line in lines if 'channel_id' in line]
    vname_lines = [line.split(':')[1].strip() for line in lines if 'video_name' in line]
    cname_lines = [line.split(':')[1].strip() for line in lines if 'channel_name' in line]
    year_check = [line.split(':')[1].strip() for line in lines if 'upload_year' in line]
    for vid, cid, vname, cname, eyear in zip(vid_lines, cid_lines, vname_lines, cname_lines, year_check):
        mv_exist = cur.execute("""SELECT video FROM mv WHERE video=?""", (vid,)).fetchone()
        if artist not in vname:
            print(f'Video title does not contain {artist}. Including video but may be inaccurate. Title: {vname}')
            verified = 3
        elif song not in vname:
            print(f'Video title does not contain {song}. Including video but may be inaccurate. Title: {vname}')
            verified = 3
        else:
            verified = 0
        cid_list.append(cid)
        if mv_exist:
            if eyear[:4] != chosen_year_q:
                print(f'Video uploaded in wrong year: {eyear}. Skipping this video..')
                continue
            else:
                print(f'Video with ID {vid} already exists in database. Skipping {song} by {artist}')
                video_type(vname, vid, cur, re)
        else:
            print(f'[DEBUG] EXTRACTED YEAR = {eyear}\nCHOSEN YEAR = {chosen_year_q}')
            if eyear[:4] == chosen_year_q:
                cur.execute("""INSERT INTO mv (video, vname, song, artist, channel, cid, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (vid, vname, song, artist, cname, cid, verified,))
                print(f'Video with ID {vid} and name {vname} added to database')
                video_type(vname, vid, cur, re)
            else:
                print(f'Video uploaded in wrong year: {eyear}. Skipping this video..')
                continue
    kp_db.commit()


def check_string_for_phrases(input_string, target_phrases, re):
    for phrase in target_phrases:
        if re.search(r'\b' + re.escape(phrase) + r'\b', input_string, flags=re.IGNORECASE):
            return True
    return False


def video_type(vid, yt_id, cur, re):
    teaser_words = ['teaser', 'teaser video', 'spoiler', 'highlight medley']
    reaction_words = ['reaction']
    mv_words = ['mv', 'music video', 'm/v', '뮤비', 'official video']
    dance_words = ['dance', 'practice', '춤', '관행', '춤 연습', '나 춤 연습해']
    perf_words = ['performance', 'stage', 'live', 'inkigayo', "[it's Live]", '[BE ORIGINAL]', '1theKILLPO', 'tour']
    lyric_words = ['lyric', 'color coded', 'lyrics', 'line distribution', '가사']
    youtube_link = f'https://www.youtube.com/watch?v={yt_id}'
    if check_string_for_phrases(vid, teaser_words, re):
        cur.execute("""INSERT INTO video_type (name, vid_id, vid_type) VALUES (?, ?, ?)""",
                    (vid, youtube_link, 'teaser'))
    elif check_string_for_phrases(vid, reaction_words, re):
        cur.execute("""INSERT INTO video_type (name, vid_id, vid_type) VALUES (?, ?, ?)""",
                    (vid, youtube_link, 'reaction'))
    elif check_string_for_phrases(vid, mv_words, re):
        cur.execute("""INSERT INTO video_type (name, vid_id, vid_type) VALUES (?, ?, ?)""",
                    (vid, youtube_link, 'mv'))
    elif check_string_for_phrases(vid, dance_words, re):
        cur.execute("""INSERT INTO video_type (name, vid_id, vid_type) VALUES (?, ?, ?)""",
                    (vid, youtube_link, 'dance'))
    elif check_string_for_phrases(vid, perf_words, re):
        cur.execute("""INSERT INTO video_type (name, vid_id, vid_type) VALUES (?, ?, ?)""",
                    (vid, youtube_link, 'performance'))
    elif check_string_for_phrases(vid, lyric_words, re):
        cur.execute("""INSERT INTO video_type (name, vid_id, vid_type) VALUES (?, ?, ?)""",
                    (vid, youtube_link, 'lyric'))
    else:
        cur.execute("""INSERT INTO video_type (name, vid_id, vid_type) VALUES (?, ?, ?)""",
                    (vid, youtube_link, 'other'))
