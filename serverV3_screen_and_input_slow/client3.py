#SCREEN SHARING AS WELL AS INPUT
#SLOW INPUT AND SCREEN 
import socket
import struct
import pickle
import cv2
import time
import threading
import keyboard
import json
import keyboard
from functools import wraps

ID = input("Enter the ipv4 address: ")
AMOUNT_OF_BYTE_PER = 4096
SERVER_IP = HOST =  ID #socket.gethostbyname(socket.gethostname()) #dont run client and host on the same laptop
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MSG = "DISCONNECT"

# Global variables for the client socket and connection state.
client = None
connecting = False
allow_input = True
latest_frame = None

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
            # Read the first 4 bytes for the frame size
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

            # Read the complete frame data
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
            frame = pickle.loads(frame_data)
            
            # Update the shared frame
            latest_frame = frame

        except Exception as e:
            print(f"[ERROR in receive_image] {e}")
            connecting = False
            break

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
    # Check if any modifier keys are pressed along with the current key.
    modifiers = []
    if keyboard.is_pressed("ctrl"):
        modifiers.append("ctrl")
    if keyboard.is_pressed("shift"):
        modifiers.append("shift")
    if keyboard.is_pressed("alt"):
        modifiers.append("alt")

    # If there are modifiers and the key is not itself a modifier, send a hotkey message.
    if modifiers and event.name not in ["ctrl", "shift", "alt"]:
        keys = modifiers + [event.name]
        message = {"type": "hotkey", "keys": keys}
    else:
        # send a normal key event message.
        message = {"key": event.name, "event_type": "down"}

    message_str = json.dumps(message)
    # Create a header with the length of the JSON message
    header = struct.pack(">L", len(message_str))
    try:
        client.sendall(header + message_str.encode("utf-8"))
    except Exception as e:
        print(f"[ERROR in send_key] {e}")


def wait_for_exit():
    global connecting, client
    while connecting:
        if keyboard.is_pressed("esc"):
            break
        time.sleep(0.1)
    print("[EXIT] 'Esc' pressed. Requesting disconnect...")
    if connecting:
        try:
            client.sendall("DISCONNECT".encode(FORMAT))
        except Exception as e:
            print(f"[ERROR in wait_for_exit] {e}")
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
    
    # Start thread to check for ESC key press.
    exit_thread = threading.Thread(target=wait_for_exit, daemon=True)
    exit_thread.start()
    
    # Start thread for receiving images.
    image_thread = threading.Thread(target=receive_image, daemon=True)
    image_thread.start()
    
    # Set up hotkeys.
    keyboard.add_hotkey("0", toggle_input)
    
    # Listen for key presses to send to the host.
    keyboard.on_press(send_key)
    
    # display images
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
            # small sleep to avoid busy waiting when no frame is available
            time.sleep(0.01)

    cv2.destroyAllWindows()
    print("Disconnected from host.")
    exit_thread.join()
    image_thread.join()
    
    try:
        client.close()
    except Exception:
        pass

if __name__ == "__main__":
    #start
    start_client()
    print("Disconnected from host.")
