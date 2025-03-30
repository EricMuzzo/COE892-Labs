from fastapi import HTTPException
from hashlib import sha256
import threading
import time

from ..models.rover import RoverModel
from . import map

class Rover():
    """A class representing the Rover object"""
    
    def __init__(self, id: int, commands: str, map: map.ServerMap, status: str = "Not Started",
                 start_x: int = 0, start_y: int = 0, orientation: str = "DOWN"):
        
        self.id: int = id
        self.commands: str = commands
        
        if status not in ['Not Started', 'Finished', 'Moving', 'Eliminated']:
            raise ValueError("Invalid status")
        self.status = status
        
        self.path_array: list[list[str]] = [["0" for _ in range(map.width)] for _ in range(map.height)]
        
        #Initialize the rover to the starting position. Default = cell(0, 0)
        try:
            self.position = map.cells[start_y][start_x]
        except:
            raise HTTPException(400, detail="Starting coordinates are out of bounds")
        
        if orientation not in ["UP", "DOWN", "LEFT", "RIGHT"]:
            raise ValueError("Invalid orientation")
        self.orientation = orientation
        
    
    def dispatch(self):
        runner = threading.Thread(target=self.run)
        runner.start()
    
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
                
                print(f"[ROVER {self.id}]: Mine hit at ({self.position.x_position}, {self.position.y_position}). Serial {self.position.serial}. Begin digging...")
                
                if not self.mine(self.position.serial):
                    print(f"[ROVER {self.id}]: Failed to mine mine with serial {self.position.serial}. Rover destroyed.")
                    return False
                
        return True
                
            
    def run(self):
        """Runs the rover through the map. Used for automated running."""
        
        eliminated = False
        #Change status
        self.status = "Moving"
        
        for cmd in list(self.commands):
            #Mark position in path array
            self.path_array[self.position.y_position][self.position.x_position] = "*"
            
            #First check the termination case: rover is on a mine and does not dig
            if isinstance(self.position, map.Mine) and cmd != "D":
                print(f"[ROVER {self.id}]: Mine hit at ({self.position.x_position}, {self.position.y_position}). Command was not \'D\'. Rover destroyed.")
                eliminated = True
                self.path_array[self.position.y_position][self.position.x_position] = "!"
                break
            
            if not isinstance(self.position, map.Mine) and cmd == "D":
                time.sleep(5)
                continue

            if not self.move(cmd):
                break
            
            time.sleep(5)
        
        self.status = "Eliminated" if eliminated else "Finished"
        
    def run_command(self, command: str) -> bool:
        """Runs a single command. Used for websocket rover control

        Returns:
            bool: Returns `True` if the rover was destroyed and `False` otherwise
        """
        
        #Mark position in path array
        self.path_array[self.position.y_position][self.position.x_position] = "*"
        
        #First check the termination case: rover is on a mine and does not dig
        if isinstance(self.position, map.Mine) and command != "D":
            print(f"[ROVER {self.id}]: Mine hit at ({self.position.x_position}, {self.position.y_position}). Command was not \'D\'. Rover destroyed.")
            self.path_array[self.position.y_position][self.position.x_position] = "!"
            self.status = "Eliminated"
            return True
        
        if not isinstance(self.position, map.Mine) and command == "D":
            return False

        self.move(command)
        return False

        
            
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
                self.position = map.Cell(self.position.x_position, self.position.y_position)
                
                print(f"[MINE {serial}]: Dig Success. Pin: {pin}. Full hash: {hash_val}")
                return pin
            
            pin += 1
            
        return None
                    
    def __repr__(self) -> str:
        return f"[ROVER {self.id}]: Position: ({self.position.x_position}, {self.position.y_position}), Orientation: {self.orientation}"
    
    def getPathArrayString(self) -> str:
        string = ''
        for row in self.path_array:
            string += " ".join(char for char in row) + "\n"
        return string
    
    
    def dump_to_model(self) -> RoverModel:
        """Converts a Rover object to a pydantic RoverModel model"""
        return RoverModel(
            id=self.id,
            commands=self.commands,
            x_position=self.position.x_position,
            y_position=self.position.y_position,
            orientation=self.orientation,
            status=self.status
        )