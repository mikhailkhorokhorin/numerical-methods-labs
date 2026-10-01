#include "rotation.hpp"

#include <cmath>
#include <numbers>
#include <stdexcept>

namespace {

constexpr std::size_t MAX_ROTATIONS = 100000;
constexpr double SYMMETRY_TOLERANCE = 1e-12;

void rotateColumns(Matrix& matrix, std::size_t i, std::size_t j, double cosine, double sine) {
    for (std::size_t k = 0; k < matrix.rows(); ++k) {
        const double left = matrix(k, i);
        const double right = matrix(k, j);
        matrix(k, i) = cosine * left + sine * right;
        matrix(k, j) = -sine * left + cosine * right;
    }
}

void rotateRows(Matrix& matrix, std::size_t i, std::size_t j, double cosine, double sine) {
    for (std::size_t k = 0; k < matrix.cols(); ++k) {
        const double top = matrix(i, k);
        const double bottom = matrix(j, k);
        matrix(i, k) = cosine * top + sine * bottom;
        matrix(j, k) = -sine * top + cosine * bottom;
    }
}

}

double offDiagonalNorm(const Matrix& matrix) {
    double sum = 0.0;
    for (std::size_t i = 0; i < matrix.rows(); ++i) {
        for (std::size_t j = i + 1; j < matrix.cols(); ++j) {
            sum += matrix(i, j) * matrix(i, j);
        }
    }
    return std::sqrt(sum);
}

EigenSystem rotationMethod(const Matrix& matrix, double eps) {
    if (matrix.rows() == 0 || !isSymmetric(matrix, SYMMETRY_TOLERANCE * normInf(matrix))) {
        throw std::invalid_argument("rotation method needs a symmetric matrix");
    }
    const std::size_t n = matrix.rows();
    Matrix a = matrix;
    EigenSystem result{.values = Vector(n),
                       .vectors = Matrix::identity(n),
                       .errors = {offDiagonalNorm(a)},
                       .rotations = 0};

    while (result.errors.back() > eps) {
        if (result.rotations == MAX_ROTATIONS) {
            throw std::runtime_error("rotation method did not converge");
        }
        std::size_t pivotRow = 0;
        std::size_t pivotCol = 1;
        for (std::size_t i = 0; i < n; ++i) {
            for (std::size_t j = i + 1; j < n; ++j) {
                if (std::abs(a(i, j)) > std::abs(a(pivotRow, pivotCol))) {
                    pivotRow = i;
                    pivotCol = j;
                }
            }
        }
        const double pivot = a(pivotRow, pivotCol);
        const double difference = a(pivotRow, pivotRow) - a(pivotCol, pivotCol);
        const double angle = difference == 0.0 ? std::copysign(std::numbers::pi / 4.0, pivot)
                                               : 0.5 * std::atan(2.0 * pivot / difference);
        const double cosine = std::cos(angle);
        const double sine = std::sin(angle);
        rotateColumns(a, pivotRow, pivotCol, cosine, sine);
        rotateRows(a, pivotRow, pivotCol, cosine, sine);
        a(pivotRow, pivotCol) = 0.0;
        a(pivotCol, pivotRow) = 0.0;
        rotateColumns(result.vectors, pivotRow, pivotCol, cosine, sine);
        ++result.rotations;
        result.errors.push_back(offDiagonalNorm(a));
    }

    for (std::size_t i = 0; i < n; ++i) {
        result.values[i] = a(i, i);
    }
    return result;
}
