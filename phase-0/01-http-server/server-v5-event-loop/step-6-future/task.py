class Task:

    def __init__(self, coroutine):

        self.coroutine = coroutine

        self.finished = False

    def run(self, value=None):

        try:

            if value is None:

                future = next(
                    self.coroutine
                )

            else:

                future = self.coroutine.send(
                    value
                )

            return future

        except StopIteration:

            self.finished = True

            return None