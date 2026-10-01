#include "matrix.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <utility>

Matrix::Matrix(std::size_t rows, std::size_t cols) : rows_(rows), cols_(cols), data_(rows * cols) {
}

Matrix::Matrix(std::initializer_list<std::initializer_list<double>> rows)
    : rows_(rows.size()), cols_(rows.size() == 0 ? 0 : rows.begin()->size()) {
    data_.reserve(rows_ * cols_);
    for (const auto& row : rows) {
        if (row.size() != cols_) {
            throw std::invalid_argument("matrix rows have different lengths");
        }
        data_.insert(data_.end(), row.begin(), row.end());
    }
}

Matrix Matrix::identity(std::size_t size) {
    Matrix result(size, size);
    for (std::size_t i = 0; i < size; ++i) {
        result(i, i) = 1.0;
    }
    return result;
}

Vector Matrix::column(std::size_t col) const {
    Vector result(rows_);
    for (std::size_t i = 0; i < rows_; ++i) {
        result[i] = (*this)(i, col);
    }
    return result;
}

Matrix Matrix::transposed() const {
    Matrix result(cols_, rows_);
    for (std::size_t i = 0; i < rows_; ++i) {
        for (std::size_t j = 0; j < cols_; ++j) {
            result(j, i) = (*this)(i, j);
        }
    }
    return result;
}

void Matrix::swapRows(std::size_t first, std::size_t second) {
    if (first == second) {
        return;
    }
    for (std::size_t j = 0; j < cols_; ++j) {
        std::swap((*this)(first, j), (*this)(second, j));
    }
}

Matrix operator*(const Matrix& lhs, const Matrix& rhs) {
    if (lhs.cols() != rhs.rows()) {
        throw std::invalid_argument("matrix sizes do not match");
    }
    Matrix result(lhs.rows(), rhs.cols());
    for (std::size_t i = 0; i < lhs.rows(); ++i) {
        for (std::size_t k = 0; k < lhs.cols(); ++k) {
            for (std::size_t j = 0; j < rhs.cols(); ++j) {
                result(i, j) += lhs(i, k) * rhs(k, j);
            }
        }
    }
    return result;
}

Vector operator*(const Matrix& matrix, const Vector& vector) {
    if (matrix.cols() != vector.size()) {
        throw std::invalid_argument("matrix and vector sizes do not match");
    }
    Vector result(matrix.rows());
    for (std::size_t i = 0; i < matrix.rows(); ++i) {
        for (std::size_t j = 0; j < matrix.cols(); ++j) {
            result[i] += matrix(i, j) * vector[j];
        }
    }
    return result;
}

double normInf(const Vector& vector) {
    double result = 0.0;
    for (const double value : vector) {
        result = std::max(result, std::abs(value));
    }
    return result;
}

double normInf(const Matrix& matrix) {
    double result = 0.0;
    for (std::size_t i = 0; i < matrix.rows(); ++i) {
        double rowSum = 0.0;
        for (std::size_t j = 0; j < matrix.cols(); ++j) {
            rowSum += std::abs(matrix(i, j));
        }
        result = std::max(result, rowSum);
    }
    return result;
}

double distanceInf(const Vector& lhs, const Vector& rhs) {
    if (lhs.size() != rhs.size()) {
        throw std::invalid_argument("vector sizes do not match");
    }
    double result = 0.0;
    for (std::size_t i = 0; i < lhs.size(); ++i) {
        result = std::max(result, std::abs(lhs[i] - rhs[i]));
    }
    return result;
}

bool isSymmetric(const Matrix& matrix, double tolerance) {
    if (!matrix.isSquare()) {
        return false;
    }
    for (std::size_t i = 0; i < matrix.rows(); ++i) {
        for (std::size_t j = i + 1; j < matrix.cols(); ++j) {
            if (std::abs(matrix(i, j) - matrix(j, i)) > tolerance) {
                return false;
            }
        }
    }
    return true;
}
