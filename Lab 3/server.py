import grpc
import requests
from concurrent import futures
from src.models import Cell, ServerMap
import json
import threading
import pika

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
        
        #Remove dig commands
        moves = moves.replace("D", "")
        
        return gc_pb2.CommandResponse(commands=moves)
    
    def GetMineSerial(self, request, context):
        
        x_pos, y_pos = request.x_pos, request.y_pos
        
        cell: Cell = map.cells[y_pos][x_pos]
        serial = cell.mine_serial
        
        return gc_pb2.SerialNumResponse(serialNum = serial)
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gc_pb2_grpc.add_GroundControlServicer_to_server(GroundControlService(), server)
    server.add_insecure_port(f"{HOST}:{PORT}")
    server.start()
    print(f"gRPC server started on port {PORT}. Listening...\n")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
        raise
    
    
def subscribeToDefusedQueue():
    """Thread function to subscribe the server to the Defused-Mines Queue and handle messages"""
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(HOST, 5672))
    channel = connection.channel()
    channel.queue_declare(queue='Defused-Mines')
    
    def callback(ch, method, properties, body):
        """Callback function for consuming a message from the 'Defused-Mines' queue.
        Extracts data from the message body and prints to console.
        """
        message = json.loads(body.decode())
        
        #Variable Extraction
        deminer_id = message["deminer_id"]
        rover_id = message["rover_id"]
        mine_x_pos, mine_y_pos = message["position"]["x_pos"], message["position"]["y_pos"]
        serial = message["serial"]
        pin = message["pin"]
        
        
        print(f"\n[GROUND CONTROL] Incoming message from Deminer {deminer_id}:")
        print(f"\tSource Rover: Rover {rover_id}")
        print(f"\tMine position: ({mine_x_pos},{mine_y_pos})")
        print(f"\tMine serial: {serial}")
        print(f"\tMine Pin: {pin}")
        
    channel.basic_consume(queue='Defused-Mines', on_message_callback=callback, auto_ack=True)
    
    try:
        print(f"[GROUND CONTROL] Waiting for defused mine pins")
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n[GROUND CONTROL] KeyboardInterrupt received. Stopping consumption")
        channel.stop_consuming()
        connection.close()

if __name__ == "__main__":
    
    print("Setting up application...")
    
    #Initialize the map into memory
    map = ServerMap(map_file_path, mine_file_path)
    print("Map initialized")
    
    #Start subscription to Defused-Mines Queue
    defused_thread = threading.Thread(target=subscribeToDefusedQueue, daemon=True)
    defused_thread.start()

    try:
        serve()     #Start gRPC server
    except KeyboardInterrupt:
        print("\n Keyboard Interrupt. Shutting down.")