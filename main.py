from task import Task


def worker(queue):
    while not queue.empty():
        task = queue.get()
        result = task.work()
        print(f"Résultat : {result}")


if __name__ == "__main__":
    task = Task(identifier=1, size=1000)
    task.work()
    json_data = task.to_json()
    print("Task serialized to JSON:")
    print(json_data)

    # Reconstruct the task from JSON
    task_copy = Task.from_json(json_data)
    print("Task deserialized from JSON:")
    print(task_copy.to_json())
    # Verify that the original and reconstructed tasks are equal
    task2 = Task.from_json(json_data)
    print("Tasks are equal:", task == task2)

    # Additional prints to verify correctness
    print(task_copy.identifier)
    print(task_copy.size)
    print(task_copy.time)

    # Test for equality
    task1 = Task(identifier=1, size=10)  # Meme task
    task2 = Task(identifier=1, size=10)  # Meme task

    # Perform work on both tasks to change their state
    task1.work()
    task2.work()

    # Verify equality (should be False because work modifies `time` and `x`)
    print(task1 == task2)  # False

    # Compare before calling `work`
    task3 = Task(identifier=1, size=10)
    print(task1 == task3)  # True (before `work` is called on task1)
