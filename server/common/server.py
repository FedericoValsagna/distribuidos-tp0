from multiprocessing import Lock, Process, Queue, Value
import os
import socket
import logging
from common.utils import Bet
from common.utils import store_bets
from common.utils import load_bets
from common.utils import has_won
from common.agency import Agency
from common.messages import ASKING_MESSAGE, NOTIFY_MESSAGGE, apuesta_recivida_message, hold_message, winners_message
from common.parser import PACKET_SIZE, fill_padding, parse_bets_message, parse_message, remove_padding, send
class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.running = True
        self.total_agencies = int(os.getenv("AGENCY_AMOUNT"))
        self.create_processes()

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        i = 0
        while self.running:
            client_sock = self.__accept_new_connection()
            if client_sock != None and self.running:
                self.queue_list[i].put(client_sock)
                i += 1
                if i == 5:
                    i = 0

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = client_sock.recv(PACKET_SIZE).decode('utf-8')
            msg = remove_padding(msg)
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            msg = parse_message(msg)
            if msg[0] == NOTIFY_MESSAGGE:
                agency = msg[1]
                with self.remaining_agencies_lock:
                    self.remaining_agencies.value -= 1
                    if self.remaining_agencies.value == 0:
                        logging.info("action: sorteo | result: success")
            elif msg[0] == ASKING_MESSAGE:
                agency = msg[1]
                with self.remaining_agencies_lock:
                    if self.remaining_agencies.value == 0:
                        winners = select_winners(agency, self.bet_lock)
                        send(client_sock, winners_message(winners))
                    else:
                        send(client_sock, hold_message())
                        client_sock.close()
            elif msg[0].isdigit():
                # Message logic
                bets = parse_bets_message(msg)
                with self.bet_lock:
                    store_bets(bets)
                logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bets)}')
                send(client_sock, apuesta_recivida_message())
                client_sock.close()
            else:
                # Unknown msg
                print("Unknown msg")
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
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
        with self.working_lock:
            self.working.value = False
        for process in self.process_list:
            process.join()
        return

    def task_assignment(self, queue: Queue, working, working_lock):
        while True:
            try:
                task = queue.get(timeout=1)
                self.__handle_client_connection(task)
            except:
                working_lock.acquire()
                if not working.value:
                    working_lock.release()
                    break
                working_lock.release()

    def create_processes(self):
        process_list = []
        queue_list = []
        working = Value('b', True)
        working_lock = Lock()
        queue_list.append(Queue())
        queue_list.append(Queue())
        queue_list.append(Queue())
        queue_list.append(Queue())
        queue_list.append(Queue())
        process_list.append(Process(target=self.task_assignment, args=(queue_list[0], working, working_lock)))
        process_list.append(Process(target=self.task_assignment, args=(queue_list[1], working, working_lock)))
        process_list.append(Process(target=self.task_assignment, args=(queue_list[2], working, working_lock)))
        process_list.append(Process(target=self.task_assignment, args=(queue_list[3], working, working_lock)))
        process_list.append(Process(target=self.task_assignment, args=(queue_list[4], working, working_lock)))
        self.process_list = process_list
        self.queue_list = queue_list
        self.working = working
        self.working_lock = working_lock

        # Shared information
        self.bet_lock = Lock()
        self.remaining_agencies = Value('i', self.total_agencies)
        self.remaining_agencies_lock = Lock()

        # Start processes
        for process in self.process_list:
            process.start()
        return
    
def select_winners(agency, bet_lock):
    winners = []
    with bet_lock:
        for bet in load_bets():
            if has_won(bet) and bet.agency == int(agency):
                winners.append(bet)
    return winners





