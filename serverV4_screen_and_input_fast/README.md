# Remote Desktop and Input Controller via TCP

## Description

This project allows a user to remotely control another computer on the **same Wi-Fi network** via real-time screen streaming and keyboard input over TCP. It consists of two main components:

- **Host (host4.py):** Captures and streams the host machine's screen to connected clients and processes remote keyboard inputs using `pyautogui`-like behavior.
- **Client (client4.py):** Connects to the host, displays the real-time stream, and sends keyboard input to the host for remote control.

> **Note:** This system is designed to be used **on different devices connected to the same local Wi-Fi network**. Running both the host and client on the same machine may result in keyboard input conflicts.

## Features

- **Real-time Screen Streaming:** Host captures and sends screen frames at high speed using `mss` and `cv2`.
- **Remote Keyboard Control:** Client captures keypresses and sends them in real-time to the host.
- **Hotkey Input Toggle:** The client can toggle input transmission using the backtick key (`).
- **Multi-threaded Execution:** Separate threads manage screen transmission and keyboard input for smoother operation.
- **Graceful Exit:** Pressing `ESC` on either side initiates a safe disconnection or server shutdown.
- **Hotkey & Modifier Support:** Host handles complex key combinations like Ctrl+Shift+Key from the client.

## Technologies Used

- **Python Version:** 3.12.6
- **Libraries:**
  - `socket` - TCP communication
  - `threading` - concurrent operations
  - `keyboard` - input capture and simulation
  - `mss` - fast screen capturing
  - `cv2` - screen display
  - `pickle` + `struct` - data serialization
  - `numpy` - image data manipulation

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/truongbaan/py-host-client.git
   cd py-host-client
   cd serverV4_screen_and_input_fast
   ```

2. **Install Python**
   - Download from [python.org](https://www.python.org/downloads/).

3. **Install Required Libraries**

   ```bash
   pip install opencv-python pyautogui keyboard mss numpy
   ```

   *(Additional setup may be required depending on your OS permissions for `keyboard`.)*

## Usage

### Run the Host (on the computer to be controlled)

```bash
python host4.py
```
- Wait for the host to display the IP address and start listening.
- The host will stream its screen and accept remote input.
- Press `ESC` to shut down the server.

### Run the Client (on a different computer on the same network)

```bash
python client4.py
```
- When prompted, enter the **IPv4 address** of the host machine.
- A window will display the host's screen in real-time.
- Press the backtick (`) key to toggle sending keyboard inputs.
- Press `ESC` to disconnect from the host and exit.

> **Reminder:** This only works on devices connected to the **same local Wi-Fi network**.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

