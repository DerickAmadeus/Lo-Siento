import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("UDP Chat Client")
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.server_ip = '192.168.56.1'
        self.port = 9998
        self.max_attempts = 3
        self.attempts = 0
        self.is_logged_in = False

        # GUI Elements
        self.setup_widgets()

    def setup_widgets(self):
        # Server IP Entry
        tk.Label(self.master, text="Server IP Address:").pack()
        self.ip_entry = tk.Entry(self.master)
        self.ip_entry.insert(0, self.server_ip)
        self.ip_entry.pack()

        # Port Entry
        tk.Label(self.master, text="Server Port:").pack()
        self.port_entry = tk.Entry(self.master)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.pack()

        # Password Entry
        tk.Label(self.master, text="Enter Server Password:").pack()
        self.password_entry = tk.Entry(self.master, show='*')
        self.password_entry.pack()
        
        self.login_button = tk.Button(self.master, text="Login", command=self.login)
        self.login_button.pack()

        # Chat Window
        self.chat_area = scrolledtext.ScrolledText(self.master, state='disabled', width=50, height=15)
        self.chat_area.pack()

        self.message_entry = tk.Entry(self.master, state='disabled')
        self.message_entry.pack()
        self.message_entry.bind("<Return>", self.send_message)

    def login(self):
        self.server_ip = self.ip_entry.get().strip() or self.server_ip
        self.port = int(self.port_entry.get().strip() or self.port)

        password = self.password_entry.get().strip()
        
        # Send password to the server
        self.client_socket.sendto(f"PASS:{password}".encode('utf-8'), (self.server_ip, self.port))

        try:
            pass_response, _ = self.client_socket.recvfrom(1024)
            if pass_response.decode('utf-8') == "PASS_OK":
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, "Password accepted! You have joined the chat.\n")
                self.chat_area.config(state='disabled')
                self.password_entry.config(state='disabled')
                self.login_button.config(state='disabled')
                self.is_logged_in = True

                # Start the name input and validation process
                self.prompt_for_name()

                # Start the message receiving thread
                threading.Thread(target=self.receive_messages, daemon=True).start()
            else:
                self.attempts += 1
                if self.attempts >= self.max_attempts:
                    messagebox.showerror("Error", "Maximum attempts reached! Connection closed.")
                    self.master.quit()
                else:
                    messagebox.showerror("Error", "Incorrect password! Please try again.")
        except socket.timeout:
            messagebox.showerror("Error", "No response from the server. Please check the server connection.")
            return

    def prompt_for_name(self):
        """Prompt the user for a name and check if it is taken."""
        while True:
            self.name = simpledialog.askstring("Name", "Enter your name:")
            if not self.name:
                messagebox.showerror("Error", "You must enter a name to join the chat.")
                continue

            # Send the name to the server for validation
            self.client_socket.sendto(self.name.encode('utf-8'), (self.server_ip, self.port))

            # Wait for the server's response
            try:
                name_response, _ = self.client_socket.recvfrom(1024)
                if name_response.decode('utf-8') == "NAME_TAKEN":
                    messagebox.showerror("Error", "Name already taken! Please choose a different name.")
                else:
                    # Name is accepted, enable the message entry field and break the loop
                    self.message_entry.config(state='normal')
                    break
            except socket.error:
                messagebox.showerror("Error", "Error communicating with the server.")
                return

    def receive_messages(self):
        while True:
            try:
                message, _ = self.client_socket.recvfrom(1024)
                message = message.decode('utf-8')
                if message:
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, message + "\n")
                    self.chat_area.config(state='disabled')
                    self.chat_area.see(tk.END)
                else:
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, "Connection closed by the server.\n")
                    self.chat_area.config(state='disabled')
                    break
            except socket.error:
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, "Error receiving message.\n")
                self.chat_area.config(state='disabled')
                break

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            if message.lower() == 'quit':
                self.client_socket.sendto('quit'.encode('utf-8'), (self.server_ip, self.port))
                self.master.quit()
            else:
                self.client_socket.sendto(message.encode('utf-8'), (self.server_ip, self.port))
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, f"You: {message}\n")
                self.chat_area.config(state='disabled')
                self.chat_area.see(tk.END)
            self.message_entry.delete(0, tk.END)

    def close_connection(self):
        self.client_socket.close()
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    chat_client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", chat_client.close_connection)  # Handle window close
    root.mainloop()
