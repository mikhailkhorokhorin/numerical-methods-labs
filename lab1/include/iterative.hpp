#pragma once

#include <cstddef>
#include <optional>

#include "matrix.hpp"

struct IterationForm {
    Matrix alpha;
    Vector beta;
};

struct IterationResult {
    Vector solution;
    std::size_t iterations = 0;
    bool converged = false;
};

IterationForm toIterationForm(const Matrix& matrix, const Vector& rhs);
IterationResult simpleIteration(const Matrix& matrix, const Vector& rhs, double eps);
IterationResult seidel(const Matrix& matrix, const Vector& rhs, double eps);
std::optional<std::size_t> aprioriIterations(const Matrix& matrix, const Vector& rhs, double eps);
