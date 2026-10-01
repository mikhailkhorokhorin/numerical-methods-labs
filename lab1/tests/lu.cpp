#include "lu.hpp"

#include <gtest/gtest.h>

#include <cstddef>
#include <stdexcept>

#include "support.hpp"

namespace {

const Matrix VARIANT{
    {1.0, 4.0, -9.0, 7.0}, {2.0, -2.0, -2.0, 3.0}, {-1.0, 3.0, -9.0, -1.0}, {-5.0, 2.0, 2.0, 1.0}};
const Vector VARIANT_RHS{-67.0, -57.0, -26.0, 52.0};

Matrix permuted(const Matrix& matrix, const LuDecomposition& lu) {
    Matrix result(matrix.rows(), matrix.cols());
    for (std::size_t i = 0; i < matrix.rows(); ++i) {
        for (std::size_t j = 0; j < matrix.cols(); ++j) {
            result(i, j) = matrix(lu.permutation[i], j);
        }
    }
    return result;
}

void expectValidFactors(const Matrix& matrix, const LuDecomposition& lu) {
    const std::size_t n = matrix.rows();
    for (std::size_t i = 0; i < n; ++i) {
        EXPECT_DOUBLE_EQ(lu.lower(i, i), 1.0);
        for (std::size_t j = i + 1; j < n; ++j) {
            EXPECT_DOUBLE_EQ(lu.lower(i, j), 0.0);
            EXPECT_DOUBLE_EQ(lu.upper(j, i), 0.0);
            EXPECT_LE(std::abs(lu.lower(j, i)), 1.0);
        }
    }
    support::expectNear(lu.lower * lu.upper, permuted(matrix, lu), 1e-9);
}

TEST(LuTest, SolvesVariant) {
    const LuDecomposition lu = decomposeLu(VARIANT);
    expectValidFactors(VARIANT, lu);
    support::expectNear(solveLu(lu, VARIANT_RHS), Vector{-5.0, 9.0, 7.0, -5.0}, 1e-12);
    EXPECT_NEAR(determinant(lu), 935.0, 1e-9);
    support::expectNear(inverse(lu) * VARIANT, Matrix::identity(4), 1e-12);
}

TEST(LuTest, PivotsAroundZeroDiagonal) {
    const Matrix matrix{{0.0, 1.0, 1.0}, {1.0, 0.0, 1.0}, {1.0, 1.0, 0.0}};
    const LuDecomposition lu = decomposeLu(matrix);
    expectValidFactors(matrix, lu);
    support::expectNear(solveLu(lu, Vector{2.0, 2.0, 2.0}), Vector{1.0, 1.0, 1.0}, 1e-12);
    EXPECT_NEAR(determinant(lu), 2.0, 1e-12);
}

TEST(LuTest, SolvesRandomSystems) {
    for (std::size_t n = 1; n <= 8; ++n) {
        const Matrix matrix = support::randomMatrix(n, static_cast<unsigned>(n));
        const Vector expected = support::randomVector(n, static_cast<unsigned>(100 + n));
        const LuDecomposition lu = decomposeLu(matrix);
        expectValidFactors(matrix, lu);
        support::expectNear(solveLu(lu, matrix * expected), expected, 1e-8);
        support::expectNear(matrix * inverse(lu), Matrix::identity(n), 1e-9);
    }
}

TEST(LuTest, RejectsSingularMatrices) {
    EXPECT_THROW(decomposeLu(Matrix{{1.0, 2.0}, {2.0, 4.0}}), std::domain_error);
    EXPECT_THROW(decomposeLu(Matrix(3, 3)), std::domain_error);
}

TEST(LuTest, RejectsInvalidShapes) {
    EXPECT_THROW(decomposeLu(Matrix(2, 3)), std::invalid_argument);
    EXPECT_THROW(decomposeLu(Matrix{}), std::invalid_argument);
    EXPECT_THROW(solveLu(decomposeLu(VARIANT), Vector(3)), std::invalid_argument);
}

}
