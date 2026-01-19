from task import Task
from queueClient import QueueClient
import time
import matplotlib.pyplot as plt
from typing import List, Optional


import argparse


class Boss(QueueClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_tasks_sent = 0
        # Utilisation d'un dictionnaire pour mapper l'ID de la tâche à sa taille
        self.task_registry = {}
        self.results_data = []  # Liste de dictionnaires pour stocker les résultats finaux

    def add_tasks(self, num_tasks: int = 10, sizes: Optional[List[int]] = None):
        if sizes is None:
            sizes = [100, 200, 500, 800, 1000, 2000, 3000, 4000, 5000, 6000]

        self.num_tasks_sent = num_tasks
        print(f"Boss is adding {num_tasks} tasks with varying sizes.")

        for i in range(num_tasks):
            size = sizes[i % len(sizes)]
            # Enregistrement de la taille prévue pour cet ID
            self.task_registry[i] = size

            task = Task(identifier=i, size=size)

            start_time = time.time()
            self.task_queue.put(task)
            elapsed_time = time.time() - start_time

            print(
                f"Task {task.identifier} (size {task.size}) dispatched in {elapsed_time:.4f}s."
            )

        print("All tasks have been added to the queue.")

    def get_results(self, save_file="performance_results.csv", plot_file=None):
        """Attend et récupère tous les résultats envoyés par Minion ou low_level"""
        print("\nBoss is collecting results...")

        results_received = 0
        self.results_data = []

        while results_received < self.num_tasks_sent:
            # get() est bloquant par défaut, ce qui est parfait ici
            task = self.result_queue.get()
            results_received += 1

            # On stocke les données structurées
            self.results_data.append(
                {
                    "identifier": task.identifier,
                    "size": self.task_registry.get(task.identifier, 0),
                    "time": task.time,
                }
            )

            print(
                f"Received result for Task {task.identifier}: completed in {task.time:.4f}s."
            )

        print("\nAll tasks have been processed.")

        self.save_results_to_file(save_file)
        if plot_file:
            self.plot_results(save_path=plot_file)
        # else:
        # self.plot_results() # Disable auto showing when running in automation

    def save_results_to_file(self, filename="performance_results.csv"):
        """Sauvegarde les résultats dans un fichier CSV"""
        # Trier par taille pour une lecture plus facile du fichier
        sorted_results = sorted(self.results_data, key=lambda x: x["size"])

        try:
            with open(filename, "w") as f:
                f.write("identifier,size,time\n")
                for res in sorted_results:
                    f.write(f"{res['identifier']},{res['size']},{res['time']:.6f}\n")
            print(f"Résultats sauvegardés dans {filename}")
        except IOError as e:
            print(f"Erreur lors de la sauvegarde du fichier: {e}")

    def plot_results(self, save_path=None):
        """Affiche un graphique des tailles de tâches vs temps d'exécution"""
        if not self.results_data:
            print("Aucune donnée à afficher.")
            return

        # Trier les données pour que la ligne du graphique soit cohérente
        sorted_data = sorted(self.results_data, key=lambda x: x["size"])

        sizes = [d["size"] for d in sorted_data]
        times = [d["time"] for d in sorted_data]

        plt.figure(figsize=(10, 6))
        plt.scatter(sizes, times, color="red", label="Points de mesure", zorder=2)
        plt.plot(
            sizes,
            times,
            linestyle="--",
            color="blue",
            alpha=0.7,
            label="Tendance",
            zorder=1,
        )

        plt.xlabel("Taille de la tâche (nb opérations)")
        plt.ylabel("Temps d'exécution (s)")
        plt.title("Performance: Taille vs Temps d'exécution")
        plt.legend()
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Graphique sauvegardé dans {save_path}")
        else:
            plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Boss Task Manager")
    parser.add_argument(
        "--csv",
        type=str,
        default="performance_results.csv",
        help="Output CSV file for results",
    )
    parser.add_argument(
        "--plot", type=str, default=None, help="Output PNG file for plot"
    )
    parser.add_argument(
        "--tasks", type=int, default=10, help="Number of tasks to generate"
    )

    args = parser.parse_args()

    boss = Boss()
    boss.add_tasks(num_tasks=args.tasks)
    boss.get_results(save_file=args.csv, plot_file=args.plot)
