# Prism

Prism is a lightweight, zero-dependency, pure ASCII peer-to-peer terminal chat application built in Python using raw sockets and threading. No central server needed — peers connect directly over TCP.

## Features

- **Strict ASCII UI**: Pure text-based interface. Runs in any terminal or command prompt.
- **Peer-to-Peer**: Direct TCP socket between two peers. No central server, no room codes.
- **Three ways to connect**: LAN, Tailscale (same account), or Tailscale Share (different accounts).
- **E2EE-Ready Protocol**: Message format (`MSG|text`) is designed to swap in encryption later without structural changes.
- **Zero Data Footprint**: Messages processed entirely in-memory. No logs, no databases, no history.
- **Immediate Disconnect**: Leave instantly with `/leave`, `/quit`, or `/q`.

## Setup

### Prerequisites

- **Python 3.6+** (no pip installs needed)
- **Tailscale** (recommended) — see connection options below

### Usage

```bash
python peer.py
```

1. **Host**: Select `[1]`, enter your display name, pick a port (default 5555).
2. **Join**: Select `[2]`, enter the host's IP and port, then your display name.
3. **Chat**: Type messages freely. Commands: `/help`, `/leave`, `/quit`, `/q`.

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

The peer receiving `LEAVE` or detecting socket closure exits to the menu.

## Architecture

- Single file (`peer.py`) handles both host and join roles
- Host opens a listener; joiner connects directly to host's IP:port
- No central relay, no room codes, no server process needed
- Future E2EE: replace `MSG|text` with `MSG|<base64(encrypted)>` — protocol unchanged
