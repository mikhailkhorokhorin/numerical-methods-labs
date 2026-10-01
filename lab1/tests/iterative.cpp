#include "iterative.hpp"

#include <gtest/gtest.h>

#include <cstddef>
#include <stdexcept>

#include "support.hpp"

namespace {

const Matrix VARIANT{
    {10.0, 0.0, 2.0, 4.0}, {2.0, 16.0, -3.0, 8.0}, {1.0, 5.0, 11.0, -4.0}, {8.0, 1.0, 6.0, -17.0}};
const Vector VARIANT_RHS{110.0, 128.0, 102.0, 81.0};
const Vector VARIANT_SOLUTION{9.0, 7.0, 6.0, 2.0};

TEST(IterativeTest, BuildsIterationForm) {
    const IterationForm form = toIterationForm(VARIANT, VARIANT_RHS);
    EXPECT_DOUBLE_EQ(form.alpha(0, 0), 0.0);
    EXPECT_DOUBLE_EQ(form.alpha(0, 2), -0.2);
    EXPECT_DOUBLE_EQ(form.alpha(3, 0), 8.0 / 17.0);
    support::expectNear(form.beta, Vector{11.0, 8.0, 102.0 / 11.0, -81.0 / 17.0}, 1e-15);
    EXPECT_NEAR(normInf(form.alpha), 10.0 / 11.0, 1e-15);
}

TEST(IterativeTest, BothMethodsSolveVariant) {
    for (const double eps : {1e-2, 1e-4, 1e-8}) {
        const IterationResult jacobi = simpleIteration(VARIANT, VARIANT_RHS, eps);
        const IterationResult gaussSeidel = seidel(VARIANT, VARIANT_RHS, eps);
        EXPECT_TRUE(jacobi.converged);
        EXPECT_TRUE(gaussSeidel.converged);
        support::expectNear(jacobi.solution, VARIANT_SOLUTION, eps);
        support::expectNear(gaussSeidel.solution, VARIANT_SOLUTION, eps);
        EXPECT_LT(gaussSeidel.iterations, jacobi.iterations);
        EXPECT_LE(jacobi.iterations, aprioriIterations(VARIANT, VARIANT_RHS, eps).value());
    }
}

TEST(IterativeTest, IterationsGrowAsPrecisionIncreases) {
    std::size_t previousJacobi = 0;
    std::size_t previousSeidel = 0;
    for (const double eps : {1e-1, 1e-3, 1e-5, 1e-7, 1e-9}) {
        const std::size_t jacobi = simpleIteration(VARIANT, VARIANT_RHS, eps).iterations;
        const std::size_t gaussSeidel = seidel(VARIANT, VARIANT_RHS, eps).iterations;
        EXPECT_GT(jacobi, previousJacobi);
        EXPECT_GT(gaussSeidel, previousSeidel);
        previousJacobi = jacobi;
        previousSeidel = gaussSeidel;
    }
}

TEST(IterativeTest, SolvesRandomDominantSystems) {
    for (std::size_t n = 1; n <= 8; ++n) {
        const Matrix matrix = support::diagonallyDominant(n, static_cast<unsigned>(n));
        const Vector expected = support::randomVector(n, static_cast<unsigned>(50 + n));
        const Vector rhs = matrix * expected;
        support::expectNear(simpleIteration(matrix, rhs, 1e-10).solution, expected, 1e-8);
        support::expectNear(seidel(matrix, rhs, 1e-10).solution, expected, 1e-8);
    }
}

TEST(IterativeTest, AprioriEstimateEdgeCases) {
    const Matrix diagonal{{2.0, 0.0}, {0.0, 4.0}};
    EXPECT_EQ(aprioriIterations(diagonal, Vector{2.0, 4.0}, 1e-6), 0U);
    EXPECT_EQ(aprioriIterations(VARIANT, Vector(4), 1e-6), 0U);
    EXPECT_EQ(aprioriIterations(VARIANT, VARIANT_RHS, 1e6), 0U);
    EXPECT_FALSE(aprioriIterations(Matrix{{1.0, 2.0}, {3.0, 1.0}}, Vector{1.0, 1.0}, 1e-6));
    EXPECT_FALSE(aprioriIterations(Matrix{{1e-300, 0.0}, {0.5, 1.0}}, Vector{1e100, 1.0}, 1e-3));
}

TEST(IterativeTest, SeidelConvergesWhereSimpleIterationOscillates) {
    const Matrix matrix{{1.0, 0.5, 0.5}, {0.5, 1.0, 0.5}, {0.5, 0.5, 1.0}};
    const Vector rhs{2.0, 2.0, 2.0};
    EXPECT_GE(normInf(toIterationForm(matrix, rhs).alpha), 1.0);
    const IterationResult jacobi = simpleIteration(matrix, rhs, 1e-10);
    EXPECT_FALSE(jacobi.converged);
    EXPECT_EQ(jacobi.iterations, 100000U);
    const IterationResult gaussSeidel = seidel(matrix, rhs, 1e-10);
    EXPECT_TRUE(gaussSeidel.converged);
    support::expectNear(gaussSeidel.solution, Vector{1.0, 1.0, 1.0}, 1e-8);
}

TEST(IterativeTest, StopsOnDivergence) {
    const Matrix matrix{{1.0, 2.0}, {3.0, 1.0}};
    const Vector rhs{1.0, 1.0};
    const IterationResult jacobi = simpleIteration(matrix, rhs, 1e-6);
    const IterationResult gaussSeidel = seidel(matrix, rhs, 1e-6);
    EXPECT_FALSE(jacobi.converged);
    EXPECT_FALSE(gaussSeidel.converged);
    EXPECT_LT(jacobi.iterations, 100000U);
    EXPECT_LT(gaussSeidel.iterations, 100000U);
}

TEST(IterativeTest, RejectsInvalidSystems) {
    EXPECT_THROW(toIterationForm(Matrix{{0.0, 1.0}, {1.0, 1.0}}, Vector{1.0, 1.0}),
                 std::domain_error);
    EXPECT_THROW(toIterationForm(VARIANT, Vector(3)), std::invalid_argument);
    EXPECT_THROW(toIterationForm(Matrix(2, 3), Vector(2)), std::invalid_argument);
    EXPECT_THROW(toIterationForm(Matrix{}, Vector{}), std::invalid_argument);
}

}
