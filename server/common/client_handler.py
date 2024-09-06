import logging
from multiprocessing import Barrier, Queue
import socket
from common.utils import Bet, has_won, load_bets, store_bets
from common import parser
from common.multiprocessing_controllers import MultiprocessingControllers


class ClientHandler:
    def __init__(self, client_socket: socket, mp_controllers: MultiprocessingControllers) -> None:
        self.client_sock = client_socket
        self.addr = client_socket.getpeername()
        self.mp_controllers = mp_controllers
        self.myID = None
        self.running = True

    def start(self):
        self.__handle_client_connection()
    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        while(self.running):
            try:
                self._read_message(self.client_sock)
            except OSError as e:
                logging.error(f"action: receive_message | result: fail | error: {e}")
            # finally:
                # client_sock.close()
    
    def _read_message(self, client_sock: socket):
        header = client_sock.recv(7)
        msg_len = int.from_bytes(header[2:6], "big", signed=False)
        header = header[0:1].decode('utf-8')
        msg = client_sock.recv(msg_len).rstrip().decode('utf-8')
        code_name = header[0]
        if code_name == "B":
            self._single_bet_message(msg)
        elif code_name == "G":
            self._multi_bet_message(client_sock, msg)
        elif code_name == "F":
            self._client_finished_sending_bets(client_sock, msg)
        else:
            logging.info("Invalid message")
    
    def _single_bet_message(self, msg: str):
        bet: Bet = parser.decode_betting_message(msg)
        self.mp_controllers.store_bets_lock.acquire()
        try:
            store_bets([bet])
        finally:
            self.mp_controllers.store_bets_lock.release()
        self.client_sock.send(parser.betting_response())
    

    def _multi_bet_message(self, client_sock: socket, msg: str):
        bets, error  = parser.decode_multibet_message(msg)
        if self.myID == None: 
            self.myID = bets[0].agency
        if len(bets) > 0:
            self.mp_controllers.multi_store_bets_lock.acquire()
            try:
                store_bets(bets)  
            finally:
                self.mp_controllers.multi_store_bets_lock.release()
        if error:
            client_sock.send(parser.unsuccesful_betting_response())
            return
        client_sock.send(parser.betting_response())

    def _client_finished_sending_bets(self, client_sock: socket, msg: str):
        client_id = parser.decode_finished_bets_message(msg)
        # logging.info(f"Agency {self.myID} | All bets has been processed. Waiting for other agencies.")
        self.mp_controllers.barrier.wait()
        winner_bets = self._select_winners()
        self.client_sock.send(parser.winner_bet_response(ids_from_bets(winner_bets)))
        self.client_sock.close()
        self.running = False

    def _select_winners(self) -> list[Bet]:
        self.mp_controllers.load_bets_lock.acquire()
        try:
            total_bets = load_bets()
        finally:
            self.mp_controllers.load_bets_lock.release()
        self.mp_controllers.has_won_lock.acquire()
        try:
            winner_bets = list(filter(has_won, total_bets))
        finally:
            self.mp_controllers.has_won_lock.release()
        # logging.info(f"Agency {self.myID} | Winners: {ids_from_bets(winner_bets)}")
        winners = list(filter(self._is_bet_from_agency, winner_bets))
        if winners == None:
            return []
        return list(winners)
        
    def _is_bet_from_agency(self, winner_bet: Bet):
        return self.myID == winner_bet.agency

def ids_from_bets(winner_bets: list[Bet]):
    ids = []
    for bet in winner_bets:
        ids.append(bet.document)
    return ids