from queueClient import QueueClient
import time


class Minion(QueueClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Process tasks from the task queue

    def work(self):
        print("Minion started working.")
        while True:
            try:
                # Get a task from the queue
                task = self.task_queue.get(timeout=10)
                print(f"Processing task {task.identifier} of size {task.size}.")

                # Measure processing time
                start_time = time.time()
                task.work()  # Effectue la résolution Ax = b
                elapsed_time = time.time() - start_time

                # Put execution time in the task
                task.execution_time = elapsed_time

                # Send the completed task with execution time back
                self.result_queue.put(task)
                print(
                    f"Task {task.identifier} completed in {elapsed_time:.2f} seconds."
                )

            except Exception as e:
                print("No more tasks or an error occurred:", e)
                break


if __name__ == "__main__":
    minion = Minion()
    minion.work()
