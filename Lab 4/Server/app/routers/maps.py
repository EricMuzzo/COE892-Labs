from fastapi import APIRouter, HTTPException
from ..models.map import Map, MapUpdate
from ..memory import state
from ..structures.map import ServerMap

router = APIRouter(
    prefix="/map",
    tags=["Map"]
)

@router.get(
    path="",
    summary="Get the 2D map array of the field",
    description="0's indicate an empty cell while 1's indicate a mine",
    response_model=Map
)
async def getMap() -> Map:
    map = state.map
    return Map(map=map.array_repr(), height=map.height, width=map.width)



@router.put(
    path="",
    summary="Update the height and width of the field",
    description="Doing this wipes the memory of the current map along with all of the mines",
    response_model=Map
)
async def updateMap(update_data: MapUpdate) -> Map:
    """For now we will assume that calling this endpoint destroys the in-memory map and
    replaces it with a new one"""
    new_map = ServerMap(map_height=update_data.height, map_width=update_data.width)
    state.map = new_map
    return Map(map=new_map.array_repr(), height=new_map.height, width=new_map.width)