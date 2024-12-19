import re
import parser_configs
from model.track import Track

MAX_PERFORMERS = 10

def dedup_tracks():
    de_duped_file = parser_configs.DEDUPED_TRACKS
    fp_dedup = open(de_duped_file, 'w')
    if not fp_dedup:
        print(f"Error opening file {de_duped_file}")
        return

    duped_file = parser_configs.DUPED_TRACKS
    fp_duped = open(duped_file, 'w')
    if not fp_duped:
        print(f"Error opening file {duped_file}")
        return

    # Read the file
    first_parse = parser_configs.PARSED_RAW_DATA
    with open(first_parse, 'r') as file:
        tracks = file.readlines()

    de_duped_tracks = []
    duped_tracks = []

    # Deduplicate the list
    for tr in tracks:
        print(tr)
        tr, notes = separate_notes(tr)
        fields = tr.split('|')
        track_id = fields[0].strip() if fields[0] != 'None' else None
        track_name = fields[1].strip().replace(',', '') if fields[1] != 'None' else None
        album = fields[2].strip() if fields[2] != 'None' else None
        release = fields[3].strip() if fields[3] != 'None' else None
        duration = fields[4].strip() if fields[4] != 'None' else None
        fields[5] = fields[5].strip()
        category = set(fields[5].split(',') if fields[5] != 'None' else [])
        if len(category) > MAX_PERFORMERS:
            lst = list(category)
            lst = lst[:MAX_PERFORMERS]
            category = set(lst)
        fields[6] = fields[6].strip()
        composer = set(fields[6].split(',') if fields[6] != 'None' else [])
        if len(composer) > MAX_PERFORMERS:
            lst = list(composer)
            lst = lst[:MAX_PERFORMERS]
            composer = set(lst)
        fields[7] = fields[7].strip()
        singers = set(fields[7].split(',') if fields[7] != 'None' else [])
        if len(singers) > MAX_PERFORMERS:
            lst = list(singers)
            lst = lst[:MAX_PERFORMERS]
            singers = set(lst)
        fields[8] = fields[8].strip()
        lyricist = set(fields[8].split(',') if fields[8] != 'None' else [])
        if len(lyricist) > MAX_PERFORMERS:
            lst = list(lyricist)
            lst = lst[:MAX_PERFORMERS]
            lyricist = set(lst)
        fields[9] = fields[9].strip()
        actors = set(fields[9].split(',') if fields[9] != 'None' else [])
        if len(actors) > MAX_PERFORMERS:
            lst = list(actors)
            lst = lst[:MAX_PERFORMERS]
            actors = set(lst)
        new_track = Track(track_id, track_name, album, release, duration, category, composer, singers, lyricist, actors,
                          notes)
        if new_track in de_duped_tracks:
            duped_tracks.append(new_track)
            fp_duped.write(new_track.piped_str() + '\n')
        else:
            de_duped_tracks.append(new_track)
            fp_dedup.write(new_track.piped_str() + '\n')

    fp_dedup.close()
    fp_duped.close()



def separate_notes(ln):
    #ln = "478|Karvatein Badal Badal|Janeman (zzz Udhas)|2000|None||Lalit (jkkjk) Sen|Pankaj Udhas|Lalit Sen|"
    #ln = "kjshjkdsh kdsjld"
    rx = re.compile(r'\((.*?)\)')
    notes = rx.findall(ln)
    #print('|'.join(notes) if len(notes) else None)
    ln = re.sub(rx, '', ln)
    #print(ln)
    return ln, ''.join(notes) if len(notes) else None


if __name__ == '__main__':
    dedup_tracks()