# Lab 4 - Python FastAPI Server

*Author:* Eric Muzzo

# Table of Contents
1. [Overview](#overview)
2. [Installation & Running the application](#installation)
3. [Docker Deployment](#docker)
4. [Notes and Comments](#notes)

## Overview <a name="overview"></a>
This is my fastAPI python REST API for the project. It was made in a nice modular format and should be fairly easy to understand.
It was deployed to Azure and then used for the frontend application.


## Installation Instructions <a name="installation"></a>

Follow the steps below to set up and run the programs for this project.

### 1. Create a Python Virtual Environment

First, navigate to the `/Server` directory and create a virtual environment:

```sh
python -m venv venv
```

### 2. Activate the Virtual Environment

Activate the virtual environment:

- On Windows:
    ```sh
    .\venv\Scripts\activate
    ```
- On macOS and Linux:
    ```sh
    source venv/bin/activate
    ```

### 3. Install Dependencies

Install the required dependencies using `pip`:

```sh
pip install -r requirements.txt
```

### 4. Run the Program

From the `/Server` directory run:

```sh
fastapi dev app/main.py     #development mode
```

```sh
fastapi run app/main.py     #deployment mode
```


## Docker Deployment <a name="docker"></a>

I won't go very in detail on deploying to Azure, but I will give a very breif overview of what to do.
Obviously, you need docker installed on your system.

1. Create the dockerfile
2. Build the docker image (Do this in the same dir as your dockerfile)
    - `docker build -t <your_image_name>:<version>`
    - I like to keep the `<version>` consistent with the version found in my fastapi App() definition. I'll then use this to overwrite the *Azure Ready* image
3. On Azure, create a Container Registry. Grab the login server hostname once this is deployed.
    - and also a new resource group
4. On your machine, login to the registry
    - `docker login something.azurecr.io`
    - Use admin credentials from the Access Keys page on Azure
5. Create an *Azure Ready* image of your most recent application image version
    - `docker tag <your_image_name>:<version> something.azurecr.io/<your_image_name>:latest`
    - For this lab, I never change the :latest tag of the Azure image. This is so that every time I push a new version of the app, it automatically replaces the existing version (if you enabled continuous deployment)
6. Push to Azure
    - `docker push something.azurecr.io/<your_image_name>:latest`
7. Create a *Web App for Containers* resource on Azure using the image we just pushed. Google this for more info its pretty simple however.
    - deploy this and that's it.

## Notes and Comments <a name="notes"></a>
I'll just give a breif description on the less self-explanatory components of my app as well as some general notes

- #### The models package:
    - If you've never used pydantic before, in terms of fastAPI apps, its a really great way taking care of data validation
    - These are basically simple data structures that you define and then use in your endpoints to tell fastAPI what kind of data a request/response should contain. FastAPI handles the rest
    - These don't do much functionally other than that, except for removing the need for you to check if data exists, is the right type, etc in each endpoint

- #### The structures package:
    - In here you will find two modules with class definitions; one for a Rover object, one for the map
    - All of the operations that happen to a rover are implemented as class methods. This way, everything is contained in the same place (and migrated from previous labs) and all I have to do is build the actual API. I don't care what goes on under the hood because I did it 
    3 times in the previous labs.
    - The ServerMap class is a fancy 2D array, except it is stored as a sort of linked list.
        - I defined a class to represent a Cell
        - Each cell has up, down, left right Cell references
        - A ServerMap instance stores a 2D list of cells
        - A Rover technically only needs to store a reference to a single cell; its position
        - When the ServerMap is instantiated, these are all linked together so traversal is as simple as calling `rover.position.up` for example.

- #### The memory
    - This is nothing more than global in-memory storage for the map and rovers once the API is running

- #### General Notes:
    - updating the map causes a wipe to existing memory
    - rovers will have delays in their execution so that doing anything real time is possible