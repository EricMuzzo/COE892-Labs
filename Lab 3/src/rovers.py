import json
from rpc import ground_control_pb2 as gc_pb2
from rpc import ground_control_pb2_grpc as gc_pb2_grpc
from .models import Cell, Map
import pika

class Rover():
    """A class representing the Rover object"""
    
    def __init__(self, id: int, map: Map, commands: str, stub: gc_pb2_grpc.GroundControlStub, start_x: int = 0, start_y: int = 0):
        self.id: int = id
        self.commands: list = list(commands)
        self.stub: gc_pb2_grpc.GroundControlStub = stub         #lets rover comm w/ server on its own
        
        self.rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
        self.rabbit_channel = self.rabbit_connection.channel()
        self.rabbit_channel.queue_declare(queue="Demine-Queue")
        
        self.path_array: list[list[str]] = [["0" for _ in range(map.num_cols)] for _ in range(map.num_rows)]
        
        #Initialize the rover to the starting position. Default = cell(0, 0)
        self.map = map
        self.position: Cell = map.cells[start_y][start_x]
        self.orientation: str = "DOWN"
        
        
    def publish_demine_task(self, x_pos: int, y_pos: int, serial: str) -> None:
        """Publishes a demining task to the rabbitMQ on the 'Demine-Queue' queue

        Args:
            x_pos (int): the x coordinate of the mine
            y_pos (int): the y coordinate of the mine
            serial (str): the serial number of the mine
        """
        
        message = {
            "id": self.id,
            "position": {
                "x_pos": x_pos,
                "y_pos": y_pos
            },
            "serial": serial
        }
        
        payload = json.dumps(message)
        
        #Publish the message to the queue
        self.rabbit_channel.basic_publish(exchange='', routing_key='Demine-Queue', body=payload)
        print(f"[ROVER {self.id}] Published demining task: {payload}")
    
    def move(self, command: str):
        "Moves the rover in the direction specified by the command and updates position and orientation."
        
        match command:
            case "M":
                match self.orientation:
                    case "DOWN":
                        self.position = self.position.down if self.position.down is not None else self.position
                    case "UP":
                        self.position = self.position.up if self.position.up is not None else self.position
                    case "LEFT":
                        self.position = self.position.left if self.position.left is not None else self.position
                    case "RIGHT":
                        self.position = self.position.right if self.position.right is not None else self.position
            case "L":
                match self.orientation:
                    case "DOWN":
                        self.orientation = "RIGHT"
                    case "UP":
                        self.orientation = "LEFT"
                    case "LEFT":
                        self.orientation = "DOWN"
                    case "RIGHT":
                        self.orientation = "UP"
            case "R":
                match self.orientation:
                    case "DOWN":
                        self.orientation = "LEFT"
                    case "UP":
                        self.orientation = "RIGHT"
                    case "LEFT":
                        self.orientation = "UP"
                    case "RIGHT":
                        self.orientation = "DOWN"
                
            
    def run(self):
        """Runs the rover through the map"""
        
        for cmd in self.commands:
            #Mark position in path array
            self.path_array[self.position.y_coord][self.position.x_coord] = "*"
            
            #First ignore all DIG commands in the stream
            if cmd == "D":
                continue
            
            #Next check if the rover is on a mine
            if self.position.value == "MINE":
                print(f"\n[ROVER {self.id}] Is on a mine at position ({self.position.x_coord},{self.position.y_coord}). Fetching serial #")

                #Fetch the mine's serial number from ground control
                serial_res = self.stub.GetMineSerial(gc_pb2.SerialNumRequest(x_pos=self.position.x_coord, y_pos=self.position.y_coord))
                serial_num = serial_res.serialNum
                print(f"[ROVER {self.id}] Serial number fetched: {serial_num}")
                
                #Publish the demining task
                self.publish_demine_task(self.position.x_coord, self.position.y_coord, serial_num)
                
                #Assume the deminer will demine the mine and the rover can consider this cleared
                self.position.value = "EMPTY"


            self.move(cmd)
            
        #Close the connection to the RabbitMQ server
        self.rabbit_channel.close()
        self.rabbit_connection.close()
        
                    
    def __repr__(self) -> str:
        return f"[ROVER {self.id}]: Position: ({self.position.x_coord}, {self.position.y_coord}), Orientation: {self.orientation}"
    
    def getPathArrayString(self) -> str:
        """Returns the rover's path (same as path_x.txt) through the map as a printable string"""
        string = ''
        for row in self.path_array:
            string += " ".join(char for char in row) + "\n"
        return string