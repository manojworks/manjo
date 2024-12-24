import parser_configs
import os
import re

# Devanagari Unicode range
pattern = re.compile("[\u0900-\u097f]+")

def fetch_and_extract():
    
    all_dir = os.fsencode(parser_configs.all_lyrics_path)

    for fr in os.listdir(all_dir):
        f_name = os.fsdecode(fr)
        with open(parser_configs.all_lyrics_path+f_name, 'r') as fh:
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
                    # lower case and replace non-alphabets with '-'
                    en_part = en_part.lower()
                    en_part = re.sub(r"[^a-z\s]", '-', en_part)
                    hi_part = ln[ef:]
                    # replace non-devanagari characters with '-'
                    hi_part = re.sub(r"[^\u0900-\u097f\s]", '-', hi_part)
                    en_content += en_part + '\n'
                    hi_content += hi_part
        with open(parser_configs.en_image_lyrics_path + f_name, 'w') as fh:
            fh.write(en_content)
        with open(parser_configs.hi_image_lyrics_path + f_name, 'w') as fh:
            fh.write(hi_content)


fetch_and_extract()