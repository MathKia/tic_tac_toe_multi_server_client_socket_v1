#color constants = UX
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
PINK = "\033[35m"

#message subject constants = use in sending structure messages
ALLOWED = "allowed moves" #reciever knows msg = updated allowed moves list
TURN = "turn" #reciever knows msg = its turn to play or not
GAME_OVER = "game over" #reciever knows msg = that game is over because there is winner or draw
PRINT = "print" #reciever knows msg = print miscellanous, can be grid board or intro messages