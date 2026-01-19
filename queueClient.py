from queueManager import QueueManager


class QueueClient:
    def __init__(self, address="localhost", port=50000, authkey=b"abc"):
        self.manager = QueueManager(address=(address, port), authkey=authkey)
        self.manager.connect()
        self.task_queue = self.manager.get_task_queue()
        self.result_queue = self.manager.get_result_queue()

    def get_results(self):
        while not self.result_queue.empty():
            result = self.result_queue.get()
            print(
                f"Result for task {result.identifier}: Computation time = {result.time:.2f} seconds"
            )
