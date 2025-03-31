# Lab 4 - Python NiceGUI Frontend

*Author:* Eric Muzzo

**Note** This is quite a brutal chunk of code that I'm not proud of. I would like to redo this at some point when I have time.
- WebSocket communication with backend does not work. If you really want to test that, use postman.

## Installation Instructions <a name="installation"></a>

Follow the steps below to set up and run the programs for this project.

### 1. Create a Python Virtual Environment

First, navigate to the `/Operator` directory and create a virtual environment:

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

From the `/Operator` directory run:

```sh
python main.py     #development mode
```

It will automatically launch on your web browser.