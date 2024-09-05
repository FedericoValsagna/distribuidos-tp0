import logging
from common.utils import Bet


def decode_betting_message(msg: str) -> Bet:
    msg = msg.split("_")
    return Bet(agency=msg[0], first_name=msg[1], last_name=msg[2], document=msg[3], birthdate=msg[4], number=msg[5])

def betting_response() -> bytes:
    return "O\n".encode('utf-8')

def unsuccesful_betting_response() -> bytes:
    return "N\n".encode('utf-8')

def decode_multibet_message(msg: str) -> tuple[list[Bet], bool]:
    error = False
    client_agency: str = msg[0]
    msg: str = msg [2:]
    bets: list[Bet] = []
    bet_lines: list[str] = msg.split("$")
    for bet in bet_lines:
        bet = bet.split("_")
        if len(bet) != 5:
            error = True
            continue
        bets.append(Bet(agency=client_agency, first_name=bet[0], last_name=bet[1], document=bet[2], birthdate=bet[3], number=bet[4]))
    return bets, error