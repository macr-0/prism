# Prism

Prism is a lightweight, zero-dependency, pure ASCII peer-to-peer terminal chat application built in Python using raw sockets and threading. No central server needed — peers connect directly over TCP.

## Features

- **Strict ASCII UI**: Pure text-based interface. Runs in any terminal or command prompt.
- **Peer-to-Peer**: Direct TCP socket between two peers. No central server, no room codes.
- **Three ways to connect**: LAN, Tailscale (same account), or Tailscale Share (different accounts).
- **E2EE-Ready Protocol**: Message format (`MSG|text`) is designed to swap in encryption later without structural changes.
- **Zero Data Footprint**: Messages processed entirely in-memory. No logs, no databases, no history.
- **Immediate Disconnect**: Leave instantly with `/leave`, `/quit`, or `/q`.

## How the Chat Works

Prism uses a direct TCP connection between two people. One person acts as the **Host** (opens a listening port) and the other **Joins** (connects to the host's IP and port). Once connected, messages flow directly between the two machines with no intermediary.

```
  Host                         Friend
+--------+                   +--------+
| peer.py|-- open port ----->| peer.py|
| (waits)|<-- TCP connect ---| (joins)|
|        |-- NAME|Alice ---->|        |
|        |<-- NAME|Bob ------|        |
|        |-- MSG|hello ---->|        |
|        |<-- MSG|hi ------|        |
|        |-- LEAVE -------->|        |
+--------+                   +--------+
```

### Step-by-step flow

1. You run `python peer.py` — a menu appears
2. One person picks **Host**, the other picks **Join**
3. **Host**: enters a display name and port — a waiting screen appears showing the host's IPs
4. **Host**: shares their IP and port with their friend (via text, DM, etc.)
5. **Friend**: picks **Join**, enters the host's IP and port, and their own display name
6. Both peers exchange display names behind the scenes (handshake)
7. The chat screen opens — both can type freely

## Setup

### Prerequisites

- **Python 3.6+** (no pip installs needed)
- **Tailscale** (recommended) — see connection options below

### Usage

```bash
python peer.py
```

## Menu Walkthrough

When you start the app, you'll see:

```
+--------------------------------------------------+
|           TERMINAL CHAT - v1.0                    |
+--------------------------------------------------+
+--------------------------------------------------+
|  [1] Host a room                                 |
|  [2] Join a room                                 |
|  [3] Exit                                        |
+--------------------------------------------------+
  Select:
```

Press `1`, `2`, or `3` and press Enter.

### Hosting

1. Select `[1]` — you'll be asked for your display name
2. Enter your name (e.g., `Alice`) — this is what your friend will see
3. Enter a port number (press Enter for default **5555**)
4. A waiting screen appears with your connection info:

```
  ==================================================
     Waiting for peer to connect...

     LAN (same WiFi): 192.168.1.10:5555
     Tailscale (same account): 100.95.127.24:5555
     Tailscale Share (different account):
       1. Go to https://login.tailscale.com/admin/machines
       2. Click Share on this machine
       3. Enter friend's email
       4. Friend accepts, then joins with above IP

     Port: 5555
  --------------------------------------------------
  (Press Ctrl+C to cancel)
```

5. Send your IP and port to your friend. The app waits until they connect.
6. Once connected, the chat screen opens automatically.

### Joining

1. Select `[2]` — you'll be asked for the host's IP
2. Enter the IP your friend shared (e.g., `100.95.127.24`)
3. Enter the port (default **5555**)
4. Enter your display name (e.g., `Bob`)
5. The app connects to the host and the chat screen opens.

### Chat Screen

Once connected, you'll see:

```
  ==================================================
     Chat with: Bob
     Type /help for commands
  --------------------------------------------------

  [You] Hello!
  [Bob] Hey! How's it going?
  [You] Good, you?
  >
```

Type a message and press Enter to send it. Your message appears as `[You]` and the other person's as `[TheirName]`.

### Commands

| Command | What it does |
|---------|-------------|
| `/help` | Show available commands |
| `/leave` | Disconnect and return to menu |
| `/quit` | Same as `/leave` |
| `/q` | Same as `/leave` |

### Disconnect

When someone leaves, the other person sees:

```
  [Bob] disconnected.
  >
```

Pressing Enter returns you to the main menu. The other peer exits to the menu on their end too.

## Connection Options

| Method | When to use | Tailscale needed? |
|--------|-------------|-------------------|
| **LAN** | Both on same WiFi/router | No |
| **Tailscale (same account)** | Friends with same Tailscale account | Yes |
| **Tailscale Share** | Friends with different Tailscale accounts | Yes |

### LAN (same WiFi)

No Tailscale required. The host sees their LAN IP (e.g. `192.168.x.x`) on the waiting screen. Both machines must be on the same local network.

### Tailscale (same account)

Both friends log into Tailscale with the same account. The host's `100.x.y.z` Tailscale IP is shown on the waiting screen. Works anywhere with internet access.

### Tailscale Share (different accounts)

For friends who each have their own Tailscale account:

1. **Host**: Open https://login.tailscale.com/admin/machines
2. Find your machine, click the **Share** button
3. Enter your friend's email address (or copy a share link)
4. **Friend**: Accept the share invitation via email/link
5. **Friend**: Run `peer.py`, select Join, and enter the host's Tailscale IP

After accepting, the shared machine appears in the friend's Tailscale client with a `100.x.y.z` IP. Enter that IP when joining.

## Protocol

Plain TCP, messages terminated by newline:

| Direction | Format | Description |
|-----------|--------|-------------|
| Both | `NAME|display_name\n` | Handshake (sent immediately after connect/accept) |
| Both | `MSG|text\n` | Chat message |
| Either | `LEAVE\n` | Disconnect notification |

### Handshake

When a connection is established:

1. **Joiner** sends `NAME|Bob\n` immediately
2. **Host** receives it, sets the peer name to `Bob`
3. **Host** replies `NAME|Alice\n`
4. **Joiner** receives it, sets the peer name to `Alice`
5. Both enter the chat screen

If the handshake fails (timeout, connection drop, or invalid data), the connection is closed and an error message is shown.

### Disconnect

When someone types `/leave`, `/quit`, or `/q`:
1. `LEAVE\n` is sent to the other peer
2. The socket is shut down
3. Both return to the main menu

If the connection drops unexpectedly (network failure, window closed), the remaining peer detects the socket close and exits to the menu within 2 seconds.

## Architecture

- Single file (`peer.py`) handles both host and join roles
- Host opens a listener; joiner connects directly to host's IP:port
- No central relay, no room codes, no server process needed
- Future E2EE: replace `MSG|text` with `MSG|<base64(encrypted)>` — protocol unchanged
