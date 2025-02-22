import time
import random
import logging
from hashlib import sha256
from rpc import ground_control_pb2 as gc_pb2
from rpc import ground_control_pb2_grpc as gc_pb2_grpc

"""All the data models for the Rover application"""
    
    
logger = logging
logger.basicConfig(level=logging.INFO, format="%(levelname)-2s [%(filename)s:%(lineno)d] %(message)s")


class Cell():
    """Represents a single cell on the map"""
    
    def __init__(self, x: int, y: int, value: str, mine_serial: str = None):
        self.x_coord: int = x
        self.y_coord: int = y
        self.value: str = value
        self.up: Cell = None
        self.down: Cell = None
        self.left: Cell = None
        self.right: Cell = None
        self.mine_serial: str = mine_serial
        
    def __repr__(self):
        return f"Cell({self.x_coord}, {self.y_coord}, {self.value})"
        
        
class Map():
    """The data structure for the 2D map grid used by the server"""
    
    def __init__(self, map_file_path: str, mine_file_path: str):
        
        self.cells: list[list[Cell]] = []
        
        #Process the map and mines files and generate Cell objects
        map_f = open(map_file_path, "r")
        header = map_f.readline().split()

        self.num_rows = int(header[0])
        self.num_cols = int(header[1])
        
        mine_f = open(mine_file_path, "r")
        mine_serials = [line.strip() for line in mine_f]
        num_serials = len(mine_serials)
        serial_cntr = 0
        
        
        for row_index, line in enumerate(map_f):
            row = []
            for col_index, cell in enumerate(line.strip().split()):
                if cell == "1":
                    cell_val = "MINE"
                    cell_mine_serial = mine_serials[serial_cntr % num_serials]
                    serial_cntr += 1
                    row.append(Cell(row_index, col_index, cell_val, cell_mine_serial))
                else:
                    cell_val = "EMPTY"
                    row.append(Cell(row_index, col_index, cell_val))
                
            self.cells.append(row)
            
        map_f.close()
        mine_f.close()
            
        #Link the cells together
        self._link_cells()
        
    def _link_cells(self):
        """Link the cells together to form a grid."""
        
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cell: Cell = self.cells[row][col]
                if row > 0:
                    cell.up = self.cells[row - 1][col]
                if row < self.num_rows - 1:
                    cell.down = self.cells[row + 1][col]
                if col > 0:
                    cell.left = self.cells[row][col - 1]
                if col < self.num_cols - 1:
                    cell.right = self.cells[row][col + 1]
            
    def print_grid(self):
        """Print the map grid with character representations of empty cells and mines."""
        for row in self.cells:
            print(" ".join("M" if cell.value == "MINE" else "E" for cell in row))
            
    def array_repr(self) -> list[list[str]]:
        """Returns a 2D array of strings of either 0 or 1"""
        
        ret_array: list[list[str]] = []
        
        for row in self.cells:
            row_array: list[str] = []
            for cell in row:
                val = "0" if cell.value == "EMPTY" else "1"
                row_array.append(val)
            ret_array.append(row_array)
            
        return ret_array
    
    
class ClientMap():
    """The data structure for the 2D map grid used by the client"""
    
    def __init__(self, grid: list[list[str]], num_rows: int, num_cols: int):
        
        self.cells: list[list[Cell]] = []
        self.num_rows = num_rows
        self.num_cols = num_cols
        
        for row_index, row in enumerate(grid):
            temp_row = []
            for col_index, cell in enumerate(row):
                
                cell_val = "MINE" if cell == "1" else "EMPTY"
                temp_row.append(Cell(x=col_index, y=row_index, value=cell_val))
                
            self.cells.append(temp_row)
            
        #Link the cells together
        self._link_cells()
        
    def _link_cells(self):
        """Link the cells together to form a grid."""
        
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cell: Cell = self.cells[row][col]
                if row > 0:
                    cell.up = self.cells[row - 1][col]
                if row < self.num_rows - 1:
                    cell.down = self.cells[row + 1][col]
                if col > 0:
                    cell.left = self.cells[row][col - 1]
                if col < self.num_cols - 1:
                    cell.right = self.cells[row][col + 1]
            
    def print_grid(self):
        """Print the map grid with character representations of empty cells and mines."""
        for row in self.cells:
            print(" ".join("M" if cell.value == "MINE" else "E" for cell in row))
            
    def array_repr(self) -> list[list[str]]:
        """Returns a 2D array of strings of either 0 or 1"""
        
        ret_array: list[list[str]] = []
        
        for row in self.cells:
            row_array: list[str] = []
            for cell in row:
                val = "0" if cell.value == "EMPTY" else "1"
                row_array.append(val)
            ret_array.append(row_array)
            
        return ret_array
    
            
