import socket
import logging
from common.utils import Bet
from common.utils import store_bets
PACKET_SIZE = 61
PADDING = '$'
SEPARATOR = '_'
class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.running = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        while self.running:
            client_sock = self.__accept_new_connection()
            if client_sock != None:
                self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            msg = client_sock.recv(PACKET_SIZE).rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # logging.info(f'Message length: {len(to_bytes(msg))}')
            # TODO: Modify the send to avoid short-writes
            bet = parse_message(msg)
            store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
            msg = "R"
            msg = fill_padding(msg)
            # print(f"largo del mensaje en bytes: {len(to_bytes(msg))}")
            # print(f"Mensaje enviado: '{msg}'")
            client_sock.send(msg.encode('utf-8'))
            # client_sock.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """
        try:
            # Connection arrived
            logging.info('action: accept_connections | result: in_progress')
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError:
            logging.info("action: closing_server_socket | result: success")

    def graceful_shutdown(self, signum, frame):
        self.running = False
        self._server_socket.close()
        return

def to_bytes(string):
    b = bytes(string, "utf-8")
    return b


def parse_message(msg: str) -> Bet:
    # Drop Padding
    msg = msg.split(PADDING)
    msg = msg[0]
    # Get Fields
    fields = msg.split(SEPARATOR)
    return Bet(fields[5], fields[0], fields[1], fields[2], fields[3], fields[4])


def fill_padding(msg: str) -> str:
    b = to_bytes(msg)
    extra_padding_required = PACKET_SIZE - len(b)
    extra_padding = PADDING * extra_padding_required
    msg += extra_padding
    return msg