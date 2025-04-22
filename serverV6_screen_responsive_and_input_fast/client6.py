#SCREEN SHARING AS WELL AS INPUT
#GO WITH HOST6

import socket
import struct
import cv2
import time
import threading
import keyboard
import json
import keyboard
from functools import wraps
import numpy as np

ID = input("Enter the ipv4 address: ")
AMOUNT_OF_BYTE_PER = 4096
SERVER_IP = HOST = ID #socket.gethostbyname(socket.gethostname()) 
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MSG = "DISCONNECT"

# Global variables for the client socket and connection state.
client = None
connecting = False
allow_input = True
latest_frame = None  # Shared variable for the most recent frame

def toggle_input():
    global allow_input
    allow_input = not allow_input #switch between sending input or not
    print("Allow input is now: " + (str)(allow_input))
    
def receive_image():
    global client, connecting, latest_frame
    payload_size = struct.calcsize(">L")
    
    data = b""
    while connecting:
        try:
            # Read the frame length
            while len(data) < payload_size:
                packet = client.recv(AMOUNT_OF_BYTE_PER)
                if not packet:
                    connecting = False
                    break
                data += packet
            if not data:
                break

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]

            # Read frame data based on the length
            while len(data) < msg_size:
                packet = client.recv(AMOUNT_OF_BYTE_PER)
                if not packet:
                    connecting = False
                    break
                data += packet
            if len(data) < msg_size:
                break
            
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            # Decode PNG image to numpy array
            frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
            
            latest_frame = frame

        except Exception as e:
            print(f"[ERROR in receive_image] {e}")
            connecting = False
            break
        
#function to check time running for others
def time_it(func):
    @wraps(func)  
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds.")
        return result
    return wrapper

@time_it
def send_key(event):
    global allow_input
    if not allow_input:
        return
    # Check if any modifier keys are pressed along with the current key
    modifiers = []
    if keyboard.is_pressed("ctrl"):
        modifiers.append("ctrl")
    if keyboard.is_pressed("shift"):
        modifiers.append("shift")
    if keyboard.is_pressed("alt"):
        modifiers.append("alt")

    # If there are modifiers and the key is not itself a modifier, send a hotkey message
    if modifiers and event.name not in ["ctrl", "shift", "alt"]:
        # Build the hotkey combination
        keys = modifiers + [event.name.lower() if isinstance(event.name, str) and 'A' <= event.name <= 'z' else event.name]
        message = {"type": "hotkey", "keys": keys}
    else:
        # normal key event message
        message = {"key": event.name, "event_type": "down"}

    message_str = json.dumps(message)
    # Create a header with the length of the JSON message
    header = struct.pack(">L", len(message_str))
    try:
        client.sendall(header + message_str.encode("utf-8"))
    except Exception as e:
        print(f"[ERROR in send_key] {e}")


def exit():
    global connecting, client
    print("[EXIT] 'Esc' pressed.")
    connecting = False

def start_client():
    global client, connecting
    try:
        print("Trying to connect to HOST")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        connecting = True
        print(f"Successfully connected to {HOST}:{PORT}")
    except socket.error as e:
        print(f"Error connecting to {HOST}:{PORT}: {e}")
        connecting = False   
        return
    
    # Start thread for receiving images(screen sharing)
    image_thread = threading.Thread(target=receive_image, daemon=True)
    image_thread.start()
    
    # Set up hotkeys.
    keyboard.add_hotkey("`", toggle_input)
    keyboard.add_hotkey("esc", exit)
    
    # Listen for key presses to send to the host.
    keyboard.on_press(send_key)
    
    # Main thread: display images
    while connecting:
        if latest_frame is not None:
            cv2.imshow("Host Screen", latest_frame)
            # Important: call waitKey in the main thread to keep the window responsive.
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key pressed in the window
                try:
                    client.sendall(DISCONNECT_MSG.encode(FORMAT))
                except Exception as e:
                    print(f"[ERROR] {e}")
                break
        else:
            # Small sleep to avoid busy waiting when no frame is available
            time.sleep(0.01)

    cv2.destroyAllWindows()
   
    try:
        client.close()
    except Exception:
        pass
    print("Disconnected from host.")
    
if __name__ == "__main__":
    start_client()
