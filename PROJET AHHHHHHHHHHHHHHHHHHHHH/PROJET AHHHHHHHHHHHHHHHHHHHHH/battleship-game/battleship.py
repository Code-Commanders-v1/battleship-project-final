import socket
import threading
import tkinter as tk
from tkinter import messagebox
from functools import partial

class BattleshipServer:
    def __init__(self, host="127.0.0.1", port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        print("Server started. Waiting for players...")
        self.clients = []
        self.boards = [None, None]  # Player boards
        self.turn = 0  # Player 1 starts
        self.LETTERS = 'ABCDEFGH'

    def handle_client(self, client, player_id):
        """Handle communication with a single client."""
        try:
            client.send(f"Welcome Player {player_id + 1}!".encode())
            client.send("Waiting for the other player...".encode())
            # Wait until both players are connected
            while len(self.clients) < 2:
                pass

            if player_id == 0:
                client.send("Your turn!".encode())
            else:
                client.send("Waiting for Player 1 to move...".encode())

            while True:
                try:
                    message = client.recv(1024).decode()
                    if message:
                        print(f"Player {player_id + 1}: {message}")
                        if message == "Game Over":
                            # Notify the other player that they have won
                            self.clients[1 - player_id].send("Game Over".encode())
                            print(f"Player {1 - player_id + 1} has won the game!")
                            break

                        # Relay the move to the other player
                        if self.turn == player_id:
                            self.turn = 1 - player_id  # Switch turns
                            self.clients[1 - player_id].send(message.encode())  # Send move to the other player
                            self.clients[1 - player_id].send("Your turn!".encode())  # Notify the other player
                            client.send("Waiting for the other player...".encode())  # Notify current player
                        else:
                            client.send("Not your turn!".encode())
                except Exception as e:
                    print(f"Error handling Player {player_id + 1}: {e}")
                    break
        except Exception as e:
            print(f"Player {player_id + 1} disconnected: {e}")
            if client in self.clients:
                self.clients.remove(client)
            # Notify the other player
            if len(self.clients) == 1:
                self.clients[0].send("The other player has disconnected. Game over.".encode())
            client.close()

    def start(self):
        """Start the server and accept connections."""
        while len(self.clients) < 2:
            client, addr = self.server.accept()
            print(f"Player {len(self.clients) + 1} connected from {addr}.")
            self.clients.append(client)
            client.send(f"You are Player {len(self.clients)}.".encode())
            threading.Thread(target=self.handle_client, args=(client, len(self.clients) - 1)).start()
        print("Both players connected. Starting the game!")
        self.clients[1].send("Waiting for Player 1 to move...".encode())
        self.clients[0].send("Your turn!".encode())

class BattleshipGame:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.root = tk.Tk()
        self.root.title("Battleship")
        self.BOARD_SIZE = 8
        self.LETTERS = 'ABCDEFGH'
        self.LENGTH_OF_SHIPS = [5, 4, 3, 3, 2]
        self.player_board = [[" " for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.enemy_board = [[" " for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.current_ship_index = 0
        self.current_orientation = "H"
        self.placing_ship = True
        self.player_turn = True

        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10)

        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)

        self.orientation_btn = tk.Button(control_frame, text="Orientation: Horizontal", command=self.toggle_orientation)
        self.orientation_btn.pack(side="left", padx=10)

        self.status_label = tk.Label(main_frame, text="Place your ships. Current ship: Size " + 
                                     str(self.LENGTH_OF_SHIPS[self.current_ship_index]), font=('Arial', 10))
        self.status_label.pack(pady=10)

        player_frame = tk.Frame(main_frame, bd=2, relief="groove")
        player_frame.pack(side="left", padx=10, pady=10)
        tk.Label(player_frame, text="Your Fleet", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=9)  # BOARD_SIZE (8) + 1
        self.player_cells = self.create_board(player_frame, self.handle_player_placement, is_player=True)

        enemy_frame = tk.Frame(main_frame, bd=2, relief="groove")
        enemy_frame.pack(side="left", padx=10, pady=10)
        tk.Label(enemy_frame, text="Enemy Waters", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=self.BOARD_SIZE + 1)
        self.enemy_cells = self.create_board(enemy_frame, self.handle_player_attack)

        # Start a thread to listen to the server
        threading.Thread(target=self.listen_to_server, daemon=True).start()

    def create_board(self, parent, click_handler, is_player=False):
        """Create a game board UI"""
        board = []
        # Add column labels (letters)
        for c in range(self.BOARD_SIZE):
            tk.Label(parent, text=self.LETTERS[c], font=('Arial', 10)).grid(row=1, column=c+1)
        
        for r in range(self.BOARD_SIZE):
            row_cells = []
            # Add row label (number)
            tk.Label(parent, text=str(r+1), font=('Arial', 10)).grid(row=r+2, column=0)
            
            for c in range(self.BOARD_SIZE):
                cell = tk.Button(parent, text=" ", width=3, height=1, 
                                bg="lightblue", relief="raised", font=('Arial', 10))
                cell.grid(row=r+2, column=c+1)
                cell.config(command=partial(click_handler, r, c))
                
                if is_player:
                    # Add hover effects for player board during placement
                    cell.bind("<Enter>", lambda e, r=r, c=c: self.on_cell_hover(r, c))
                    cell.bind("<Leave>", lambda e: self.on_cell_leave())
                
                row_cells.append(cell)
            board.append(row_cells)
        return board
    
    def on_cell_hover(self, row, col):
        """Highlight potential ship placement on hover"""
        if self.placing_ship and self.current_ship_index < len(self.LENGTH_OF_SHIPS):
            ship_length = self.LENGTH_OF_SHIPS[self.current_ship_index]
            if self.check_ship_fit(ship_length, row, col, self.current_orientation):
                if self.current_orientation == "H":
                    for c in range(col, min(col + ship_length, self.BOARD_SIZE)):
                        self.player_cells[row][c].config(bg="lightgreen")
                else:
                    for r in range(row, min(row + ship_length, self.BOARD_SIZE)):
                        self.player_cells[r][col].config(bg="lightgreen")
    
    def on_cell_leave(self):
        """Clear hover highlights"""
        if self.placing_ship:
            for r in range(self.BOARD_SIZE):
                for c in range(self.BOARD_SIZE):
                    if self.player_board[r][c] == " ":
                        self.player_cells[r][c].config(bg="lightblue")
                    else:
                        self.player_cells[r][c].config(bg="gray")
    
    def toggle_orientation(self):
        """Switch between horizontal and vertical ship placement"""
        self.current_orientation = "V" if self.current_orientation == "H" else "H"
        self.orientation_btn.config(text=f"Orientation: {'Horizontal' if self.current_orientation == 'H' else 'Vertical'}")
    
    def check_ship_fit(self, ship_length, row, column, orientation):
        """Check if ship fits at given location"""
        if orientation == "H":
            return column + ship_length <= self.BOARD_SIZE
        return row + ship_length <= self.BOARD_SIZE
    
    def ship_overlaps(self, board, row, column, orientation, ship_length):
        """Check if ship overlaps with existing ships"""
        if orientation == "H":
            return any(board[row][c] == "X" for c in range(column, column + ship_length))
        return any(board[r][column] == "X" for r in range(row, row + ship_length))
    
    def handle_player_placement(self, row, col):
        """Handle player's ship placement"""
        if not self.placing_ship:
            return
            
        ship_length = self.LENGTH_OF_SHIPS[self.current_ship_index]
        
        if (self.check_ship_fit(ship_length, row, col, self.current_orientation) and 
            not self.ship_overlaps(self.player_board, row, col, self.current_orientation, ship_length)):
            
            # Place the ship
            if self.current_orientation == "H":
                for c in range(col, col + ship_length):
                    self.player_board[row][c] = "X"
                    self.player_cells[row][c].config(bg="gray")
            else:
                for r in range(row, row + ship_length):
                    self.player_board[r][col] = "X"
                    self.player_cells[r][col].config(bg="gray")
            
            self.current_ship_index += 1
            
            if self.current_ship_index < len(self.LENGTH_OF_SHIPS):
                self.status_label.config(text=f"Place your ships. Current ship: Size {self.LENGTH_OF_SHIPS[self.current_ship_index]}")
            else:
                self.status_label.config(text="All ships placed! Attack the enemy waters!")
                self.placing_ship = False
    
    def handle_player_attack(self, row, col):
        """Send the player's move to the server."""
        if self.placing_ship or not self.player_turn:
            return
        self.send_move(row, col)
        self.player_turn = False
        self.status_label.config(text="Waiting for the other player...")
    
    def send_move(self, row, col):
        """Send the player's move to the server."""
        self.client.send(f"{row},{col}".encode())
    
    def listen_to_server(self):
        """Listen for messages from the server."""
        while True:
            try:
                message = self.client.recv(1024).decode()
                if message.startswith("Your turn!"):
                    self.player_turn = True
                    self.status_label.config(text="Your turn! Attack the enemy waters.")
                elif message.startswith("Waiting"):
                    self.player_turn = False
                    self.status_label.config(text="Waiting for the other player...")
                elif "," in message:  # Opponent's move
                    row, col = map(int, message.split(","))
                    self.handle_opponent_move(row, col)
                elif message.startswith("The other player has disconnected"):
                    messagebox.showinfo("Game Over", "The other player has disconnected. Game over.")
                    self.root.quit()
                elif message.startswith("Game Over"):
                    messagebox.showinfo("Game Over", "You have won the game!")
                    self.ask_restart()
            except Exception as e:
                print(f"Error in listen_to_server: {e}")
                break
    
    def handle_opponent_move(self, row, col):
        """Process the opponent's move."""
        if self.player_board[row][col] == "X":
            self.player_board[row][col] = "H"  # Mark as hit
            self.player_cells[row][col].config(bg="red", text="X")
            self.status_label.config(text="Your ship was hit!")
        else:
            self.player_board[row][col] = "M"  # Mark as miss
            self.player_cells[row][col].config(bg="white", text="•")
            self.status_label.config(text="Opponent missed!")

        # Check if all ships are sunk
        if self.count_hit_ships(self.player_board) == sum(self.LENGTH_OF_SHIPS):
            self.client.send("Game Over".encode())  # Notify the server
            messagebox.showinfo("Defeat", "All your ships have been sunk!")
            self.ask_restart()
    
    def count_hit_ships(self, board):
        """Count successful hits on ships"""
        return sum(1 for r in range(self.BOARD_SIZE) for c in range(self.BOARD_SIZE) if board[r][c] == "H")
    
    def ask_restart(self):
        """Prompt to restart the game"""
        if messagebox.askyesno("Game Over", "Would you like to play again?"):
            # Reset game state
            self.placing_ship = True
            self.current_ship_index = 0
            self.player_turn = True
            self.current_orientation = "H"
            self.orientation_btn.config(text="Orientation: Horizontal", state="normal")
            
            # Clear boards
            self.reset_boards()
            
            # Reset UI
            for r in range(self.BOARD_SIZE):
                for c in range(self.BOARD_SIZE):
                    self.player_cells[r][c].config(text=" ", bg="lightblue")
                    self.enemy_cells[r][c].config(text=" ", bg="lightblue", state="normal")
            
            # Update status
            self.status_label.config(text=f"Place your ships. Current ship: Size {self.LENGTH_OF_SHIPS[self.current_ship_index]}")
        else:
            self.root.quit()

if __name__ == "__main__":
    try:
        game = BattleshipGame(host="127.0.0.1", port=12345)
        game.root.mainloop()
    except tk.TclError as e:
        print("Error: Unable to initialize the GUI. Ensure you are running this script in a GUI-capable environment.")
        print(f"Details: {e}")