from common.parser import BET_SEPARATOR

NOTIFY_MESSAGGE = "N"
ASKING_MESSAGE = "A"
WINNERS_MESSAGE = "W"
HOLD_MESSAGE = "S"
RECEIVED_MESSAGE = "R"

def winners_message(winners):
    msg = WINNERS_MESSAGE + BET_SEPARATOR
    for winner in winners:
        msg += winner.document
        msg += BET_SEPARATOR
    msg = msg[0:len(msg) - 1]
    return msg

def hold_message():
    return HOLD_MESSAGE

def apuesta_recivida_message():
    return RECEIVED_MESSAGE