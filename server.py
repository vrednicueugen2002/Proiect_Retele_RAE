import socket
import threading
import subprocess
import os

class ScriptServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.clients = {}
        self.commands = {}
        self.scripts = {}
        self.lock = threading.Lock()

    def handle_client(self, conn, addr):
        print(f"New connection from {addr}")
        client_id = addr

        try:
            while True:
                data = conn.recv(4096).decode()
                if not data:
                    break

                parts = data.split(' ')
                command = parts[0]

                if command == "PUBLISH":
                    command_name = parts[1]
                    script_names = parts[2:]

                    with self.lock:
                        self.commands[command_name] = (client_id, script_names)
                        if client_id not in self.clients:
                            self.clients[client_id] = []
                        if command_name not in self.clients[client_id]:
                            self.clients[client_id].append(command_name)

                    print(f"Client {addr} published command {command_name} with scripts: {script_names}")

                    for script_name in script_names:
                        script_content = self.receive_script(conn)
                        with self.lock:
                            self.scripts[script_name] = script_content
                        print(f"Received script {script_name} from {addr}")

                elif command == "EXECUTE":
                    command_name = parts[1]
                    input_data = conn.recv(4096).decode()

                    with self.lock:
                        if command_name in self.commands and self.commands[command_name][0] == client_id:
                            script_sequence = self.commands[command_name][1]
                        else:
                            conn.sendall("ERROR: Command not found or unauthorized".encode())
                            continue

                    output = self.execute_command(script_sequence, input_data)
                    conn.sendall(output.encode())

                    # Scrie output-ul intr-un fisier
                    result_filename = f"{command_name}_result.txt"
                    with open(result_filename, 'w') as result_file:
                        result_file.write(output)

                elif command == "DELETE":
                    command_name = parts[1]

                    with self.lock:
                        if command_name in self.commands and self.commands[command_name][0] == client_id:
                            del self.commands[command_name]
                            self.clients[client_id].remove(command_name)
                            conn.sendall("DELETED".encode())
                            print(f"Client {addr} deleted command {command_name}")
                        else:
                            conn.sendall("ERROR: Command not found or unauthorized".encode())

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            conn.close()
            print(f"Connection from {addr} closed")

    def receive_script(self, conn):
        script_content = []
        while True:
            line = conn.recv(4096).decode()
            if line.strip() == "END_OF_SCRIPT":
                break
            script_content.append(line)
        return '\n'.join(script_content)

    def execute_command(self, script_sequence, input_data):
        current_input = input_data
        final_output = ""

        for script_name in script_sequence:
            with self.lock:
                script_content = self.scripts[script_name]

            script_file = f"{script_name}.py"
            with open(script_file, 'w') as f:
                f.write(script_content)

            result = subprocess.run(
                ['python', script_file],
                input=current_input,
                text=True,
                capture_output=True
            )
            current_input = result.stdout
            final_output += current_input

            os.remove(script_file)

        return final_output

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    server = ScriptServer()
    server.start()
