import os
import subprocess
import time
import pandas as pd
import matplotlib.pyplot as plt
import sys


def run_python_benchmark():
    print("--- Running Python Benchmark ---")

    # 1. Start Server
    server = subprocess.Popen(
        [sys.executable, "queueManager.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(5)  # Wait for server

    # 2. Start Worker
    worker = subprocess.Popen(
        [sys.executable, "minion.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(1)

    # 3. Start Boss
    print("Running Boss for Python...")
    subprocess.run(
        [sys.executable, "boss.py", "--csv", "results_python.csv", "--tasks", "5"]
    )

    # Cleanup
    worker.terminate()
    server.terminate()
    server.wait()
    print("Python Benchmark Done.\n")


def run_cpp_benchmark():
    print("--- Running C++ Benchmark ---")

    # Check if executable exists in build folder
    exe_path = os.path.abspath("low_level.exe")
    if not os.path.exists(exe_path):
        possible_paths = ["build/Release/low_level.exe", "build/low_level", "low_level"]
        for p in possible_paths:
            if os.path.exists(p):
                exe_path = os.path.abspath(p)
                break

    if not os.path.exists(exe_path):
        print(
            f"WARNING: C++ executable not found at {exe_path}. Skipping C++ benchmark."
        )
        return False

    print(f"Using C++ executable: {exe_path}")

    # Add DLL paths to environment for Windows
    env = os.environ.copy()
    if os.name == "nt":
        dll_paths = [
            os.path.abspath("build/_deps/cpr-build/cpr/Release"),
            os.path.abspath("build/_deps/curl-build/lib/Release"),
            os.path.abspath("build/_deps/zlib-build/Release"),
            os.path.dirname(exe_path),
        ]
        env["PATH"] = os.pathsep.join(dll_paths) + os.pathsep + env["PATH"]

    # 1. Start Server
    server = subprocess.Popen(
        [sys.executable, "queueManager.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2)

    # 2. Start Proxy
    proxy = subprocess.Popen(
        [sys.executable, "proxy.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(2)

    # 3. Start Worker
    # Must use the modified env so it finds the DLLs
    worker = subprocess.Popen(
        [exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
    )

    # 4. Start Boss
    print("Running Boss for C++...")
    subprocess.run(
        [sys.executable, "boss.py", "--csv", "results_cpp.csv", "--tasks", "5"]
    )

    # Cleanup
    worker.terminate()
    proxy.terminate()
    server.terminate()
    server.wait()
    print("C++ Benchmark Done.\n")
    return True


def generate_comparison_plot():
    print("--- Generating Comparison Plot ---")

    data_python = None
    data_cpp = None

    if os.path.exists("results_python.csv"):
        data_python = pd.read_csv("results_python.csv")

    if os.path.exists("results_cpp.csv"):
        data_cpp = pd.read_csv("results_cpp.csv")

    plt.figure(figsize=(10, 6))

    if data_python is not None:
        data_python = data_python.sort_values(by="size")
        plt.plot(
            data_python["size"],
            data_python["time"],
            marker="o",
            label="Python (NumPy)",
            color="blue",
        )

    if data_cpp is not None:
        data_cpp = data_cpp.sort_values(by="size")
        plt.plot(
            data_cpp["size"],
            data_cpp["time"],
            marker="x",
            label="C++ (Eigen+OpenMP)",
            color="red",
        )

    plt.xlabel("Taille de la Matrice (N)")
    plt.ylabel("Temps d'exécution (s)")
    plt.title("Comparaison de Performance: Python vs C++")
    plt.legend()
    plt.grid(True)
    plt.savefig("benchmark_comparison.png")
    print("Plot saved to benchmark_comparison.png")

    # Generate Markdown Table
    md_table = "\n### Résultats de Performance\n\n| Taille (N) | Python (s) | C++ (s) | Speedup |\n|---|---|---|---|\n"

    if data_python is not None and data_cpp is not None:
        # Merge on size
        merged = pd.merge(data_python, data_cpp, on="size", suffixes=("_py", "_cpp"))
        for _, row in merged.iterrows():
            speedup = row["time_py"] / row["time_cpp"] if row["time_cpp"] > 0 else 0
            md_table += f"| {int(row['size'])} | {row['time_py']:.4f} | {row['time_cpp']:.4f} | {speedup:.2f}x |\n"
    elif data_python is not None:
        for _, row in data_python.iterrows():
            md_table += f"| {int(row['size'])} | {row['time']:.4f} | N/A | N/A |\n"

    return md_table


if __name__ == "__main__":
    # Clean old results
    if os.path.exists("results_python.csv"):
        os.remove("results_python.csv")
    if os.path.exists("results_cpp.csv"):
        os.remove("results_cpp.csv")

    run_python_benchmark()
    run_cpp_benchmark()
    table = generate_comparison_plot()
    print(table)

    # Update README
    with open("README.md", "a", encoding="utf-8") as f:
        f.write("\n## 📊 Comparaison de Performances\n")
        f.write("Graphique généré automatiquement :\n\n")
        f.write("![Benchmark](benchmark_comparison.png)\n")
        f.write(table)
    print("README.md updated.")
