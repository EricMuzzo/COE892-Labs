from nicegui import ui, run
import httpx

API_BASE = "https://coe892lab42022em-hzhha3aaaca6eyhu.canadacentral-01.azurewebsites.net"

state = {
    "width": 0,
    "height": 0,
    "cell_refs": [],
    "grid_container": None,
    "selected_rover_id": None
}


async def fetch_map_data():
    """Function to fetch map data"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/map")
        response.raise_for_status()
        return response.json()
    
    
async def update_map_data(width, height):
    """Function to fetch map data"""
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{API_BASE}/map", json={
            "width": width,
            "height": height
        })
        response.raise_for_status()
        return response.json()
    
    
async def fetch_mines():
    """Function to fetch mine data"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/mines")
        response.raise_for_status()
        return response.json()
    
    
async def fetch_mine(id: int):
    """Function to fetch mine"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/mines/{id}")
        response.raise_for_status()
        return response.json()
    
    
async def create_mine(serial: str, x_position: int, y_position: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE}/mines", json={
            "serial": serial,
            "x_position": x_position,
            "y_position": y_position
        })
        response.raise_for_status()
        return response.json()
    
    
async def delete_mine(id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{API_BASE}/mines/{id}")
        response.raise_for_status()
    
    
async def fetch_rovers():
    """Function to fetch rovers"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/rovers")
        response.raise_for_status()
        return response.json()
    
    
async def fetch_rover(id: int):
    """Function to fetch rover"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/rovers/{id}")
        response.raise_for_status()
        return response.json()
    
    
async def send_dispatch_call(id: int):
    """Function to fetch rover"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE}/rovers/{id}/dispatch")
        response.raise_for_status()
        return response.json()
    
    
async def create_rover(commands: str, x_position: int, y_position: int, orientation: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE}/rovers", json={
            "commands": commands,
            "x_position": x_position,
            "y_position": y_position,
            "orientation": orientation
        })
        response.raise_for_status()
        return response.json()
    
    
