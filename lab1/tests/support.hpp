#pragma once

#include <gtest/gtest.h>

#include <cmath>
#include <cstddef>
#include <random>

#include "matrix.hpp"

namespace support {

inline void expectNear(const Vector& actual, const Vector& expected, double tolerance) {
    ASSERT_EQ(actual.size(), expected.size());
    for (std::size_t i = 0; i < actual.size(); ++i) {
        EXPECT_NEAR(actual[i], expected[i], tolerance) << "index " << i;
    }
}

inline void expectNear(const Matrix& actual, const Matrix& expected, double tolerance) {
    ASSERT_EQ(actual.rows(), expected.rows());
    ASSERT_EQ(actual.cols(), expected.cols());
    for (std::size_t i = 0; i < actual.rows(); ++i) {
        for (std::size_t j = 0; j < actual.cols(); ++j) {
            EXPECT_NEAR(actual(i, j), expected(i, j), tolerance) << "at (" << i << ", " << j << ")";
        }
    }
}

inline Matrix randomMatrix(std::size_t n, unsigned seed) {
    std::mt19937 generator(seed);
    std::uniform_real_distribution<double> distribution(-10.0, 10.0);
    Matrix result(n, n);
    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < n; ++j) {
            result(i, j) = distribution(generator);
        }
    }
    return result;
}

inline Vector randomVector(std::size_t n, unsigned seed) {
    std::mt19937 generator(seed);
    std::uniform_real_distribution<double> distribution(-10.0, 10.0);
    Vector result(n);
    for (auto& value : result) {
        value = distribution(generator);
    }
    return result;
}

inline Matrix diagonallyDominant(std::size_t n, unsigned seed) {
    Matrix result = randomMatrix(n, seed);
    for (std::size_t i = 0; i < n; ++i) {
        double sum = 0.0;
        for (std::size_t j = 0; j < n; ++j) {
            sum += j == i ? 0.0 : std::abs(result(i, j));
        }
        result(i, i) = std::copysign(sum + 1.0, result(i, i));
    }
    return result;
}

inline Matrix randomSymmetric(std::size_t n, unsigned seed) {
    const Matrix base = randomMatrix(n, seed);
    Matrix result(n, n);
    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < n; ++j) {
            result(i, j) = (base(i, j) + base(j, i)) / 2.0;
        }
    }
    return result;
}

}
