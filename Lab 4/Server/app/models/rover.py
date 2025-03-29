from pydantic import BaseModel, Field
from typing import Literal


class RoverBase(BaseModel):
    """Used for creation"""
    commands: str = Field(..., example="MRLDRLMDD")
    x_position: int = Field(default=0, description="The x coordinate of the rover on the map")
    y_position: int = Field(default=0, description="The y coordinate of the rover on the map")
    orientation: Literal["UP", "DOWN", "LEFT", "RIGHT"] = Field(default="DOWN", description="The starting orientation")

class RoverModel(RoverBase):
    """Used for responses, includes the id."""
    id: int = Field(..., description="The id of the rover")
    status: Literal['Not Started', 'Finished', 'Moving', 'Eliminated'] = Field(default='Not Started', description="The status of the rover")

    
class RoverUpdate(BaseModel):
    """Model used for validating PUT endpoint request body."""
    commands: str = Field(..., example="MRLDRLMDD")