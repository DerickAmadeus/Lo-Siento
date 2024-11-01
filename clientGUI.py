import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("UDP Chat Client")

        # Socket setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Server information
        self.server_ip = '192.168.56.1'
        self.server_port = 9998
        
        # Main frames
        self.setup_ui()
        
    def setup_ui(self):
        # Server IP and Port input
        tk.Label(self.master, text="Server IP:").grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = tk.Entry(self.master, width=20)
        self.ip_entry.insert(0, '192.168.56.1')
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.master, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        self.port_entry = tk.Entry(self.master, width=10)
        self.port_entry.insert(0, '9998')
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)

        # Message area
        self.chat_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, state="disabled", width=50, height=20)
        self.chat_area.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # Message entry
        self.message_entry = tk.Entry(self.master, width=40)
        self.message_entry.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        self.message_entry.bind("<Return>", self.send_message)

        # Send button
        send_button = tk.Button(self.master, text="Send", command=self.send_message)
        send_button.grid(row=2, column=3, padx=5, pady=5)

        # Connect button
        connect_button = tk.Button(self.master, text="Connect", command=self.connect)
        connect_button.grid(row=0, column=4, padx=5, pady=5)

    def connect(self):
        # Get IP and port
        self.server_ip = self.ip_entry.get().strip()
        self.server_port = int(self.port_entry.get().strip())
        
        # Password prompt
        max_attempts = 3
        for attempt in range(max_attempts):
            password = simpledialog.askstring("Password", f"Enter server password (attempt {attempt + 1}/{max_attempts}):", show='*')
            if password is None:
                return  # User canceled

            self.client_socket.sendto(f"PASS:{password}".encode('utf-8'), (self.server_ip, self.server_port))
            pass_response, _ = self.client_socket.recvfrom(1024)
            if pass_response.decode('utf-8') == "PASS_OK":
                break
            elif attempt == max_attempts - 1:
                messagebox.showerror("Error", "Maximum attempts reached! Connection closed.")
                return
            else:
                messagebox.showerror("Error", "Incorrect password!")

        # Name prompt
        while True:
            name = simpledialog.askstring("Name", "Enter your name:")
            if name is None:
                return  # User canceled

            self.client_socket.sendto(name.encode('utf-8'), (self.server_ip, self.server_port))
            name_response, _ = self.client_socket.recvfrom(1024)
            if name_response.decode('utf-8') == "NAME_OK":
                self.chat_area.config(state="normal")
                self.chat_area.insert(tk.END, f"Welcome, {name}!\n")
                self.chat_area.config(state="disabled")
                break
            else:
                messagebox.showerror("Error", "Name is already taken!")

        # Start receiving messages in a thread
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            try:
                message, _ = self.client_socket.recvfrom(1024)
                message = message.decode('utf-8')
                if message == "PASS_OK":
                    pass  # Handled in connect
                elif message == "PASS_FAIL":
                    pass  # Handled in connect
                else:
                    self.chat_area.config(state="normal")
                    self.chat_area.insert(tk.END, message + "\n")
                    self.chat_area.yview(tk.END)
                    self.chat_area.config(state="disabled")
            except socket.error:
                messagebox.showerror("Error", "Connection closed by the server.")
                break

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            # Display the user's own message in the chat area
            self.chat_area.config(state="normal")
            self.chat_area.insert(tk.END, f"You: {message}\n")
            self.chat_area.yview(tk.END)
            self.chat_area.config(state="disabled")

            # Send message to the server
            self.client_socket.sendto(message.encode('utf-8'), (self.server_ip, self.server_port))
            self.message_entry.delete(0, tk.END)

            # If the user types 'quit', close the client
            if message.lower() == 'quit':
                self.client_socket.close()
                self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()


#WilsonGay