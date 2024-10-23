import socket
import threading

# Dictionary to store client sockets and their corresponding names
clients = {}

# Function to broadcast a message to all clients
def broadcast(message):
    for client_socket in clients:
        try:
            # Send the message to all clients, including the sender
            client_socket.send(message.encode('utf-8'))
        except socket.error:
            # If sending fails, close the connection
            client_socket.close()
            remove_client(client_socket)

# Function to remove a client from the clients dictionary
def remove_client(client_socket):
    if client_socket in clients:
        del clients[client_socket]

# Function to handle each client's connection
def handle_client(client_socket, client_address):
    try:
        # Receive the client's name
        client_name = client_socket.recv(1024).decode('utf-8')
        welcome_message = f"{client_name} has joined the chat!"
        print(welcome_message)
        broadcast(welcome_message)

        # Add the client to the dictionary
        clients[client_socket] = client_name

        # Handle incoming messages
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message or message.lower() == 'quit':
                goodbye_message = f"{client_name} has left the chat."
                print(goodbye_message)
                broadcast(goodbye_message)
                break
            else:
                full_message = f"{client_name}: {message}"
                print(full_message)
                broadcast(full_message)
    except socket.error as e:
        print(f"Connection error with {client_address}: {e}")
    finally:
        # Remove the client and close the connection
        remove_client(client_socket)
        client_socket.close()

# Main server function
def start_server(host='0.0.0.0', port=9998):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server started on {host}:{port}")

    while True:
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address}")
        # Start a new thread for each client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

# Run the server
if __name__ == "__main__":
    start_server()
    
# wilson Anjing
