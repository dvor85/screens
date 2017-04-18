#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os


def translate(file_in):
    TRANS = {
        'A': "Ф",
        'B': "И",
        'C': "С",
        'D': "В",
        'E': "У",
        'F': "А",
        'G': "П",
        'H': "Р",
        'I': "Ш",
        'J': "О",
        'K': "Л",
        'L': "Д",
        'M': "Ь",
        'N': "Т",
        'O': "Щ",
        'P': "З",
        'Q': "Й",
        'R': "К",
        'S': "Ы",
        'T': "Е",
        'U': "Г",
        'V': "М",
        'W': "Ц",
        'X': "Ч",
        'Y': "Н",
        'Z': "Я",
        '`': "Ё",
        ';': "Ж",
        "'": "Э",
        ',': "Б",
        '.': "Ю",
        '[': "Х",
        ']': "Ъ"
    }

    with open(file_in, 'r') as fin:
        keys = fin.read().split('|')
    for i, k in enumerate(keys):
        keys[i] = TRANS.get(k, k)
    return "|".join(keys)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: {0} <file>".format(os.path.basename(sys.argv[0]))
        sys.exit(1)
    file_in = sys.argv[1]
    print translate(file_in)
