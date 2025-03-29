from pydantic import BaseModel, Field
from typing import Optional

class MineBase(BaseModel):
    serial: str = Field(..., max_length=10, description="The alphanumeric serial number of the mine. Maximum of 10 characters")
    x_position: int = Field(..., description="The x coordinate of the mine on the map")
    y_position: int = Field(..., description="The y coordinate of the mine on the map")
    
class MineModel(MineBase):
    """Used for"""
    id: int = Field(..., description="The id of the rover")
    
class MineUpdate(MineBase):
    serial: Optional[str] = None
    x_position: Optional[int] = None
    y_position: Optional[int] = None