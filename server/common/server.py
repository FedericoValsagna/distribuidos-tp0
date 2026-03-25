from multiprocessing import Lock, Process, Queue, Value
import socket
import logging
from common.utils import Bet
from common.utils import store_bets
from common.utils import load_bets
from common.utils import has_won
from common.agency import Agency
PACKET_SIZE = 8192
PADDING = '$'
SEPARATOR = '_'
BET_SEPARATOR = "!"
class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.running = True
        self.agencies = {}
        self.remaining_agencies = 0
        self.winner_selected = False
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
                # self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = client_sock.recv(PACKET_SIZE).decode('utf-8')
            msg = remove_padding(msg)
            if len(msg) == 0:
                return
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            msg = parse_message(msg)
            if msg[0] == "N":
                agency = msg[1]
                self.agencies[agency].finished = True
                self.remaining_agencies -= 1
                print(f"Remaining agencies: {self.remaining_agencies}")
                if self.remaining_agencies == 0:
                    # Launch winners
                    logging.info("action: sorteo | result: success")
                    with self.bet_lock:
                        self.choose_winners()
                        self.winner_selected = True
            elif msg[0] == "A":
                agency = msg[1]
                print("A msg")
                if self.winner_selected:
                    # Launch winners
                    send_winners(client_sock, self.agencies[agency])
                else:
                    msg = "S"
                    msg = fill_padding(msg)
                    client_sock.send(msg.encode('utf-8'))
                    client_sock.close()
            elif msg[0] in {"1", "2", "3", "4", "5"}:
                # Check if its in dictionary
                    if msg[0] not in self.agencies:
                        self.agencies[msg[0]] = Agency(addr)
                        self.remaining_agencies += 1
                        print(f"Remaining agencies: {self.remaining_agencies}")

                    # Message logic
                    bets = parse_bets_message(msg)
                    with self.bet_lock:
                        store_bets(bets)
                    logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bets)}')
                    msg = "Apuesta recibida"
                    msg = fill_padding(msg)
                    client_sock.send(msg.encode('utf-8'))
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
    
    def choose_winners(self):
        for bet in load_bets():
            if has_won(bet):
                self.agencies[str(bet.agency)].winners.add(bet)

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
        self.bet_lock = Lock()
        
        for process in self.process_list:
            process.start()
        return
    
def send_winners(socket, agency):
    msg = "W" + BET_SEPARATOR
    for winner in agency.winners:
        msg += winner.document
        msg += BET_SEPARATOR
    msg = msg[0:len(msg) - 1]
    print(f"Sending winners msg to client: {agency}, message: {msg}")
    msg = fill_padding(msg)
    socket.send(msg.encode('utf-8'))

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

def parse_bets_message(msg: [str]) -> list[Bet]:
    bets = []
    id = msg[0]
    for i in range(1, len(msg)):
        bet = get_bet(msg[i], id)
        bets.append(bet)
    return bets


def get_bet(msg: str, id) -> Bet:
    fields = msg.split(SEPARATOR)
    return Bet(id, fields[0], fields[1], fields[2], fields[3], fields[4])

def fill_padding(msg: str) -> str:
    b = to_bytes(msg)
    extra_padding_required = PACKET_SIZE - len(b)
    extra_padding = PADDING * extra_padding_required
    msg += extra_padding
    return msg
