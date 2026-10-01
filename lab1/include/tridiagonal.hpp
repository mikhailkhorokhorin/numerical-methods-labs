#pragma once

#include "matrix.hpp"

struct TridiagonalSystem {
    Vector lower;
    Vector diagonal;
    Vector upper;
    Vector rhs;
};

Vector solveTridiagonal(const TridiagonalSystem& system);
bool meetsStabilityCondition(const TridiagonalSystem& system);
