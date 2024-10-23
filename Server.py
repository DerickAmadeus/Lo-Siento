import socket
import threading

# Dictionary to store client addresses and their corresponding names
clients = {}

# Function to broadcast a message to all clients
def broadcast(message, sender_address=None):
    for client_address in clients:
        if client_address != sender_address:  # Do not send the message back to the sender
            try:
                # Send the message to all clients except the sender
                server_socket.sendto(message.encode('utf-8'), client_address)
            except socket.error:
                # If sending fails, remove the client
                remove_client(client_address)

# Function to remove a client from the clients dictionary
def remove_client(client_address):
    if client_address in clients:
        del clients[client_address]

# Function to handle incoming messages
def handle_client_message(message, client_address):
    if client_address not in clients:
        # New client: add them to the dictionary
        client_name = message
        clients[client_address] = client_name
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
def start_server(host='0.0.0.0', port=9998):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Server started on {host}:{port}")

    while True:
        try:
            # Receive message from a client
            message, client_address = server_socket.recvfrom(1024)
            message = message.decode('utf-8')

            # Handle the client's message in a separate thread
            client_thread = threading.Thread(target=handle_client_message, args=(message, client_address))
            client_thread.start()
        except socket.error as e:
            print(f"Socket error: {e}")

# Run the server
if __name__ == "__main__":
    start_server()
