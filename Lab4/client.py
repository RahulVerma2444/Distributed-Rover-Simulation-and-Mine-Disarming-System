import time
import grpc
import rover_pb2_grpc
import rover_pb2
import hashlib

#Sources: https://www.youtube.com/watch?v=WB37L7PjI5k

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = rover_pb2_grpc.roverStub(channel)
        roverNumber = input("Input rover number:") #get rover number from user
        
        map_request = rover_pb2.FileName(mapID = "map1.txt") #send map file to server
        map_reply = stub.GetMap(map_request) #get the map and rows/columns of map from the server
        mineMap = str(map_reply).split(": ")[1].replace("\\", "").replace("\n", "").strip('\"')
        mineMap1 = mineMap.replace("[", "").replace("]", "").replace("\'","").replace(", ", "")

        mineMapArray = [[0 for i in range(map_reply.columns)] for j in range(map_reply.rows)]
        k=0
        for i in range(0,map_reply.rows):
            for j in range(0,map_reply.columns):
                mineMapArray[i][j] = int(mineMap1[k])
                k=k+1        


        f = open(f"path_{roverNumber}.txt", "w") #open the respective path file for the rover
        roverMap = [[0 for i in range(map_reply.columns)] for j in range(map_reply.rows)]
        roverMap[0][0] = '*'
        i = 0
        j = 0

        command_request = rover_pb2.Api(api_name = f"https://coe892.reev.dev/lab1/rover/{roverNumber}") #send respective api name to server
        command_replies = stub.GetStreamCommands(command_request) #get the list of commands from the server
        direction_rover_i = 0
        
        for command_reply in command_replies: #run through each of the rover commands
            f = open(f"path_{roverNumber}.txt", "w")        
            command = str(command_reply).split(": ")[1].replace('\"', '').replace("\n", "")
            print(str(command_reply).split(": ")[1].replace('\"', '').replace("\n", ""))

            direction_rover = ['down', 'right', 'up', 'left']
            if command == 'R': #rotate to right
                direction_rover_i = direction_rover_i + 1
                if (direction_rover_i > 3):
                    direction_rover_i = 0
            elif command == 'L': #rotate to left
                direction_rover_i = direction_rover_i - 1
                if (direction_rover_i < 0):
                    direction_rover_i = 3
            elif command == 'M': #move forward in correct direction only if in bounds
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
            elif command == 'D': #dig command
                mine_request = rover_pb2.Mine_Number(mine_index = (int(roverNumber)-1)) #send mine index to server
                mine_reply = stub.GetMine(mine_request) #recieve the mine serial number
                print("Initiate finding of mine pin")
                mine_reply_formatted = str(mine_reply).split(": ")[1].replace('\"', '').replace("\n", "")

                pin = -1
                while (True): #loop for finding pin for cracking sha256 encoding
                    pin = pin + 1
                    tempMineKey = str(pin) + mine_reply_formatted
                    sha_signature = \
                        hashlib.sha256(tempMineKey.encode()).hexdigest()
                    if (sha_signature.startswith("000000")): #when starts with 6 consecutive 0s found:
                        print("Mine: " + mine_reply_formatted) #print mine number, pin number, sha sig, and break
                        print("PIN Number: " + str(pin))
                        print("SHA Signature: " + str(sha_signature))
                        break
                        
                pin_request = rover_pb2.Index(index_number = str(pin)) #shares the mine pin with the server
                pin_reply = stub.SharePin(pin_request)
                mineMapArray[j][i] = '0' #sets mine map position equal to 0
                
            success = 1 #success set to 1 if traversed through all commands without being exploded by a mine
            if not (command == 'M' and j > 3): #updates the path file with "*"
                roverMap[j][i] = "*"
                roverMap_string = '\n'.join(['\t'.join(map(str, row)) for row in roverMap])
                f.write(roverMap_string)

            if mineMapArray[j][i] == 1 and command != 'D': #if mine not dug and landed on a mine
                success = 0
                success_request = rover_pb2.CommandSuccess(success = "Exploded by a mine") #sends to server that rover exploded by mine
                success_reply = stub.ListCommands(success_request) #receive the server reply
                print("CommandSuccess Response Recieved")
                print(success_reply)
                break

        if(success == 1): #if traversed through commands successfully
            success_request = rover_pb2.CommandSuccess(success = "Commands successful") #sends to server commands executed successfully
            success_reply = stub.ListCommands(success_request) #gets reply from server
            print("CommandSuccess Response Recieved")
            print(success_reply)

        f.close()

if __name__ == "__main__":
    run()