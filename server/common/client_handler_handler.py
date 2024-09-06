import logging
from multiprocessing import Barrier, Process, Queue
import socket
from common.client_handler import ClientHandler
from common.multiprocessing_controllers import MultiprocessingControllers


class ClientHandlerHandler:
    def __init__(self, sock: socket, mp_controllers: MultiprocessingControllers):
        self.client_handler = ClientHandler(sock, mp_controllers=mp_controllers)
        self.client_process = Process(target=start_connection, args= [self.client_handler])
        self.client_process.start()

def start_connection(ch: ClientHandler):
    ch.start()
    # logging.info("Process Finish")

    