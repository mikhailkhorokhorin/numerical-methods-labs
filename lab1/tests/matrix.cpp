#include "matrix.hpp"

#include <gtest/gtest.h>

#include <stdexcept>

#include "support.hpp"

namespace {

TEST(MatrixTest, BuildsFromRowsAndIdentity) {
    const Matrix matrix{{1.0, 2.0, 3.0}, {4.0, 5.0, 6.0}};
    EXPECT_EQ(matrix.rows(), 2U);
    EXPECT_EQ(matrix.cols(), 3U);
    EXPECT_FALSE(matrix.isSquare());
    EXPECT_DOUBLE_EQ(matrix(1, 2), 6.0);
    support::expectNear(Matrix::identity(2), Matrix{{1.0, 0.0}, {0.0, 1.0}}, 0.0);
    EXPECT_EQ(Matrix{}.rows(), 0U);
}

TEST(MatrixTest, RejectsRaggedRows) {
    EXPECT_THROW((Matrix{{1.0, 2.0}, {3.0}}), std::invalid_argument);
}

TEST(MatrixTest, ExtractsColumnsTransposesAndSwapsRows) {
    Matrix matrix{{1.0, 2.0}, {3.0, 4.0}, {5.0, 6.0}};
    support::expectNear(matrix.column(1), Vector{2.0, 4.0, 6.0}, 0.0);
    support::expectNear(matrix.transposed(), Matrix{{1.0, 3.0, 5.0}, {2.0, 4.0, 6.0}}, 0.0);
    matrix.swapRows(0, 2);
    matrix.swapRows(1, 1);
    support::expectNear(matrix, Matrix{{5.0, 6.0}, {3.0, 4.0}, {1.0, 2.0}}, 0.0);
}

TEST(MatrixTest, Multiplies) {
    const Matrix lhs{{1.0, 2.0}, {3.0, 4.0}};
    const Matrix rhs{{0.0, 1.0}, {1.0, 0.0}};
    support::expectNear(lhs * rhs, Matrix{{2.0, 1.0}, {4.0, 3.0}}, 0.0);
    support::expectNear(lhs * Vector{1.0, -1.0}, Vector{-1.0, -1.0}, 0.0);
    EXPECT_THROW(lhs * Matrix(3, 1), std::invalid_argument);
    EXPECT_THROW(lhs * Vector(3), std::invalid_argument);
}

TEST(MatrixTest, ComputesInfinityNorms) {
    EXPECT_DOUBLE_EQ(normInf(Vector{1.0, -7.0, 3.0}), 7.0);
    EXPECT_DOUBLE_EQ(normInf(Matrix{{1.0, -2.0}, {-3.0, 0.5}}), 3.5);
    EXPECT_DOUBLE_EQ(distanceInf(Vector{1.0, 2.0}, Vector{1.5, -1.0}), 3.0);
    EXPECT_THROW(distanceInf(Vector{1.0}, Vector{1.0, 2.0}), std::invalid_argument);
}

TEST(MatrixTest, ChecksSymmetry) {
    EXPECT_TRUE(isSymmetric(Matrix{{1.0, 2.0}, {2.0, 3.0}}));
    EXPECT_FALSE(isSymmetric(Matrix{{1.0, 2.0}, {2.1, 3.0}}));
    EXPECT_TRUE(isSymmetric(Matrix{{1.0, 2.0}, {2.1, 3.0}}, 0.2));
    EXPECT_FALSE(isSymmetric(Matrix(2, 3)));
}

}
