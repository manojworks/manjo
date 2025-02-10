import csv
import re
import psycopg2
from psycopg2 import DatabaseError
import logging

import parser_configs as pc

ARRAY_PREFIX = 'ARRAY['
ARRAY_SUFFIX = ']'
STRING_WRAPPER = '\''
INSERT_STMT = "insert into mweb.tracks (title, album, release_year, duration, categories, composers, singers, writers, actors, notes) values ({}, {}, {}, {}, {}, {}, {}, {}, {}, {})"

connection = psycopg2.connect(
    host="hostname",
    database="database",
    user="username",
    password="password"
)

logging.basicConfig(filename="csv2db.log", encoding='utf-8', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())

def convert_csv_to_db():

    #ctr = 0

    cursor = connection.cursor()

    with open(pc.DEDUPED_TRACKS, 'rt') as csvfile:
        csvfile = csv.reader(csvfile, delimiter='|')
        for row in csvfile:
            try:
                #print(row)

                # ignore id, postgres will supply its own
                id_for_test = row[0]

                # clean up title - replace - with space, / with space, . with empty
                if row[1].strip() == 'None':
                    title = 'NULL'
                else:
                    title = row[1].strip().replace('-', ' ').replace('/', ' ').replace('.', '')
                    # remove all more than one whitespace
                    title = STRING_WRAPPER + title.replace(r'\s{2,}', ' ') + STRING_WRAPPER

                # from album only remove extra white spaces
                if row[2].strip() == 'None':
                    album = 'NULL'
                else:
                    album = STRING_WRAPPER + row[2].strip().replace(r'\s{2,}', ' ') + STRING_WRAPPER

                # release year should all be 4 digits or null
                release_year = row[3].strip()
                if re.match(r'^[1-2][\d]{3}$', release_year) is None:
                    #print(id_for_test, release_year)
                    release_year = 'NULL'

                # duration is number of seconds. should be numeric or None
                duration = row[4].strip()
                if re.match(r'^[0-9]*$', duration) is None:
                    #print(id_for_test, duration)
                    duration = 'NULL'

                # categories is null or a comma separated string which is to be converted into postgres array of text
                categories = make_pg_array(row[5])
                #print(id_for_test, categories)

                # composers is null or a comma separated string which is to be converted into postgres array of text
                composers = make_pg_array(row[6])
                #print(id_for_test, composers)

                # singers is null or a comma separated string which is to be converted into postgres array of text
                singers = make_pg_array(row[7])
                #print(id_for_test, singers)

                # writers is null or a comma separated string which is to be converted into postgres array of text
                writers = make_pg_array(row[8])
                #print(id_for_test, writers)

                # actors is null or a comma separated string which is to be converted into postgres array of text
                actors = make_pg_array(row[9])
                #print(id_for_test, actors)

                # from notes only remove extra white spaces
                if row[10].strip() == 'None':
                    notes = 'NULL'
                else:
                    notes = STRING_WRAPPER + row[10].strip().replace(r'\s{2,}', ' ') + STRING_WRAPPER
            except IndexError:
                print(row)
                continue

            insert_stmt = INSERT_STMT.format(title, album, release_year, duration, categories, composers, singers, writers, actors, notes)
            try:
                cursor.execute(insert_stmt)
            except DatabaseError as e:
                print(insert_stmt)
                print(e)
                logging.debug(row)
                logging.debug(insert_stmt)

            # ctr += 1
            # if ctr == 10:
            #     break

    connection.commit()
    connection.close()

def make_pg_array(param):

    param = param.strip()
    if param == 'None':
        param = 'NULL'
    else:
        parts = param.split(',')
        param = ARRAY_PREFIX
        for c in parts:
            param += '\'' + c + '\'' + ','
        # walk back one comma
        param = param[:-1]
        param += ARRAY_SUFFIX

    return param

convert_csv_to_db()
