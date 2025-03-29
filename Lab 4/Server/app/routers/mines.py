from fastapi import APIRouter, HTTPException

from ..models.generic import ListResponse
from ..models.mine import MineModel, MineBase, MineUpdate
from ..memory import state
from ..structures.map import Mine

router = APIRouter(
    prefix="/mines",
    tags=["Mines"]
)



@router.get(
    path="",
    summary="Retrieve a list of all mines",
    response_model=ListResponse[MineModel],
    status_code=200
)
async def getMines() -> ListResponse[MineModel]:
    cells = state.map.cells
    mine_list = []
    for row in cells:
        for cell in row:
            if isinstance(cell, Mine):
                mine_list.append(cell.dump_to_model())
                
    return ListResponse(records=mine_list)
                



@router.get(
    path="/{id}",
    summary="Retrieve a single mine",
    response_model=MineModel,
    status_code=200
)
async def getMine(id: int) -> MineModel:
    map = state.map
    mine = map.get_mine_by_id(id)
    
    if mine is None:
        raise HTTPException(404, detail=f"Mine with id {id} not found")
    
    return mine.dump_to_model()



@router.post(
    path="",
    summary="Create a mine",
    description="Adds a Mine object to the Map. If one already exists, the data will be overwritten.",
    response_model=MineModel,
    status_code=201
)
async def createMine(mine: MineBase) -> MineModel:
    """Creates a mine. If mine already exists at given position, then the mine
    will be overwritten with the new data.
    """
    
    new_mine = Mine(x=mine.x_position, y=mine.y_position, serial=mine.serial)
    state.map.add_mine(new_mine)
    
    return new_mine.dump_to_model()



@router.put(
    path="/{id}",
    summary="Update a mine",
    response_model=MineModel,
    status_code=200
)
async def updateMine(id: int, update_data: MineUpdate) -> MineModel:
    
    map = state.map
    mine = map.get_mine_by_id(id)
    
    if mine is None:
        raise HTTPException(404, detail=f"Mine with id {id} not found")
    
    update_args = update_data.model_dump(exclude_none=True)
    
    updated_mine = state.map.update_mine(id, update_args)
    return updated_mine.dump_to_model()


@router.delete(
    path="/{id}",
    summary="Delete a mine",
    description="Deletes the mine with the given ID and replaces that Cell with the standard Cell type",
    status_code=204
)
async def deleteMine(id: int):
    map = state.map
    mine = map.get_mine_by_id(id)
    
    if mine is None:
        raise HTTPException(404, detail=f"Mine with id {id} not found")
    
    map.delete_mine(id)