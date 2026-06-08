# 📐 Prism

Prism is a lightweight, zero-dependency, strict ASCII terminal chat application built in Python using raw sockets and multi-threading. It utilizes a **Client-Server architecture** to orchestrate multiple concurrent, completely isolated 2-person private conversations over a single central server IP address.

While the user experience feels like a direct peer-to-peer (P2P) connection, all traffic is securely managed and routed through a central server using dynamically generated unique room codes. No databases, no logs, and no message history are retained—ensuring clean, ephemeral communication straight from your command line.

## ✨ Features

- **Strict ASCII UI:** Pure text-based interface. Runs perfectly in any native terminal or command prompt.
- **Client-Server Architecture:** Centralized server handles multiple pairs simultaneously on a single host IP. Rooms are capped at a hard maximum of 2 participants.
- **Dynamic Code Generation:** The server allocates unique access codes to hosts, allowing clients to bridge together into isolated threads.
- **Zero Data Footprint:** Messages are processed entirely in-memory. No databases, no account configuration, and zero message retention. Once a room closes, the data vanishes.
- **Automatic Disconnect Handling:** If one user leaves, the server notifies the remaining peer and automatically bounces them back to the main menu after a 5-second graceful timeout.

## ⚙️ Setup & Installation

### 1. Prerequisites
- **Python:** You must have the **latest version of Python 3** installed on your system. No additional third-party dependencies or `pip` installs are needed.

### 2. Download the App
- Download the project code as a `.zip` file from this GitHub repository.
- Extract the zip file to your preferred folder. You will use the two core files: `server.py` and `client.py`.

### 3. Start the Central Server (`server.py`)
Open a terminal window on your host machine or VPS and run the server script first:
```bash
python server.py
