import grpc
import requests
from concurrent import futures
from src.models import Cell, ServerMap
import logging

from rpc import ground_control_pb2 as gc_pb2
from rpc import ground_control_pb2_grpc as gc_pb2_grpc

#============================================
# Constants
#============================================
map_file_path = "./res/map.txt"
mine_file_path = "./res/mines.txt"
baseURL = "https://coe892.reev.dev/lab1/rover/"
HOST = "localhost"
PORT = 5001



class GroundControlService(gc_pb2_grpc.GroundControlServicer):
    
    def GetMap(self, request, context):
        
        print("\nMap requested")
        
        #Protobuf format conversion
        map_array = map.array_repr()
        map_rows = [gc_pb2.MapRow(cells=row) for row in map_array]
        
        return gc_pb2.MapResponse(grid=map_rows, numRows = map.num_rows, numCols = map.num_cols)
    
    def GetCommands(self, request, context):
        
        rover_id = request.rover_id
        print(f"Commands requested for Rover {rover_id}")
        
        endpoint = f"{baseURL}/{str(rover_id)}"
        response = requests.get(endpoint).json()
        
        #Parse the json response body
        moves:str = response["data"]["moves"]
        
        return gc_pb2.CommandResponse(commands=moves)
    
    def GetMineSerial(self, request, context):
        
        x_pos, y_pos = request.x_pos, request.y_pos
        print(f"Serial number requested for cell ({x_pos},{y_pos})")
        
        cell: Cell = map.cells[y_pos][x_pos]
        serial = cell.mine_serial
        
        return gc_pb2.SerialNumResponse(serialNum = serial)
    
    def ReportStatus(self, request, context):
        
        rover_id = request.rover_id
        success = "Completed" if request.success == True else "Failure"
        message = request.msg
        
        print(f"[STATUS REPORT: ROVER {rover_id}]: {success}")
        print(f"   {message}")
        return gc_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
    
    def ShareMinPin(self, request, context):
        
        rover_id = request.rover_id
        pin = request.pin
        
        print(f"[PIN REPORT: ROVER {rover_id}]: {pin}")
        return gc_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gc_pb2_grpc.add_GroundControlServicer_to_server(GroundControlService(), server)
    server.add_insecure_port(f"{HOST}:{PORT}")
    server.start()
    logging.info(f"Server started on port {PORT}. Listening...\n")
    server.wait_for_termination()

if __name__ == "__main__":
    
    print("Setting up application...")
    logging.basicConfig(level=logging.INFO)
    logging.info("Log configured")
    
    #Initialize the map into memory
    map = ServerMap(map_file_path, mine_file_path)
    logging.info("Map initialized")

    serve()