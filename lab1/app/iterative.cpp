#include <iostream>

#include "cli.hpp"

int main() {
    return runTask(runIterative, std::cin, std::cout, std::cerr);
}
