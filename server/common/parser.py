import logging

from common.utils import Bet


PACKET_SIZE = 8192
PADDING = '$'
SEPARATOR = '_'
BET_SEPARATOR = "!"

def to_bytes(string):
    """
    Given a string it returns it as an array of bytes using UTF-8 encoding.
    """
    b = bytes(string, "utf-8")
    return b

def remove_padding(msg: str) -> str:
    """
    Given a message it will remove the padding to fill the packet length.
    """
    # Drop Padding
    msg = msg.split(PADDING)
    return msg[0]

def parse_message(msg: str) -> list[str]:
    """
    Given a message it will return a list of strings of it's contents.
    """
    msg = msg.split(BET_SEPARATOR)
    return msg

def fill_padding(msg: str) -> str:
    """
    Given a message it will add the padding to fill the packet length.
    """
    b = to_bytes(msg)
    extra_padding_required = PACKET_SIZE - len(b)
    extra_padding = PADDING * extra_padding_required
    msg += extra_padding
    return msg

def _get_bet(msg: str, id) -> Bet:
    """
    Given a bet message it will return the corresponding Bet object.
    """
    fields = msg.split(SEPARATOR)
    return Bet(id, fields[0], fields[1], fields[2], fields[3], fields[4])

def parse_bets_message(msg) -> list[Bet]:
    """
    Given a bets batch message it returns all the bets from the message.
    """
    bets = []
    id = msg[0]
    for i in range(1, len(msg)):
        bet = _get_bet(msg[i], id)
        bets.append(bet)
    return bets

def send(socket, msg):
    """ 
    Send a message to the socket
    """
    msg = fill_padding(msg)
    socket.send(msg.encode('utf-8'))

def read_message(socket):
    """
    Read a message from the socket
    """
    msg = socket.recv(PACKET_SIZE).decode('utf-8')
    msg = remove_padding(msg)
    addr = socket.getpeername()
    logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
    msg = parse_message(msg)
    return msg

