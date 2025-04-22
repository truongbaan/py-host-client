# Remote Desktop and Input Controller via TCP (v6)

## Description

This Python-based project enables remote control of a computer on the **same local Wi-Fi network** through real-time screen streaming and keyboard input using TCP sockets. The solution consists of two scripts:

- **`host6.py`**: Captures the host's screen and streams it to a connected client. It also listens for keyboard input commands from the client and simulates key presses.
- **`client6.py`**: Connects to the host, displays the live screen feed using OpenCV, and sends keypress events to the host.

> **Important:** These scripts are intended to be run on **separate devices**. Running both on the same device can cause input conflicts due to keyboard simulation libraries.

## Features

- **Real-Time Screen Streaming**
  - Host captures the full screen using `mss`.
  - Frames are resized, PNG-compressed, and sent over TCP.
  - Client decodes and displays the frames using OpenCV.

- **Remote Keyboard Control**
  - Client captures keypresses and sends structured JSON messages.
  - Host simulates key events using the `keyboard` module.
  - Supports single keys and combinations like Ctrl+Shift+Key.

- **Threaded Architecture**
  - Host and client handle input and streaming in parallel threads for smooth operation.

- **Input Toggle**
  - Pressing the backtick (`\``) key on either side toggles whether input is allowed.

- **Graceful Shutdown**
  - Pressing `ESC` on the client sends a disconnect message.
  - Pressing `ESC` on the host initiates shutdown.

- **Execution Time Logging**
  - Decorators log execution time of core functions for performance monitoring.

## Technologies Used

- **Python Version:** 3.12.6
- **Editor:** Visual Studio Code
- **Libraries:**
  - `socket`, `threading`, `struct`, `json`, `time`, `queue`
  - `mss`, `cv2 (OpenCV)`, `numpy`
  - `keyboard` (for key capturing and simulation)

## Installation

1. **Clone the Repository**
   ```bash
   git clone <your-repo-link>
   cd <your-repo-name>
   ```

2. **Install Python 3.12.6**
   Download from [python.org](https://www.python.org/downloads/)

3. **Install Dependencies**
   ```bash
   pip install opencv-python keyboard mss numpy
   ```
   *Note: On some operating systems, `keyboard` might require administrator/root privileges.*

## Usage

### On the Host Machine
```bash
python host6.py
```
- Starts listening on your machine's IPv4 address and port 5050.
- Begins screen streaming and input processing once a client connects.
- Press `t` or `ESC` to terminate the server safely.

### On the Client Machine
```bash
python client6.py
```
- Enter the **IPv4 address** of the host when prompted.
- A real-time feed of the host screen appears in a window.
- Key presses are captured and sent to the host.
- Press " \` " (backtick) to toggle input mode.
- Press `ESC` to safely disconnect.

> Ensure both devices are connected to the **same local network**.

## Notes

- The host compresses frames as PNG, which balances quality and compression speed.
- Host supports multiple clients but does not yet differentiate them.
- `keyboard` is used on both ends; permissions may vary across platforms.
- A thread-safe queue buffers key events to avoid congestion.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

