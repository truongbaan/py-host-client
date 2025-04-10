import socket
import keyboard
import threading
import time

ID = input("Provide me the id: ")
HOST = ID #socket.gethostbyname(socket.gethostname()) 
PORT = 5050
FORMAT = "utf-8"
AMOUNT_OF_BYTE_PER = 128

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
connecting = False
allow_input = True

def toggle_input():
    global allow_input
    allow_input = not allow_input #switch between sending input or not
    
def connect_to_server():
    #Try to reconnect for 5 seconds before giving up
    global client, connecting
    if not connecting:
        print("[INFO] Lost connection. Attempting to reconnect...")
    
    start_time = time.time()
    while time.time() - start_time < 5:  # Try for 5 seconds
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            client.settimeout(2)  # Timeout per attempt
            client.connect((HOST, PORT))
            print("[INFO] Reconnected to the host.")
            connecting = True
            return True
        except (socket.timeout, ConnectionRefusedError):
            time.sleep(1)  # wait before retrying
        except Exception as e:
            print(f"[ERROR] Reconnection failed: {e}")
    
    print("[ERROR] Could not reconnect after 5 seconds. Exiting...")
    return False  # Reconnection failed

def send_key(event):
    global connecting
    #send key press data to the host
    if allow_input:
        key_data = event.name.encode(FORMAT)
        try:
            client.sendall(key_data)
        except Exception as e:
            print(f"[ERROR] Could not send key data: {e}")
            connecting = connect_to_server()

def receive_messages():
    global connecting
    #Continuously receive and print messages from the server.
    while connecting:
        try:
            msg = client.recv(AMOUNT_OF_BYTE_PER).decode(FORMAT)
            if not msg:
                break
            
            print(f"[SERVER RESPOND] {msg}")
            
            if "DISCONNECT" in msg:
                connecting = False
                break
            
        except Exception as e:
            print(f"[ERROR] Failed to receive server response: {e}")
            connecting = connect_to_server()
            break
    client.close()

def wait_for_exit():
    global connecting
    #check esc key press to break
    while connecting:
        if keyboard.is_pressed("esc"):
            print("[EXIT] 'Esc' pressed. Requesting for disconnecting...")
            break
        time.sleep(0.1)  # Reduce CPU usage
   
    if connecting:
        try:
            client.sendall("DISCONNECT".encode(FORMAT))
            connecting = False
        except Exception as e:
            print(f"[ERROR] Could not send disconnect message: {e}")
    


def start_client():    
    global client, connecting
    
    #first connection
    try:
        print("Trying to connect to HOST")
        client.connect((HOST, PORT))
        connecting = True
        print(f"Successfully connected to {HOST} : {PORT}")
    except socket.error as e:
        print(f"Error connecting to {HOST}:  {PORT}: {e}")
        connecting = False   
        
    # Start listening for incoming messages
    receive_thread = threading.Thread(target=receive_messages, daemon=True)
    receive_thread.start()

    # Start listening for 'esc' to exit
    exit_thread = threading.Thread(target=wait_for_exit, daemon=True)
    exit_thread.start()

    # Set up hotkeys.
    # Use add_hotkey to toggle input on pressing "0".
    keyboard.add_hotkey("0", toggle_input)
    
    # Listen for key presses
    keyboard.on_press(send_key)

    # Keep the main thread alive until exit
    exit_thread.join()

if __name__ == "__main__":
    start_client()
    print("Disconnected from host.")