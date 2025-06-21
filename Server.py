
import socket
import threading
import uuid
import datetime
import json
import algorithms
import sqlite3

HOST = 'localhost'
PORT = 12345

rooms = {}
names = {}
solve_times = {} 

def init_db():
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            name TEXT PRIMARY KEY,
            score REAL
        )
    """)
    conn.commit()
    conn.close()

def update_player_score(name, add_score):
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("SELECT score FROM scores WHERE name = ?", (name,))
    row = c.fetchone()
    if row:
        new_score = row[0] + add_score
        c.execute("UPDATE scores SET score = ? WHERE name = ?", (new_score, name))
    else:
        c.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, add_score))
    conn.commit()
    conn.close()

def handle_client(conn, addr):
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            parts = data.split("|")
            if parts[0] == "HOST":
                name = parts[1]
                code = str(uuid.uuid4())[:6].upper()
                rooms[code] = [conn]
                names[conn] = name
                conn.send(f"ROOMCODE|{code}".encode())
                broadcast_lobby(code)
            elif parts[0] == "JOIN":
                name, code = parts[1], parts[2]
                if code in rooms and len(rooms[code]) < 4:
                    rooms[code].append(conn)
                    names[conn] = name
                    conn.send(f"JOINED|{code}".encode())
                    broadcast_lobby(code)
                else:
                    conn.send("ERROR|Room full or not found".encode())
            elif parts[0] == "START":
                room_code = None
                for code, clients in rooms.items():
                    if conn in clients and clients[0] == conn:
                        room_code = code
                        break
                
                if room_code:
                    solve_times[room_code] = {} 
                    difficulty = parts[1] if len(parts) > 1 else "Easy"
                    difficulty = difficulty.lower()
                    print(f"Starting game in room {room_code} with difficulty {difficulty}")
                    game_data = {
                        "status": "game_start",
                        "players": [names[c] for c in rooms[room_code]],
                        "timestamp": str(datetime.datetime.now()),
                        "board": json.dumps(algorithms.SudokuGenerator(difficulty).generate()[0]),
                        "difficulty": difficulty
                    }
                    for client in rooms[room_code]:
                        try:
                            client.send(f"GAMEDATA|{json.dumps(game_data)}".encode())
                        except:
                            disconnect_client(client)
            elif parts[0] == "LEADERBOARD":
                conn_db = sqlite3.connect("scores.db")
                c = conn_db.cursor()
                c.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
                top = [{"name": row[0], "score": row[1]} for row in c.fetchall()]
                conn_db.close()
                leaderboard_data = {"top": top}
                try:
                    conn.send(f"LEADERBOARD_TOP|{json.dumps(leaderboard_data)}".encode())
                except:
                    disconnect_client(conn)
            elif parts[0] == "SOLVED":
                finish_time = float(parts[1])
                room_code = None
                for code, clients in rooms.items():
                    if conn in clients:
                        room_code = code
                        break
                if room_code:
                    name = names[conn]
                    if room_code not in solve_times:
                        solve_times[room_code] = {}
                    solve_times[room_code][name] = finish_time
                    if len(solve_times[room_code]) == len(rooms[room_code]):
                        leaderboard = sorted(
                            solve_times[room_code].items(),
                            key=lambda x: x[1]
                        )
                        leaderboard_data = {
                            "leaderboard": [
                                {"name": n, "time": t}
                                for n, t in leaderboard
                            ]
                        }
                        for client in rooms[room_code]:
                            try:
                                client.send(f"LEADERBOARD|{json.dumps(leaderboard_data)}".encode())
                            except:
                                disconnect_client(client)

                        difficulty = "easy"
                        if "board" in game_data and "difficulty" in game_data:
                            difficulty = game_data["difficulty"].lower()
                        elif "difficulty" in game_data:
                            difficulty = game_data["difficulty"].lower()
                        else:
                            difficulty = "easy"
                        diff_mod = {"easy": 100, "medium": 300, "hard": 500, "expert": 1000}
                        modifier = diff_mod.get(difficulty, 100)
                        for name, t in leaderboard:
                            update_player_score(name, t * modifier)

                        for client in rooms[room_code]:
                            if client in names:
                                del names[client]
                        del rooms[room_code]
                        if room_code in solve_times:
                            del solve_times[room_code]
    except:
        disconnect_client(conn)

def broadcast_lobby(code):
    players = [names[c] for c in rooms[code]]
    msg = "LOBBY|" + "|".join(players)
    for client in rooms[code]:
        try:
            client.send(msg.encode())
        except:
            disconnect_client(client)

def disconnect_client(conn):
    for code, clients in list(rooms.items()):
        if conn in clients:
            clients.remove(conn)
            if not clients:
                del rooms[code]
            else:
                broadcast_lobby(code)
    if conn in names:
        del names[conn]
    conn.close()

def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Master Server running on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
