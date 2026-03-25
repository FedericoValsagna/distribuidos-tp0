from common.parser import BET_SEPARATOR

NOTIFY_MESSAGGE = "N"
ASKING_MESSAGE = "A"

def winners_message(winners):
    msg = "W" + BET_SEPARATOR
    for winner in winners:
        msg += winner.document
        msg += BET_SEPARATOR
    msg = msg[0:len(msg) - 1]
    return msg

def hold_message():
    return "S"

def apuesta_recivida_message():
    return "Apuesta recibida"