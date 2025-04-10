#THIS ONE ALLOW INPUT, SO DONT RUN HOST AND CLIENT ON THE SAME COMPUTER
#GO WITH CLIENT.PY
import socket
import threading
import keyboard
import time
import pyautogui

PORT = 5050
AMOUNT_OF_BYTE_PER = 128
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_MSG = "DISCONNECT"
server_running = True

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) 
server.bind(ADDR)

connections = [] #for multiple connection

def handle_client(conn, addr):
    global server_running, connections
    print(f"[NEW CONNECTION] {addr} connected.")
    if conn not in connections:
        connections.append(conn)
        
    # Disable Nagle's algorithm on this connection as well
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    connected = True
    while connected and server_running:
        try:
            msg = conn.recv(AMOUNT_OF_BYTE_PER).decode(FORMAT)
            
            if not msg:
                break
            
            # Process each key individually
            # (If msg contains multiple characters, treat each as a separate key)
            if msg == "space" or msg == "backspace" or msg == "shift":
                pyautogui.press(msg)
            else:
                for key in msg:
                    pyautogui.press(key)
                    print(f"[{addr}] Key pressed: {key}")

            if msg == "DISCONNECT":
                connected = False
                        
            print(f"[{addr}] {msg}")
            conn.send(f"Message received: {msg}".encode(FORMAT))
            
        except ConnectionResetError:
            print(f"[ERROR] Client {addr} disconnected unexpectedly.")
            break  # Handle client disconnection gracefully

    if conn in connections:
        connections.remove(conn)
    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def stop():
    global server_running, connections
    while server_running:
        if keyboard.is_pressed("esc"):
            print("\n[SHUTTING DOWN SERVER] Key 'esc' pressed.")
            server_running = False
            
            # Close all active client connections
            for conn in list(connections):
                try:
                    conn.sendall(DISCONNECT_MSG.encode(FORMAT))
                    time.sleep(0.1) # wait a bit for them to get the message
                    conn.close()
                except Exception as e:
                    print(f"[ERROR] Could not close connection: {e}")
            connections.clear()  # Clear the list of active connections
            
            server.close() #server close
            break

def start_host():
    global server_running
    server.listen()
    server.settimeout(1)  # Set a timeout so accept() doesn't block forever
    print(f"[LISTENING] Server is listening on {SERVER}")

    while server_running:
        try:
            conn, addr = server.accept()
            if server_running == False:
                conn.close()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            active_threads = threading.enumerate()
            print("Active Threads:")
            for thread in active_threads:
                print(f"Thread Name: {thread.name}, Alive: {thread.is_alive()}")
        except socket.timeout:
            # Timeout reached, check the server_running flag and loop again
            continue
        except OSError:
            # exit the loop gracefully.
            break

    print("[SERVER STOPPED]")

if __name__ == "__main__":
    # Start the shutdown listener in a separate daemon thread
    shutdown_thread = threading.Thread(target=stop, daemon=True)
    shutdown_thread.start()


    print(f"[STARTING SERVER]: {SERVER}")
    start_host()
    shutdown_thread.join()
    print("[SERVER EXITED]")
