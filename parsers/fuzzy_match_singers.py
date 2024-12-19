# 1. create a master list of singers from good singers file
# 2. create list of parsed singers from all singers file
# 3. using fuzzy match to match singers from master list to parsed list
# 4. list all matched singers against the good singer
import csv
from configparser import ConfigParser
import connections.pg_connect as pg
import psycopg2
from thefuzz import fuzz
import pickle
import parser_configs


def fetch_clean_singers():
    with open(parser_configs.GOOD_SINGERS_FILE, 'r') as file:
        singers = file.readlines()

    ignore_list = [94, 100, 109, 118, 130, 131, 147, 187, 195, 205, 215, 255, 256, 293, 304, 332]

    wiki_singers = [singer.split(',')[1].strip() for singer in singers if singer.split(',')[0] not in ignore_list]

    return wiki_singers

def fetch_all_singers():
    with open(parser_configs.ALL_SINGERS_FILE, 'r') as file:
        singers = file.readlines()

    bad_singers = list(set([singer.split(',')[1].strip() for singer in singers]))
    return bad_singers

def save_singers_not_perfect_match():

    good_singers = fetch_clean_singers()
    all_singers = fetch_all_singers()

    fw = open(parser_configs.FUZZY_MATCHED_SINGERS_FILE, 'w')

    for gs in good_singers:
        for s in all_singers:
            fr = fuzz.ratio(gs, s)
            # try with anything between 85% and less than 100% match
            if 85 < fr < 100:
                fw.write(s + ',' + gs + '\n')

    fw.close()

def singers_perfect_match():

    perfect_singers_f = parser_configs.PARFECT_MATCHED_SINGERS_FILE
    f = open(perfect_singers_f, "w")

    good_singers = fetch_clean_singers()
    all_singers = fetch_all_singers()

    for gs in good_singers:
        for s in all_singers:
            fr = fuzz.ratio(gs, s)
            if  fr == 100:
                f.write(s + ',' + s + '\n')

    f.close()



    # look at all rows of public.all_tracks for columns - singer_0, singer_1, singer_2, singer_3, singer_4
    # and see if there is a match with the near matches values
    # if there is a match, then update the corresponding singer column of wh.all_tracks with the
    # key of the near_matches dictionary
    # while updating, check if the singer is already present in the singer_0, singer_1, singer_2, singer_3, singer_4
    # if it is, then do not update the column and retain the row id key in a separate list

def update_near_singer_matches():

    with open(parser_configs.FUZZY_MATCHED_SINGERS_FILE, 'r') as fr:
        near_matches = csv.reader(fr)
        near_matches = {row[0]: row[1] for row in near_matches}

    config = pg.load_config(parser_configs.PG_DATABASE_INI)
    conn = pg.init_db(config)
    db = conn.cursor()
    db.execute(parser_configs.SQL_ALL_SINGERS)
    all_singers = db.fetchall()
    for row in all_singers:
        for i in range(1, 5):
            if row[i] in near_matches.keys():
                print('update id ' , row[0], 'old val ' , row[i], 'new val ' , near_matches[row[i]])
                sel_stmt = f"select singers from wh.all_tracks where id = {row[0]}"
                db.execute(sel_stmt)
                wh_arr = db.fetchone()[0]
                if wh_arr is None:
                    wh_arr = []
                wh_arr = [val for val in wh_arr if val is not None]
                print(wh_arr)
                if near_matches[row[i]] not in wh_arr:
                    wh_arr.append(near_matches[row[i]])

                    upd_stmt = f"update wh.all_tracks set singers = array{wh_arr} where id = {row[0]}"
                    print(upd_stmt)
                    db.execute(upd_stmt)
                    conn.commit()

    conn.close()

def fetch_clean_composers():
    with open(parser_configs.GOOD_COMPOSERS_FILE, 'r') as file:
        comps = file.readlines()
    return [c.strip() for c in comps]

def fetch_all_composers():
    with open(parser_configs.ALL_COMPOSERS_FILE, 'r') as file:
        comps = file.readlines()

    all_comps = [(c.split(',')[0], c.split(',')[1].strip()) for c in comps]
    return all_comps

def composers_imperfect_match():

    perfect_composers_f = parser_configs.COMPOSERS_IMPERFECT_MATCH
    f = open(perfect_composers_f, "w")

    good_composers = fetch_clean_composers()
    all_composers = fetch_all_composers()

    for gc in good_composers:
        for c in all_composers:
            fr = fuzz.ratio(gc.strip(), c[1].strip())
            if 85 < fr < 100:
                f.write(c[0] + ',' + c[1] + ',' + gc + '\n')

    f.close()


