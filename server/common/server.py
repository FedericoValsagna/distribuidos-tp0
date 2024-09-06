import multiprocessing
import socket
import logging
from common.utils import Bet, has_won, load_bets, store_bets
from common import parser
from common.client_handler import ClientHandler
from common.client_handler_handler import ClientHandlerHandler
from common.multiprocessing_controllers import MultiprocessingControllers

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.running = True
        self.client_sockets = {}
        self.remaining_bet_agencies = 5
        self.clients = {}
        self.mp_controllers = MultiprocessingControllers()

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
                addr = client_sock.getpeername()
                if addr not in self.clients:
                    self.clients[addr] = ClientHandlerHandler(client_sock, self.mp_controllers) 


    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """
        try:
            c, addr = self._server_socket.accept()
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
