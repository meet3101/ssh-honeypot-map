import paramiko
import socket
import threading
import datetime
import sys
import os
import logging

logging.getLogger("paramiko").setLevel(logging.CRITICAL)

sys.path.append(os.path.dirname(__file__))
from db import init_db, log_attempt
from geoip import geolocate

HOST_KEY = paramiko.RSAKey(filename=os.path.join(os.path.dirname(__file__), "honeypot_key"))
LISTEN_PORT = 2222

class FakeServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        print(f"[DEBUG] Auth attempt received: user={username}", flush=True)
        timestamp = datetime.datetime.now().isoformat()
        geo = geolocate(self.client_ip)
        print(f"[CAPTURED] {timestamp} | {self.client_ip} | user={username} pass={password} | {geo['country']}, {geo['city']}", flush=True)
        log_attempt(timestamp, self.client_ip, username, password,
                    geo["country"], geo["city"], geo["lat"], geo["lon"])
        self.event.set()
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED

def handle_connection(client_socket, addr):
    client_ip = addr[0]
    transport = None
    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)
        server = FakeServer(client_ip)
        transport.start_server(server=server)
        server.event.wait(15)
    except paramiko.ssh_exception.SSHException:
        pass
    except EOFError:
        pass
    except Exception as e:
        print(f"[ERROR] {client_ip}: {e}", flush=True)
    finally:
        try:
            if transport:
                transport.close()
            client_socket.close()
        except Exception:
            pass

def main():
    init_db()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", LISTEN_PORT))
    sock.listen(100)
    print(f"SSH Honeypot listening on port {LISTEN_PORT}... Ctrl+C to stop")

    while True:
        try:
            client, addr = sock.accept()
            print(f"Connection attempt from {addr[0]}:{addr[1]}", flush=True)
            threading.Thread(target=handle_connection, args=(client, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nShutting down honeypot...")
            break

if __name__ == "__main__":
    main()
