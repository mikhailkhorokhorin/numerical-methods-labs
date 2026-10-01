#include "qr.hpp"

#include <cmath>
#include <optional>
#include <stdexcept>
#include <utility>

namespace {

constexpr std::size_t MAX_ITERATIONS = 100000;

using Complex = std::complex<double>;
using ComplexPair = std::pair<Complex, Complex>;

double columnTail(const Matrix& matrix, std::size_t col, std::size_t fromRow) {
    double sum = 0.0;
    for (std::size_t i = fromRow; i < matrix.rows(); ++i) {
        sum += matrix(i, col) * matrix(i, col);
    }
    return std::sqrt(sum);
}

ComplexPair blockEigenvalues(const Matrix& matrix, std::size_t j) {
    const double a = matrix(j, j);
    const double b = matrix(j, j + 1);
    const double c = matrix(j + 1, j);
    const double d = matrix(j + 1, j + 1);
    const double halfTrace = (a + d) / 2.0;
    const Complex root = std::sqrt(Complex((a - d) * (a - d) / 4.0 + b * c, 0.0));
    return {halfTrace + root, halfTrace - root};
}

bool isStable(const ComplexPair& current, const std::optional<ComplexPair>& last, double eps) {
    if (!last) {
        return false;
    }
    return std::abs(current.first - last->first) <= eps &&
           std::abs(current.second - last->second) <= eps;
}

std::optional<std::vector<Complex>> extractEigenvalues(
    const Matrix& matrix, double eps, std::vector<std::optional<ComplexPair>>& previous) {
    const std::size_t n = matrix.rows();
    std::vector<Complex> values;
    values.reserve(n);
    bool converged = true;
    std::size_t j = 0;
    while (j < n) {
        if (j + 1 == n || columnTail(matrix, j, j + 1) <= eps) {
            values.emplace_back(matrix(j, j), 0.0);
            ++j;
            continue;
        }
        const ComplexPair current = blockEigenvalues(matrix, j);
        const bool isolated =
            columnTail(matrix, j, j + 2) <= eps && columnTail(matrix, j + 1, j + 2) <= eps;
        const bool stable = isStable(current, previous[j], eps);
        previous[j] = current;
        converged = converged && isolated && stable;
        values.push_back(current.first);
        values.push_back(current.second);
        j += 2;
    }
    if (!converged) {
        return std::nullopt;
    }
    return values;
}

}

QrDecomposition decomposeQr(const Matrix& matrix) {
    if (!matrix.isSquare() || matrix.rows() == 0) {
        throw std::invalid_argument("QR decomposition needs a non-empty square matrix");
    }
    const std::size_t n = matrix.rows();
    QrDecomposition result{.q = Matrix::identity(n), .r = matrix};
    Vector v(n);
    for (std::size_t k = 0; k + 1 < n; ++k) {
        const double norm = columnTail(result.r, k, k);
        if (norm == 0.0) {
            continue;
        }
        v.assign(n, 0.0);
        for (std::size_t i = k; i < n; ++i) {
            v[i] = result.r(i, k);
        }
        v[k] += std::copysign(norm, v[k]);
        double squaredNorm = 0.0;
        for (std::size_t i = k; i < n; ++i) {
            squaredNorm += v[i] * v[i];
        }
        for (std::size_t j = 0; j < n; ++j) {
            double dot = 0.0;
            for (std::size_t i = k; i < n; ++i) {
                dot += v[i] * result.r(i, j);
            }
            const double factor = 2.0 * dot / squaredNorm;
            for (std::size_t i = k; i < n; ++i) {
                result.r(i, j) -= factor * v[i];
            }
        }
        for (std::size_t i = 0; i < n; ++i) {
            double dot = 0.0;
            for (std::size_t j = k; j < n; ++j) {
                dot += result.q(i, j) * v[j];
            }
            const double factor = 2.0 * dot / squaredNorm;
            for (std::size_t j = k; j < n; ++j) {
                result.q(i, j) -= factor * v[j];
            }
        }
        for (std::size_t i = k + 1; i < n; ++i) {
            result.r(i, k) = 0.0;
        }
    }
    return result;
}

QrEigenvalues qrAlgorithm(const Matrix& matrix, double eps) {
    if (!matrix.isSquare() || matrix.rows() == 0) {
        throw std::invalid_argument("QR algorithm needs a non-empty square matrix");
    }
    Matrix a = matrix;
    std::vector<std::optional<ComplexPair>> previous(matrix.rows());
    for (std::size_t iteration = 0; iteration <= MAX_ITERATIONS; ++iteration) {
        if (auto values = extractEigenvalues(a, eps, previous)) {
            return QrEigenvalues{.values = std::move(*values), .iterations = iteration};
        }
        const QrDecomposition qr = decomposeQr(a);
        a = qr.r * qr.q;
    }
    throw std::runtime_error("QR algorithm did not converge");
}
