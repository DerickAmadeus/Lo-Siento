import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            # Receive messages from the server
            message, _ = client_socket.recvfrom(1024)
            message = message.decode('utf-8')
            if message == "PASS_OK":
                print("Password accepted! You have joined the chat.")
            elif message == "PASS_FAIL":
                print("Password incorrect! Try again.")
            elif message:
                print("\n" + message)
            else:
                # Server has closed the connection
                print("\nConnection closed by the server.")
                break
        except socket.error:
            print("\nError receiving message.")
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = input("Enter the server IP address (default: 192.168.56.1): ").strip() or '192.168.56.1'
    port = input("Enter the server port (default: 9998): ").strip()
    port = int(port) if port else 9998

    try:
        # Allow up to 3 attempts to input the correct password
        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            password = input(f"Enter the server password (attempt {attempts+1}/{max_attempts}): ").strip()
            client_socket.sendto(f"PASS:{password}".encode('utf-8'), (server_ip, port))

            # Wait for password validation response
            pass_response, _ = client_socket.recvfrom(1024)
            if pass_response.decode('utf-8') == "PASS_OK":
                break
            else:
                print("Incorrect password!")
                attempts += 1

            # If 3 attempts are used up, close the connection
            if attempts == max_attempts:
                print("Maximum attempts reached! Connection closed.")
                return

        # Get the client's name after password is accepted
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