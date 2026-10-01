#include <iostream>

#include "cli.hpp"

int main() {
    return runTask(runRotation, std::cin, std::cout, std::cerr);
}
