class Track:

    def __init__(self, tid, track_name, album=None, release=None, duration=None, category_list=None,
                 composer_list=None, singer_list=None, writer_list=None, actor_list=None, notes=None):
        self._track_id = tid
        self._track_name = track_name
        self._album = album
        self._release_year = release
        self._duration = duration
        self._categories = category_list
        self._composers = composer_list
        self._singers = singer_list
        self._writers = writer_list
        self._actors = actor_list
        self._notes = notes

    def piped_str(self) -> str:

        piped_fmt = f"{self._track_id}|"
        piped_fmt += f"{self._track_name}|" if self._track_name else "None|"
        piped_fmt += f"{self._album}|" if self._album else "None|"
        piped_fmt += f"{self._release_year}|" if self._release_year else "None|"
        piped_fmt += f"{self._duration}|" if self._duration else "None|"

        if self._categories == set():
            piped_fmt += "None|"
        else:
            piped_fmt += ",".join(self._categories) + "|"

        if self._composers == set():
            piped_fmt += "None|"
        else:
            piped_fmt += ",".join(self._composers) + "|"

        if self._singers == set():
            piped_fmt += "None|"
        else:
            piped_fmt += ",".join(self._singers) + "|"

        if self._writers == set():
            piped_fmt += "None|"
        else:
            piped_fmt += ",".join(self._writers) + "|"

        if self._actors == set():
            piped_fmt += "None|"
        else:
            piped_fmt += ",".join(self._actors) + "|"

        piped_fmt += f"{self._notes}" if self._notes else "None"

        return piped_fmt

    def __str__(self):
        return f"ID: {self._track_id} Track: {self._track_name}"

    def __eq__(self, other):
        # deliberately left out certain fields for comparison
        if isinstance(other, Track):
            return (self._track_name == other._track_name
                    and self._album == other._album
                    and self._release_year == other._release_year
                    and self._composers == other._composers
                    and self._singers == other._singers
                    and self._writers == other._writers)
        return False