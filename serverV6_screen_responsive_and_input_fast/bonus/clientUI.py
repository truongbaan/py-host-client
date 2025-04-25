import tkinter as tk
#same like client6, just add a UI for better seeing
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

#OUTPUT is used to display the text, HOST is the variable to get the ID to connect
global HOST, OUTPUT
HOST = OUTPUT = ""
SERVER_IP = HOST
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MSG = "DISCONNECT"

# Global variables for the client socket and connection state.
client = None
connecting = False
allow_input = True
latest_frame = None  # Shared variable for the most recent frame

def toggle_input():
    global allow_input, OUTPUT
    allow_input = not allow_input #switch between sending input or not
    OUTPUT = ("Allow input is now: " + (str)(allow_input))
    
def receive_image():
    global client, connecting, latest_frame, OUTPUT
    payload_size = struct.calcsize(">L")
    
    data = b""
    while connecting:
        try:
            # Read the frame length
            while len(data) < payload_size:
                packet = client.recv(4096)
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
                packet = client.recv(4096)
                if not packet:
                    connecting = False
                    break
                data += packet
            if len(data) < msg_size:
                break
            
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            # Decode JPEG image to numpy array
            frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
            
            latest_frame = frame

        except Exception as e:
            OUTPUT = (f"[ERROR in receive_image] {e}")
            connecting = False
            break
        
def time_it(func):
    @wraps(func)  # Preserves the original function's metadata (name, docstring, etc.)
    def wrapper(*args, **kwargs):
        global OUTPUT
        start_time = time.perf_counter()  # Use perf_counter for high-resolution timing
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        OUTPUT = (f"Function '{func.__name__}' executed in {execution_time:.4f} seconds.")
        return result
    return wrapper

@time_it
def send_key(event):
    global allow_input, OUTPUT
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
        # Build the hotkey combination
        keys = modifiers + [event.name.lower() if isinstance(event.name, str) and 'A' <= event.name <= 'z' else event.name]
        message = {"type": "hotkey", "keys": keys}
    else:
        # Otherwise, send a normal key event message.
        message = {"key": event.name, "event_type": "down"}

    message_str = json.dumps(message)
    # Create a header with the length of the JSON message (using 4 bytes for example)
    header = struct.pack(">L", len(message_str))
    try:
        client.sendall(header + message_str.encode("utf-8"))
    except Exception as e:
        OUTPUT = (f"[ERROR in send_key] {e}")
    

def start_client():
    global client, connecting, OUTPUT, HOST
    try:
        print("Trying to connect to HOST")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        connecting = True
        OUTPUT = (f"Successfully connected to {HOST}:{PORT}")
    except socket.error as e:
        OUTPUT = (f"Error connecting to {HOST}:{PORT}: {e}")
        connecting = False   
        return
    
    # Start thread for receiving images.
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
                    OUTPUT = (f"[ERROR] {e}")
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
    

def on_receive():
    global HOST, OUTPUT
    user_input = entry.get()
    print(f"Received text: {user_input}")
    entry.delete(0, tk.END)  # clears the input field
    output_var.set(OUTPUT)  # update the read-only field
    HOST = (str)(user_input)
    threading.Thread(target=start_client, daemon=True).start()
    
def exit():
    global connecting, client, OUTPUT
    print("[EXIT] 'Esc' pressed. Requesting disconnect...")
    if connecting:
        try:
            client.sendall("DISCONNECT".encode(FORMAT))
        except Exception as e:
            OUTPUT = (f"[ERROR in wait_for_exit] {e}")
    connecting = False
    keyboard.clear_all_hotkeys()
    keyboard.unhook_all()
    output_var.set("Exit from the host")

PLACEHOLDER = "Enter IPV4 to connect:"

def set_placeholder():
    entry.insert(0, PLACEHOLDER)
    entry.config(fg='gray')

def clear_placeholder(event):
    if entry.get() == PLACEHOLDER:
        entry.delete(0, tk.END)
        entry.config(fg='black')

def restore_placeholder(event):
    if not entry.get():
        set_placeholder()

def main():
    global entry, output_var

    root = tk.Tk()
    root.title("Client app")
    root.geometry("250x200")

    # Input Entry (editable)
    entry = tk.Entry(root)
    entry.pack(pady=10)
    set_placeholder()
    entry.bind("<FocusIn>", clear_placeholder)
    entry.bind("<FocusOut>", restore_placeholder)
    
    # Output Entry (read-only)
    output_var = tk.StringVar()
    output_entry = tk.Entry(root, textvariable=output_var, state='readonly')
    output_entry.pack(pady=10)

    # Button to receive and show text
    receive_button = tk.Button(root, text="Connect", command=on_receive)
    receive_button.pack(pady=5)

    # Placeholder Button
    placeholder_button = tk.Button(root, text="Stop connect", command=exit)
    placeholder_button.pack(pady=5)

    root.mainloop()#need to use to keep the UI on

if __name__ == "__main__":
    main()
