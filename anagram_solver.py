from collections import Counter
import sys
import time

letters = ['m', 'p', 'l', 'c', 'u', 's']
letters_count = Counter(letters)

    anagrams = set()
    for word in dictionary:
        if not set(word) - set(letters):
            check_word = set()
            for k, v in Counter(word).items():
                if v <= letters_count[k]:
                    check_word.add(k)
            if check_word == set(word):
                anagrams.add(word)
    out = list(anagrams)
    for w in out:
        print(w)