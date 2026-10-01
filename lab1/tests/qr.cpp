#include "qr.hpp"

#include <gtest/gtest.h>

#include <algorithm>
#include <complex>
#include <cstddef>
#include <stdexcept>
#include <vector>

#include "lu.hpp"
#include "rotation.hpp"
#include "support.hpp"

namespace {

using Complex = std::complex<double>;

const Matrix VARIANT{{6.0, -3.0, 7.0}, {9.0, 1.0, -6.0}, {3.0, -5.0, 5.0}};

std::vector<Complex> sorted(std::vector<Complex> values) {
    std::sort(values.begin(), values.end(), [](Complex lhs, Complex rhs) {
        return lhs.real() != rhs.real() ? lhs.real() < rhs.real() : lhs.imag() < rhs.imag();
    });
    return values;
}

void expectValues(const std::vector<Complex>& actual, const std::vector<Complex>& expected,
                  double tolerance) {
    const auto lhs = sorted(actual);
    const auto rhs = sorted(expected);
    ASSERT_EQ(lhs.size(), rhs.size());
    for (std::size_t i = 0; i < lhs.size(); ++i) {
        EXPECT_NEAR(std::abs(lhs[i] - rhs[i]), 0.0, tolerance) << "index " << i;
    }
}

void expectValidDecomposition(const Matrix& matrix) {
    const QrDecomposition qr = decomposeQr(matrix);
    const std::size_t n = matrix.rows();
    support::expectNear(qr.q.transposed() * qr.q, Matrix::identity(n), 1e-12);
    support::expectNear(qr.q * qr.r, matrix, 1e-10);
    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < i; ++j) {
            EXPECT_DOUBLE_EQ(qr.r(i, j), 0.0);
        }
    }
}

TEST(QrTest, DecomposesMatrices) {
    expectValidDecomposition(VARIANT);
    expectValidDecomposition(Matrix{{0.0, 1.0}, {0.0, 2.0}});
    for (std::size_t n = 1; n <= 7; ++n) {
        expectValidDecomposition(support::randomMatrix(n, static_cast<unsigned>(n)));
    }
}

TEST(QrTest, FindsComplexEigenvaluesOfVariant) {
    const QrEigenvalues eigen = qrAlgorithm(VARIANT, 1e-10);
    expectValues(eigen.values,
                 {Complex(-3.82791541, 0.0), Complex(7.91395771, 3.86745327),
                  Complex(7.91395771, -3.86745327)},
                 1e-7);
}

TEST(QrTest, MoreIterationsForHigherPrecision) {
    EXPECT_LT(qrAlgorithm(VARIANT, 1e-2).iterations, qrAlgorithm(VARIANT, 1e-8).iterations);
}

TEST(QrTest, FindsImaginaryPair) {
    const QrEigenvalues eigen = qrAlgorithm(Matrix{{0.0, -1.0}, {1.0, 0.0}}, 1e-10);
    expectValues(eigen.values, {Complex(0.0, 1.0), Complex(0.0, -1.0)}, 1e-12);
}

TEST(QrTest, TriangularMatrixNeedsNoIterations) {
    const QrEigenvalues eigen = qrAlgorithm(Matrix{{1.0, 2.0}, {0.0, 3.0}}, 1e-6);
    EXPECT_EQ(eigen.iterations, 0U);
    expectValues(eigen.values, {Complex(1.0, 0.0), Complex(3.0, 0.0)}, 0.0);
}

TEST(QrTest, MatchesRotationMethodOnSymmetricMatrices) {
    for (std::size_t n = 2; n <= 6; ++n) {
        const Matrix matrix = support::randomSymmetric(n, static_cast<unsigned>(n));
        std::vector<Complex> expected;
        for (const double value : rotationMethod(matrix, 1e-12).values) {
            expected.emplace_back(value, 0.0);
        }
        expectValues(qrAlgorithm(matrix, 1e-10).values, expected, 1e-7);
    }
}

TEST(QrTest, EigenvaluesMatchTraceAndDeterminant) {
    for (std::size_t n = 2; n <= 6; ++n) {
        const Matrix matrix = support::randomMatrix(n, static_cast<unsigned>(10 + n));
        const QrEigenvalues eigen = qrAlgorithm(matrix, 1e-10);
        Complex sum = 0.0;
        Complex product = 1.0;
        double trace = 0.0;
        for (std::size_t i = 0; i < n; ++i) {
            sum += eigen.values[i];
            product *= eigen.values[i];
            trace += matrix(i, i);
        }
        const double det = determinant(decomposeLu(matrix));
        EXPECT_NEAR(std::abs(sum - trace), 0.0, 1e-7);
        EXPECT_NEAR(std::abs(product - det), 0.0, 1e-6 * std::max(1.0, std::abs(det)));
    }
}

TEST(QrTest, ThrowsWhenEigenvaluesHaveEqualModuli) {
    const Matrix cyclic{{0.0, 0.0, 1.0}, {1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}};
    EXPECT_THROW(qrAlgorithm(cyclic, 1e-6), std::runtime_error);
}

TEST(QrTest, RejectsInvalidShapes) {
    EXPECT_THROW(decomposeQr(Matrix(2, 3)), std::invalid_argument);
    EXPECT_THROW(decomposeQr(Matrix{}), std::invalid_argument);
    EXPECT_THROW(qrAlgorithm(Matrix(3, 2), 1e-6), std::invalid_argument);
}

}
