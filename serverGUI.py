import socket
import threading

class ChatServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", 9998))  # Bind to all available interfaces
        self.server_socket.listen(5)  # Listen for incoming connections
        self.clients = []  # List to hold connected clients
        self.usernames = {}  # Dictionary to map client sockets to usernames

        print("Chat server started on port 9998.")
        self.accept_connections()

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connection from {addr} has been established!")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        # Get the username
        client_socket.send("Enter your username: ".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8')
        self.usernames[client_socket] = username  # Store the username
        self.clients.append(client_socket)
        self.broadcast_message(f"{username} has joined the chat.", client_socket)
        print(f"{username} has joined the chat.")

        while True:
            try:
                msg = client_socket.recv(1024).decode('utf-8')
                if msg:
                    print(f"{username}: {msg}")
                    self.broadcast_message(f"{username}: {msg}", client_socket)
            except Exception as e:
                print("Error:", e)
                break

        client_socket.close()
        self.clients.remove(client_socket)  # Remove the client from the list
        del self.usernames[client_socket]  # Remove the username
        self.broadcast_message(f"{username} has left the chat.", client_socket)

    def broadcast_message(self, msg, sender_socket):
        for client in self.clients:
            if client != sender_socket:  # Send to all clients except the sender
                try:
                    client.send(msg.encode('utf-8'))
                except Exception as e:
                    print("Error sending message:", e)

if __name__ == "__main__":
    ChatServer()
