# Lab 2 - Distributed Cloud Computing

## Instructions

Follow the steps below to set up and run the programs for this project.

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

Install the required dependencies using `pip`:

```sh
pip install -r requirements.txt
```

### 4. Run the Server

```sh
python server.py
```

### 5. Run the Client

```sh
python client.py
```

## Notes

- Ensure you have Python installed on your system.
- Make sure to activate the virtual environment each time you work on the project.
- The command seen below which is used to create the gRPC python files was slightly modified to resolve relative import issues within the ground_control_pb2_grpc.py file
    - Line 7 was modified from `import ground_control_pb2 as ground__control__pb2` to `from . import ground_control_pb2 as ground__control__pb2`