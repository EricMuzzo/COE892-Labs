from models import *
import requests
import time
from threading import Thread

path = "./res/map1.txt"
num_rovers = 10
baseURL = "https://coe892.reev.dev/lab1/rover/"


def init_rovers(map_width: int, map_height: int):
    """Generates the rover objects by grabbing JSON data from API endpoint"""
    rovers: dict[int, Rover] = {}
    
    #Grab the rover data
    for rover_id in range(1, num_rovers+1):
        endpoint = f"{baseURL}/{rover_id}"
        response = requests.get(endpoint).json()

        #Parse the json response body
        moves = response["data"]["moves"]

        #Initialize rover object
        rover = Rover(rover_id, moves, grid.cells[0][0], map_width, map_height)
        rovers[rover_id] = rover
        
    return rovers
    
    
def static_main():
    """Non-threaded version of the program"""
    
    rovers: dict[int, Rover] = init_rovers(map_width=grid.num_cols, map_height=grid.num_rows)
    print("\nRovers initialized:")
    for rover in rovers:
        print(rovers[rover])
        
    for rover in rovers.values():
        print(f"[ROVER {rover.id}]: starting...")
        rover.run()
        print(f"[ROVER {rover.id}]: finished.")
        
        output = open(f"./out/path_{rover.id}.txt", "w")
        output.write(rover.getPathArrayString())
        output.close()
      
        
def roverThread(rover_id: int):
    """Thread function for each rover when threading option is selected"""
    
    endpoint = f"{baseURL}/{rover_id}"
    response = requests.get(endpoint).json()

    #Parse the json response body
    moves = response["data"]["moves"]

    #Initialize rover object
    rover = Rover(rover_id, moves, grid.cells[0][0], grid.num_cols, grid.num_rows)

    print(f"[ROVER {rover.id}]: starting...")
    rover.run()
    print(f"[ROVER {rover.id}]: finished.")
    
    output = open(f"./out/path_{rover.id}.txt", "w")
    output.write(rover.getPathArrayString())
    output.close()
   
    
def dynamic_main():
    """Threaded version of the program"""
    
    threads = []
    for i in range (1, num_rovers+1):
        t = Thread(target=roverThread, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
 
   
if __name__ == "__main__":
    
    option = input("Enter 1 for non-threaded version, 2 for threaded version: ")
    
    start_time = time.time()
    #Initialize the map grid and rover objects
    grid = Map(path)
    print("Map initialized")
    
    if option == "1":
        static_main()
    elif option == "2":
        dynamic_main()
    else:
        print("Invalid option. Aborting")
        exit(1)
    
    end_time = time.time()
    exec_time = end_time - start_time
    print(f"\nExecution time: {exec_time} seconds")