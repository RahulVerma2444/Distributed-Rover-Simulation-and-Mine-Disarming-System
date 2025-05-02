from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import hashlib

import uvicorn



app = FastAPI()

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

global rovers

rovers = [rover1, rover2, rover3, rover4, rover5, rover6, rover7, rover8, rover9, rover10]

res1 = [val for val in rover1.values[0]][1]
res2 = [val for val in rover2.values[0]][1]
res3 = [val for val in rover3.values[0]][1]
res4 = [val for val in rover4.values[0]][1]
res5 = [val for val in rover5.values[0]][1]
res6 = [val for val in rover6.values[0]][1]
res7 = [val for val in rover7.values[0]][1]
res8 = [val for val in rover8.values[0]][1]
res9 = [val for val in rover9.values[0]][1]
res10 = [val for val in rover10.values[0]][1]

global res

res = [res1, res2, res3, res4, res5, res6, res7, res8, res9, res10]

global serialNumber

fmines = open("mines.txt", "r")
serialNumber = fmines.readlines()
fmines.close()

status = ["Not Started", "Not Started", "Not Started", "Not Started", "Not Started", "Not Started", "Not Started", "Not Started", "Not Started", "Not Started"]

latest_position = ["(0, 0)", "(0, 0)", "(0, 0)", "(0, 0)", "(0, 0)", "(0, 0)", "(0, 0)", "(0, 0)", "(0, 0)", "(0, 0)"]

@app.get("/map")
def getMap():
    fmap = open("map1.txt", "r")
    mineMap = []

    char_array = []
    for m in range(1, 28):
        char = fmap.read(1)
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
    return {"Map": mineMap}

@app.put("/map")
def updateMap(height: int, width: int, newMap: str):
    fmap = open("map1.txt", "w")
    fmap.write(f"{height} {width}\n")
    fmap.close()
    fmap = open("map1.txt", "a")
    newMap1 = newMap.replace("n", "\n")
    fmap.write(newMap1)
    fmap.close()

@app.get("/mines")
def getMines():
    coordinates = [[0, 1], [2, 0]]
    return {"Mines": serialNumber,
            "Coordinates": coordinates}

@app.get("/mines/:{mine_id}")
def queryMineById(mine_id: int):# -> Mine:
    mines = getMines()
    if mine_id >= len(mines['Mines']):
        raise HTTPException(
            status_code=404, detail=f"Mine with {mine_id=} does not exist."
        )
    return {"Mine": mines['Mines'][mine_id],
            "Coordinates": mines['Coordinates']}

@app.delete("/mines/:{mine_id}")
def deleteMine(mine_id: int):
    if mine_id >= len(rovers):
        raise HTTPException(
            status_code=404, detail=f"Index Out of Bounds"
        )
    serialNumber.pop(mine_id-1)


@app.post("/mines")
def createMine(serialNumberInput: str): #-> Id:
    serialNumber.append(serialNumberInput)
    length = len(serialNumber)
    print(serialNumber)
    return {"MineID": length}

@app.put("/mines/:{mine_id}")
def updateMine(mine_id: int | None = None, newSerialNumber: str | None = None): #-> Mine:
    serialNumber[mine_id-1] = newSerialNumber
    return {"Mine Serial Number": serialNumber[mine_id-1]}


@app.get("/rovers")
def getRovers():
    rover_id = []
    commands = []
    for i in range(len(rovers)):
        rover_id.append(i)
    for i in range(len(res)):
        commands.append(res[i])
    print(rover_id)
    print(commands)

    return {"RoverID": rover_id,
            "Commands": commands,
            "Status": status}

@app.get("/rovers/:{rover_id}")
def queryRoverById(rover_id: int):# -> Any: #FIX RETURN TYPE
    rovers = getRovers()
    if rover_id >= len(rovers['RoverID']):
        raise HTTPException(
            status_code=404, detail=f"Rover with {rover_id=} does not exist."
        )
    return {"RoverID": rover_id,
            "Status": status[rover_id-1],
            "Latest Position": latest_position[rover_id-1],
            "Commands": rovers['Commands'][rover_id]}


@app.post("/rovers")
def createRover(commands: str): #-> Rover_Id:
    length = len(rovers)
    rovers.append(length)
    res.append(commands)
    status.append("Not Started")
    latest_position.append("(0, 0)")
    print(rovers)
    return {"RoverID": length}


@app.delete("/rovers/:{rover_id}")
def deleteRover(rover_id: int):
    if rover_id >= len(rovers):
        raise HTTPException(
            status_code=404, detail=f"Index Out of Bounds"
        )
    rovers.pop(rover_id-1)
    res.pop(rover_id-1)
    print(rovers)
    status.pop(rover_id-1)
    latest_position.pop(rover_id-1)


@app.put("/rovers/:{rover_id}")
def sendCommands(rover_id: int, commands: str):
    print(status[rover_id-1])
    if status[rover_id-1] != "Not Started" and status[rover_id-1] != "Finished":
        raise HTTPException(
            status_code=404, detail=f"Rover Status is not Not Started or Finished"
        )
    res[rover_id-1] = commands

@app.post("/rovers/:{rover_id}/dispatch")
def dispatchRover(rover_id: int): #-> Any: #FIX RETURN TYPE
    status_rover = ''
    roverMap = [
        ['*', 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    i = 0
    j = 0

    mineMap = getMap()["Map"]
    rovers = getRovers()
    if rover_id >= len(rovers['RoverID']):
        raise HTTPException(
            status_code=404, detail=f"Rover with {rover_id=} does not exist."
        )
    serialNumber = queryMineById(rover_id)["Mine"]
    rover_val = queryRoverById(rover_id)["Commands"]

    direction_rover_i = 0
    for direction in rover_val:
        f = open(f"path_{rover_id}", "w")

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
            status_rover = "ELIMINATED"
            break
    if(status_rover != 'ELIMINATED'):
        status_rover = 'Finished'

    status[rover_id-1] = status_rover
    latest_position[rover_id-1] = f"({i}, {j})"

    return {"RoverID": rover_id,
            "Status": status_rover,
            "Latest Position": f"({i}, {j})",
            "Commands": rovers['Commands'][rover_id]}

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8081)