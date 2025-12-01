from multiprocessing import Process, Manager
from task import Task


def worker(queue):
    while not queue.empty():
        task = queue.get()
        result = task.work()
        print(f"Résultat : {result}")


if __name__ == "__main__":
    manager = Manager()
    task_queue = manager.Queue()
    # Remplir avec des objets Task
    for i in range(10):
        t = Task(i, 100)
        task_queue.put(t)
    # Démarrer les Minions
    processes = [Process(target=worker, args=(task_queue,)) for _ in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
