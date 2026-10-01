#include <iostream>

#include "cli.hpp"

int main() {
    return runTask(runTridiagonal, std::cin, std::cout, std::cerr);
}
