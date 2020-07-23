from vncdotool import api
import pytesseract
from PIL import Image
import cv2
from collections import Counter
import time
def all_anagrams(letters, dict):
    letters_count = Counter(letters)

    anagrams = set()
    for word in dictionary:
        # Check if all the unique letters in word are in the
        # scrambled letters
        if not set(word) - set(letters):
            check_word = set()
            # Check if the count of each letter is less than or equal
            # to the count of that letter in scrambled letter input
            for k, v in Counter(word).items():
                if v <= letters_count[k]:
                    check_word.add(k)
            # Check if check_words is exactly equal to the unique letters
            # in the word of dictionary
            if check_word == set(word):
                anagrams.add(word)

    return sorted(list(anagrams), key=lambda x: len(x))[::-1]
dictionary = None
with open('words_alpha.txt', 'r') as f:
    dictionary = [word.lower().strip() for word in f.read().split('\n') if len(word) >= 3 and len(word) <= 7]
with api.connect('localhost::2222') as client:
    # while True:
    #     x = int(input('x:'))
    #     y = int(input('y:'))
    #     w = int(input('w:'))
    #     h = int(input('h:'))
    #     client.captureRegion('screenshot.png', x, y, w, h)
    print('waiting for game start')
    client.expectRegion('gamestart.png', 150, 1350, maxrms=10)
    print('game started')
    client.captureRegion('letters.png', 0, 1950, 1125, 200)
    print('captured letters')
    image = cv2.imread('letters.png')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, gray = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    gray = cv2.medianBlur(gray, 3)

    cv2.imwrite('gray.png', gray)
    pil_img = Image.fromarray(gray)
    tesseract_options = '--psm 7 --oem 0 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    letters = list(pytesseract.image_to_string(pil_img, config=tesseract_options).replace(' ', '', -1).lower())
    # i d l h a a -> a a d h i l
    print(letters)
    # h a d a l -> a a d h l 
    # 4 0 2 1  -> 0 1 2 3 5
    combos = all_anagrams(letters, dictionary)
    coords = []

    size = { 7: 3000, 6: 2000, 5: 1200, 4: 400, 3: 100}

    possible_score = 0
    for c in combos:
        possible_score += size[len(c)]
        l_copy = letters[:]
        word = []
        for letter in c:
            i = l_copy.index(letter)
            l_copy[i] = '-'
            word.append(80 + i * 160)
        coords.append(word)
    print('-' * 20 + '\n', possible_score, '\n' + '-' * 20 + '\n')
    if possible_score <= 150000:
        print('not worth it')
    for i, coord in enumerate(coords):
        # print('inputting ' + combos[i], coord)
        for tap in coord:
            client.mouseMove(tap, 2030)
            client.mousePress(1)
            time.sleep(.03)
        client.mouseMove(570, 1500)
        client.mousePress(1)
        time.sleep(.08)
        
