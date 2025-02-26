"""
Files on disk - filename is also the title of the track. File contents are track lyrics.
DB - track title is described by title_en.
Task - find the file on disk that matches the track title in db and update the lyrics_en column in table with the contents of the file.
Do the same with and lyrics_hi column that maps to a different folder that contains Hindi lyrics.

There are ~60,000 titles in DB.

"""
import logging
import os

import psycopg2
import re

import parser_configs as pc

logging.basicConfig(filename="titles.log", encoding='utf-8', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())

def fetch_titles_from_db(cnx):

    cursor = cnx.cursor()


    cursor.execute("SELECT id, title_en FROM mweb.songs_tracks where lyrics_en is null")

    titles = cursor.fetchall()

    db_map = {}
    for title in titles:
        normalized = normalize_title(title[1])
        if re.match('^[a-z]+$', normalized) is None:
            logging.debug(f'failed for normalize title in database: {title}')
            continue
        else:
            db_map[normalized] = (title[0], title[1])

    cursor.close()

    return db_map

def normalize_title(title):
    title = title.strip()
    title = re.sub('[0-9]', '', title)
    title = title.replace('_', '')
    title = title.replace('-', '')
    title = title.replace('.', '')
    title = title.replace('!', '')
    title = title.replace('&', '')
    title = title.replace(' ', '')
    return title.lower()

def fetch_lyrics_from_files():

    file_map = {}
    lyrics_files = os.listdir(pc.en_image_lyrics_path)
    for file in lyrics_files:
        with open(os.path.join(pc.en_image_lyrics_path, file), 'r') as lyrics:
            dot_index = file.rindex('.')
            f_name = file[:dot_index]
            f_name = normalize_title(f_name)
            # log if there are any characters other than a-z
            if re.match('^[a-z]+$', f_name) is None:
                logging.debug(f'failed for normalize title in file system: {file} with name {f_name}')
                continue
            else:
                file_map[f_name] = (lyrics.name, lyrics.read())

    return file_map

def update_lyrics_en(cnx, lyrics_en, song_id):
    cursor = cnx.cursor()
    upd_stmt = """update mweb.songs_tracks set lyrics_en = %s where id = %s"""
    try:
        cursor.execute(upd_stmt, (lyrics_en, song_id))
        cnx.commit()
    except psycopg2.DatabaseError as e:
        logging.error(f'failed to update lyrics_en in database for song id {song_id}: {e}')
    finally:
        cursor.close()


if __name__ == '__main__':

    connection = psycopg2.connect(
        host="10.0.0.72",
        database="manjo",
        user="manjo",
        password="manjo"
    )

    titles_in_db = fetch_titles_from_db(connection)
    titles_in_files = fetch_lyrics_from_files()

    for db_title in titles_in_db.keys():
        if db_title in titles_in_files:
            title_in_db = titles_in_db[db_title][1]
            db_id = titles_in_db[db_title][0]
            title_lyrics = titles_in_files[db_title][1]

            if title_in_db.lower() in title_lyrics:
                logging.debug(f'match found for {db_title}')
                update_lyrics_en(connection, title_lyrics, db_id)

    connection.close()