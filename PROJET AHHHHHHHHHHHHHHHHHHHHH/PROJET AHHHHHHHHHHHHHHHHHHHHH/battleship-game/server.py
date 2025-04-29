import socket
import threading

class BattleshipServer:
    def __init__(self, host="127.0.0.1", port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        print("Server started. Waiting for players...")
        self.clients = []
        self.boards = [None, None]  # Player boards
        self.turn = 0  # Player 1 starts

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
        # Notify both players that the game is starting
        self.clients[0].send("Your turn!".encode())
        self.clients[1].send("Waiting for Player 1 to move...".encode())

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

if __name__ == "__main__":
    server = BattleshipServer()
    server.start()