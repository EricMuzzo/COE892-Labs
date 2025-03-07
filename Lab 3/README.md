# Lab 3 - Distributed Cloud Computing

## Setup

Follow the steps below to set up your environment for this project.

### 1. Create a Python Virtual Environment

First, navigate to the project directory and create a virtual environment:

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

Install the required dependencies using `pip` and the provided `requirements.txt` file:

```sh
pip install -r requirements.txt
```

### 4. Create the RabbitMQ Server with Docker

Ensure you have docker installed on your system and the Docker Daemon is running. Run the following command to create the RabbitMQ container:

```sh
docker run --name mqserver -p 5672:5672 rabbitmq
```
- This creates a RabbitMQ container named **mqserver** and maps the default AMQP port **5672**
- Ensure the container is running either through CMD or through Docker Desktop

## Running the application

To run this application according to the lab instructions, you will need 4 terminals:
1. The Ground Control Server
2. The client script
3. Deminer 1
4. Deminer 2

*Note: It would likely be easier to initialize the deminers via the client script but the lab manual specifies having a CLI for them taking user input to instantiate 2 deminers; Deminer 1 and Deminer 2. Thus, terminals 3 and 4 adhere to the lab manual*

### 1. Run the Server

```sh
python server.py
```

### 2. Run the Deminers

- In terminal 3: `python src/deminers.py`
- Then input either 1 or 2 for the deminer ID

- In terminal 4: `python src/deminers.py`
- Then input either 1 or 2 for the deminer ID

### 3. Run the Client

```sh
python client.py
```

- Then specify a rover ID (1-10)

## Notes

- The procedure I implemented works on the assumption that when a Rover comes across a mine and publishes a demining task to the 'Demine-Queue', it assumes that the deminers will demine the mine and therefore sets the value of that cell on the map to 'EMPTY' and proceeds with map traversal without waiting on confirmation.
- Ensure you have Python installed on your system.
- Make sure to activate the virtual environment each time you work on the project.
- Ensure the RabbitMQ docker container is running on your system
- The import statement seen below which is created from the gRPC compiler was slightly modified to resolve relative import issues within the ground_control_pb2_grpc.py file
    - Line 6 was modified from `import ground_control_pb2 as ground__control__pb2` to `from . import ground_control_pb2 as ground__control__pb2`