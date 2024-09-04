from common.utils import Bet


def decode_betting_message(msg: str) -> Bet:
    msg = msg.split("_")
    return Bet(agency=msg[0], first_name=msg[1], last_name=msg[2], document=msg[3], birthdate=msg[4], number=msg[5])

def betting_response() -> bytes:
    return "O\n".encode('utf-8')