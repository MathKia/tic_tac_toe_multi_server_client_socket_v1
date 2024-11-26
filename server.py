import json #to send dict structured msgs = json dumps
import socket #to do socket communication
from constants import RESET, BLUE, PINK #color constants imported from constants.py
from constants import ALLOWED, PRINT, TURN, GAME_OVER #msg subject constants imported from constants.py

#mark constants = colored player marking
X = f'{BLUE}X{RESET}'
O = f'{PINK}O{RESET}'


class TicTacToeServer:
    """
    This python file is now separating the server from the clients
    the server will be responsible for:
        - creating a server socket to host the game session
        - clients will connect to this host through [HOST IP, PORT]
        - server will allow max 2 clients to connect to a session
        - server will broadcast certain messages to all clients
        - server will send specific message to 1 client depending on client being current player
        - server will update the game grid with the played moves and update allowed list to remove played moves
        - server will check if there is a winner or draw and will end game session
    """

    def __init__(self, HOST, PORT): #initalize the server  + game attributes
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #server socket w INET + TCP
        print("Socket created successfully for host.")
        self.server.bind((HOST, PORT)) #bind server to provide ip add + port
        print(f"Socket bound to {HOST}:{PORT}")
        self.server.listen(2) #server listen for 2 client connections to then start game sesh
        print("Server listening for connections...")

        self.clients = [] #attr = store client connections
        self.turn = None #attr = alternate user turn
        self.allowed_moves = [1, 2, 3, 4, 5, 6, 7, 8, 9] #attr = allowed moves to be played, gets updated after each play
        self.block_dict = {
            1: "1",
            2: "2",
            3: "3",
            4: "4",
            5: "5",
            6: "6",
            7: "7",
            8: "8",
            9: "9"
        } #attr = to update the grid with markings
        self.counter = 0 #attr = tracks game round and when to change turn
        self.game_on = True #attr = keeps game loop going till false
        self.current_player = None #attr = tracks which player client turn it is
        self.non_current_player = None #attr =  tracks which player client turn it isnt
        self.message = {'subject': None, 'data': None} #attr =  message structure for json load/dump, subject = specific content --> specific actions

        self.accept_connections() #run meth = get 2 clients

        self.game_loop() #run meth = game sesh after 2 clients joined

    def accept_connections(self): #meth =  server accepts 2 client connections, + to clients list
        while len(self.clients) < 2:
            connection, addr = self.server.accept()
            self.clients.append(connection)
            print(f"Client {addr} has connected")

        self.send_msg(PRINT, f"You are {X}", self.clients[0]) #self.clients[0] = first client to join server  will always be X
        self.send_msg(PRINT, f"You are {O}", self.clients[1]) #self.clients[1] = second client to join server  will always be O

        print("Two players have joined the game.")

    def broadcast(self, subject, msg): #meth = broadcast a message to all player clients in self.clients[] (2 players)
        for c in self.clients:
            self.send_msg(subject, msg, c)

    def send_msg(self, subject, msg, c): #meth = send message to a specific client
        self.message['subject'] = subject #subject = topic/heading of what the msg is for specific action from reciever
        self.message['data'] = msg #msg = actual content/data of msg for reciever
        json_msg = json.dumps(self.message) + "\n" #json dumps to send structured dict msg over socket, "\n" to seperate multiple messages sent in 1 go
        c.send(json_msg.encode('utf-8')) #socket library server send msg meth

    def grid_board(self): #meth = calls to update grid board string format and return for print
        grid = (f"{self.block_dict[1]} | {self.block_dict[2]} | {self.block_dict[3]}\n"
                f"_________\n"
                f"{self.block_dict[4]} | {self.block_dict[5]} | {self.block_dict[6]}\n"
                f"_________\n"
                f"{self.block_dict[7]} | {self.block_dict[8]} | {self.block_dict[9]}\n")
        return grid

    def make_move(self, move, player): #meth = makes the players move, update block dict of markings for grid + allowed moves list, sends to opponent
        move = int(move)
        self.block_dict[move] = X if player == self.clients[0] else O #update grid markings of player's mark
        self.allowed_moves.remove(move) #updates allowed moves list
        self.send_msg(subject=ALLOWED, msg=self.allowed_moves, c=self.non_current_player) #sends new allowed moves to opponent

    def check_winner(self): #meth = checks if winner or draw, and who is winner and loser

        conditions = [[self.block_dict[1], self.block_dict[2], self.block_dict[3]],
                      [self.block_dict[4], self.block_dict[5], self.block_dict[6]],
                      [self.block_dict[7], self.block_dict[8], self.block_dict[9]],
                      [self.block_dict[1], self.block_dict[5], self.block_dict[9]],
                      [self.block_dict[7], self.block_dict[5], self.block_dict[3]],
                      [self.block_dict[1], self.block_dict[4], self.block_dict[7]],
                      [self.block_dict[2], self.block_dict[5], self.block_dict[8]],
                      [self.block_dict[3], self.block_dict[6], self.block_dict[9]],
                      ] #all conditions to win in ttt
        for condition in conditions: #loop checks if any conditions met and action for winner
            if condition[0] == condition[1] == condition[2]: #if first condition is same as 2nd and 3rd in the above patterns = winner
                winner = condition[0] #winner = the marking of the player in the grid of block dict
                if winner == X:
                    self.send_msg(GAME_OVER, "w", self.clients[0]) # send w msg to x player
                    self.send_msg(GAME_OVER, "l", self.clients[1]) # send l msg to o player
                elif winner == O:
                    self.send_msg(GAME_OVER, "l", self.clients[0]) # send l msg to x player
                    self.send_msg(GAME_OVER, "w", self.clients[1]) # send w msg to o player
                    self.close_connections() #game over so exit server connections
                return True

        if len(self.allowed_moves) == 0: #no more allowed moves and no winner = draw
            self.broadcast(GAME_OVER, "d") # send to both player clients
            self.close_connections() #game over so exit server connections
            return True

    def close_connections(self): #closes the socket connections and server
        for c in self.clients:
            c.close()
        self.server.close()

    def game_loop(self): #meth = actual game play logic
        self.broadcast(PRINT, "Let's play Tic Tac Toe!") #intro msg for both players
        self.broadcast(subject=ALLOWED, msg=self.allowed_moves) #gives both players the complete allowed moves list
        self.broadcast(PRINT, self.grid_board()) #gives both players ttt board

        while self.game_on: #game loops till game on = False

            self.turn = X if self.counter % 2 == 0 else O # check counter to determine turn, X if counter even O if odd

            if self.turn == X:
                self.current_player = self.clients[0] #current player = player X to make move
                self.non_current_player = self.clients[1] #non_current player = player O recieves move made
            elif self.turn == O:
                self.current_player = self.clients[1] #current player = player O to make move
                self.non_current_player = self.clients[0] #current player = player X to recieve move made

            self.send_msg(TURN, True, self.current_player) #send to current player that it is their turn
            self.send_msg(TURN, False, self.non_current_player) #send to non current player that it is NOT their turn
            player_move = self.current_player.recv(1024).decode('utf-8') #recieves current player's move
            self.make_move(move=player_move, player=self.current_player) #update grid + allowed moves list with player's move to send to opponent
            self.counter += 1 #that is the entire turn done so increase counter w 1 to allow turn to alternate for next loop
            self.broadcast(PRINT, self.grid_board()) #shows both clients updated grid board

            if self.check_winner(): #after a move is played check if game over: winner or draw
                self.game_on = False #if game over then game on = False and loop exited
                break


if __name__ == "__main__": #intialize script
    ip_addr = input("Enter ip address: ")
    port = input("Enter port: ")
    HOST = ip_addr #host IP
    PORT = port #random port
    client = TicTacToeServer(HOST, PORT)
