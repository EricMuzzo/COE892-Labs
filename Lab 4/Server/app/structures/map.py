from fastapi import HTTPException
from ..models.mine import MineModel

class Cell():
    """Represents a single cell on the map"""
    
    def __init__(self, x: int, y: int):
        self.x_position: int = x
        self.y_position: int = y
        self.up: Cell = None
        self.down: Cell = None
        self.left: Cell = None
        self.right: Cell = None
        
        
    def __repr__(self):
        return f"Cell({self.x_position}, {self.y_position})"


class Mine(Cell):
    """Represents a mine cell type"""
    def __init__(self, x, y, serial):
        
        super().__init__(x, y)
        
        self.id: int = int(f"{y}{x}")       #id is of the form (row, column)
        self.serial: str = serial
        self.mine_pin: str = None
        
    def __repr__(self):
        return f"Mine({self.x_position}, {self.y_position}) Serial: {self.serial}"
    
    def dump_to_model(self) -> MineModel:
        """Converts a Mine object to a pydantic MineModel model"""
        return MineModel(
            id=self.id,
            serial=self.serial,
            x_position=self.x_position,
            y_position=self.y_position
        )

     
class ServerMap():
    """The data structure for the 2D map grid used by the server"""
    
    def __init__(self, map_height: int=12, map_width: int=12):
        
        self.height = map_height
        self.width = map_width
        
        grid = [[0 for i in range(map_width)] for j in range(map_height)]
        self.cells: list[list[Cell | Mine]] = []
        
        #Populate Map
        for row_index, row in enumerate(grid):
            temp_row = []
            for col_index, cell in enumerate(row):
                temp_row.append(Cell(x=col_index, y=row_index))
                
            self.cells.append(temp_row)
            
        #Link the cells together
        self._link_cells()
        
    def _link_cells(self):
        """Link the cells together to form a grid."""
        
        for row in range(self.height):
            for col in range(self.width):
                cell = self.cells[row][col]
                if row > 0:
                    cell.up = self.cells[row - 1][col]
                if row < self.height - 1:
                    cell.down = self.cells[row + 1][col]
                if col > 0:
                    cell.left = self.cells[row][col - 1]
                if col < self.width - 1:
                    cell.right = self.cells[row][col + 1]
            
    def print_grid(self):
        """Print the map grid with character representations of empty cells and mines."""
        for row in self.cells:
            print(" ".join("M" if isinstance(cell, Mine) else "E" for cell in row))
            
    def array_repr(self) -> list[list[int]]:
        """Returns a 2D array of integers of either 0 or 1"""
        
        ret_array: list[list[int]] = []
        
        for row in self.cells:
            row_array: list[int] = []
            for cell in row:
                val = 1 if isinstance(cell, Mine) else 0
                row_array.append(val)
            ret_array.append(row_array)
            
        return ret_array 
    
    
    def get_mine_by_id(self, id: int) -> Mine:
        """Gets the Mine from the map with the given `id`

        Args:
            id (int): id of the mine

        Returns:
            Mine: Mine object
        """
        for row in self.cells:
            for cell in row:
                if isinstance(cell, Mine) and cell.id == id:
                    return cell
                
        return None
    
    
    def update_mine(self, id: int, args: dict) -> Mine:
        """Update the mine with the given id with the arguments provided in `args`"""
            
        
        mine = self.get_mine_by_id(id)      #current mine copy
        
        new_x = args.get("x_position", mine.x_position)
        new_y = args.get("y_position", mine.y_position)
        
        #Check if new position is different and occupied by existing mine
        if (new_x != mine.x_position or new_y != mine.y_position):
            target_cell = self.cells[new_y][new_x]
            if isinstance(target_cell, Mine) and target_cell.id != mine.id:
                raise HTTPException(status_code=400, detail=f"A mine already exists at position ({new_x}, {new_y})")
    
        if 'serial' in args:
            mine.serial = args['serial']
        
        #if mine moved positions, update the map grid
        if new_x != mine.x_position or new_y != mine.y_position:
            self.cells[mine.y_position][mine.x_position] = Cell(mine.x_position, mine.y_position)   #delete old mine
            
            #update internal coordinates
            mine.x_position = new_x
            mine.y_position = new_y
            mine.id = int(f"{new_y}{new_x}")
            
            #add to new location
            self.cells[new_y][new_x] = mine
            self._link_cells()
                
        return mine
    
    
    def delete_mine(self, id: int):
        """Deletes the Mine from the Map with the given `id` and replaces it with Cell"""
        
        current_mine = self.get_mine_by_id(id)
        x, y = current_mine.x_position, current_mine.y_position
        
        self.cells[y][x] = Cell(x=x, y=y)
        self._link_cells()
        
    
    def add_mine(self, mine: Mine) -> bool:
        """Adds a Mine object to the maps cell array"""
        
        #Ensure it is in bounds
        try:
            self.cells[mine.y_position][mine.x_position] = mine
        except IndexError:
            raise HTTPException(400, detail="Mine coordinates are out of bounds")
        self._link_cells()