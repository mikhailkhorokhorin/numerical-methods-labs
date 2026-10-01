#pragma once

#include <cstddef>
#include <vector>

#include "matrix.hpp"

struct LuDecomposition {
    Matrix lower;
    Matrix upper;
    std::vector<std::size_t> permutation;
    int sign = 1;
};

LuDecomposition decomposeLu(const Matrix& matrix);
Vector solveLu(const LuDecomposition& lu, const Vector& rhs);
double determinant(const LuDecomposition& lu);
Matrix inverse(const LuDecomposition& lu);
