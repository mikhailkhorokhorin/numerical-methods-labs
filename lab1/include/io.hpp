#pragma once

#include <complex>
#include <cstddef>
#include <iosfwd>
#include <string>

#include "matrix.hpp"

std::size_t readSize(std::istream& input);
double readNumber(std::istream& input);
double readTolerance(std::istream& input);
Vector readVector(std::istream& input, std::size_t size);
Matrix readMatrix(std::istream& input, std::size_t size);
void expectEnd(std::istream& input);

std::string formatNumber(double value);
std::string formatScientific(double value);
std::string formatComplex(std::complex<double> value);
std::string formatVector(const Vector& vector);
void writeMatrix(std::ostream& output, const Matrix& matrix);
