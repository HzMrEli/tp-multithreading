#include <Eigen/Dense>
#include <cpr/cpr.h>
#include <iostream>
#include <nlohmann/json.hpp>

int main() {
  // Configuration du proxy
  cpr::Url proxy_url = "http://localhost:8080";

  // Requête HTTP via le proxy
  auto response = cpr::Get(cpr::Url{"http://httpbin.org/get"},
                           cpr::Proxies{{"http", proxy_url.string()},
                                        {"https", proxy_url.string()}});

  // Vérifier la réponse
  if (response.status_code == 200) {
    std::cout << "Response from server:\n" << response.text << std::endl;

    // Parse JSON response
    nlohmann::json json_data = nlohmann::json::parse(response.text);
    std::cout << "JSON parsed: " << json_data.dump(4) << std::endl;
  } else {
    std::cerr << "Failed to connect: " << response.error.message << std::endl;
  }

  // Exemple Eigen
  Eigen::MatrixXd matrix(2, 2);
  matrix(0, 0) = 3;
  matrix(0, 1) = 2.5;
  matrix(1, 0) = -1;
  matrix(1, 1) = matrix(0, 1) + matrix(0, 0);
  std::cout << "Eigen Matrix:\n" << matrix << std::endl;

  return 0;
}
