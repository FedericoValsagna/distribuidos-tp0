import socket
import logging

from common.utils import Bet, store_bets
from common import parser

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
            read_message(client_sock)
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

def single_bet_message(client_sock: socket, msg: str):
    client_sock.send(parser.betting_response())
    bet: Bet = parser.decode_betting_message(msg)
    store_bets([bet])
    

def multi_bet_message(client_sock: socket, msg: str):
    bets, error  = parser.decode_multibet_message(msg)
    if len(bets) > 0:
        store_bets(bets)
    if error:
        logging.info(f"action: apuesta_recibida   | result: fail | cantidad: {len(bets)}")
        client_sock.send(parser.unsuccesful_betting_response())
        return
    logging.info(f"action: apuesta_recibida   | result: success | cantidad: {len(bets)}")
    client_sock.send(parser.betting_response())

def read_message(client_sock: socket):
    header = client_sock.recv(7)
    msg_len = int.from_bytes(header[2:6], "big", signed=False)
    header = header[0:1].decode('utf-8')
    msg = client_sock.recv(msg_len).rstrip().decode('utf-8')
    code_name = header[0]
    if code_name == "B":
        single_bet_message(client_sock, msg)
    elif code_name == "G":
        multi_bet_message(client_sock, msg)
    else:
        logging.info("Invalid message")
    