#include "lu.hpp"

#include <cmath>
#include <numeric>
#include <stdexcept>
#include <utility>

namespace {

constexpr double SINGULARITY_TOLERANCE = 1e-12;

}

LuDecomposition decomposeLu(const Matrix& matrix) {
    if (!matrix.isSquare() || matrix.rows() == 0) {
        throw std::invalid_argument("LU decomposition needs a non-empty square matrix");
    }
    const std::size_t n = matrix.rows();
    const double threshold = SINGULARITY_TOLERANCE * normInf(matrix);
    LuDecomposition result{.lower = Matrix::identity(n),
                           .upper = matrix,
                           .permutation = std::vector<std::size_t>(n),
                           .sign = 1};
    std::iota(result.permutation.begin(), result.permutation.end(), std::size_t{0});
    Matrix& lower = result.lower;
    Matrix& upper = result.upper;

    for (std::size_t k = 0; k < n; ++k) {
        std::size_t pivot = k;
        for (std::size_t i = k + 1; i < n; ++i) {
            if (std::abs(upper(i, k)) > std::abs(upper(pivot, k))) {
                pivot = i;
            }
        }
        if (std::abs(upper(pivot, k)) <= threshold) {
            throw std::domain_error("matrix is singular");
        }
        if (pivot != k) {
            upper.swapRows(k, pivot);
            for (std::size_t j = 0; j < k; ++j) {
                std::swap(lower(k, j), lower(pivot, j));
            }
            std::swap(result.permutation[k], result.permutation[pivot]);
            result.sign = -result.sign;
        }
        for (std::size_t i = k + 1; i < n; ++i) {
            const double factor = upper(i, k) / upper(k, k);
            lower(i, k) = factor;
            upper(i, k) = 0.0;
            for (std::size_t j = k + 1; j < n; ++j) {
                upper(i, j) -= factor * upper(k, j);
            }
        }
    }
    return result;
}

Vector solveLu(const LuDecomposition& lu, const Vector& rhs) {
    const std::size_t n = lu.upper.rows();
    if (rhs.size() != n) {
        throw std::invalid_argument("right-hand side size does not match the matrix");
    }
    Vector solution(n);
    for (std::size_t i = 0; i < n; ++i) {
        double sum = rhs[lu.permutation[i]];
        for (std::size_t j = 0; j < i; ++j) {
            sum -= lu.lower(i, j) * solution[j];
        }
        solution[i] = sum;
    }
    for (std::size_t i = n; i-- > 0;) {
        double sum = solution[i];
        for (std::size_t j = i + 1; j < n; ++j) {
            sum -= lu.upper(i, j) * solution[j];
        }
        solution[i] = sum / lu.upper(i, i);
    }
    return solution;
}

double determinant(const LuDecomposition& lu) {
    double result = lu.sign;
    for (std::size_t i = 0; i < lu.upper.rows(); ++i) {
        result *= lu.upper(i, i);
    }
    return result;
}

Matrix inverse(const LuDecomposition& lu) {
    const std::size_t n = lu.upper.rows();
    Matrix result(n, n);
    Vector unit(n);
    for (std::size_t j = 0; j < n; ++j) {
        unit.assign(n, 0.0);
        unit[j] = 1.0;
        const Vector column = solveLu(lu, unit);
        for (std::size_t i = 0; i < n; ++i) {
            result(i, j) = column[i];
        }
    }
    return result;
}
