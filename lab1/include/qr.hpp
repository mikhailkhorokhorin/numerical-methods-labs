#pragma once

#include <complex>
#include <cstddef>
#include <vector>

#include "matrix.hpp"

struct QrDecomposition {
    Matrix q;
    Matrix r;
};

struct QrEigenvalues {
    std::vector<std::complex<double>> values;
    std::size_t iterations = 0;
};

QrDecomposition decomposeQr(const Matrix& matrix);
QrEigenvalues qrAlgorithm(const Matrix& matrix, double eps);
