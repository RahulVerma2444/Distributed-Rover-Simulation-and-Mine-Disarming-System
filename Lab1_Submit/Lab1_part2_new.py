import threading
from tokenize import String

import requests
from concurrent.futures import ThreadPoolExecutor
import json
import pandas as pd
import time
import hashlib
from numpy.ma.extras import row_stack

def roverPath(roverValues, path, mineNum):
    res = [val for val in roverValues.values[0]]
    rover_val = str(res[1])
    fmap = open("map1.txt", "r")
    mineMap = []

    char_array = [];
    for m in range(1, 28):
        char = fmap.read(1)
        print(char)
        print(m)
        if m >= 5 and char != ' ' and char != '\n':
            char_array.append(char)
        if m == 1:
            rows = char
        if m == 3:
            columns = char

    n = 0


    for k in range(int(rows)):
        a = []
        for l in range(int(columns)):
            a.append(char_array[n])
            n = n + 1
        mineMap.append(a)


    fmap.close()

    f = open(path, "w")
    fmines = open("mines.txt", "r")

    f = open(path, "w")
    roverMap = [
        ['*', 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    i = 0
    j = 0

    serialNumber = fmines.readlines()[mineNum]




    direction_rover_i = 0
    for direction in rover_val:
        f = open(path, "w")

        direction_rover = ['down', 'right', 'up', 'left']
        if direction == 'R':
            direction_rover_i = direction_rover_i + 1
            if (direction_rover_i > 3):
                direction_rover_i = 0
        elif direction == 'L':
            direction_rover_i = direction_rover_i - 1
            if (direction_rover_i < 0):
                direction_rover_i = 3
        elif direction == 'M':
            if direction_rover[direction_rover_i] == 'down':
                if (j <= 2):
                    j = j + 1
            elif direction_rover[direction_rover_i] == 'right':
                if (i >= 1):
                    i = i - 1
            elif direction_rover[direction_rover_i] == 'left':
                if (i <= 1):
                    i = i + 1
            elif direction_rover[direction_rover_i] == 'up':
                if (j >= 2):
                    j = j - 1
            #print(direction_rover[direction_rover_i])
        elif direction == 'D':
            pin = 0
            while (True):
                pin = pin + 1
                tempMineKey = str(pin) + serialNumber
                sha_signature = \
                    hashlib.sha256(tempMineKey.encode()).hexdigest()
                if (sha_signature.startswith("000000")):
                    print("PIN Number: " + str(pin))
                    print("SHA Signature: " + str(sha_signature))
                    break


        if not direction == 'M' and j > 3:
            roverMap[j][i] = "*"
            roverMap_string = '\n'.join(['\t'.join(map(str, row)) for row in roverMap])

            print(roverMap_string)
            print("done")
            f.write(roverMap_string)

        if mineMap[j][i] == '1' and direction != 'D':
            # if not dug
            print('LANDED ON A MINE!')
            break

    f.close()
    fmines.close()

    return 0


rover1 = pd.read_json("https://coe892.reev.dev/lab1/rover/1")
rover2 = pd.read_json("https://coe892.reev.dev/lab1/rover/2")
rover3 = pd.read_json("https://coe892.reev.dev/lab1/rover/3")
rover4 = pd.read_json("https://coe892.reev.dev/lab1/rover/4")
rover5 = pd.read_json("https://coe892.reev.dev/lab1/rover/5")
rover6 = pd.read_json("https://coe892.reev.dev/lab1/rover/6")
rover7 = pd.read_json("https://coe892.reev.dev/lab1/rover/7")
rover8 = pd.read_json("https://coe892.reev.dev/lab1/rover/8")
rover9= pd.read_json("https://coe892.reev.dev/lab1/rover/9")
rover10 = pd.read_json("https://coe892.reev.dev/lab1/rover/10")

response1 = requests.get("https://coe892.reev.dev/lab1/rover/1")

print(response1.json())

res = [val for val in rover1.values[0]]

start_seq = time.time()

roverPath(rover1, "path_1.txt", 0)
roverPath(rover2, "path_2.txt", 1)
roverPath(rover3, "path_3.txt", 2)
roverPath(rover4, "path_4.txt", 3)
roverPath(rover5, "path_5.txt", 4)
roverPath(rover6, "path_6.txt", 5)
roverPath(rover7, "path_7.txt", 6)
roverPath(rover8, "path_8.txt", 7)
roverPath(rover9, "path_9.txt", 8)
roverPath(rover10, "path_10.txt", 9)

end_seq = time.time()
time_seq = end_seq - start_seq

rovers = [rover1, rover2, rover3, rover4, rover5, rover6, rover7, rover8, rover9, rover10]

start_parallel = time.time()

t1 = threading.Thread(target=roverPath, args=(rover1, "path_1.txt"))
t2 = threading.Thread(target=roverPath, args=(rover2, "path_2.txt"))
t3 = threading.Thread(target=roverPath, args=(rover3, "path_3.txt"))
t4 = threading.Thread(target=roverPath, args=(rover4, "path_4.txt"))
t5 = threading.Thread(target=roverPath, args=(rover5, "path_5.txt"))
t6 = threading.Thread(target=roverPath, args=(rover6, "path_6.txt"))
t7 = threading.Thread(target=roverPath, args=(rover7, "path_7.txt"))
t8 = threading.Thread(target=roverPath, args=(rover8, "path_8.txt"))
t9 = threading.Thread(target=roverPath, args=(rover9, "path_9.txt"))
t10 = threading.Thread(target=roverPath, args=(rover10, "path_10.txt"))

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()
t7.start()
t8.start()
t9.start()
t10.start()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
t6.join()
t7.join()
t8.join()
t9.join()
t10.join()


end_parallel = time.time()
time_parallel = end_parallel - start_parallel
print("Sequential time: " + str(time_seq))
print("Parallel time: " + str(time_parallel))
print("Time Difference: " + str(time_seq - time_parallel))