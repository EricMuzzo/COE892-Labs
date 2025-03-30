from fastapi import FastAPI
from .routers import maps, rovers, mines
from .structures.map import ServerMap
from .memory import state

description = """
A centralized RESTful API for the Rover mining system. COE892 Lab 4
"""


tags_metadata = [
    {
        "name": "Rovers",
        "description": "Operations with rover objects"
    },
    {
        "name": "Map",
        "description": "Operations on the map"
    },
    {
        "name": "Mines",
        "description": "Operations on mines within the map"
    }
]


#============================================================
#   Application setup
#============================================================

app = FastAPI(
    title="Central API",
    description=description,
    version="1.1.2",
    contact={
        "name": "Eric Muzzo",
        "email": "ericm02@me.com"
    },
    openapi_tags=tags_metadata
)

@app.on_event("startup")
async def startup():
    state.map = ServerMap()
    print("Map initialized")
    state.rovers = {}
    
@app.on_event("shutdown")
async def shutdown():
    pass

#============================================================
#   Register the routes
#============================================================

app.include_router(maps.router)
app.include_router(rovers.router)
app.include_router(mines.router)


@app.get("/")
async def root():
    return {"message": "FastAPI WebSocket and REST API Central Server"}