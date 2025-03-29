from fastapi import APIRouter, HTTPException, status
import random

from ..memory import state

from ..models.rover import RoverBase, RoverModel, RoverUpdate
from ..models.generic import ListResponse
from ..structures.rover import Rover

router = APIRouter(
    prefix="/rovers",
    tags=["Rovers"]
)


@router.get(
    path="",
    summary="Get a list of rovers",
    description="Retrieve a list of all rovers",
    response_model=ListResponse[RoverModel],
    status_code=200
)
async def getRovers() -> ListResponse[RoverModel]:
    rovers_dict = state.rovers              #The rovers dictionary in memory
    rovers = list(rovers_dict.values())     #The rover objects as a list
    
    rovers_list = [rover.dump_to_model() for rover in rovers]
    
    return ListResponse(records=rovers_list)


@router.get(
    path="/{id}",
    summary="Retrieve a single rover",
    response_model=RoverModel,
    status_code=200
)
async def getRover(id: int) -> RoverModel:

    rover = state.rovers.get(id)        
    if rover is None:
        raise HTTPException(404, detail=f"Rover with id {id} not found")
    return rover.dump_to_model()


@router.post(
    path="",
    summary="Create a rover",
    response_model=RoverModel,
    status_code=status.HTTP_201_CREATED
)
async def createRover(rover: RoverBase) -> RoverModel:
    #remember to check for valueerror on Rover instantiation
    
    #First assign it an ID
    id = random.randint(1, 100)
    while id in state.rovers.keys():
        id = random.randint(1, 100)
    
    #Create the rover
    new_rover = Rover(id=id, commands=rover.commands, map=state.map,
                    start_x=rover.x_position, start_y=rover.y_position, orientation=rover.orientation)
    
    state.rovers[id] = new_rover
    
    created_rover = RoverModel(**rover.model_dump(), status=new_rover.status, id=id)
    return created_rover



@router.post(
    path="/{id}/dispatch",
    summary="Dispatch a rover",
    response_model=RoverModel,
    status_code=status.HTTP_201_CREATED
)
async def dispatchRover(id: int) -> RoverModel:
    rover = state.rovers.get(id)
    if rover is None:
        raise HTTPException(404, detail=f"Rover with id {id} not found")
    
    if rover.status == 'Moving':
        raise HTTPException(409, detail=f"Rover {id} is currently running. Please wait.")
    
    if rover.status == 'Eliminated':
        raise HTTPException(400, detail=f"Rover {id} has been destroyed.")
    
    rover.dispatch()
    
    rover = state.rovers.get(id)
    
    return rover.dump_to_model()



@router.put(
    path="/{id}",
    summary="Send a list of commands to the rover",
    response_model=RoverModel,
    status_code=status.HTTP_200_OK
)
async def updateRover(id: int, commands: RoverUpdate) -> RoverModel:
    
    rover = state.rovers.get(id)
    if rover is None:
        raise HTTPException(404, detail=f"Rover with id {id} not found")
    
    if rover.status == 'Moving':
        raise HTTPException(400, detail=f"Rover {id} is currently running. Please wait.")
    
    if rover.status == 'Eliminated':
        raise HTTPException(400, detail=f"Rover {id} has been destroyed.")
    
    state.rovers[id].commands = commands
    rover = state.rovers.get(id)
    
    return rover.dump_to_model()
    


@router.delete(
    path="/{id}",
    summary="Delete a rover",
    status_code=status.HTTP_204_NO_CONTENT
)
async def deleteRover(id: int):
    if id not in state.rovers.keys():
        raise HTTPException(404, detail=f"Rover with id {id} not found")
    
    del state.rovers[id]