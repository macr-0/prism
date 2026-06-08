import socket
import threading
import time
import msvcrt
import sys
import os

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555


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


def receive_messages(sock, chat_active, state):
    while chat_active[0]:
        try:
            line = recv_line(sock)
            if line is None:
                break
            if not line:
                continue
            handle_server_message(line, chat_active, state)
        except Exception:
            break
    chat_active[0] = False


def handle_server_message(message, chat_active, state):
    if message.startswith("ROOM|"):
        pass
    elif message.startswith("JOINED|"):
        pass
    elif message.startswith("MSG|"):
        parts = message.split("|", 2)
        name = parts[1]
        text = parts[2] if len(parts) > 2 else ""
        if state.get("peer_name") is None and name != "System":
            state["peer_name"] = name
        print(f"\r  [{name}] {text}")
        print("  > ", end="", flush=True)
    elif message.startswith("PEER_DISCONNECTED|"):
        name = message.split("|", 1)[1]
        print(f"\n  {name} disconnected.")
        print("  > ", end="", flush=True)
    elif message.startswith("ROOM_CLOSED"):
        parts = message.split("|", 1)
        code = parts[1] if len(parts) > 1 else ""
        if not code or code == state.get("room_code"):
            print("  Session ended.")
            chat_active[0] = False
    elif message.startswith("ERROR|"):
        err = message.split("|", 1)[1]
        print(f"\n  Error: {err}")


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


def display_chat_header(room_code):
    print()
    print("  " + "=" * 50)
    print(f"     CHAT ROOM: {room_code}")
    print(f"     Type /help for commands")
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


def wait_for_response(sock, expected_prefix, timeout=30):
    sock.settimeout(timeout)
    try:
        while True:
            line = recv_line(sock)
            if line is None:
                return None
            if line.startswith(expected_prefix):
                sock.settimeout(None)
                return line
            if line.startswith("ERROR|"):
                sock.settimeout(None)
                return line
    except socket.timeout:
        sock.settimeout(None)
        return None


def run_chat(sock, display_name, is_host=False, room_code=None):
    chat_active = [True]
    state = {"peer_name": None, "room_code": room_code}

    if is_host:
        sock.sendall(f"HOST|{display_name}\n".encode())
        resp = wait_for_response(sock, "ROOM|")
        if resp:
            room_code = resp.split("|", 1)[1]
            state["room_code"] = room_code

    recv_thread = threading.Thread(target=receive_messages, args=(sock, chat_active, state), daemon=True)
    recv_thread.start()

    if room_code:
        clear_screen()
        display_chat_header(room_code)

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

                if lower in ("/leave", "/quit", "/q" ):
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


def main():
    global SERVER_IP, SERVER_PORT
    clear_screen()
    display_banner()

    prompt = input("  Server address (Enter for 127.0.0.1:5555): ").strip()
    if prompt:
        if ":" in prompt:
            SERVER_IP, port_str = prompt.rsplit(":", 1)
            SERVER_PORT = int(port_str)
        else:
            SERVER_IP = prompt

    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((SERVER_IP, SERVER_PORT))
        except Exception as e:
            print(f"  Connection failed: {e}")
            retry = input("  Retry? (y/n): ").strip().lower()
            if retry == "y":
                continue
            return

        display_menu()
        choice = input("  Select: ").strip()

        if choice == "1":
            name = input("  Enter your display name: ").strip()
            if not name:
                name = "Anonymous"
            run_chat(sock, name, is_host=True)

        elif choice == "2":
            name = input("  Enter your display name: ").strip()
            if not name:
                name = "Anonymous"
            code = input("  Enter the room code: ").strip().upper()
            if not code:
                print("  No code provided.")
                sock.close()
                continue
            sock.sendall(f"JOIN|{code}|{name}\n".encode())
            resp = wait_for_response(sock, "JOINED|")
            if resp is None or resp.startswith("ERROR|"):
                err = resp.split("|", 1)[1] if resp and resp.startswith("ERROR|") else "No response from server"
                print(f"  {err}")
                sock.close()
                continue
            run_chat(sock, name, is_host=False, room_code=code)

        elif choice == "3":
            print("  Goodbye!")
            sock.close()
            return

        else:
            print("  Invalid selection.")

        sock.close()


if __name__ == "__main__":
    main()
