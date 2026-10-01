#include "tridiagonal.hpp"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <stdexcept>

namespace {

constexpr double SINGULARITY_TOLERANCE = 1e-12;

void validate(const TridiagonalSystem& system) {
    const std::size_t n = system.diagonal.size();
    if (n == 0 || system.rhs.size() != n || system.lower.size() + 1 != n ||
        system.upper.size() + 1 != n) {
        throw std::invalid_argument("tridiagonal system has inconsistent sizes");
    }
}

double lowerAt(const TridiagonalSystem& system, std::size_t row) {
    return row == 0 ? 0.0 : system.lower[row - 1];
}

double upperAt(const TridiagonalSystem& system, std::size_t row) {
    return row + 1 == system.diagonal.size() ? 0.0 : system.upper[row];
}

}

Vector solveTridiagonal(const TridiagonalSystem& system) {
    validate(system);
    const std::size_t n = system.diagonal.size();
    double scale = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        scale = std::max({scale, std::abs(lowerAt(system, i)), std::abs(system.diagonal[i]),
                          std::abs(upperAt(system, i))});
    }

    Vector p(n);
    Vector q(n);
    for (std::size_t i = 0; i < n; ++i) {
        const double a = lowerAt(system, i);
        const double previousP = i == 0 ? 0.0 : p[i - 1];
        const double previousQ = i == 0 ? 0.0 : q[i - 1];
        const double denominator = system.diagonal[i] + a * previousP;
        if (std::abs(denominator) <= SINGULARITY_TOLERANCE * scale) {
            throw std::domain_error("zero denominator in the Thomas algorithm");
        }
        p[i] = -upperAt(system, i) / denominator;
        q[i] = (system.rhs[i] - a * previousQ) / denominator;
    }

    Vector solution(n);
    solution[n - 1] = q[n - 1];
    for (std::size_t i = n - 1; i-- > 0;) {
        solution[i] = p[i] * solution[i + 1] + q[i];
    }
    return solution;
}

bool meetsStabilityCondition(const TridiagonalSystem& system) {
    validate(system);
    const auto isZero = [](double value) {
        return value == 0.0;
    };
    if (std::ranges::any_of(system.lower, isZero) || std::ranges::any_of(system.upper, isZero)) {
        return false;
    }
    bool strict = false;
    for (std::size_t i = 0; i < system.diagonal.size(); ++i) {
        const double diagonal = std::abs(system.diagonal[i]);
        const double offDiagonal = std::abs(lowerAt(system, i)) + std::abs(upperAt(system, i));
        if (diagonal < offDiagonal) {
            return false;
        }
        strict = strict || diagonal > offDiagonal;
    }
    return strict;
}
