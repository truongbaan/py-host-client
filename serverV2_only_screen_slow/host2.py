#GO WITH CLIENT2
#CONNECT AND SHARE HOST SCREEN TO CLIENT

import socket
import threading
import keyboard
import time
import mss
import pickle
import struct
import numpy as np
import cv2

PORT = 5050
AMOUNT_OF_BYTE_PER = 64
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_MSG = "DISCONNECT"
server_running = True
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

connections = []  # For multiple connections

def handle_client(conn, addr):
    global server_running, connections
    print(f"[NEW CONNECTION] {addr} connected.")
    if conn not in connections:
        connections.append(conn)
        
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    # initialize the screen capture tool once per connection
    with mss.mss() as sct:
        while server_running:
            try:
                msg = conn.recv(AMOUNT_OF_BYTE_PER).decode(FORMAT)
                if not msg:
                    break
                
                # break loop if client request
                if msg == DISCONNECT_MSG:
                    break
           
                if msg == "GET_SCREEN":# Capture screen and process frame.
                    screenshot = sct.grab(sct.monitors[1])
                    frame = np.array(screenshot)
                    frame = cv2.resize(frame, (800, 600))  # Resize
                    data = pickle.dumps(frame)
                    # Send the length of the data first (as 4 bytes) then the data.
                    conn.sendall(struct.pack(">L", len(data)) + data)
                    
            except ConnectionResetError:
                print(f"[ERROR] Client {addr} disconnected unexpectedly.")
                break

    if conn in connections:
        connections.remove(conn)
    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def stop():
    global server_running, connections
    while server_running:
        if keyboard.is_pressed("esc"):
            print("\n[SHUTTING DOWN SERVER] Key 'ESC' pressed.")
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
            break

def start_host():
    global server_running
    server.listen()
    server.settimeout(1)  # So accept() doesn’t block forever
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")

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
    # Start the stop function in a separate daemon thread.
    shutdown_thread = threading.Thread(target=stop, daemon=True)
    shutdown_thread.start()

    print(f"[STARTING SERVER]: {SERVER}")
    start_host()
    shutdown_thread.join()
    print("[SERVER EXITED]")
