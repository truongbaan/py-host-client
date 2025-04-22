#THIS ONLY SHOW SCREEN
import socket
import struct
import pickle
import cv2

ID = input("Provide me the id: ")
SERVER_IP = ID # socket.gethostbyname(socket.gethostname()) #try on same laptop (at your own risk)
PORT = 5050
FORMAT = 'utf-8'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))
print("[CONNECTED] Client connected to server.")
payload_size = struct.calcsize(">L")

while True:
    try:
        # request a screen frame.
        client_socket.sendall("GET_SCREEN".encode(FORMAT)) 
        data = b""
        while len(data) < payload_size: # Receive the header which contains the length of the frame data.
            packet = client_socket.recv(4096)
            if not packet:
                break
            data += packet

        if not data:
            break

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        while len(data) < msg_size: # get frame
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)

        #display
        cv2.imshow("Host Screen", frame)
        if cv2.waitKey(1) == 27:  # ESC key to exit
            break

    except Exception as e:
        print(f"[ERROR] {e}")
        break

client_socket.sendall("DISCONNECT".encode(FORMAT))
client_socket.close()
cv2.destroyAllWindows()
