#include "rotation.hpp"

#include <gtest/gtest.h>

#include <algorithm>
#include <cstddef>
#include <stdexcept>

#include "support.hpp"

namespace {

const Matrix VARIANT{{3.0, 2.0, 6.0}, {2.0, -3.0, -7.0}, {6.0, -7.0, 3.0}};

void expectEigenpairs(const Matrix& matrix, const EigenSystem& eigen, double tolerance) {
    const std::size_t n = matrix.rows();
    support::expectNear(eigen.vectors.transposed() * eigen.vectors, Matrix::identity(n), 1e-12);
    for (std::size_t i = 0; i < n; ++i) {
        const Vector vector = eigen.vectors.column(i);
        Vector scaled = vector;
        for (auto& value : scaled) {
            value *= eigen.values[i];
        }
        support::expectNear(matrix * vector, scaled, tolerance);
    }
}

TEST(RotationTest, SolvesVariant) {
    const EigenSystem eigen = rotationMethod(VARIANT, 1e-10);
    Vector sorted = eigen.values;
    std::sort(sorted.begin(), sorted.end());
    support::expectNear(sorted, Vector{-9.70682766, 2.47747768, 10.22934998}, 1e-8);
    expectEigenpairs(VARIANT, eigen, 1e-9);
}

TEST(RotationTest, ErrorDecreasesWithEveryRotation) {
    const double eps = 1e-12;
    const EigenSystem eigen = rotationMethod(VARIANT, eps);
    ASSERT_EQ(eigen.errors.size(), eigen.rotations + 1);
    EXPECT_NEAR(eigen.errors.front(), offDiagonalNorm(VARIANT), 0.0);
    EXPECT_LE(eigen.errors.back(), eps);
    for (std::size_t k = 1; k < eigen.errors.size(); ++k) {
        EXPECT_LT(eigen.errors[k], eigen.errors[k - 1]);
    }
}

TEST(RotationTest, MoreRotationsForHigherPrecision) {
    EXPECT_LT(rotationMethod(VARIANT, 1e-2).rotations, rotationMethod(VARIANT, 1e-10).rotations);
}

TEST(RotationTest, SolvesRandomSymmetricMatrices) {
    for (std::size_t n = 1; n <= 7; ++n) {
        const Matrix matrix = support::randomSymmetric(n, static_cast<unsigned>(n));
        expectEigenpairs(matrix, rotationMethod(matrix, 1e-12), 1e-9);
    }
}

TEST(RotationTest, HandlesEqualDiagonalEntries) {
    const EigenSystem eigen = rotationMethod(Matrix{{2.0, -1.0}, {-1.0, 2.0}}, 1e-12);
    EXPECT_EQ(eigen.rotations, 1U);
    Vector sorted = eigen.values;
    std::sort(sorted.begin(), sorted.end());
    support::expectNear(sorted, Vector{1.0, 3.0}, 1e-12);
}

TEST(RotationTest, DiagonalMatrixNeedsNoRotations) {
    const EigenSystem eigen = rotationMethod(Matrix{{5.0, 0.0}, {0.0, -1.0}}, 1e-6);
    EXPECT_EQ(eigen.rotations, 0U);
    support::expectNear(eigen.values, Vector{5.0, -1.0}, 0.0);
    support::expectNear(eigen.vectors, Matrix::identity(2), 0.0);
}

TEST(RotationTest, RejectsNonSymmetricMatrices) {
    EXPECT_THROW(rotationMethod(Matrix{{1.0, 2.0}, {3.0, 4.0}}, 1e-6), std::invalid_argument);
    EXPECT_THROW(rotationMethod(Matrix(2, 3), 1e-6), std::invalid_argument);
    EXPECT_THROW(rotationMethod(Matrix{}, 1e-6), std::invalid_argument);
}

}
