# Rock-Paper-Scissors Game with Socket Programming

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import socket
import threading
import json
import time
import random
from PIL import Image, ImageTk
import io
import base64

class ModernButton(tk.Button):
    """Custom modern button with hover effects"""
    def __init__(self, parent, text="", command=None, bg_color="#4a90e2", hover_color="#357abd", **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        self.config(
            bg=bg_color,
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        self.config(bg=self.hover_color)
    
    def on_leave(self, e):
        self.config(bg=self.bg_color)

class RPSGameGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 Rock Paper Scissors - Multiplayer")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        
        # Center window on screen
        self.center_window()
        
        # Game state variables
        self.game_state = "menu"  # menu, connecting, waiting, playing, result
        self.player_name = ""
        self.server_host = "localhost"
        self.server_port = 12345
        self.is_server = False
        self.socket = None
        self.server_socket = None
        
        # Game data
        self.opponent_name = ""
        self.player_score = 0
        self.opponent_score = 0
        self.player_move = None
        self.opponent_move = None
        self.last_result = None
        
        # GUI frames
        self.current_frame = None
        
        # Create main menu
        self.show_main_menu()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
    
    def clear_frame(self):
        """Clear current frame"""
        if self.current_frame:
            self.current_frame.destroy()
    
    def create_title_label(self, parent, text, size=24):
        """Create styled title label"""
        return tk.Label(
            parent,
            text=text,
            font=("Arial", size, "bold"),
            fg="#ffffff",
            bg="#1a1a2e"
        )
    
    def create_subtitle_label(self, parent, text, size=12):
        """Create styled subtitle label"""
        return tk.Label(
            parent,
            text=text,
            font=("Arial", size),
            fg="#a0a0a0",
            bg="#1a1a2e"
        )
    
    def create_styled_entry(self, parent, placeholder="", width=30):
        """Create styled entry widget"""
        entry = tk.Entry(
            parent,
            font=("Arial", 12),
            bg="#2d2d44",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=5,
            width=width
        )
        
        # Add placeholder functionality
        if placeholder:
            entry.insert(0, placeholder)
            entry.bind('<FocusIn>', lambda e: self.on_entry_focus_in(e, placeholder))
            entry.bind('<FocusOut>', lambda e: self.on_entry_focus_out(e, placeholder))
            entry.config(fg="#888888")
        
        return entry
    
    def on_entry_focus_in(self, event, placeholder):
        """Handle entry focus in"""
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(fg="white")
    
    def on_entry_focus_out(self, event, placeholder):
        """Handle entry focus out"""
        if event.widget.get() == "":
            event.widget.insert(0, placeholder)
            event.widget.config(fg="#888888")
    
    def show_main_menu(self):
        """Display main menu"""
        self.clear_frame()
        self.game_state = "menu"
        
        self.current_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.current_frame.pack(expand=True, fill="both")
        
        # Title section
        title_frame = tk.Frame(self.current_frame, bg="#1a1a2e")
        title_frame.pack(pady=(50, 30))
        
        # Game title
        title = self.create_title_label(title_frame, "🎮 ROCK PAPER SCISSORS", 28)
        title.pack()
        
        subtitle = self.create_subtitle_label(title_frame, "Multiplayer Battle Arena", 14)
        subtitle.pack(pady=(5, 0))
        
        # Input section
        input_frame = tk.Frame(self.current_frame, bg="#1a1a2e")
        input_frame.pack(pady=20)
        
        # Player name input
        name_label = self.create_subtitle_label(input_frame, "Enter your name:", 12)
        name_label.pack()
        
        self.name_entry = self.create_styled_entry(input_frame, "Player Name")
        self.name_entry.pack(pady=(5, 15))
        
        # Server connection inputs
        connection_frame = tk.Frame(input_frame, bg="#1a1a2e")
        connection_frame.pack()
        
        server_label = self.create_subtitle_label(connection_frame, "Server Connection:", 12)
        server_label.pack()
        
        # Host and port in same row
        host_port_frame = tk.Frame(connection_frame, bg="#1a1a2e")
        host_port_frame.pack(pady=(5, 0))
        
        self.host_entry = self.create_styled_entry(host_port_frame, "localhost", 20)
        self.host_entry.pack(side="left", padx=(0, 5))
        
        self.port_entry = self.create_styled_entry(host_port_frame, "12345", 10)
        self.port_entry.pack(side="left")
        
        # Buttons section
        button_frame = tk.Frame(self.current_frame, bg="#1a1a2e")
        button_frame.pack(pady=40)
        
        # Server button
        server_btn = ModernButton(
            button_frame,
            text="🖥️ START SERVER",
            command=self.start_server,
            bg_color="#27ae60",
            hover_color="#2ecc71"
        )
        server_btn.pack(pady=5, ipadx=20)
        
        # Client button
        client_btn = ModernButton(
            button_frame,
            text="🔗 JOIN GAME",
            command=self.join_game,
            bg_color="#3498db",
            hover_color="#5dade2"
        )
        client_btn.pack(pady=5, ipadx=20)
        
        # Status label
        self.status_label = self.create_subtitle_label(self.current_frame, "", 10)
        self.status_label.pack(pady=(20, 0))
    
    def get_entry_value(self, entry, placeholder):
        """Get actual value from entry (not placeholder)"""
        value = entry.get()
        return "" if value == placeholder else value
    
    def start_server(self):
        """Start game server"""
        name = self.get_entry_value(self.name_entry, "Player Name")
        if not name:
            messagebox.showerror("Error", "Please enter your name!")
            return
        
        self.player_name = name
        self.is_server = True
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.server_port))
            self.server_socket.listen(1)
            
            # Start server thread
            server_thread = threading.Thread(target=self.server_listen, daemon=True)
            server_thread.start()
            
            self.show_waiting_screen("Server started! Waiting for players...")
            
        except Exception as e:
            messagebox.showerror("Server Error", f"Could not start server: {e}")
    
    def join_game(self):
        
        name = self.get_entry_value(self.name_entry, "Player Name")
        host = self.get_entry_value(self.host_entry, "localhost")
        port = self.get_entry_value(self.port_entry, "12345")
        
        if not name:
            messagebox.showerror("Error", "Please enter your name!")
            return
        
        self.player_name = name
        self.server_host = host if host else "localhost"
        
        try:
            self.server_port = int(port) if port else 12345
        except ValueError:
            messagebox.showerror("Error", "Invalid port number!")
            return
        
        self.show_connecting_screen()
        
        # Connect in separate thread
        connect_thread = threading.Thread(target=self.connect_to_server, daemon=True)
        connect_thread.start()
    
    def server_listen(self):
        
        try:
            client_socket, address = self.server_socket.accept()
            self.socket = client_socket
            
            # Receive opponent name
            data = self.socket.recv(1024).decode('utf-8')
            msg = json.loads(data)
            if msg['type'] == 'join':
                self.opponent_name = msg['data']['name']
                
                # Send acknowledgment
                response = {"type": "game_start", "data": {"opponent": self.player_name}}
                self.socket.send(json.dumps(response).encode('utf-8'))
                
                # Start game
                self.root.after(0, self.show_game_screen)
                
                # Start message handler
                msg_thread = threading.Thread(target=self.handle_messages, daemon=True)
                msg_thread.start()
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Server Error", f"Connection error: {e}"))
    
    def connect_to_server(self):
       
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            # Send join message
            join_msg = {"type": "join", "data": {"name": self.player_name}}
            self.socket.send(json.dumps(join_msg).encode('utf-8'))
            
            # Wait for game start
            data = self.socket.recv(1024).decode('utf-8')
            msg = json.loads(data)
            if msg['type'] == 'game_start':
                self.opponent_name = msg['data']['opponent']
                self.root.after(0, self.show_game_screen)
                
                # Start message handler
                msg_thread = threading.Thread(target=self.handle_messages, daemon=True)
                msg_thread.start()
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Connection Error", f"Could not connect: {e}"))
            self.root.after(0, self.show_main_menu)
    
    def handle_messages(self):
       
        while True:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                msg = json.loads(data)
                if msg['type'] == 'move':
                    self.opponent_move = msg['data']['move']
                    self.root.after(0, self.process_round)
                elif msg['type'] == 'result':
                    self.handle_result(msg['data'])
                
            except Exception as e:
                print(f"Message handling error: {e}")
                break
    
    def show_connecting_screen(self):
        
        self.clear_frame()
        self.game_state = "connecting"
        
        self.current_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.current_frame.pack(expand=True, fill="both")
        
        # Connecting animation
        title = self.create_title_label(self.current_frame, "🔗 CONNECTING...", 24)
        title.pack(pady=(150, 20))
        
        subtitle = self.create_subtitle_label(self.current_frame, f"Connecting to {self.server_host}:{self.server_port}", 12)
        subtitle.pack()
        
        # Cancel button
        cancel_btn = ModernButton(
            self.current_frame,
            text="Cancel",
            command=self.show_main_menu,
            bg_color="#e74c3c",
            hover_color="#c0392b"
        )
        cancel_btn.pack(pady=30)
        
        # Animate dots
        self.animate_dots(title, "🔗 CONNECTING")
    
    def show_waiting_screen(self, message):
        
        self.clear_frame()
        self.game_state = "waiting"
        
        self.current_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.current_frame.pack(expand=True, fill="both")
        
        title = self.create_title_label(self.current_frame, "⏳ WAITING...", 24)
        title.pack(pady=(150, 20))
        
        subtitle = self.create_subtitle_label(self.current_frame, message, 12)
        subtitle.pack()
        
        # Cancel button
        cancel_btn = ModernButton(
            self.current_frame,
            text="Cancel",
            command=self.show_main_menu,
            bg_color="#e74c3c",
            hover_color="#c0392b"
        )
        cancel_btn.pack(pady=30)
        
        # Animate dots
        self.animate_dots(title, "⏳ WAITING")
    
    