import glob
from bs4 import BeautifulSoup
import logging
import re
import parser_configs

logging.basicConfig(filename="hl4u.log", encoding='utf-8', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())

f_out = open(parser_configs.output_file_path, "w")
f_err = open(parser_configs.error_log, "w")


def parse_songs():

    file_list = glob.glob(parser_configs.html_files_path)
    for filepath in file_list:
        parse_attributes(filepath)


def parse_attributes(filepath):

    try:
        with open(filepath, encoding="latin-1") as fp:
            soup = BeautifulSoup(fp, "html.parser")
            each_song = soup.find_all("table", {"class": "b1 w760 bgff pad2 allef"})
            for track in each_song:

                track_name = ""
                singer_list = ""
                music_dirs_list = ""
                actors_list = ""
                album = ""
                writers_list = ""
                categories_list = ""
                release = ""

                rows = track.find_all("tr")
                for ir, row in enumerate(rows):
                    cols = row.find_all("td")

                    for ic, col in enumerate(cols):
                        if ir == 0 and ic == 1:
                            track_name = col.find("a").text
                            # remove apostrophe from track name
                            track_name = track_name.replace("'", "")
                        elif ir == 0 and ic == 2:
                            singer_list = ""
                            singers = col.find_all("a")
                            for singer in singers:
                                if singer.text[-1] == ',':
                                    singer_list += singer.text[:-1]
                                else:
                                    singer_list += singer.text
                                singer_list += ","
                            singer_list = singer_list[:-1]
                            singer_list = singer_list.replace("'", "")
                        elif ir == 0 and ic == 3:
                            music_dirs_list = ""
                            music_dirs = col.find_all("a")
                            for m_dir in music_dirs:
                                if m_dir.text[-1] == ',':
                                    music_dirs_list += m_dir.text[:-1]
                                else:
                                    music_dirs_list += m_dir.text
                                music_dirs_list += ","
                            music_dirs_list = music_dirs_list[:-1]
                            music_dirs_list = music_dirs_list.replace("'", "")
                        elif ir == 0 and ic == 4:
                            actors_list = ""
                            actors = col.find_all("a")
                            for actor in actors:
                                if actor.text[-1] == ',':
                                    actors_list += actor.text[:-1]
                                else:
                                    actors_list += actor.text
                                actors_list += ","
                            actors_list = actors_list[:-1]
                            actors_list = actors_list.replace("'", "")
                        elif ir == 1 and ic == 0:
                            album_release = col.find("a").text.strip()
                            yy_part = re.search(r'\(\d{4}\)', album_release)
                            if yy_part:
                                ind = album_release.rindex(yy_part.group(0))
                                album = album_release[:ind]
                                album = album.replace("'", "")
                                release = yy_part.group(0)[1:-1]
                            else:
                                album = album_release
                                release = ""
                        elif ir == 1 and ic == 1:
                            writers_list = ""
                            lyrics = col.find_all("a")
                            for ly in lyrics:
                                if ly.text[-1] == ',':
                                    writers_list += ly.text[:-1]
                                else:
                                    writers_list += ly.text
                                writers_list += ","
                            writers_list = writers_list[:-1]
                            writers_list = writers_list.replace("'", "")
                        elif ir == 1 and ic == 2:
                            categories_list = ""
                            categories = col.find_all("a")
                            for cat in categories:
                                if cat.text[-1] == ',':
                                    categories_list += cat.text[:-1]
                                else:
                                    categories_list += cat.text
                                categories_list += ","
                            categories_list = categories_list[:-1]
                            categories_list = categories_list.replace("'", "")
                        else:
                            pass
                duration = ""
                song_attr = f"{track_name}|{album}|{release}|{duration}|{categories_list}|{music_dirs_list}|{singer_list}|{writers_list}|{actors_list}\n"

                f_out.write(song_attr)
    except Exception as e:
        logging.debug("Exception occurred while parsing file: %s", filepath)
        logging.debug(e)
        logging.debug(track_name, singer_list, music_dirs_list, actors_list, album, writers_list, categories_list)
        f_err.write(filepath + "\n")
    else:
        logging.debug("Successfully parsed file: %s ", filepath)


parse_songs()

f_out.close()
f_err.close()