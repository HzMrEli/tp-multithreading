import time
import json
import numpy as np


class Task:
    def __init__(self, identifier=0, size=None):
        self.identifier = identifier
        # choosee the size of the problem
        self.size = size or np.random.randint(300, 3_000)
        # Generate the input of the problem
        self.a = np.random.rand(self.size, self.size)
        self.b = np.random.rand(self.size)
        # prepare room for the results
        self.x = np.zeros((self.size))
        self.time = 0

    def work(self):
        start = time.perf_counter()
        self.x = np.linalg.solve(self.a, self.b)
        self.time = time.perf_counter() - start

    def to_json(self) -> str:
        return json.dumps(
            {
                "a": self.a.tolist(),
                "b": self.b.tolist(),
                "x": self.x.tolist(),
                "identifier": self.identifier,
                "size": self.size,
                "time": self.time,
            }
        )

    @staticmethod
    def from_json(text: str) -> "Task":
        data = json.loads(text)
        task = Task(data["identifier"], data["size"])
        task.a = np.array(data["a"])
        task.b = np.array(data["b"])
        task.x = np.array(data["x"])
        task.time = data["time"]
        return task

    def __eq__(self, other: "Task") -> bool:
        return (
            self.identifier == other.identifier
            and self.size == other.size
            and np.allclose(self.a, other.a)
            and np.allclose(self.b, other.b)
            and np.allclose(self.x, other.x)
            and self.time == other.time
        )
