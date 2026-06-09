import socket
import threading
import time
import msvcrt
import sys
import os

DEFAULT_PORT = 5555


def recv_line(sock):
    buf = b""
    while True:
        c = sock.recv(1)
        if not c:
            return None
        if c == b"\n":
            return buf.decode().strip()
        buf += c


def clear_screen():
    os.system("cls")


def get_tailscale_ip():
    try:
        import subprocess
        kwargs = {"capture_output": True, "text": True, "timeout": 5}
        try:
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        except AttributeError:
            pass
        result = subprocess.run(["tailscale", "ip", "-4"], **kwargs)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def receive_messages(sock, chat_active, peer_name):
    while chat_active[0]:
        try:
            line = recv_line(sock)
            if line is None:
                break
            if not line:
                continue
            handle_peer_message(line, chat_active, peer_name)
        except Exception:
            break
    chat_active[0] = False


def handle_peer_message(message, chat_active, peer_name):
    if message.startswith("MSG|"):
        parts = message.split("|", 2)
        text = parts[1] if len(parts) > 1 else ""
        print(f"\r  [{peer_name}] {text}")
        print("  > ", end="", flush=True)
    elif message.startswith("LEAVE"):
        print(f"\n  {peer_name} disconnected.")
        print("  > ", end="", flush=True)
        chat_active[0] = False


def display_banner():
    print("+--------------------------------------------------+")
    print("|           TERMINAL CHAT - v1.0                    |")
    print("+--------------------------------------------------+")


def display_menu():
    print("+--------------------------------------------------+")
    print("|  [1] Host a room                                 |")
    print("|  [2] Join a room                                 |")
    print("|  [3] Exit                                        |")
    print("+--------------------------------------------------+")


def display_chat_header(peer_name):
    print()
    print("  " + "=" * 50)
    print(f"     Chat with: {peer_name}")
    print("     Type /help for commands")
    print("  " + "-" * 50)
    print()


def display_chat_help():
    print()
    print("  Commands:")
    print("  /help   - Show this help")
    print("  /leave  - Leave the chat")
    print("  /quit   - Leave the chat")
    print("  /q      - Leave the chat")
    print("  (anything else) - Send as a message")
    print()


def run_chat(sock, display_name, peer_name):
    chat_active = [True]

    recv_thread = threading.Thread(target=receive_messages, args=(sock, chat_active, peer_name), daemon=True)
    recv_thread.start()

    clear_screen()
    display_chat_header(peer_name)

    line_buf = []
    while chat_active[0]:
        if msvcrt.kbhit():
            c = msvcrt.getch()
            if c == b"\r":
                user_input = "".join(line_buf)
                line_buf = []
                sys.stdout.write("\n")
                sys.stdout.flush()

                if not chat_active[0]:
                    break

                if not user_input.strip():
                    print("  > ", end="", flush=True)
                    continue

                lower = user_input.strip().lower()

                if lower in ("/leave", "/quit", "/q"):
                    try:
                        sock.sendall("LEAVE\n".encode())
                    except Exception:
                        pass
                    chat_active[0] = False
                    break

                if lower == "/help":
                    display_chat_help()
                    print("  > ", end="", flush=True)
                    continue

                try:
                    sock.sendall(f"MSG|{user_input}\n".encode())
                except Exception:
                    chat_active[0] = False
                    break

                print(f"  [You] {user_input}")
                print("  > ", end="", flush=True)

            elif c == b"\x08":
                if line_buf:
                    line_buf.pop()
                    sys.stdout.write("\x08 \x08")
                    sys.stdout.flush()
            else:
                try:
                    ch = c.decode()
                    line_buf.append(ch)
                    sys.stdout.write(ch)
                    sys.stdout.flush()
                except Exception:
                    pass
        else:
            time.sleep(0.05)

    recv_thread.join(timeout=2)


def host_room(display_name):
    print("\n  Enter port (Enter for 5555):")
    port_str = input("  > ").strip()
    port = int(port_str) if port_str else DEFAULT_PORT

    tailscale_ip = get_tailscale_ip()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", port))
    except OSError as e:
        print(f"  Bind failed: {e}")
        return
    server.listen(1)

    clear_screen()
    print()
    print("  " + "=" * 50)
    print("     Waiting for peer to connect...")
    if tailscale_ip:
        print(f"     Tailscale IP: {tailscale_ip}")
    else:
        print("     IP: (check your Tailscale IP)")
    print(f"     Port: {port}")
    print("  " + "-" * 50)
    print()
    print("  (Press Ctrl+C to cancel)")

    try:
        conn, addr = server.accept()
        server.close()
    except KeyboardInterrupt:
        print("\n  Cancelled.")
        server.close()
        return

    try:
        peer_line = recv_line(conn)
        if peer_line and peer_line.startswith("NAME|"):
            peer_name = peer_line.split("|", 1)[1]
        else:
            peer_name = "Unknown"
        conn.sendall(f"NAME|{display_name}\n".encode())
    except Exception:
        conn.close()
        print("  Handshake failed.")
        return

    run_chat(conn, display_name, peer_name)
    conn.close()


def join_room():
    print("\n  Enter host's Tailscale IP:")
    ip = input("  > ").strip()
    if not ip:
        print("  No IP provided.")
        return

    print("\n  Enter port (Enter for 5555):")
    port_str = input("  > ").strip()
    if port_str:
        try:
            port = int(port_str)
        except ValueError:
            print(f"  Invalid port: {port_str}")
            return
    else:
        port = DEFAULT_PORT

    print("\n  Enter your display name:")
    name = input("  > ").strip()
    if not name:
        name = "Anonymous"

    print(f"\n  Connecting to {ip}:{port}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
    except Exception as e:
        print(f"  Connection failed: {e}")
        sock.close()
        return

    try:
        sock.sendall(f"NAME|{name}\n".encode())
        peer_line = recv_line(sock)
        if peer_line and peer_line.startswith("NAME|"):
            peer_name = peer_line.split("|", 1)[1]
        else:
            peer_name = "Unknown"
    except Exception:
        sock.close()
        print("  Handshake failed.")
        return

    run_chat(sock, name, peer_name)
    sock.close()


def main():
    clear_screen()
    display_banner()

    while True:
        display_menu()
        choice = input("  Select: ").strip()

        if choice == "1":
            print("\n  Enter your display name:")
            name = input("  > ").strip()
            if not name:
                name = "Anonymous"
            host_room(name)

        elif choice == "2":
            join_room()

        elif choice == "3":
            print("  Goodbye!")
            return

        else:
            print("  Invalid selection.")


if __name__ == "__main__":
    main()
