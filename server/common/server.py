import socket
import logging

from common.utils import Bet, has_won, load_bets, store_bets
from common import parser

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.running = True
        self.client_sockets = {}
        self.remaining_bet_agencies = 5

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
            self._read_message(client_sock)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        # finally:
            # client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """
        try:
            # Connection arrived
            # logging.info('action: accept_connections | result: in_progress')
            c, addr = self._server_socket.accept()
            # logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError:
            logging.info("action: closing_server_socket | result: success")

    def graceful_shutdown(self, signum, frame):
        self.running = False
        logging.info("Shutting down server socket")
        self._server_socket.close()
        for client_id, socket in self.client_sockets.items():
            logging.info(f"Shutting down Client {client_id} socket")
            socket.close()
        return

    def _read_message(self,client_sock: socket):
        header = client_sock.recv(7)
        msg_len = int.from_bytes(header[2:6], "big", signed=False)
        header = header[0:1].decode('utf-8')
        msg = client_sock.recv(msg_len).rstrip().decode('utf-8')
        code_name = header[0]
        if code_name == "B":
            self._single_bet_message(client_sock, msg)
            client_sock.close()
        elif code_name == "G":
            self._multi_bet_message(client_sock, msg)
            client_sock.close()
        elif code_name == "F":
            self._client_finished_sending_bets(client_sock, msg)
        else:
            logging.info("Invalid message")
            client_sock.close()
    
    def _single_bet_message(self, client_sock: socket, msg: str):
        bet: Bet = parser.decode_betting_message(msg)
        store_bets([bet])
        client_sock.send(parser.betting_response())
    

    def _multi_bet_message(self,client_sock: socket, msg: str):
        bets, error  = parser.decode_multibet_message(msg)
        if len(bets) > 0:
            store_bets(bets)
        if error:
            # logging.info(f"action: apuesta_recibida   | result: fail | cantidad: {len(bets)}")
            client_sock.send(parser.unsuccesful_betting_response())
            return
        # logging.info(f"action: apuesta_recibida   | result: success | cantidad: {len(bets)}")
        client_sock.send(parser.betting_response())

    def _client_finished_sending_bets(self, client_sock: socket, msg: str):
        client_id = parser.decode_finished_bets_message(msg)
        self.remaining_bet_agencies -= 1
        self.client_sockets[client_id] = client_sock
        if self.remaining_bet_agencies == 0:
            # Winner selection
            logging.info("action: sorteo | result: success")
            winner_bets = self._select_winners()
            agencies = self._order_winners_by_agency(winner_bets)
            # Send bet response to all clients
            for agency, winner_ids in agencies.items():
                agency_socket = self.client_sockets[agency]
                agency_socket.send(parser.winner_bet_response(winner_ids))
            
        
    
    def _select_winners(self) -> list[Bet]:
        total_bets = load_bets()
        winner_bets = filter(has_won, total_bets)
        return winner_bets

    def _order_winners_by_agency(self, winners_bets: list[Bet]) -> list[str]:
        agencies = {}
        for i in range(1, 6):
            agencies[str(i)] = []
        for bet in winners_bets:
            agency = str(bet.agency)
            if agency not in agencies:
                agencies[agency] = []
            agencies[agency].append(bet.document)
        
                
        return agencies

    def _broadcast_winner(self, winner: str):
        for _, client_info in self.client_sockets.items:
            (_, client_socket) = client_info
            client_socket.send(parser.winner_response())

    