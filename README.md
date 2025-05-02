# Remote Desktop and Input Controller via TCP (v1 → v6.1)

## Overview

This repository documents my learning journey in building a Python-based remote desktop and input controller system over TCP. It begins as a simple host-client connector and evolves into a robust, user-friendly tool with real-time screen sharing and input simulation. The system enables one device to control another over the **same local Wi-Fi network**, streaming the host's screen and sending keyboard events.

## Evolution Summary

## v1: Simple TCP Key Transmission

* **Goal:** Learn Python socket programming and real-time key event handling.
* **Implementation:**

  * Two scripts: `host.py` and `client.py`.
  * Clients capture keystrokes using the `keyboard` library; hosts simulate them with `pyautogui`.
  * Built-in toggle (`0` key) to enable/disable input (client only); `ESC` to disconnect or shut down.

---

## v2: Screen Sharing Only

* **Goal:** Combine socket communication with real-time screen capture.
* **Implementation:**

  * Host captures screen using `mss`, resizes frames, serializes via `pickle` + `struct`.
  * Client receives and displays frames with OpenCV (`cv2`).
  * Supports multiple clients; clients send `GET_SCREEN` requests.

---

## v3: Unified Streaming & Input Handling

* **Goal:** Merge screen streaming and key event simulation in a single application.
* **Implementation:**

  * Single-host script handles both tasks with threads.
  * Clients use `keyboard` and JSON messages to send input; host processes via `pyautogui`..

---

## v4: Hotkey Toggles & Robustness

* **Goal:** Enhance usability and speed.
* **Implementation:**

  * Toggle input via backtick key (\`) for convenience. (client only)
  * Added exception handling for network drops and disconnections.
  * Input simulation library change: change from pyautogui to keyboard.

---

## v6: Queues & Multiple Clients

* **Goal:** Ensure thread safety and support concurrent clients. Both client and host can disable/enable input
* **Implementation:**

  * Utilized `queue.Queue` to buffer incoming key events.
  * Host streams PNG-compressed frames
  * Both client and host can toggle input mode

---

## v6.1: GUI & Payload Dropper

* **Goal:** Provide a user-friendly client interface and seamless server deployment.
* **Implementation:**

  * **Client UI**: Built with **Tkinter** (`clientUI.py`), featuring IP entry, status display, and connect/disconnect buttons.
  * **Dropper**: `payload.py` writes and launches `making.py` (the host server) invisibly, then deletes itself for minimal footprint.
  * Platform support: Windows and Linux
* **Key Takeaways:**

  * Creating simple GUIs for networked applications.
  * Understanding dropper patterns and cleanup strategies.
  * Ensuring cross-platform compatibility (Windows, Linux).

---

## Features (v6.1)

* Real-time screen sharing via TCP.
* Remote keyboard input capture and simulation.
* Modifier and hotkey support (e.g., Ctrl+Shift+Key).
* Graceful shutdown via `ESC` key.
* Input toggle via backtick (\`) key.
* Cross-platform launch with automatic cleanup.
* GUI client (Tkinter) for ease of use.
* Execution time logging via decorators.

## Technologies

* **Python 3.12.6**
* **Editor**: Visual Studio Code

### Key Libraries:

* Networking: `socket`, `struct`, `json`, `threading`, `queue`
* Input: `keyboard`, `pyautogui` (v1 and v3), `keyboard` only (v4+)
* Image processing: `mss`, `numpy`, `cv2`
* GUI: `tkinter`
* Utilities: `time`, `pickle`, `subprocess`, `platform`, `os`, `functools`, `sys`

## Getting Started

Each version folder (`v1/`, `v2/`, ..., `v6.1/`) contains a self-contained example:

1. Review the **README.md** in that folder for specific libraries and usage.
2. Install required dependencies listed for that version.
3. Run the host and client scripts in separate terminals or machines on the same Wi-Fi network.

## Notes

* `keyboard` library may require administrator/root access.
* Avoid running host and client on the same device.
* `making.py` is auto-deleted after launch.
* Toggle input allows safe experimentation.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Final Thoughts

A simple tcp connection through ipv4 with screen sharing and input manipulation from both host and client, this could be useful for those one want the other to access and control keyboard input of your computer (in same network) but not through any apps if you scare of privacy and apps collecting information, you could just run the code yourself and can also modify the code base on your thought.
