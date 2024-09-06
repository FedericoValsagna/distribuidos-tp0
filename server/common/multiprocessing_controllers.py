import logging
from multiprocessing import Barrier, Lock


class MultiprocessingControllers:
    def __init__(self):
        self.barrier = Barrier(parties=5, action=log_bet_win)
        self.store_bets_lock = Lock()
        self.multi_store_bets_lock = Lock()
        self.load_bets_lock = Lock()
        self.has_won_lock = Lock()



def log_bet_win():
    logging.info("action: sorteo | result: success")