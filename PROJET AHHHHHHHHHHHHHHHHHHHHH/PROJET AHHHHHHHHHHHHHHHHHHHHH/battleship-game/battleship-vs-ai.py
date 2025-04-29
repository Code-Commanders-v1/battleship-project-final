import random
import tkinter as tk
from tkinter import messagebox
from functools import partial
from stable_baselines3 import DQN

# Load the trained model
model = DQN.load("battleship_dqn")

# Use the model to predict the AI's moves
def get_ai_move(observation):
    action, _states = model.predict(observation)
    return divmod(action, 8)  # Convert action to (row, col)

class BattleshipGame:
    def __init__(self):
        # Constants
        self.LENGTH_OF_SHIPS = [2, 3, 3, 4, 5]
        self.BOARD_SIZE = 8
        self.LETTERS = 'ABCDEFGH'
        
        # Game state
        self.placing_ship = True
        self.current_ship_index = 0
        self.current_orientation = "H"  # Default horizontal placement
        self.player_turn = True
        self.difficulty = "medium"  # easy, medium, hard
        
        # Initialize boards
        self.reset_boards()
        
        # UI Setup
        self.root = tk.Tk()
        self.root.title("Battleship")
        self.setup_ui()
        
        # Place computer ships
        self.place_ships(self.computer_board)
        
    def reset_boards(self):
        """Initialize all game boards"""
        self.player_board = [[" " for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.computer_board = [[" " for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.player_guess_board = [[" " for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.computer_guess_board = [[" " for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
    
    def setup_ui(self):
        """Create the game interface"""
        # Main frames
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=20)
        
        # Control frame
        control_frame = tk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Orientation toggle button
        self.orientation_btn = tk.Button(control_frame, text="Orientation: Horizontal", 
                                       command=self.toggle_orientation)
        self.orientation_btn.pack(side=tk.LEFT, padx=5)
        
        # Difficulty selector
        difficulty_frame = tk.Frame(control_frame)
        difficulty_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(difficulty_frame, text="Difficulty:").pack()
        self.difficulty_var = tk.StringVar(value=self.difficulty)
        tk.OptionMenu(difficulty_frame, self.difficulty_var, "easy", "medium", "hard", 
                     command=self.set_difficulty).pack()
        
        # Player board frame
        player_frame = tk.Frame(main_frame, bd=2, relief="groove")
        player_frame.grid(row=1, column=0, padx=20, pady=10)
        tk.Label(player_frame, text="Your Fleet", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=9)  # BOARD_SIZE (8) + 1
        
        # Computer board frame
        computer_frame = tk.Frame(main_frame, bd=2, relief="groove")
        computer_frame.grid(row=1, column=1, padx=20, pady=10)
        tk.Label(computer_frame, text="Enemy Waters", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=self.BOARD_SIZE + 1)
        
        # Create boards
        self.player_cells = self.create_board(player_frame, self.handle_player_placement, is_player=True)
        self.computer_cells = self.create_board(computer_frame, self.handle_player_attack)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Place your ships. Current ship: Size " + 
                                    str(self.LENGTH_OF_SHIPS[self.current_ship_index]), font=('Arial', 10))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Disable computer board until ship placement is done
        self.set_computer_board_state(False)
    
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
    
    def set_difficulty(self, level):
        """Set computer difficulty level"""
        self.difficulty = level
    
    def set_computer_board_state(self, active):
        """Enable/disable computer board buttons"""
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                state = "normal" if active else "disabled"
                self.computer_cells[r][c].config(state=state)
    
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
    
    def place_ships(self, board, is_player=False):
        """Place ships randomly for computer"""
        for ship_length in self.LENGTH_OF_SHIPS:
            placed = False
            while not placed:
                orientation = random.choice(["H", "V"])
                row = random.randint(0, self.BOARD_SIZE - 1)
                column = random.randint(0, self.BOARD_SIZE - 1)
                
                if (self.check_ship_fit(ship_length, row, column, orientation) and 
                    not self.ship_overlaps(board, row, column, orientation, ship_length)):
                    
                    if orientation == "H":
                        for c in range(column, column + ship_length):
                            board[row][c] = "X"
                    else:
                        for r in range(row, row + ship_length):
                            board[r][column] = "X"
                    placed = True
    
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
                self.set_computer_board_state(True)
                self.orientation_btn.config(state="disabled")
                messagebox.showinfo("Ready", "All ships placed! Now attack the computer's board!")
    
    def handle_player_attack(self, row, col):
        """Handle player's attack on computer's board"""
        if self.placing_ship or not self.player_turn:
            return
            
        if self.player_guess_board[row][col] != " ":
            return
            
        # Record the attack
        if self.computer_board[row][col] == "X":
            self.player_guess_board[row][col] = "X"
            self.computer_cells[row][col].config(bg="red", text="X")
            self.status_label.config(text="Hit!")
            
            if self.is_ship_sunk(self.computer_board, self.player_guess_board, row, col):
                self.status_label.config(text="Hit! You sunk a ship!")
        else:
            self.player_guess_board[row][col] = "-"
            self.computer_cells[row][col].config(bg="white", text="•")
            self.status_label.config(text="Miss!")
        
        self.player_turn = False
        
        # Check for win
        if self.count_hit_ships(self.player_guess_board, self.computer_board) == sum(self.LENGTH_OF_SHIPS):
            messagebox.showinfo("Victory!", "Congratulations! You sunk all enemy ships!")
            self.ask_restart()
        else:
            self.root.after(1000, self.computer_turn)
    
    def computer_turn(self):
        """Handle computer's attack with difficulty-based strategy"""
        row, col = self.get_computer_target()
        
        # Record the attack
        if self.player_board[row][col] == "X":
            self.computer_guess_board[row][col] = "X"
            self.player_cells[row][col].config(bg="red", text="X")
            self.status_label.config(text="Enemy hit your ship!")
            
            if self.is_ship_sunk(self.player_board, self.computer_guess_board, row, col):
                self.status_label.config(text="Enemy sunk your ship!")
        else:
            self.computer_guess_board[row][col] = "-"
            self.player_cells[row][col].config(bg="white", text="•")
            self.status_label.config(text="Enemy missed!")
        
        self.player_turn = True
        
        # Check for win
        if self.count_hit_ships(self.computer_guess_board, self.player_board) == sum(self.LENGTH_OF_SHIPS):
            messagebox.showinfo("Defeat", "All your ships have been sunk!")
            self.ask_restart()
    
    def get_computer_target(self):
        """Get computer's target based on difficulty"""
        # First look for hits that haven't been fully explored
        target = self.find_next_target()
        
        if target:
            return target
        
        # If no target found, make random guess with difficulty adjustments
        if self.difficulty == "easy":
            return self.random_target()
        elif self.difficulty == "medium":
            return self.smart_random_target()
        else:  # hard
            return self.strategic_target()
    
    def find_next_target(self):
        """Look for adjacent cells to existing hits"""
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                if self.computer_guess_board[r][c] == "X":
                    # Check adjacent cells
                    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nr, nc = r + dr, c + dc
                        if (0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and 
                            self.computer_guess_board[nr][nc] == " "):
                            return nr, nc
        return None
    
    def random_target(self):
        """Completely random targeting"""
        row, col = random.randint(0, self.BOARD_SIZE - 1), random.randint(0, self.BOARD_SIZE - 1)
        while self.computer_guess_board[row][col] != " ":
            row, col = random.randint(0, self.BOARD_SIZE - 1), random.randint(0, self.BOARD_SIZE - 1)
        return row, col
    
    def smart_random_target(self):
        """Random but with checkerboard pattern (more efficient)"""
        while True:
            row = random.randint(0, self.BOARD_SIZE - 1)
            col = random.randint(0, self.BOARD_SIZE - 1)
            if (row + col) % 2 == 0 and self.computer_guess_board[row][col] == " ":
                return row, col
            elif self.computer_guess_board[row][col] == " ":
                # Occasionally check other cells
                if random.random() < 0.2:
                    return row, col
    
    def strategic_target(self):
        """More advanced targeting strategy"""
        # First try checkerboard pattern
        target = self.smart_random_target()
        if target:
            return target
        
        # If no checkerboard cells left, pick any remaining
        return self.random_target()
    
    def is_ship_sunk(self, board, guess_board, row, col):
        """Check if a hit belongs to a sunk ship"""
        # Check horizontal
        left = col
        while left >= 0 and board[row][left] == "X":
            left -= 1
        left += 1
        
        right = col
        while right < self.BOARD_SIZE and board[row][right] == "X":
            right += 1
        right -= 1
        
        horizontal_sunk = all(guess_board[row][c] == "X" for c in range(left, right + 1))
        
        # Check vertical
        top = row
        while top >= 0 and board[top][col] == "X":
            top -= 1
        top += 1
        
        bottom = row
        while bottom < self.BOARD_SIZE and board[bottom][col] == "X":
            bottom += 1
        bottom -= 1
        
        vertical_sunk = all(guess_board[r][col] == "X" for r in range(top, bottom + 1))
        
        return horizontal_sunk or vertical_sunk
    
    def count_hit_ships(self, guess_board, opponent_board):
        """Count successful hits on ships"""
        return sum(1 for r in range(self.BOARD_SIZE) for c in range(self.BOARD_SIZE)
                   if guess_board[r][c] == "X" and opponent_board[r][c] == "X")
    
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
                    self.computer_cells[r][c].config(text=" ", bg="lightblue", state="disabled")
            
            # Place new computer ships
            self.place_ships(self.computer_board)
            
            # Update status
            self.status_label.config(text=f"Place your ships. Current ship: Size {self.LENGTH_OF_SHIPS[self.current_ship_index]}")
        else:
            self.root.quit()

if __name__ == "__main__":
    try:
        game = BattleshipGame()
        game.root.mainloop()
    except tk.TclError as e:
        print("Error: Unable to initialize the GUI. Ensure you are running this script in a GUI-capable environment.")
        print(f"Details: {e}")