#  Prism

Prism is a lightweight, zero-dependency, strict ASCII terminal chat application built in Python using raw sockets and multi-threading. It utilizes a **Client-Server architecture** to orchestrate multiple concurrent, completely isolated 2-person private conversations over a single central server IP address.

While the user experience feels like a direct peer-to-peer (P2P) connection, all traffic is securely managed and routed through a central server using dynamically generated unique room codes. No databases, no logs, and no message history are retained—ensuring clean, ephemeral communication straight from your command line.

##  Features

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
```
**Step 1: Enter the target IP address to bind the server socket.**

**Step 2: Enter the Port number you want the server to listen on.**
### 4. Launch the Client App (client.py)
- Open a separate terminal window (and have your friend open one on their machine) and run:
  ```bash
  python client.py
  ```
 ### How to Chat
 - Once client.py is open, choose your routing mode:
    **Option A: Hosting a Room**
   1. Select Host from the menu.
   2. Enter the central server's IP and Port.
   3. Enter your temporary Display Name (required every time you open the program).
   4. The server will register a new session and generate a unique room code. Give this code to your friend!
   5. Wait for the server to pair your friend to your room thread, then begin chatting.

   **Option B: Joining an Existing Room**
   1. Select Join from the menu.
   2. Enter the unique room code provided by the Host.
   3. Enter your temporary Display Name (required every time you open the program).
   4. The server will authenticate the code, bridge your connection to the host, and drop you into the chat room.

  ### Prerequisites
  - Python 3.x
