# Python TCP Screen Sharing System

## Description
This project demonstrates a simple TCP-based screen sharing system using Python. The host computer continuously captures its screen, compresses each frame, and transmits these frames over a TCP connection to one or more client computers. The client displays the host’s screen in real-time using OpenCV. This project is intended for educational and experimental purposes on local networks.

> **Warning:**  
> **Do not run both the host and client on the same computer** as it may cause interference with your local inputs.

>**Note:**
The screen display on the client side may experience a noticeable delay and very low FPS due to Python's real-time screen capture, network transmission, and image decoding process. This system is not optimized for high-performance streaming.

## Features
- **Real-Time Screen Sharing:**  
  The host continuously captures the screen, processes the image, and sends it to connected clients.
- **Multiple Client Support:**  
  The host accepts multiple simultaneous connections, sending updated screen images to each client.
- **TCP Communication:**  
  The host and clients communicate over IPv4 TCP sockets for reliable data transmission.
- **Graceful Shutdown on Host:**  
  On the host, pressing the `ESC` key safely shuts down the server and disconnects all clients.

## Technologies Used
- **Programming Language:** Python 3.12.6
- **Libraries and Modules:**
  - socket
  - threading
  - keyboard
  - time
  - mss
  - pickle
  - struct
  - numpy
  - OpenCV (cv2)
- **IDE:** Visual Studio Code

## Installation
To set up and run this project on your local machine, follow these steps:

1. **Install Python:**  
   Download and install [Python 3.12.6](https://www.python.org/downloads/).

2. **Install Required Libraries:**  
   Open your terminal or command prompt and run:
   ```bash
   pip install keyboard mss numpy opencv-python
   ```

3. **Clone the Repository:**  
   Use Git to clone the project repository:
   ```bash
   git clone <your-repo-link>
   cd <your-repo-name>
   ```

## Usage Guide

### Running the Host
On the host computer, run the host script:
```bash
python host2.py
```
- The host will start listening on its local IP (displayed on startup) at port 5050.
- It uses the `mss` library to capture the screen, resizes the frame to 800x600, and compresses it before sending it to each connected client.
- Press `ESC` to safely shut down the server and disconnect all clients.

### Running the Client
On a client computer, run the client script:
```bash
python client2.py
```
- When prompted, enter the host's IP address.
- The client sends a `GET_SCREEN` command to request a screen frame from the host.
- The received frame (sent via a TCP connection and unpickled) is displayed in real-time using OpenCV.
- To exit, press the `ESC` key in the OpenCV window.

## License
This project is licensed under the MIT License - see the LICENSE file in the main directory for details.
