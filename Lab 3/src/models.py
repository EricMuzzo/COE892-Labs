"""All the data models for the Rover application"""

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
    
            
class ServerMap(Map):
    """The data structure for the 2D map grid used by the server"""
    
    def __init__(self, map_file_path: str, mine_file_path: str):
        
        #Process the map file and call the parent constructor
        with open(map_file_path, "r") as map_f:
            header = map_f.readline().split()
            num_rows = int(header[0])
            num_cols = int(header[1])
            
            grid = [line.strip().split() for line in map_f]
        
        super().__init__(grid, num_rows, num_cols)
        
        #Process the mine file and add mine serials into the data structure
        with open(mine_file_path, "r") as mine_f:
            mine_serials = [line.strip() for line in mine_f]
            num_serials = len(mine_serials)
            serial_cntr = 0
        
        for row in self.cells:
            for cell in row:
                if cell.value == "MINE":
                    cell.mine_serial = mine_serials[serial_cntr % num_serials]
                    serial_cntr += 1