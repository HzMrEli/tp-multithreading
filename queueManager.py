from multiprocessing import Queue
from multiprocessing.managers import BaseManager
import time

task_queue = Queue()
result_queue = Queue()


class QueueManager(BaseManager):
    pass


QueueManager.register("get_task_queue", callable=lambda: task_queue)
QueueManager.register("get_result_queue", callable=lambda: result_queue)

if __name__ == "__main__":
    manager = QueueManager(address=("", 50000), authkey=b"abc")
    # manager.start()
    s = manager.get_server()
    s.serve_forever()
    print("QueueManager started.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down manager.")
        manager.shutdown()
