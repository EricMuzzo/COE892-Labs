from pydantic import BaseModel, Field

class Map(BaseModel):
    """Response model for GET endpoint requests"""
    map: list[list[int]] = Field(..., description="2D Array of cells. 0=empty, 1=mine present")
    height: int = Field(..., description="The height (# of rows) of the map")
    width: int = Field(..., description="The width (# of columns) of the map")
    
    
class MapUpdate(BaseModel):
    """Used to update the height and width of the field"""
    height: int = Field(..., description="The height (# of rows) of the map")
    width: int = Field(..., description="The width (# of columns) of the map")