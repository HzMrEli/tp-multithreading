#include <Eigen/Dense>
#include <chrono>
#include <cpr/cpr.h>
#include <iostream>
#include <nlohmann/json.hpp>
#include <omp.h>

using json = nlohmann::json;

class Task {
public:
  int identifier;
  int size;
  Eigen::MatrixXd A;
  Eigen::VectorXd b;
  Eigen::VectorXd x;
  double time;

  Task(int id = 0, int s = 0) : identifier(id), size(s), time(0.0) {
    A.resize(s, s);
    b.resize(s);
    x.resize(s);
  }

  static Task from_json(const json &j) {
    Task t(j["identifier"], j["size"]);

    auto matrixA = j["a"];
    auto matrixb = j["b"];

    for (int i = 0; i < t.size; i++) {
      for (int j_idx = 0; j_idx < t.size; j_idx++) {
        t.A(i, j_idx) = matrixA[i][j_idx];
      }
      t.b(i) = matrixb[i];
    }
    return t;
  }

  json to_json() const {
    json j;
    j["identifier"] = identifier;
    j["size"] = size;
    j["time"] = time;

    j["a"] = json::array();
    for (int i = 0; i < size; ++i) {
      json row = json::array();
      for (int j_idx = 0; j_idx < size; ++j_idx) {
        row.push_back(A(i, j_idx));
      }
      j["a"].push_back(row);
    }

    j["b"] = json::array();
    for (int i = 0; i < size; ++i) {
      j["b"].push_back(b(i));
    }

    j["x"] = json::array();
    for (int i = 0; i < size; ++i) {
      j["x"].push_back(x(i));
    }

    return j;
  }

  void work() {
    omp_set_num_threads(8);
    Eigen::setNbThreads(8);

    auto start = std::chrono::high_resolution_clock::now();
    x = A.householderQr().solve(b);
    auto end = std::chrono::high_resolution_clock::now();
    time = std::chrono::duration<double>(end - start).count();
  }
};

int main() {

  while (true) {
    std::cout << "En attente d'une tâche depuis Boss..." << std::endl;

    cpr::Response response = cpr::Get(cpr::Url{"http://127.0.0.1:8000/"});
    if (response.status_code != 200 || response.text.empty()) {
      std::cerr << "Toutes les taches ont été effectuées" << std::endl;
      break;
    }

    json received_json = json::parse(response.text);
    Task task = Task::from_json(received_json);

    std::cout << "Tâche reçue ! ID: " << task.identifier
              << ", Taille: " << task.size << std::endl;

    task.work();
    std::cout << "Temps de calcul pour la tâche " << task.identifier << " : "
              << task.time << " secondes." << std::endl;

    json result_json = task.to_json();
    cpr::Response post_response =
        cpr::Post(cpr::Url{"http://127.0.0.1:8000/"},
                  cpr::Header{{"Content-Type", "application/json"}},
                  cpr::Body{result_json.dump()});

    if (post_response.status_code == 200) {
      std::cout << "Résultat envoyé avec succès au Boss !" << std::endl;
    } else {
      std::cerr << "Erreur lors de l'envoi du résultat. Code HTTP: "
                << post_response.status_code << std::endl;
    }
  }
  return 0;
}
