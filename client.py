import json  #for structure dict msg to load by reciever socket
import socket  #for client sockets to connect to server, recv msgs, send msgs
from constants import RED, GREEN, YELLOW, RESET #color constants imported from constants.py
from constants import ALLOWED, PRINT, TURN, GAME_OVER #msg subject constants imported from constants.py


class TicTacToeClient:
    """
    This python file is the client side for the tic tac toe game seperate from the server
    the client is responsible for :
        - connecting to the server socket on [HOST IP, PORT]
        - waiting for server to signal if it is the client's turn
        - if it is the client's turn then allow an input option for player to choose move
        - check if the player's move is valid: numeric and in allowed moves
        - check for server's messages about whether the game is over and who is winner
    """

    def __init__(self, host, port): #initalize client socket to connect to server socket + listen to server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #client socket w INET + TCP
        self.client.connect((host, port)) #connet to server socket addr
        print("Connected to the server.")

        self.allowed_moves = [] #attr = list of allowed moves to play, recvs updates from server every time opp move played
        self.turn = None #attr = recv update from server to check if client's turn to play move or not

        self.listen_to_server() #meth = starts the client to continuosly listen to server for any msgs for entire game sesh + specific msgs = specific acts

    def listen_to_server(self):  # constantly listen for every message server sends to client
        try:
            buffer = ""  # buffer allows separation for all messages queued
            while True:  # runs for as long as main program/game session runs
                try:
                    data = self.client.recv(1024)  # queue of messages received
                    if not data:  # if `recv` returns an empty string, the connection is closed
                        raise ConnectionResetError("Server closed the connection.")

                    buffer += data.decode('utf-8')
                    while "\n" in buffer:  # loop to split messages in queue
                        message, buffer = buffer.split("\n", 1)
                        message = json.loads(message)  # JSON load the structured dict message recv from server
                        self.process_message(message)  # based on message subject specific action is done by client
                except ConnectionResetError:
                    print(f"{RED}Server or opponent has dropped the game. End of game session.{RESET}")
                    self.cleanup_and_exit()
                except (socket.error, json.JSONDecodeError) as e:  # error handling if disconnected from server
                    print(f"{RED}Disconnected from the server due to error: {e}.{RESET}")
                    self.cleanup_and_exit()

        except Exception as e:
            print(f"{RED}Unexpected error: {e}{RESET}")
            self.cleanup_and_exit()

    def cleanup_and_exit(self):
        try:
            self.client.close()
        except socket.error:
            pass
        exit(0)

    def process_message(self, message): #meth = specific subject -> specific action

        if message["subject"] == ALLOWED:
            self.allowed_moves = message["data"] #update moves allowed list on clients side

        if message["subject"] == GAME_OVER:  #end game on client side
            if message["data"] == "w":
                print(f"GAME OVER: {GREEN}You won!{RESET}") #tells client they won game
            elif message["data"] == "l":
                print(f"GAME OVER: {RED}You lost!{RESET}") #tells client they loss game
            else:
                print(f"GAME OVER: {YELLOW}It's a draw!{RESET}") #tells client they drew game
            exit(0) #exit sesh

        if message["subject"] == TURN: #tells client whose turn it is
            if message["data"]: #true = client's trun
                print(f"{GREEN}It is your turn{RESET}")
                self.turn = True
                self.send_move() #calls send move meth for client to choose valid move to send to server
            else: #false = not the client turn
                print(f"{RED}It is your opponent's turn{RESET}")
                self.turn = False

        if message["subject"] == PRINT: #tells client to print msg, could be grid board or intro msg
            print(message["data"])

    def check_move(self, move): #meth = checks if client chose move valid: is number and is in allowed moves list
        if move.isnumeric() and int(move) in self.allowed_moves:
            return True
        else:
            print(f"{RED}That is not a valid move{RESET}")

    def send_move(self): #meth = client can choose move, only if move checked as valid will move be sent and turn will be complete
        while self.turn: #loops until client move is valid --> number + in allowed moves list
            move = input("Enter block number to mark: ")
            if self.check_move(move): #check move valid
                self.client.send(move.encode('utf-8')) #sends move to server
                self.turn = False #end of client turn
                break


if __name__ == "__main__": #intialize client
    ip_addr = input("Enter ip address: ")
    port = input("Enter port: ")
    HOST = ip_addr # public IP 4 addr of EC2 server instance
    PORT = port #random port
    client = TicTacToeClient(HOST, PORT)
