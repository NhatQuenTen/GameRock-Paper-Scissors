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