import socket
import threading
from datetime import datetime

# Dictionary to store client addresses and their corresponding names
clients = {}
# Dictionary to keep track of name attempts for each client
name_attempts = {}

# Predefined password for the server
server_password = "secret123"

# Log file to store chat history
chat_history_file = "chat.txt"

# Function to write a message to the chat history file with a timestamp
def save_to_history(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(chat_history_file, "a") as file:
        file.write(f"[{timestamp}] {message}\n")

# Function to broadcast a message to all clients
def broadcast(message, sender_address=None):
    save_to_history(message)  # Save message to chat history with timestamp
    for client_address in clients:
        if client_address != sender_address:  # Do not send the message back to the sender
            try:
                server_socket.sendto(message.encode('utf-8'), client_address)
            except socket.error:
                remove_client(client_address)

# Function to remove a client from the clients dictionary
def remove_client(client_address):
    if client_address in clients:
        del clients[client_address]
    if client_address in name_attempts:
        del name_attempts[client_address]

# Function to handle incoming messages
def handle_client_message(message, client_address):
    if client_address not in clients:
        # New client: check for the password first
        if message.startswith("PASS:"):
            client_password = message[5:]
            if client_password == server_password:
                server_socket.sendto("PASS_OK".encode('utf-8'), client_address)
            else:
                server_socket.sendto("PASS_FAIL".encode('utf-8'), client_address)
        else:
            # Expect the client name if the password was correct
            client_name = message

            # Initialize the name attempt count if not present
            if client_address not in name_attempts:
                name_attempts[client_address] = 0

            if client_name in clients.values():
                server_socket.sendto("NAME_TAKEN".encode('utf-8'), client_address)
            else:
                clients[client_address] = client_name
                del name_attempts[client_address]  # Clear name attempts after successful entry
                server_socket.sendto("NAME_OK".encode('utf-8'), client_address)  # Notify client that name is accepted
                welcome_message = f"{client_name} has joined the chat!"
                print(welcome_message)
                broadcast(welcome_message, sender_address=client_address)
    else:
        # Existing client: process their message
        client_name = clients[client_address]
        if message.lower() == 'quit':
            goodbye_message = f"{client_name} has left the chat."
            print(goodbye_message)
            broadcast(goodbye_message, sender_address=client_address)
            remove_client(client_address)
        else:
            full_message = f"{client_name}: {message}"
            print(full_message)
            broadcast(full_message, sender_address=client_address)

# Main server function
def start_server(host='25.11.93.199', port=2620):  # Change the host and port as needed
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Server started on {host}:{port}")

    # No need to initialize chat history file here; just append to it
    # Initial message (optional)
    save_to_history("Server started.")

    while True:
        try:
            message, client_address = server_socket.recvfrom(1024)
            message = message.decode('utf-8')
            client_thread = threading.Thread(target=handle_client_message, args=(message, client_address))
            client_thread.start()
        except socket.error as e:
            print(f"Socket error: {e}")

# Run the server
if __name__ == "__main__":
    start_server()
