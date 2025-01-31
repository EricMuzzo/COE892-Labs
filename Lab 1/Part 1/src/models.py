import time
"""All the data models for the Rover application"""
    
class Cell():
    """Represents a single cell on the map"""
    
    def __init__(self, x: int, y: int, value: str):
        self.x_coord: int = x
        self.y_coord: int = y
        self.value: str = value
        self.up: Cell = None
        self.down: Cell = None
        self.left: Cell = None
        self.right: Cell = None
        
    def __repr__(self):
        return f"Cell({self.x_coord}, {self.y_coord}, {self.value})"
        
        
class Map():
    """The data structure for the 2D map grid"""
    
    def __init__(self, map_file_path: str):
        
        self.cells: list[list[Cell]] = []
        
        #Process the map file and generate Cell objects
        f = open(map_file_path, "r")
        header = f.readline().split()

        self.num_rows = int(header[0])
        self.num_cols = int(header[1])
        
        for row_index, line in enumerate(f):
            row = []
            for col_index, cell in enumerate(line.strip().split()):
                cell_val = "MINE" if cell == "1" else "EMPTY"
                row.append(Cell(row_index, col_index, cell_val))
            self.cells.append(row)
            
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
            
class Rover():
    """A class representing the Rover object"""
    
    def __init__(self, id: int, commands: str, start_cell: Cell, map_width: int, map_height: int):
        self.id: int = id
        self.commands: list = list(commands)
        self.path_array: list[list[str]] = [["0" for _ in range(map_width)] for _ in range(map_height)]
        
        #Initialize the rover to the starting position at cell(0, 0)
        self.position: Cell = start_cell
        self.orientation: str = "DOWN"
        
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
            case "D":
                print(f"[ROVER {self.id}]: Mine hit at ({self.position.x_coord}, {self.position.y_coord}). Mine dug. Proceeding...")
            
    def run(self):
        """Runs the rover through the map"""
        
        for cmd in self.commands:
            #Mark position in path array
            self.path_array[self.position.x_coord][self.position.y_coord] = "*"
            
            #First check the termination case: rover is on a mine and does not dig
            if self.position.value == "MINE" and cmd != "D":
                print(f"[ROVER {self.id}]: Mine hit at ({self.position.x_coord}, {self.position.y_coord}). Command was not \'D\'. Rover destroyed.")
                break
            
            self.move(cmd)
            
    def __repr__(self):
        return f"[ROVER {self.id}]: Position: ({self.position.x_coord}, {self.position.y_coord}), Orientation: {self.orientation}"
    
    def getPathArrayString(self):
        string = ''
        for row in self.path_array:
            string += " ".join(char for char in row) + "\n"
        return string