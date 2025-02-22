import grpc
from rpc import ground_control_pb2 as gc_pb2
from rpc import ground_control_pb2_grpc as gc_pb2_grpc

from src.models import logger, Map, Rover

#============================================
# Constants
#============================================
HOST = "localhost"
PORT = 5001


def fetch_map() -> Map:
    """Fetch the map from the server and process it into a Map data structure"""
    
    map_res = stub.GetMap(gc_pb2.MapRequest())
    
    #Convert back to 2D list formal
    map_grid = [list(row.cells) for row in map_res.grid]
    
    numRows:int = map_res.numRows
    numCols:int = map_res.numCols
    
    #Store in Map Data Structure
    map = Map(grid=map_grid, num_rows=numRows, num_cols=numCols)
    
    logger.info("Map received and processed")
    
    return map


def init_rover(rover_id: int) -> Rover:
    """Generates the rover object"""
    
    #Get and process rover's commands from the server
    
    cmd_res = stub.GetCommands(gc_pb2.CommandRequest(rover_id=rover_id))
    commands:str = cmd_res.commands
    
    #Instantiate object
    rover = Rover(id=rover_id, map=map, commands=commands, stub=stub)
    logger.info(f"Commands received and processed: {commands}")
    
    return rover
    

if __name__ == "__main__":
    
    while True:
        id = int(input("Enter a rover id: "))
        if 1 <= id <= 10:
            break
        print("Invalid rover ID. ID must be between 1 and 10.")
    
    
    #=================================================================
    # Setup server communication
    #=================================================================
    try:
        channel = grpc.insecure_channel(f"{HOST}:{PORT}")
        stub = gc_pb2_grpc.GroundControlStub(channel)
    except Exception as e:
        logger.critical(f"Failed to establish communication with server")
        exit()
        

    #=================================================================
    # Get and process the map from the server
    #=================================================================
    map:Map = fetch_map()
    
    
    #=================================================================
    # Get rover commands and instantiate the Rover object
    #=================================================================
    rover = init_rover(id)
    logger.info(f"Rover {rover.id} initialized")
    
    #=================================================================
    # Run the rover
    #=================================================================
    print(f"\n[ROVER {rover.id}]: starting...\n")
    
    rover.run()
    
    # write rover's path to file
    output = open(f"./out/path_{rover.id}.txt", "w")
    output.write(rover.getPathArrayString())
    output.close()
    logger.info(f"Rover {rover.id}'s output path written to file")
    
    print(f"\n[ROVER {rover.id}]: finished.")