class Rover():
    """A class representing the Rover object"""
    
    def __init__(self, id: int, map: ClientMap, commands: str, stub: gc_pb2_grpc.GroundControlStub, start_x: int = 0, start_y: int = 0):
        self.id: int = id
        self.commands: list = list(commands)
        self.stub: gc_pb2_grpc.GroundControlStub = stub         #lets rover comm w/ server on its own
        self.path_array: list[list[str]] = [["0" for _ in range(map.num_cols)] for _ in range(map.num_rows)]
        
        #Initialize the rover to the starting position. Default = cell(0, 0)
        self.position: Cell = map.cells[start_y][start_x]
        self.orientation: str = "DOWN"
        
        
    def move(self, command: str) -> bool:
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
            case "D":
                
                print(f"[ROVER {self.id}]: Mine hit at ({self.position.x_coord}, {self.position.y_coord}). Fetching serial number")
                
                #Request the mine serial number
                serial_res = self.stub.GetMineSerial(gc_pb2.SerialNumRequest(x_pos=self.position.x_coord, y_pos=self.position.y_coord))
                serial_num = serial_res.serialNum
                
                print(f"[ROVER {self.id}]: Serial number fetched: {serial_num}. Begin digging...")
                
                #Mine the mine
                pin = self.mine(serial_num)
                
                if pin is None:
                    #print(f"[ROVER {self.id}]: Failed to mine mine with serial {self.position.mine_serial}. Rover destroyed.")
                    raise Exception("Mining failed for unknown reason")
                
                
                #Report the pin to the server
                self.stub.ShareMinPin(gc_pb2.MinePin(rover_id=self.id, pin=str(pin)))
                print(f"[ROVER {self.id}]: Mine pin {pin} reported to server.")
                
        return True
                
            
    def run(self):
        """Runs the rover through the map"""
        
        report_msg = ""
        success = True
        
        for cmd in self.commands:
            #Mark position in path array
            self.path_array[self.position.y_coord][self.position.x_coord] = "*"
            
            #print(f"[ROVER {self.id}]: Executing command {cmd}. Current pos: ({self.position.x_coord},{self.position.y_coord}) Orientation: {self.orientation}")
            
            #First check the termination case: rover is on a mine and does not dig
            if self.position.value == "MINE" and cmd != "D":
                report_msg = f"[ROVER {self.id}]: Mine hit at ({self.position.x_coord}, {self.position.y_coord}). Command was not \'D\'. Rover destroyed."
                print(f"{report_msg}")
                success = False
                break
            
            if self.position.value != "MINE" and cmd == "D":
                continue

            try:
                self.move(cmd)
            except Exception as e:
                report_msg = str(e)
                logging.exception(report_msg)
                success = False
                break
            
        #Report the rover's status to the server
        self.stub.ReportStatus(gc_pb2.ExecutionStatus(rover_id=self.id, success=success, msg=report_msg))
            
    def hashKey(self, pin: str, serial: str) -> str:
        temp_key = pin + serial
        
        hash_key = sha256(temp_key.encode()).hexdigest()
        
        return hash_key
        
            
    def mine(self, serial: str) -> int:
        """Attempts to mine the current mine with the given serial number.

        Args:
            serial (str): The serial number of the mine

        Returns:
           (bool) : True if the mine was successfully mined, False otherwise
        """
        
        pin = 0
        while True:
            hash_val = self.hashKey(str(pin), serial)
            
            if hash_val.startswith("000000"):
                
                #Clear the current cell
                self.position.value = "EMPTY"
                
                print(f"[MINE {serial}]: Dig Success. Pin: {pin}. Full hash: {hash_val}")
                return pin
            
            pin += 1
            
        return None
                    
    def __repr__(self) -> str:
        return f"[ROVER {self.id}]: Position: ({self.position.x_coord}, {self.position.y_coord}), Orientation: {self.orientation}"
    
    def getPathArrayString(self) -> str:
        string = ''
        for row in self.path_array:
            string += " ".join(char for char in row) + "\n"
        return string