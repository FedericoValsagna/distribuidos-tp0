from common.utils import Bet


PACKET_SIZE = 8192
PADDING = '$'
SEPARATOR = '_'
BET_SEPARATOR = "!"

def to_bytes(string):
    b = bytes(string, "utf-8")
    return b

def remove_padding(msg: str) -> str:
    # Drop Padding
    msg = msg.split(PADDING)
    return msg[0]

def parse_message(msg: str) -> list[str]:
    msg = msg.split(BET_SEPARATOR)
    return msg

def fill_padding(msg: str) -> str:
    b = to_bytes(msg)
    extra_padding_required = PACKET_SIZE - len(b)
    extra_padding = PADDING * extra_padding_required
    msg += extra_padding
    return msg

def get_bet(msg: str, id) -> Bet:
    fields = msg.split(SEPARATOR)
    return Bet(id, fields[0], fields[1], fields[2], fields[3], fields[4])

def parse_bets_message(msg) -> list[Bet]:
    bets = []
    id = msg[0]
    for i in range(1, len(msg)):
        bet = get_bet(msg[i], id)
        bets.append(bet)
    return bets

def send(socket, msg):
    msg = fill_padding(msg)
    socket.send(msg.encode('utf-8'))