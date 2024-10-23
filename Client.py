import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            # Receive messages from the server
            message, _ = client_socket.recvfrom(1024)
            message = message.decode('utf-8')
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
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Get the client's name
        name = input("Enter your name: ").strip()
        client_socket.sendto(name.encode('utf-8'), (server_ip, port))

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
                client_socket.sendto('quit'.encode('utf-8'), (server_ip, port))
                break
            else:
                client_socket.sendto(message.encode('utf-8'), (server_ip, port))

    except socket.gaierror as e:
        print(f"Address-related error: {e}")
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        client_socket.close()
        print("Connection closed.")

# Run the client
if __name__ == "__main__":
    start_client()
