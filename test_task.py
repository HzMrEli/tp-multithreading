import unittest
import numpy as np
from task import Task


class TestTask(unittest.TestCase):
    def test_solve_linear_system(self):
        """
        Teste si la solution x du système Ax = B est correcte.
        """
        task_instance = Task()
        # task_instance.work()
        result_ax = np.dot(task_instance.a, task_instance.x)

        np.testing.assert_allclose(result_ax, task_instance.b)


if __name__ == "__main__":
    unittest.main()
