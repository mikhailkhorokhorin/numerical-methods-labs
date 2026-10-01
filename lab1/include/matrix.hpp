#pragma once

#include <cstddef>
#include <initializer_list>
#include <vector>

using Vector = std::vector<double>;

class Matrix {
public:
    Matrix() = default;
    Matrix(std::size_t rows, std::size_t cols);
    Matrix(std::initializer_list<std::initializer_list<double>> rows);

    static Matrix identity(std::size_t size);

    std::size_t rows() const { return rows_; }
    std::size_t cols() const { return cols_; }
    bool isSquare() const { return rows_ == cols_; }

    double& operator()(std::size_t row, std::size_t col) { return data_[row * cols_ + col]; }
    double operator()(std::size_t row, std::size_t col) const { return data_[row * cols_ + col]; }

    Vector column(std::size_t col) const;
    Matrix transposed() const;
    void swapRows(std::size_t first, std::size_t second);

private:
    std::size_t rows_ = 0;
    std::size_t cols_ = 0;
    Vector data_;
};

Matrix operator*(const Matrix& lhs, const Matrix& rhs);
Vector operator*(const Matrix& matrix, const Vector& vector);

double normInf(const Vector& vector);
double normInf(const Matrix& matrix);
double distanceInf(const Vector& lhs, const Vector& rhs);
bool isSymmetric(const Matrix& matrix, double tolerance = 0.0);