async def delete_rover(id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{API_BASE}/rovers/{id}")
        response.raise_for_status()
    

async def dispatch_rover(rover_id: int, dialog):
    ui.notify(f"Dispatching rover {rover_id}", type='positive')
    dialog.close()
    
    await send_dispatch_call(rover_id)

async def render_map(data=None, mine_records=None, rover_records=None):
    
    if data is None:
        data = await fetch_map_data()
        
    if mine_records is None:
        mine_data = await fetch_mines()
        mine_records = mine_data.get("records", [])
        
    mine_lookup = {(m["y_position"], m["x_position"]): m["id"] for m in mine_records}
    
    if rover_records is None:
        rover_data = await fetch_rovers()
        rover_records = rover_data.get("records", [])
        
    rover_lookup = {(r["y_position"], r["x_position"]): r for r in rover_records}

    game_map = data["map"]
    state["height"] = data["height"]
    state["width"] = data["width"]

    state["cell_refs"].clear()
    
    if state["grid_container"] is not None:
        state["grid_container"].clear()

    # Create a centered column for the grid
    with state["grid_container"]:
        with ui.element("div").classes("grid border").style(
            f"""
            max-width: 90vw;
            width: min(800px, 100%);
            max-height: 60vh;
            overflow-y: auto;
            display: grid;
            grid-template-columns: repeat({state["width"]}, 1fr);
            gap: 2px;
            """
        ):
            for row in range(state["height"]):
                row_cells = []
                for col in range(state["width"]):
                    value = game_map[row][col]
                    emoji = ""
                    if value == 1:
                        emoji = "💣"
                    if (row, col) in rover_lookup:
                        emoji = "🚗"

                    tooltip_text = f"({row}, {col})"
                    if (row, col) in mine_lookup:
                        tooltip_text += f"\nMine {mine_lookup[(row, col)]}"
                    if (row, col) in rover_lookup:
                        tooltip_text += f"\nRover {rover_lookup[(row, col)]['id']}"
                        
                    def handle_click(r=rover_lookup.get((row, col))):
                        if r:
                            state["selected_rover_id"] = r["id"]
                            show_rover_dispatch_popup(r)

                    # Square cell with aspect ratio 1:1
                    label = ui.label(emoji).classes(
                        "border flex items-center justify-center text-xl bg-white"
                    ).style(
                        "aspect-ratio: 1 / 1; width: 100%;"
                    ).tooltip(tooltip_text).on("click", handle_click)

                    if emoji:
                        label.text = emoji
                        
                    row_cells.append(label)
                state["cell_refs"].append(row_cells)

 
def show_rover_dispatch_popup(rover):
    dialog = ui.dialog()

    with dialog:
        with ui.card().classes("w-72 p-4"):
            with ui.row().classes("justify-between items-center"):
                ui.label(f"Rover {rover['id']}").classes("text-lg font-bold")
                ui.button("❌", on_click=dialog.close).props("flat")

            ui.label(f"Position: ({rover['x_position']}, {rover['y_position']})")
            ui.label(f"Orientation: {rover['orientation']}")
            ui.label(f"Commands: {rover['commands']}")
            ui.label(f"Status: {rover['status']}")

            with ui.row().classes("justify-end mt-4"):
                ui.button("Dispatch", color="orange", on_click=lambda: dispatch_rover(rover["id"], dialog))

    dialog.open()
    

              
def update_cell(row: int, col: int, emoji: str):
    """Update an individual cell's emoji"""
    cell = state["cell_refs"][row][col]
    cell.text = emoji
    cell.update()
 
    
    
def render_map_controls():
    """Render the map control panel (left column)"""
    with ui.column().classes("items-center w-full sm:w-1/2 lg:w-1/3 max-w-sm"):
        ui.label("🗺️ Map Controls").classes("text-lg font-semibold mb-2")

        width_input = ui.input("Width").classes("w-32 mb-2")
        height_input = ui.input("Height").classes("w-32 mb-2")

        # Initialize input values from current state
        width_input.value = str(state["width"])
        height_input.value = str(state["height"])

        def validate_int(value: str) -> bool:
            return value.strip().isdigit()

        async def handle_map_update():
            if not (validate_int(width_input.value) and validate_int(height_input.value)):
                ui.notify("Width and height must be valid integers", type="warning")
                return

            confirm_dialog = ui.dialog()
            with confirm_dialog:
                ui.label("⚠️ Warning: Updating the map will erase current state. Continue?")
                with ui.row().classes("justify-end mt-4"):
                    ui.button("Cancel", on_click=confirm_dialog.close)
                    ui.button("Confirm", color="red", on_click=lambda: confirm_dialog.submit("confirm"))

            result = await confirm_dialog
            if result != "confirm":
                return

            new_width = int(width_input.value)
            new_height = int(height_input.value)

            updated_data = await update_map_data(new_width, new_height)

            # Update internal state
            state["width"] = new_width
            state["height"] = new_height

            # Update the map grid visually
            await render_map(data=updated_data)

        ui.button("Update Map", color="red", on_click=handle_map_update)
        


def render_mine_controls():
    """Render the mines control panel (middle column)"""

    mine_list_container = None

    with ui.column().classes("items-center w-full sm:w-1/2 lg:w-1/3 max-w-sm border-l border-gray-300 pl-4"):
        ui.label("💣 Mines Panel").classes("text-lg font-semibold mb-2")


        def open_create_mine_dialog():
            dialog = ui.dialog()
            with dialog:
                with ui.card().classes("items-center p-4 w-80"):
                    ui.label("Create New Mine").classes("text-lg font-bold mb-2")

                    serial_input = ui.input("Serial Number").props("maxlength=10").classes("mb-2 w-48")
                    x_input = ui.input("X Position").classes("mb-2 w-48")
                    y_input = ui.input("Y Position").classes("mb-4 w-48")

                    with ui.row().classes("justify-end gap-2"):
                        ui.button("Cancel", on_click=dialog.close)
                        ui.button("Submit", color="green", on_click=lambda: submit_create_mine(dialog, serial_input, x_input, y_input))

            dialog.open()

        async def submit_create_mine(dialog, serial_input, x_input, y_input):
            serial = serial_input.value.strip()
            x = x_input.value.strip()
            y = y_input.value.strip()

            # Validation
            if not serial or not serial.isalnum() or len(serial) > 10:
                ui.notify("Serial must be alphanumeric and ≤ 10 characters", type="warning")
                return
            if not (x.isdigit() and y.isdigit()):
                ui.notify("X and Y must be integers", type="warning")
                return

            x = int(x)
            y = int(y)

            # Send POST request
            await create_mine(serial, x, y)

            # Close dialog and update the map
            dialog.close()
            await render_map()
            await refresh_mine_list()
        
        ui.button("Create Mine", on_click=open_create_mine_dialog)
        
        mine_list_container = ui.column().classes("w-full mt-4 gap-2")

        async def refresh_mine_list():
            mine_list_container.clear()
            data = await fetch_mines()
            for mine in data["records"]:
                with mine_list_container:
                    ui.button(f"Mine {mine['id']}", on_click=lambda m=mine: show_mine_popup(m["id"])) \
                        .classes("w-full text-left bg-gray-100 hover:bg-gray-200")

        async def show_mine_popup(mine_id: int):
            # Fetch full mine data
            mine = await fetch_mine(mine_id)

            dialog = ui.dialog()
            with dialog:
                with ui.card().classes("items-center w-72 p-4"):
                    with ui.row().classes("justify-between items-center"):
                        ui.label(f"Mine {mine['id']}").classes("text-lg font-bold")
                        ui.button("❌", on_click=dialog.close).props("flat")

                    ui.label(f"Serial: {mine['serial']}")
                    ui.label(f"X Position: {mine['x_position']}")
                    ui.label(f"Y Position: {mine['y_position']}")

                    with ui.row().classes("justify-end mt-4"):
                        ui.button("Delete", color="red", on_click=lambda: delete_mine_and_refresh(mine['id'], dialog))

            dialog.open()

        async def delete_mine_and_refresh(mine_id: int, dialog):
            response = await delete_mine(mine_id)

            dialog.close()
            await render_map()
            await refresh_mine_list()

        # Load initial list when the app loads
        ui.timer(0.1, refresh_mine_list, once=True)
        


def render_rover_controls():
    """Render the rover control panel (right column)"""

    rover_list_container = None

    with ui.column().classes("items-center w-full sm:w-1/2 lg:w-1/3 max-w-sm border-l border-gray-300 pl-4"):
        ui.label("Rover Panel").classes("text-lg font-semibold mb-2")


        def open_create_rover_dialog():
            dialog = ui.dialog()
            with dialog:
                with ui.card().classes("items-center p-4 w-80"):
                    ui.label("Create New Rover").classes("text-lg font-bold mb-2")

                    commands = ui.input("Command Sequence").classes("mb-2 w-48")
                    x_input = ui.input("Starting X Position").classes("mb-2 w-48")
                    y_input = ui.input("Starting Y Position").classes("mb-4 w-48")
                    orientation = ui.select(["DOWN", "UP", "LEFT", "RIGHT"], value="DOWN")

                    with ui.row().classes("justify-end gap-2"):
                        ui.button("Cancel", on_click=dialog.close)
                        ui.button("Submit", color="green", on_click=lambda: submit_create_rover(dialog, commands, x_input, y_input, orientation))

            dialog.open()

        async def submit_create_rover(dialog, commands, x_input, y_input, orientation):
            commands = commands.value.strip().replace(" ", "")
            start_x = x_input.value.strip()
            start_y = y_input.value.strip()
            orientation = orientation.value

            # Validation
            if not (start_x.isdigit() and start_y.isdigit()):
                ui.notify("X and Y must be integers", type="warning")
                return

            x = int(start_x)
            y = int(start_y)

            # Send POST request
            await create_rover(commands, x, y, orientation)

            # Close dialog and update the map
            dialog.close()
            await render_map()
            await refresh_rover_list()
        
        ui.button("Create Rover", on_click=open_create_rover_dialog)
        
        rover_list_container = ui.column().classes("w-full mt-4 gap-2")

        async def refresh_rover_list():
            rover_list_container.clear()
            data = await fetch_rovers()
            for rover in data["records"]:
                with rover_list_container:
                    ui.button(f"Rover {rover['id']}", on_click=lambda m=rover: show_rover_popup(m["id"])) \
                        .classes("w-full text-left bg-gray-100 hover:bg-gray-200")

        async def show_rover_popup(rover_id: int):
            # Fetch full rover data
            rover = await fetch_rover(rover_id)

            dialog = ui.dialog()
            with dialog:
                with ui.card().classes("w-72 p-4"):
                    with ui.row().classes("justify-between items-center"):
                        ui.label(f"Rover {rover['id']}").classes("text-lg font-bold")
                        ui.button("❌", on_click=dialog.close).props("flat")

                    ui.label(f"Commands: {rover['commands']}")
                    ui.label(f"X Position: {rover['x_position']}")
                    ui.label(f"Y Position: {rover['y_position']}")
                    ui.label(f"Orientation: {rover['orientation']}")
                    ui.label(f"Status: {rover['status']}")

                    with ui.row().classes("justify-end mt-4"):
                        ui.button("Delete", color="red", on_click=lambda: delete_rover_and_refresh(rover['id'], dialog))
                        ui.button("Place On Map", color="blue", on_click=lambda r=rover: place_rover_on_map(r, dialog))

            dialog.open()

        async def delete_rover_and_refresh(rover_id: int, dialog):
            response = await delete_rover(rover_id)

            dialog.close()
            await render_map()
            await refresh_rover_list()
            
        
        def place_rover_on_map(rover, dialog):
            row = rover["y_position"]
            col = rover["x_position"]
            update_cell(row, col, "🚗")
            dialog.close()

        # Load initial list when the app loads
        ui.timer(0.1, refresh_rover_list, once=True)


@ui.page("/")
async def main():
    with ui.row().classes("w-full justify-center mb-4"):
        ui.label("COE892 Lab 4 Rover Simulator").classes("text-2xl font-bold")

    # Grid container placeholder (will be populated later)
    with ui.row().classes("w-full justify-center") as grid_row:
        state["grid_container"] = ui.column().classes("w-full items-center")

    # Initial map render
    await render_map()
    
    # --- Control Section ---
    # Control Section
    with ui.row().classes("w-full justify-evenly mt-8 flex-wrap"):
        render_map_controls()
        render_mine_controls()
        render_rover_controls()

# Start the app
ui.run(title="Rover Operator UI")