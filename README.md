# Projet Multi-Threading

Ce projet met en œuvre une architecture **Producteur-Consommateur** distribuée et multi-langage (Python et C++) pour la résolution parallèle de problèmes mathématiques (résolution de systèmes linéaires $Ax = b$).

## Architecture

Le système est composé de plusieurs modules communiquant entre eux via un gestionnaire de files d'attente centralisé.

### Composants Principaux

1.  **QueueManager (`queueManager.py`)** :
    - Le serveur central qui maintient deux files d'attente synchronisées : `task_queue` (tâches à faire) et `result_queue` (résultats terminés).
    - Utilise `multiprocessing.managers.BaseManager` pour exposer les files sur le réseau.

2.  **Boss (`boss.py`)** :
    - Le **Producteur**. Il génère des tâches contenant des matrices aléatoires de tailles variables.
    - Envoie les tâches dans la `task_queue`.
    - Récupère et affiche les résultats depuis la `result_queue`.

3.  **Task (`task.py`)** :
    - Définit la structure d'une tâche (Identifiant, matrice A, vecteur b).
    - Gère la sérialisation/désérialisation JSON pour l'interopérabilité Python/C++.
    - Contient la logique de résolution via `numpy`.

### Types de "Minions" (Consommateurs)

Le projet supporte deux types de travailleurs (workers) :

- **Minion Python (`minion.py`)** :
  - Se connecte directement au `QueueManager`.
  - Récupère une tâche, la résout avec `NumPy`, et renvoie le résultat.
  - Simple et direct.

- **Minion C++ (`low_level.cpp` + `proxy.py`)** :
  - Conçu pour la performance et pour démontrer l'interopérabilité.
  - **Proxy (`proxy.py`)** : Un serveur HTTP léger qui fait le pont entre le `QueueManager` (Python) et le monde extérieur via une API REST (GET/POST).
  - **Low Level Worker (`low_level.cpp`)** : Un client C++ qui récupère les tâches via le proxy HTTP, les résout efficacement en utilisant la bibliothèque **Eigen** et parallélise les calculs avec **OpenMP**.

## Installation et Prérequis

### Python

Le projet utilise `uv` pour la gestion des dépendances.
Dépendances requises : `numpy`, `matplotlib`.

````bash
# Avec uv
uv sync

### C++

Le worker C++ nécessite les bibliothèques suivantes :
*   [Eigen](https://eigen.tuxfamily.org/) (Algèbre linéaire)
*   [CPR](https://github.com/libcpr/cpr) (C++ Requests pour HTTP)
*   [nlohmann/json](https://github.com/nlohmann/json) (Parsing JSON)
*   OpenMP (généralement inclus avec GCC/Clang/MSVC)

**Compilation sur Windows (avec CMake) :**

Assurez-vous d'avoir installe `cmake` et un compilateur C++ (comme Visual Studio avec l'extension C++ ou MinGW).

```bash
# 1. Configurer le projet (téléchargement automatique des dépendances)
cmake -B build

# 2. Compiler en mode Release
cmake --build build --config Release
````

L'exécutable généré sera dans `build/Release/low_level.exe`.

**Compilation alternative (Linux/macOS avec g++) :**

```bash
g++ low_level.cpp -o low_level -O3 -fopenmp -I /path/to/eigen -I /path/to/json -lcpr
```

## Utilisation

Pour lancer le système complet, ouvrez plusieurs terminaux et exécutez les commandes dans l'ordre suivant :

### 1. Démarrer le Serveur (QueueManager)

Ce composant doit toujours tourner en premier.

```bash
python queueManager.py
```

### 2. Démarrer un Worker (Au choix)

**Option A : Worker Python**

```bash
python minion.py
```

**Option B : Worker C++**
D'abord, lancez le proxy pour faire le pont :

```bash
python proxy.py
```

Ensuite, lancez l'exécutable C++ compilé :

```bash
./low_level
```

### 3. Démarrer le Boss (Lancement des tâches)

Une fois le serveur et les workers prêts, lancez le Boss pour générer du travail.

```bash
python boss.py
```

Le Boss va générer une série de tâches, les envoyer, et vous verrez les workers les traiter en temps réel. Une fois fini, le Boss affichera les temps d'exécution.

## Tests

- `main.py` et `test_task.py` contiennent des tests unitaires pour valider la classe `Task` et la sérialisation JSON.

## Comparaison de Performances

![Benchmark](benchmark_comparison.png)

### Résultats de Performance

| Taille (N) | Python (s) | C++ (s) | Speedup |
| ---------- | ---------- | ------- | ------- |
| 100        | 0.0004     | 0.0011  | 0.34x   |
| 200        | 0.0007     | 0.0031  | 0.21x   |
| 500        | 0.0058     | 0.0306  | 0.19x   |
| 800        | 0.0195     | 0.1127  | 0.17x   |
| 1000       | 0.0371     | 0.2143  | 0.17x   |

## Conclusion

Ce projet met en évidence un fait surprenant : **malgré les optimisations en C++, Python est globalement plus rapide que C++ pour ces types de calculs**. Cette performance inattendue s'explique par le fait que **NumPy est massivement optimisé en C** et tire parti d'algorithmes spécialisés pour la manipulation de matrices. Toutefois, **C++ reste intéressant pour des tâches très spécifiques nécessitant un contrôle bas niveau**, mais pour des calculs matriciels classiques, **Python est clairement plus performant**.
