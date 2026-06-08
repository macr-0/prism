import socket
import threading
import random
import string
import time

HOST = "0.0.0.0"
PORT = 5555
rooms = {}
rooms_lock = threading.Lock()


def generate_room_code():
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(chars, k=6))
        with rooms_lock:
            if code not in rooms:
                return code


def broadcast_to_room(code, message, exclude_conn=None):
    with rooms_lock:
        if code in rooms:
            for conn in rooms[code]:
                if conn != exclude_conn:
                    try:
                        conn.sendall((message + "\n").encode())
                    except Exception:
                        pass


def handle_client(conn, addr):
    room_code = None
    display_name = None

    buf = b""
    should_exit = False
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                line = line.decode().strip()
                if not line:
                    continue

                parts = line.split("|", 2)
                cmd = parts[0]

                if cmd == "HOST":
                    display_name = parts[1] if len(parts) > 1 else "Anonymous"
                    code = generate_room_code()
                    with rooms_lock:
                        rooms[code] = [conn]
                    room_code = code
                    conn.sendall(f"ROOM|{code}\n".encode())

                elif cmd == "JOIN":
                    if len(parts) < 3:
                        conn.sendall("ERROR|Invalid JOIN format\n".encode())
                        continue
                    code = parts[1]
                    display_name = parts[2]
                    with rooms_lock:
                        if code not in rooms:
                            conn.sendall("ERROR|Room not found\n".encode())
                            continue
                        if len(rooms[code]) >= 2:
                            conn.sendall("ERROR|Room is full\n".encode())
                            continue
                        rooms[code].append(conn)
                    room_code = code
                    conn.sendall(f"JOINED|{display_name}\n".encode())
                    broadcast_to_room(code, f"MSG|System|{display_name} joined the chat", exclude_conn=conn)

                elif cmd == "MSG":
                    if room_code:
                        text = parts[1] if len(parts) > 1 else ""
                        broadcast_to_room(room_code, f"MSG|{display_name}|{text}", exclude_conn=conn)

                elif cmd == "LEAVE":
                    should_exit = True
                    break
            if should_exit:
                break

    except Exception:
        pass
    finally:
        room_to_cleanup = None
        peer_conn = None
        with rooms_lock:
            if room_code and room_code in rooms:
                if conn in rooms[room_code]:
                    rooms[room_code].remove(conn)
                    if rooms[room_code]:
                        peer_conn = rooms[room_code][0]
                        room_to_cleanup = room_code
                    else:
                        del rooms[room_code]
        if peer_conn:
            try:
                peer_conn.sendall(f"PEER_DISCONNECTED|{display_name}\n".encode())
            except Exception:
                pass
            def close_room_after_delay(rc):
                time.sleep(5)
                with rooms_lock:
                    if rc in rooms and rooms[rc]:
                        try:
                            rooms[rc][0].sendall(f"ROOM_CLOSED|{rc}\n".encode())
                        except Exception:
                            pass
                        del rooms[rc]
            threading.Thread(target=close_room_after_delay, args=(room_to_cleanup,), daemon=True).start()
        conn.close()


def main():
    print("=== Chat Server ===")
    host = input("  Bind IP (Enter for 0.0.0.0): ").strip()
    if not host:
        host = "0.0.0.0"
    port_str = input("  Port (Enter for 5555): ").strip()
    if port_str:
        try:
            port = int(port_str)
        except ValueError:
            print(f"  Invalid port: {port_str}")
            return
    else:
        port = 5555

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((host, port))
    except OSError as e:
        print(f"  Bind failed: {e}")
        return
    server.listen()
    print(f"Server listening on {host}:{port}")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.close()


if __name__ == "__main__":
    main()
