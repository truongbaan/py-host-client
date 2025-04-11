# Python TCP Host-Client Connector

## Description
This is a simple Python project designed to establish a connection between multiple client computers and a host computer over a TCP connection using IPv4. The project demonstrates socket programming with the ability for clients to send keyboard input events to the host in real-time. The host will simulate these key presses using the pyautogui module.

This project is created for educational and experimental purposes on local networks.

**Warning:**  
> **Do not run both the host and client on the same computer** as it may cause interference with your local inputs.

## Features
- Establish TCP connection between host and multiple clients.
- Clients send real-time key press events to the host.
- Host simulates the key presses using pyautogui.
- Clients can toggle the sending of key events on or off.
- Automatic reconnection mechanism if the client loses connection.
- Press ESC to safely disconnect (client) or shut down the server (host).

## Technologies Used
- **Programming Language:** Python 3.12.6
- **Libraries:**
  - socket
  - threading
  - keyboard
  - pyautogui
  - time

- **IDE:** Visual Studio Code

## Installation
If you want to run this project on your local machine, follow these steps:

1. **Install Python:**
   - Download and install [Python 3.12.6](https://www.python.org/downloads/).

2. **Install Required Libraries:**
   - Open a terminal or command prompt and run:
     ```bash
     pip install pyautogui keyboard
     ```

3. **Clone the Repository:**
   - Use Git to clone the project repository:
     ```bash
     git clone <your-repo-link>
     cd <your-repo-name>
     ```

## Usage Guide

### Running the Host
On the host computer:
```bash
python host.py
```
- The host will start listening on the local IP and port 5050.
- Press `ESC` to safely shut down the server and disconnect all clients.

### Running the Client
On the client computer:
```bash
python client.py
```
- Input the host's IP address when prompted.
- Press `0` to toggle input sending on/off.
- Press `ESC` to disconnect from the host safely.

> Note: Do not run both `host.py` and `client.py` on the same computer since the host uses pyautogui to simulate key presses which might interfere with your own inputs.

## License
This project is licensed under the MIT License - see the LICENSE file in the main directory for details.

