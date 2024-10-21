import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Listbox

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("Chat Client")

        # Create a text area for displaying messages
        self.text_area = scrolledtext.ScrolledText(master, state='disabled', wrap='word')
        self.text_area.grid(row=0, column=0, columnspan=2)

        # Create a listbox to display usernames
        self.user_list = Listbox(master, height=10, width=30)
        self.user_list.grid(row=0, column=2, sticky='ns')

        # Create an entry box for user input
        self.message_entry = tk.Entry(master)
        self.message_entry.grid(row=1, column=0, sticky='ew')
        self.message_entry.bind("<Return>", self.send_message)  # Send message on Enter key

        # Create a send button
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1)

        # Create a socket object
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("192.168.56.1", 9998))  # Replace with your server's IP

        # Get the username
        self.username = self.get_username()
        self.client_socket.send(self.username.encode('utf-8'))  # Send the username to the server

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True  # Ensure thread exits when main program does
        self.receive_thread.start()

    def get_username(self):
        # Prompt for the username
        username_window = tk.Toplevel(self.master)
        username_window.title("Enter Username")

        tk.Label(username_window, text="Enter your username:").pack(pady=10)
        username_entry = tk.Entry(username_window)
        username_entry.pack(pady=5)

        def submit_username():
            self.username = username_entry.get()
            username_window.destroy()

        tk.Button(username_window, text="Submit", command=submit_username).pack(pady=10)
        username_window.transient(self.master)  # Make it a modal window
        username_window.grab_set()  # Prevent interaction with other windows until this is closed
        self.master.wait_window(username_window)  # Wait for the username window to close
        return self.username

    def receive_messages(self):
        while True:
            try:
                msg = self.client_socket.recv(1024).decode('utf-8')
                if msg:
                    # Update the text area with the received message
                    self.text_area.configure(state='normal')
                    self.text_area.insert(tk.END, msg + "\n")
                    self.text_area.configure(state='disabled')
            except Exception as e:
                print("Error receiving message:", e)
                break

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            self.text_area.configure(state='normal')
            self.text_area.insert(tk.END, f"{self.username}: {message}\n")
            self.text_area.configure(state='disabled')
            self.client_socket.send(message.encode('utf-8'))  # Send the message to the server
            self.message_entry.delete(0, tk.END)  # Clear the input field

if __name__ == "__main__":
    root = tk.Tk()
    chat_client = ChatClient(root)
    root.mainloop()
