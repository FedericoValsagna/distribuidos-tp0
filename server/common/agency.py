class Agency:
    def __init__(self, addr):
        self.addr = addr
        self.finished = False
        self.winners = set()
    #     self.socket = None

    # def add_socket(self, socket):
    #     self.socket = socket