import json
import numpy as np
import sys

class LettersMap:
    def __init__(self, letters="en"):
        """ Unicode list of letters in a language
        lang: List with unicodes
        """
        if letters == "en":
            # small case chars in EN
            # care for the upper bound of range object
            #TODO: not sure why list with three items was added
            self.letters = [chr(alpha) for alpha in range(97, 122 + 1)] + ["é", "è", "á"]
        else:
            self.lang_spec = json.load(open(letters, encoding="utf-8"))
            self.number_sym_map = self.lang_spec["number_sym_map"]
            self.letters = self.lang_spec["glyphs"]

        self.index_char = {}
        self._create_index()

    def _create_index(self):

        # populate first 17 indexes with this. here _ is the pad, $ is for start, # for end, * for mask,
        # then comes apostrophe U+0027, followed by % and ! being unused
        self.char_index = {"_": 0, "$": 1, "#": 2, "*": 3, "'": 4, "%": 5, "!": 6, "?": 7, ":": 8, " ": 9, "-": 10, ",": 11,
                    ".": 12, "(": 13, ")": 14, "/": 15, "^": 16}

        # add numbers 0 to 9 to the map. 17 added to value to account for 17 entries above
        for index, char in enumerate([chr(alpha) for alpha in range(48, 58)], 17):
            self.char_index[char] = index

        # finally add letters to the map. in case of hindi this comes from hi_scripts json file.
        # also the index value starts from 27 which accounts for 17 initial characters and 10 numbers above
        for index, char in enumerate(self.letters, 27):
            self.char_index[char] = index

        # reverse the letter to index mapping
        for char, index in self.char_index.items():
            self.index_char[index] = char

    def size(self):
        return len(self.char_index)

    def word2vec(self, word):
        """Converts given string of letters(word) to vector
        first add tokens for start ($) and end (#)
        """
        try:
            vec = [self.char_index["$"]] + [self.char_index[ind] for ind in list(word)] + [self.char_index["#"]]

            vec = np.asarray(vec, dtype=np.int64)
            return vec

        except Exception as error:
            print("token not found. error finding index for word ", word)
            print(error)
            sys.exit()

    def vec2word(self, vec):
        """Converts vector to string of letters(word)"""
        char_list = [self.index_char[i] for i in vec]

        word = "".join(char_list).replace("$", "").replace("#", "")  # remove tokens
        word = word.replace("_", "").replace("*", "")  # remove tokens
        return word