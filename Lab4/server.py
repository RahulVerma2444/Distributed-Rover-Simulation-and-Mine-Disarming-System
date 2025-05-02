from concurrent import futures
import time

import rover_pb2
import rover_pb2_grpc
import grpc
import json
import pandas as pd

class roverServicer(rover_pb2_grpc.roverServicer):
    def GetMap(self, request, context): #function for getting the map
        print("GetMap Request Made:")
        mapFile = str(request).split(": ")[1].replace("\n", "").strip('\"')
        
        fmap = open(str(mapFile), "r")
        mineMap = []
        char_array = []
        for m in range(1, 28): #extract commands, rows, and map
            char = fmap.read(1)
            if m >= 5 and char != ' ' and char != '\n':
                char_array.append(char)
            if m == 1:
                rows = char
            if m == 3:
                columns = char
        n = 0

        for k in range(int(rows)): #send map to array a
            a = []
            for l in range(int(columns)):
                a.append(char_array[n])
                n = n + 1
            mineMap.append(a)
        print(mineMap)

        fmap.close()
        
        map_reply = rover_pb2.Map()
        map_reply.map_display_array.append(f"{mineMap}") #send the mine map back to client
        map_reply.rows = int(rows) #send the number of rows to client
        map_reply.columns = int(columns) #send the number of columns to client
        return map_reply
    
    def GetStreamCommands(self, request, context): #method for getting list of rover commands
        print("GetStreamCommands Request Made:")
        print(request)

        print(str(request).split(": ")[1].replace('\"', ''))
        request_formatted = str(request).split(": ")[1].replace('\"', '')
        roverValues = pd.read_json(request_formatted) #reading from api for list of commands
        res = [val for val in roverValues.values[0]]
        rover_val = str(res[1])
        
        for i in rover_val: #ouputting stream of commands sequentially for client to read
            command_reply = rover_pb2.Commands()
            command_reply.commands_display = f"{i}"
            yield command_reply
        
        
    
    def GetMine(self, request, context): #method for retrieving mine serial number
        print("GetMine Request Made:")
        fmines = open("mines.txt", "r")
        mine_reply = rover_pb2.Mine()
        serialNumber = fmines.readlines()[request.mine_index].replace("\n", "") #getting mine serial number based on index number provided by client
        mine_reply.mine_serial = f"{serialNumber}" #sending serial number to client
        return mine_reply
    
    def ListCommands(self, request, context): #method for knowing whether commands executed successfully
        print("ListCommands Request Made")
        success_reply = rover_pb2.Success()
        if request.success == "Exploded by a mine": #if client says "Exploded by a mine"
            success_reply.success_rate = "Unsuccessful path" #server sends back "Unsuccessful path"
        elif request.success == "Commands successful": #if client says "Commands Successful"
            success_reply.success_rate = "Successful path" #server sends back "Successful path"
        return success_reply
    
    def SharePin(self, request, context): #method for getting mine pin from client
        print("SharePin Request Made")
        pin_reply = rover_pb2.Pin() #getting mine pin from client
        pin_reply.pin_number = f"{request.index_number} successfully recieved" #indicating to client that pin was successfully recieved
        return pin_reply
    

def serve(): #method for handling server operations
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rover_pb2_grpc.add_roverServicer_to_server(roverServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    server.wait_for_termination()
 

if __name__ == "__main__":
    serve()