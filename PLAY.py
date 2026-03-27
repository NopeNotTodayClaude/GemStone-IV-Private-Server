"""
GemStone IV - Simple Console Client
Double-click this file or run: python PLAY.py
"""

import socket
import threading
import sys
import os

HOST = "127.0.0.1"
PORT = 4901

def receive_loop(sock):
    """Continuously read from server and print to screen."""
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                print("\n*** Disconnected from server. ***")
                break
            text = data.decode("utf-8", errors="replace")
            # Print server text (flush to show immediately)
            print(text, end="", flush=True)
    except (ConnectionResetError, ConnectionAbortedError, OSError):
        print("\n*** Connection lost. ***")
    finally:
        os._exit(0)

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 50)
    print("  GemStone IV - Private Server Client")
    print("  Connecting to %s:%d..." % (HOST, PORT))
    print("=" * 50)
    print()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("ERROR: Cannot connect to server!")
        print("Make sure the server is running first:")
        print("  python server/main.py")
        print()
        input("Press Enter to exit...")
        return
    except Exception as e:
        print(f"ERROR: {e}")
        input("Press Enter to exit...")
        return

    # Start background thread to receive server messages
    recv_thread = threading.Thread(target=receive_loop, args=(sock,), daemon=True)
    recv_thread.start()

    # Main loop: read player input and send to server
    try:
        while True:
            line = input()
            if line.lower() in ("quit", "exit"):
                print("Goodbye!")
                break
            sock.sendall((line + "\n").encode("utf-8"))
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
