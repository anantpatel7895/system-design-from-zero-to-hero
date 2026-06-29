class Future:

    def __init__(self):

        self.done = False

        self.result = None

        self.waiting_task = None

    def set_result(self, value):

        self.done = True

        self.result = value