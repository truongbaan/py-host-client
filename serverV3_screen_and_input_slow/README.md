# Remote Desktop and Input Controller via TCP

## Description

This project demonstrates a TCP-based connection that enables remote control and real-time screen streaming. It consists of two main components:

Host (host3.py): Captures the host computer’s screen and streams it to connected clients. It also processes incoming key events to simulate key presses using the pyautogui library.

Client (client3.py): Connects to the host over a local network, displays the streamed screen, and sends keyboard events in real-time to control the host remotely.

**Important:**

> **Do not run the host and client on the same computer** as the host uses pyautogui to simulate key presses, which may interfere with normal input operations.

## Features

- **Real-time Screen Streaming:**\
  The host captures its screen continuously and streams it over a TCP connection.
- **Remote Input Handling:**\
  Clients capture and send keyboard events, which the host processes to simulate key presses.
- **Toggle Input Feature:**\
  Clients can enable or disable the sending of key events by pressing a designated hotkey (0).
- **Graceful Disconnection:**\
  Both client and host listen for the `ESC` key to safely disconnect or shut down the session.
- **Multi-threaded Operation:**\
  Uses Python's threading library to handle multiple simultaneous client connections and concurrent tasks such as screen streaming and input processing.

## Technologies Used

- **Programming Language:** Python 3.12.6
- **Libraries:**
  - `socket` for network communication
  - `threading` for handling concurrent connections and processes
  - `keyboard` for capturing key events on the client side
  - `pyautogui` for simulating key presses on the host side
  - `mss` for high-performance screen capturing (host)
  - `cv2` (OpenCV) for displaying the streamed screen on the client
  - `pickle` and `struct` for serializing and sending image frames and messages
  - `numpy` for array manipulation in image processing
- **IDE/Editor:** Visual Studio Code

## Installation

To run the project locally, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/truongbaan/py-host-client.git
   cd py-host-client
   cd serverV3_screen_and_input_slow
   ```

2. **Install Python:**\
   Download and install [Python 3.12.6](https://www.python.org/downloads/).

3. **Install Required Libraries:**\
   In a terminal or command prompt inside your project directory, run:

   ```bash
   pip install opencv-python pyautogui keyboard mss numpy
   ```

   *(If necessary, install additional libraries with pip.)*

## Usage Guide

### Running the Host

On the host computer (ensure this machine is dedicated to hosting):

1. Open a terminal and run:
   ```bash
   python host3.py
   ```
2. The host will start streaming its screen on port **5050** and wait for client connections.
3. To stop the server and disconnect all clients, press the `ESC` key on the host machine.

### Running the Client

On the client computer:

1. Open a terminal and run:
   ```bash
   python client3.py
   ```
2. When prompted, enter the **IPv4 address** of the host computer.
3. A window will open displaying the host’s screen.
4. To toggle key input transmission (enable/disable), press the `0` key.
5. To disconnect from the host, press the `ESC` key.

> **Note:** Running host and client on the same computer is not recommended due to potential input interference.

> **Reminder:** This only works on devices connected to the **same local Wi-Fi network**.

## License

This project is licensed under the MIT License - see the LICENSE file in the main directory for details.

