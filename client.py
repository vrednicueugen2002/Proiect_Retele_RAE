import socket

class ScriptClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.pipelines = {}

    def publish_command(self):
        command_name = input("Enter a name for the pipeline: ")

        script_files = []
        print("Enter paths to your script files. Type 'done' when finished:")
        while True:
            path = input("Script path: ")
            if path.lower() == 'done':
                break
            script_files.append(path)

        if not script_files:
            print("No scripts provided. Aborting command publication.")
            return

        self.pipelines[command_name] = script_files

        script_names = [script.split('/')[-1] for script in script_files]
        data = f"PUBLISH {command_name} " + ' '.join(script_names)
        self.socket.sendall(data.encode())
        print(f"Sent command publication: {command_name} with scripts: {script_names}")

        for script_file in script_files:
            with open(script_file, 'r') as file:
                script_content = file.read()
                self.socket.sendall(script_content.encode())
                self.socket.sendall("END_OF_SCRIPT\n".encode())
                print(f"Sent script content of {script_file}")

    def execute_command(self):
        if not self.pipelines:
            print("No pipelines available. Please publish a command first.")
            return

        print("Available pipelines:")
        for command_name in self.pipelines:
            print(f"{command_name}: {self.pipelines[command_name]}")

        command_name = input("Enter the pipeline name to execute: ")
        if command_name not in self.pipelines:
            print("Invalid pipeline name. Aborting execution.")
            return

        input_data = input("Enter input data for the pipeline: ")
        data = f"EXECUTE {command_name}"
        self.socket.sendall(data.encode())
        self.socket.sendall(input_data.encode())

        output = self.socket.recv(4096).decode()
        print(f"Received output: {output}")

        result_filename = f"{command_name}_result.txt"
        print(f"Received result file {result_filename}")

    def delete_command(self):
        command_name = input("Enter the name of the pipeline to delete: ")

        if command_name not in self.pipelines:
            print("Invalid pipeline name. Aborting deletion.")
            return

        data = f"DELETE {command_name}"
        self.socket.sendall(data.encode())

        response = self.socket.recv(4096).decode()
        if response == "DELETED":
            del self.pipelines[command_name]
            print(f"Pipeline {command_name} deleted successfully.")
        else:
            print(f"Failed to delete pipeline {command_name}: {response}")

    def menu(self):
        while True:
            print("\nOptions:")
            print("1. Publish a new command")
            print("2. Execute a command")
            print("3. Delete a command")
            print("4. Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                self.publish_command()
            elif choice == '2':
                self.execute_command()
            elif choice == '3':
                self.delete_command()
            elif choice == '4':
                self.close()
                break
            else:
                print("Invalid choice. Please try again.")

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    client = ScriptClient()
    client.menu()
