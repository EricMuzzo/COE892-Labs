import pika
import json
from hashlib import sha256

class Deminer:
    """An instance of a deminer object used for demining mines"""
    
    def __init__(self, id):
        self.id = id
        
        self.rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters("localhost", 5672))
        self.rabbit_channel = self.rabbit_connection.channel()
        
        self.rabbit_channel.queue_declare(queue="Demine-Queue")
        self.rabbit_channel.queue_declare(queue="Defused-Mines")
        
    def start(self):
        """Startup the deminer instance"""
        
        try:
            self.rabbit_channel.basic_consume(queue="Demine-Queue", on_message_callback=self.on_task_received, auto_ack=True)
            print(f"\n[DEMINER {self.id}] awaiting tasks")
            self.rabbit_channel.start_consuming()
        except KeyboardInterrupt:
            print(f"\n[DEMINER {self.id}] KeyboardInterrupt received. Stopping consumption")
            self.rabbit_channel.stop_consuming()
            self.rabbit_connection.close()
        
    def on_task_received(self, channel, method, properties, body: bytes):
        """Handles a task in the queue"""

        message = json.loads(body.decode())
        
        #Variable Extraction
        rover_id = message["id"]
        x_pos, y_pos = message["position"]["x_pos"], message["position"]["y_pos"]
        serial = message["serial"]
        
        print(f"\n[DEMINER {self.id}] is processing a request from Rover {rover_id} for serial {serial} at position ({x_pos},{y_pos})")
        
        #Find the pin
        pin = self.mine(serial)
        
        payload = json.dumps({
            "deminer_id": self.id,
            "rover_id": rover_id,
            "position": {
                "x_pos": x_pos,
                "y_pos": y_pos
            },
            "serial": serial,
            "pin": pin
        })
        
        #Publish message to channel
        self.rabbit_channel.basic_publish(
            exchange='',
            routing_key='Defused-Mines',
            body=payload
        )
        
        print(f"[DEMINER {self.id}] Found pin {pin}, published to 'Defused-Mines' Queue")
        
    def mine(self, serial: str) -> str:
        """Attempts to mine the current mine with the given serial number.

        Args:
            serial (str): The serial number of the mine

        Returns:
           (str) : The pin found
        """
        
        pin = 0
        while True:
            hash_val = self.hashKey(str(pin), serial)
            
            if hash_val.startswith("000000"):
                return str(pin)
            
            pin += 1
    
    
    def hashKey(self, pin: str, serial: str) -> str:
        temp_key = pin + serial
        
        hash_key = sha256(temp_key.encode()).hexdigest()
        
        return hash_key
        
    
if __name__ == "__main__":
    
    while True:
        deminer_id = input("Enter a Deminer number (1 or 2): ")
        if deminer_id == "1" or deminer_id == "2":
            break
        print("Invalid Deminer ID")
        
    print("Setting up deminer...")
    
    deminer = Deminer(deminer_id)
    deminer.start()