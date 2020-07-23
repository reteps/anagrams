from vncdotool import api
import pytesseract
from PIL import Image
import cv2
from collections import Counter
import time
import subprocess
import json
import solver
trie_node = {}

with open('dict_trie.json') as f:
    trie_node = json.load(f)

stats = []
lastboard = ''
with api.connect('localhost::2222') as client:
    while True:
        print('[INFO] WAITING')
        client.expectRegion('start.png', 360, 450, maxrms=10)
        client.captureRegion('board.png', 175, 1175, 775, 775)
        image = cv2.imread('board.png')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, gray = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        gray = cv2.medianBlur(gray, 3)

        cv2.imwrite('gray.png', gray)
        pil_img = Image.fromarray(gray)
        output = subprocess.run("gocr -i gray.png".split(" "), stdout=subprocess.PIPE)
        output = output.stdout.decode("utf-8")
        replacements = {'l': 'I', '\n':'',' ':'','0':'O'}
        for k in replacements.keys():
            output = output.replace(k, replacements[k], -1)
        letters = list(output.lower())
        if len(letters) != 16:
            print('ERROR only ', len(letters), 'letters detected')
            exit()
        def chunks(letters):
            for i in range(0, len(letters), 4):
                yield letters[i:i + 4]
        board = list(chunks(letters))
        if ''.join(letters) != lastboard:
            print(''.join(letters))
        score_map = {3: 100, 4: 400, 5: 800, 6: 1400, 7: 1700, 8: 2000, 9: 2600}
        s = 0
        words = solver.allPossibleWords(board, 3, 11, trie_node)
        for word in words:
            s += score_map[len(word)]
        if ''.join(letters) != lastboard:
            print(s,'\n' + '-'*10)
            stats.append(s)
            stats.sort()
            stats.reverse()
            for stat in stats[:5]:
                print(stat)
        
        lastboard = ''.join(letters)
        if s == 175000:
            time.sleep(4)
            continue
        for word in sorted(words, key=len, reverse=True):
            if len(word) >= 7:
                print(word)
            # map x,y to position of mouse
            coords = words[word]
            # print(word)
            start_x = 250 + 200 * coords[0][1]
            start_y = 1250 + 200 * coords[0][0]
            client.mouseMove(start_x, start_y)
            client.mouseDown(1)
            if len(word) >= 7:
                client.pause(.015)
            elif len(word) == 3:
                client.pause(.005)
            else:
                client.pause(.01)
            for i, letter in enumerate(coords[1:]):
                x, y = letter[1], letter[0]
                mouse_x = 250 + 200 * x
                mouse_y = 1250 + 200 * y
                client.mouseMove(mouse_x, mouse_y)
                if len(word) >= 7:
                    client.pause(.015)
                elif len(word) == 3:
                    client.pause(.005)
                else:
                    client.pause(.01)
            client.mouseUp(1)
            if len(word) >= 7:
                client.pause(.015)
            elif len(word) == 3:
                client.pause(.005)
            else:
                client.pause(.01)
        time.sleep(5)
