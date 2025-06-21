import customtkinter as ctk
import socket
import threading
import json
from UI.modules.aspectRatioContainer import AspectRatioContainer
from UI.views.board import Board
import time

SERVER_HOST = 'localhost'
SERVER_PORT = 12345

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lobby Client")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER_HOST, SERVER_PORT))

        self.name_var = ctk.StringVar()
        self.join_code_var = ctk.StringVar()

        self.room_code_label = None
        self.players_frame = None

        self.build_start_screen()

        threading.Thread(target=self.listen_server, daemon=True).start()

    def build_start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.grid_rowconfigure(0, weight=1)   
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)  
        self.root.grid_rowconfigure(3, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)  

        ctk.CTkLabel(self.root, text="S U D O K U   M U L T I P L A Y E R",
                    font=("Arial", 24, "bold")).grid(row=1, column=0, pady=(20, 10), sticky="n")

        content = ctk.CTkFrame(self.root)
        content.grid(row=3, column=0, sticky="nsew", padx=80, pady=40)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        content.grid_rowconfigure(2, weight=1)
        content.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(content, text="Enter Your Name:").grid(row=0, column=0, sticky="nse", padx=(10, 5), pady=5)
        ctk.CTkEntry(content, textvariable=self.name_var).grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=5)
        ctk.CTkButton(content, text="Host", command=self.host_room, height=40).grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        ctk.CTkEntry(content, textvariable=self.join_code_var).grid(row=2, column=0, sticky="nsew", padx=(10, 5), pady=5)
        ctk.CTkButton(content, text="Join", command=self.join_room, height=40).grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=5)
        ctk.CTkButton(content, text="Leaderboard", command=self.request_global_leaderboard, height=40).grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=(10, 0))




    def host_room(self):
        name = self.name_var.get()
        if name:
            self.sock.send(f"HOST|{name}".encode())

    def join_room(self):
        name = self.name_var.get()
        code = self.join_code_var.get().upper()
        if name and code:
            self.sock.send(f"JOIN|{name}|{code}".encode())

    def build_lobby_screen(self, code):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.grid_rowconfigure((0, 1, 2), weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        self.room_code_label = ctk.CTkLabel(self.root, text=f"Room Code: {code}", font=("Arial", 20))
        self.room_code_label.grid(row=0, column=0, pady=10, sticky="nsew")

        copy_btn = ctk.CTkButton(self.root, text="Copy", width=60, command=lambda: self.copy_to_clipboard(code))
        copy_btn.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.players_frame = ctk.CTkFrame(self.root)
        self.players_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        for i in range(4):
            self.players_frame.grid_rowconfigure(i, weight=1)
        self.players_frame.grid_columnconfigure(0, weight=1)

        self.difficulty_var = ctk.StringVar(value="Easy")
        self.difficulty_dropdown = ctk.CTkOptionMenu(
            self.root, variable=self.difficulty_var, values=["Debug","Easy", "Medium", "Hard", "Expert"],
        )
        self.difficulty_dropdown.grid(row=2, column=1, pady=10, padx=(0, 10))
        self.difficulty_dropdown.grid_remove()

        self.start_button = ctk.CTkButton(self.root, text="Start Game", command=self.start_game)
        self.start_button.grid(row=2, column=0, pady=10)
        self.start_button.grid_remove()

    def copy_to_clipboard(self, code):
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        self.root.update()

    def get_host_name(self):
        for widget in self.players_frame.winfo_children():
            print(widget.cget("text"))
            return widget.cget("text")
        print("No host found")
        return ""

    def start_game(self):
        difficulty = self.difficulty_var.get()
        self.sock.send(f"START|{difficulty}".encode())

    def update_lobby(self, players):
        for widget in self.players_frame.winfo_children():
            widget.destroy()
        
        for i, name in enumerate(players):
            label = ctk.CTkLabel(self.players_frame, text=name, font=("Arial", 16))
            label.grid(row=i, column=0, pady=5, sticky="nsew")
        
        if players and self.name_var.get() == players[0]:
            self.start_button.grid()
            self.difficulty_dropdown.grid()
        else:
            self.start_button.grid_remove()
            self.difficulty_dropdown.grid_remove()

    def listen_server(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                if not msg:
                    break
                parts = msg.split("|")
                if parts[0] == "ROOMCODE":
                    self.root.after(0, self.build_lobby_screen, parts[1])
                elif parts[0] == "JOINED":
                    self.root.after(0, self.build_lobby_screen, parts[1])
                elif parts[0] == "LOBBY":
                    players = parts[1:]
                    self.root.after(0, self.update_lobby, players)
                elif parts[0] == "GAMEDATA":
                    game_data = json.loads(parts[1])
                    self.root.after(0, self.handle_game_start, game_data)
                elif parts[0] == "ERROR":
                    print("Error:", parts[1])
                elif parts[0] == "LEADERBOARD":
                    leaderboard_data = json.loads(parts[1])
                    self.root.after(0, self.show_leaderboard, leaderboard_data)
                elif parts[0] == "LEADERBOARD_TOP":
                    leaderboard_data = json.loads(parts[1])
                    self.root.after(0, self.show_global_leaderboard, leaderboard_data)
            except Exception as e:
                print("Error in listener:", e)
                break

    def handle_game_start(self, game_data):
        print("Game starting with data:", game_data)
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self.boardCont = AspectRatioContainer(self.root, 1/1, Board, on_solved=self.on_board_solved)
        self.boardCont.grid(column = 0, row = 0, rowspan=2, sticky="nsew", padx=10, pady=10)
        self.board = self.boardCont.get()
        self.board.set_board(json.loads(game_data["board"]))
        self.start_time = time.time()
        self.debug_fin = ctk.CTkButton(self.root, text="Finish Debug", command=self.on_board_solved)
        self.debug_fin.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
        

    def on_board_solved(self):
        self.solve_time = time.time() - self.start_time
        self.sock.send(f"SOLVED|{self.solve_time}".encode())
        self.show_waiting_screen()

    def show_waiting_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.root, text="Waiting for other players...", font=("Arial", 20))
        label.pack(expand=True)

    def show_leaderboard(self, leaderboard_data):
        for widget in self.root.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.root, text="Leaderboard", font=("Arial", 22)).pack(pady=10)
        for idx, entry in enumerate(leaderboard_data["leaderboard"], 1):
            name = entry["name"]
            t = entry["time"]
            ctk.CTkLabel(self.root, text=f"{idx}. {name} - {t:.2f} s", font=("Arial", 16)).pack()
        ctk.CTkButton(self.root, text="Back to Menu", command=self.build_start_screen).pack(pady=20)

    def show_global_leaderboard(self, leaderboard_data):
        for widget in self.root.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.root, text="Top 10 Players (Overall Score)", font=("Arial", 22)).pack(pady=10)
        for idx, entry in enumerate(leaderboard_data["top"], 1):
            name = entry["name"]
            score = entry["score"]
            ctk.CTkLabel(self.root, text=f"{idx}. {name} - {score:.2f}", font=("Arial", 16)).pack()
        ctk.CTkButton(self.root, text="Back to Menu", command=self.build_start_screen).pack(pady=20)

    def request_global_leaderboard(self):
        self.sock.send("LEADERBOARD".encode())

if __name__ == "__main__":
    ctk.set_default_color_theme("blue")
    ctk.set_appearance_mode("System")
    root = ctk.CTk()
    root.geometry("600x600")
    app = ClientApp(root)
    root.mainloop()
