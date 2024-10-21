import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            # Receive messages from the server
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print("\n" + message)
            else:
                # Server has closed the connection
                print("\nConnection closed by the server.")
                break
        except socket.error:
            print("\nError receiving message.")
            break

def start_client(server_ip='192.168.56.1', port=9998):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((server_ip, port))
        print("Connected to the server!")

        # Get the client's name
        name = input("Enter your name: ").strip()
        client_socket.send(name.encode('utf-8'))

        # Start a thread to receive messages
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True
        receive_thread.start()

        # Send messages to the server
        while True:
            message = input().strip()
            if message == '':
                continue  # Ignore empty messages
            if message.lower() == 'quit':
                client_socket.send('quit'.encode('utf-8'))
                break
            else:
                client_socket.send(message.encode('utf-8'))

    except socket.gaierror as e:
        print(f"Address-related error connecting to server: {e}")
    except socket.error as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()
        print("Connection closed.")

# Run the client
if __name__ == "__main__":
    start_client()

