# Prism

Prism is a lightweight, zero-dependency, pure ASCII peer-to-peer terminal chat application built in Python using raw sockets and threading. No central server needed — peers connect directly over TCP using Tailscale for NAT traversal.

## Features

- **Strict ASCII UI**: Pure text-based interface. Runs in any terminal or command prompt.
- **Peer-to-Peer**: Direct TCP socket between two peers. No central server, no room codes.
- **Tailscale Ready**: Auto-detects your Tailscale IP for easy sharing.
- **E2EE-Ready Protocol**: Message format (`MSG|text`) is designed to swap in encryption later without structural changes.
- **Zero Data Footprint**: Messages processed entirely in-memory. No logs, no databases, no history.
- **Immediate Disconnect**: Leave instantly with `/leave`, `/quit`, or `/q`.

## Setup

### Prerequisites

- **Python 3.6+** (no pip installs needed)
- **Tailscale** (recommended) — both peers on the same tailnet

### Usage

```bash
python peer.py
```

1. **Host**: Select `[1]`, enter your display name, pick a port (default 5555). Share your Tailscale IP and port with your peer.
2. **Join**: Select `[2]`, enter the host's Tailscale IP and port, then your display name.
3. **Chat**: Type messages freely. Commands: `/help`, `/leave`, `/quit`, `/q`.

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
