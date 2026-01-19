cmake_minimum_required(VERSION 3.14)
project(tp-multithreading)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Configuration pour OpenMP
find_package(OpenMP)

include(FetchContent)

# 1. Eigen (Algèbre linéaire)
message(STATUS "Fetching Eigen...")
FetchContent_Declare(
  eigen
  GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
  GIT_TAG 3.4.0
  GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(eigen)

# 2. JSON
message(STATUS "Fetching nlohmann/json...")
FetchContent_Declare(
  json
  GIT_REPOSITORY https://github.com/nlohmann/json.git
  GIT_TAG v3.11.3
  GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(json)

# 3. CPR (Requêtes HTTP)
message(STATUS "Fetching CPR...")
FetchContent_Declare(
  cpr
  GIT_REPOSITORY https://github.com/libcpr/cpr.git
  GIT_TAG 1.10.5
  GIT_SHALLOW TRUE
)
# Options pour CPR pour éviter de construire les tests/exemples
set(CPR_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(CPR_FORCE_USE_SYSTEM_CURL OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(cpr)

# Exécutable Low Level
add_executable(low_level low_level.cpp)
target_link_libraries(low_level PRIVATE Eigen3::Eigen nlohmann_json::nlohmann_json cpr::cpr)

# Exécutable Client (Test)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/client.cpp")
    add_executable(client client.cpp)
    target_link_libraries(client PRIVATE Eigen3::Eigen nlohmann_json::nlohmann_json cpr::cpr)
endif()

# Lien avec OpenMP si trouvé
if(OpenMP_CXX_FOUND)
    target_link_libraries(low_level PRIVATE OpenMP::OpenMP_CXX)
    message(STATUS "OpenMP found and linked.")
else()
    message(WARNING "OpenMP not found. Calculations will not be parallelized on CPU.")
endif()
