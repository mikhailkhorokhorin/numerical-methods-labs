#include "tridiagonal.hpp"

#include <gtest/gtest.h>

#include <cstddef>
#include <random>
#include <stdexcept>

#include "lu.hpp"
#include "support.hpp"

namespace {

const TridiagonalSystem VARIANT{.lower = {8.0, -3.0, -9.0, 1.0},
                                .diagonal = {16.0, -13.0, -21.0, 16.0, -9.0},
                                .upper = {-9.0, -5.0, 9.0, -5.0},
                                .rhs = {-27.0, -84.0, -225.0, -89.0, 69.0}};

Matrix toMatrix(const TridiagonalSystem& system) {
    const std::size_t n = system.diagonal.size();
    Matrix result(n, n);
    for (std::size_t i = 0; i < n; ++i) {
        result(i, i) = system.diagonal[i];
        if (i > 0) {
            result(i, i - 1) = system.lower[i - 1];
        }
        if (i + 1 < n) {
            result(i, i + 1) = system.upper[i];
        }
    }
    return result;
}

TEST(TridiagonalTest, SolvesVariant) {
    support::expectNear(solveTridiagonal(VARIANT), Vector{0.0, 3.0, 9.0, -3.0, -8.0}, 1e-12);
    EXPECT_TRUE(meetsStabilityCondition(VARIANT));
}

TEST(TridiagonalTest, MatchesLuOnRandomSystems) {
    std::mt19937 generator(7);
    std::uniform_real_distribution<double> distribution(-10.0, 10.0);
    for (std::size_t n = 1; n <= 12; ++n) {
        TridiagonalSystem system{.lower = Vector(n - 1),
                                 .diagonal = Vector(n),
                                 .upper = Vector(n - 1),
                                 .rhs = Vector(n)};
        for (auto* part : {&system.lower, &system.upper, &system.rhs}) {
            for (auto& value : *part) {
                value = distribution(generator);
            }
        }
        for (auto& value : system.diagonal) {
            value = 25.0 + distribution(generator);
        }
        const Matrix matrix = toMatrix(system);
        support::expectNear(solveTridiagonal(system), solveLu(decomposeLu(matrix), system.rhs),
                            1e-10);
    }
}

TEST(TridiagonalTest, SolvesSingleEquation) {
    const TridiagonalSystem system{.lower = {}, .diagonal = {4.0}, .upper = {}, .rhs = {8.0}};
    support::expectNear(solveTridiagonal(system), Vector{2.0}, 0.0);
}

TEST(TridiagonalTest, RejectsInconsistentSizes) {
    const TridiagonalSystem system{
        .lower = {1.0}, .diagonal = {1.0, 2.0}, .upper = {}, .rhs = {1.0, 2.0}};
    EXPECT_THROW(solveTridiagonal(system), std::invalid_argument);
    EXPECT_THROW(meetsStabilityCondition(system), std::invalid_argument);
    EXPECT_THROW(solveTridiagonal(TridiagonalSystem{}), std::invalid_argument);
}

TEST(TridiagonalTest, RejectsZeroDenominator) {
    const TridiagonalSystem system{
        .lower = {1.0}, .diagonal = {0.0, 1.0}, .upper = {1.0}, .rhs = {1.0, 1.0}};
    EXPECT_THROW(solveTridiagonal(system), std::domain_error);
}

TEST(TridiagonalTest, ChecksStabilityCondition) {
    const TridiagonalSystem weak{
        .lower = {1.0}, .diagonal = {1.0, 1.0}, .upper = {1.0}, .rhs = {0.0, 0.0}};
    const TridiagonalSystem violated{
        .lower = {3.0}, .diagonal = {5.0, 1.0}, .upper = {1.0}, .rhs = {0.0, 0.0}};
    const TridiagonalSystem decoupled{.lower = {1.0, 0.0},
                                      .diagonal = {1.0, 1.0, 1.0},
                                      .upper = {1.0, 0.0},
                                      .rhs = {1.0, 1.0, 1.0}};
    EXPECT_FALSE(meetsStabilityCondition(weak));
    EXPECT_FALSE(meetsStabilityCondition(violated));
    EXPECT_FALSE(meetsStabilityCondition(decoupled));
    EXPECT_THROW(solveTridiagonal(decoupled), std::domain_error);
}

}
