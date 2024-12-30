import parser_configs
import os
import re

# Devanagari Unicode range
pattern = re.compile("[\u0900-\u097f]+")

def clean_lyrics(en, hi):
    # apply to en
    en = re.sub(r'[^a-zA-Z]', ' ', en)

    # apply to hi
    hi = re.sub(r"[^\u0900-\u097f]", ' ', hi)

    # remove extra spaces from both
    en = re.sub(r'\s+', ' ', en)
    en = en.lower().strip()
    hi = re.sub(r'\s+', ' ', hi)
    hi = hi.strip()

    en += '\n'
    hi += '\n'

    return en, hi


def fetch_and_extract():

    uniq_pairs = {tuple()}
    counter = 1

    f_pairs = open(parser_configs.en_hi_lyrics_pairs, 'w')

    all_dir = os.fsencode(parser_configs.all_lyrics_path)

    for fr in os.listdir(all_dir):
        f_name = os.fsdecode(fr)
        with open(parser_configs.all_lyrics_path + f_name, 'r') as fh:
            hi_content = ''
            en_content = ''
            lines = fh.readlines()
            for ln in lines:
                # find the first (ef) english character
                # rest of line is hindi
                part = re.search(pattern, ln)
                if part:
                    ef = part.start()
                    en_part = ln[:ef]
                    hi_part = ln[ef:]
                    en_part, hi_part = clean_lyrics(en_part, hi_part)
                    if len(en_part.strip()) == 0 or len(hi_part.strip()) == 0:
                        continue
                    en_content += en_part
                    hi_content += hi_part

                    if (en_part, hi_part) in uniq_pairs:
                        continue
                    else:
                        f_pairs.write('[EN-{}]{}'.format(counter, en_part))
                        f_pairs.write('[HI-{}]{}'.format(counter, hi_part))
                        counter += 1
                        uniq_pairs.add((en_part, hi_part))




        with open(parser_configs.en_image_lyrics_path + f_name, 'w') as fh:
            fh.write(en_content)
        with open(parser_configs.hi_image_lyrics_path + f_name, 'w') as fh:
            fh.write(hi_content)

    f_pairs.close()

fetch_and_extract()