def verify_update_imperfect_composers():
    with open(parser_configs.COMPOSERS_IMPERFECT_MATCH, 'r') as fr:
        rdr = csv.reader(fr)
        imperfect_matches = {row[0]: (row[1], row[2]) for row in rdr}

    config = pg.load_config(parser_configs.PG_DATABASE_INI)
    conn = pg.init_db(config)
    db = conn.cursor()
    db.execute(parser_configs.SQL_ALL_COMPOSERS)
    all_composers = db.fetchall()

    # iterate over all tracks in wh schema
    # retrieve the composer array
    # check the contents of the array.
    # if for the given id, the composer array contains the composer name
    # its all good. otherwise add it to the array.
    for row in all_composers:
        row_id = row[0]

        subs_composer = imperfect_matches.get(str(row_id))
        if subs_composer is None:
            continue

        curr_comp = row[1]
        if curr_comp is None:
            curr_comp = []
        else:
            curr_comp = [val for val in curr_comp if val]
        if subs_composer[1] not in curr_comp:
            curr_comp.append(subs_composer[1])
            upd_stmt = f"update wh.all_tracks set composers = array{curr_comp} where id = {row_id}"
            print(upd_stmt)
            db.execute(upd_stmt)
            conn.commit()

    conn.close()
    fr.close()


def fetch_clean_writers():
    with open(parser_configs.GOOD_WRITERS_FILE, 'r') as file:
        wr = file.readlines()
    return set([c.strip() for c in wr])

def fetch_all_writers():
    with open(parser_configs.ALL_WRITERS_FILE, 'r') as file:
        wr = file.readlines()

    all_writers = [(w.split(',')[0], w.split(',')[1].strip()) for w in wr]
    return all_writers

def writers_perfect_match():

    perfect_f = parser_configs.PERFECT_WRITERS
    f = open(perfect_f, "w")

    cw = fetch_clean_writers()
    all_w = fetch_all_writers()

    for gs in cw:
        for s in all_w:
            fr = fuzz.ratio(gs, s[1])
            if  fr == 100:
                f.write(s[0] + ',' +  s[1] + '\n')

    f.close()

def update_good_writers():
    config = pg.load_config(parser_configs.PG_DATABASE_INI)
    conn = pg.init_db(config)
    db = conn.cursor()

    with open(parser_configs.PERFECT_WRITERS, 'r') as fr:
        rdr = csv.reader(fr)

        for writer in rdr:
            stmt = f"update wh.all_tracks set writers = array_append(writers, '{writer[1]}') where id = {writer[0]}"
            print(stmt)
            db.execute(stmt)
            conn.commit()

    conn.close()

def writers_imperfect_match():

    f = parser_configs.WRITERS_IMPERFECT_MATCH
    f = open(f, "w")

    clean = fetch_clean_writers()
    all = fetch_all_writers()

    for c in clean:
        for w in all:
            fr = fuzz.ratio(c.strip(), w[1].strip())
            if 85 < fr < 100:
                f.write(w[0] + ',' + w[1] + ',' + c + '\n')

    f.close()


def verify_update_imperfect_writers():
    with open(parser_configs.WRITERS_IMPERFECT_MATCH, 'r') as fr:
        rdr = csv.reader(fr)
        imperfect_matches = {row[0]: (row[1], row[2]) for row in rdr}

    config = pg.load_config(parser_configs.PG_DATABASE_INI)
    conn = pg.init_db(config)
    db = conn.cursor()
    db.execute(parser_configs.SQL_ALL_WRITERS)
    all_writers = db.fetchall()

    for row in all_writers:
        row_id = row[0]

        subs_writer = imperfect_matches.get(str(row_id))
        if subs_writer is None:
            continue

        curr_writer = row[1]
        if curr_writer is None:
            curr_writer = []
        else:
            curr_writer = [val for val in curr_writer if val]
        if subs_writer[1] not in curr_writer:
            curr_writer.append(subs_writer[1])
            upd_stmt = f"update wh.all_tracks set writers = array{curr_writer} where id = {row_id}"
            print(upd_stmt)
            db.execute(upd_stmt)
            conn.commit()

    conn.close()
    fr.close()

verify_update_imperfect_composers()