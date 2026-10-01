#pragma once

#include <cstddef>

#include "matrix.hpp"

struct EigenSystem {
    Vector values;
    Matrix vectors;
    Vector errors;
    std::size_t rotations = 0;
};

double offDiagonalNorm(const Matrix& matrix);
EigenSystem rotationMethod(const Matrix& matrix, double eps);
