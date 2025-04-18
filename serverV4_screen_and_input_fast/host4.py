#GO WITH CLIENT 4
#HAS KEYBOARD INPUT SO DONT TRY ON THE SAME LAPTOP
import socket
import threading
import keyboard 
import time
import mss
import pickle
import struct
import numpy as np
import cv2
import json

PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_MSG = "DISCONNECT"
server_running = True

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow immediate reuse of the port
server.bind(ADDR)
from functools import wraps

#just for checking the time each function, could be deleted
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
def process_key_event(msg):
    try:
        data = json.loads(msg)
        if data.get("type") == "hotkey":
            keys = data.get("keys")
            if keys:
                for key in keys:
                    keyboard.press(key)
                for key in reversed(keys):
                    keyboard.release(key)
        else:
            key = data.get("key")
            event_type = data.get("event_type")
            if event_type == "down":
                if key != "caps lock":
                    try:
                        keyboard.press_and_release(key)
                    except ValueError or KeyError:
                        pass #just ignore it
    except json.JSONDecodeError:
        # Handle non-JSON messages if needed.
        pass

connections = []  # For multiple connections

@time_it
def handle_input(conn):
    while server_running:
        try:
            # Read the 4-byte length header first.
            header = conn.recv(4)
            if not header:
                break
            msg_length = struct.unpack(">L", header)[0]
            data = b""
            # Read the full JSON message based on the length.
            while len(data) < msg_length:
                packet = conn.recv(msg_length - len(data))
                if not packet:
                    break
                data += packet
            if len(data) != msg_length:
                break
            message = data.decode("utf-8")
            process_key_event(message)
        except Exception as e:
            print(f"[ERROR in key events] {e}")
            break

@time_it
def stream_screen(conn):
    with mss.mss() as sct:
        while server_running:
            screenshot = sct.grab(sct.monitors[1])
            frame = np.array(screenshot)
            frame = cv2.resize(frame, (800, 600))
            data = pickle.dumps(frame)
            try:
                conn.sendall(struct.pack(">L", len(data)) + data)
            except Exception as e:
                break
            time.sleep(1/240)

@time_it
def handle_client(conn, addr):
    # Start threads for input handling and screen streaming
    print(f"[CONNECT TO] {addr}")
    threading.Thread(target=handle_input, args=(conn,), daemon=True).start()
    threading.Thread(target=stream_screen, args=(conn,), daemon=True).start()

@time_it
def stop():
    global server_running, connections
    print("\n[SHUTTING DOWN SERVER] Key 'esc' pressed.")
    server_running = False
    
    # Close all active client connections.
    for conn in list(connections):
        try:
            conn.sendall(DISCONNECT_MSG.encode(FORMAT))
            time.sleep(0.1)  # Wait a bit for the client to get the message
            conn.close()
        except Exception as e:
            print(f"[ERROR] Could not close connection: {e}")
    connections.clear()
    
    server.close()  # Close the server socket

@time_it
def start_host():
    global server_running
    server.listen()
    server.settimeout(1)  # So accept() doesn’t block forever
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")

    keyboard.add_hotkey("esc", stop)
    
    while server_running:
        try:
            conn, addr = server.accept()
            if not server_running:
                conn.close()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except socket.timeout:
            continue
        except OSError:
            break

    print("[SERVER STOPPED]")

if __name__ == "__main__":
    print(f"[STARTING SERVER]: {SERVER}")
    start_host()
    print("[SERVER EXITED]")
