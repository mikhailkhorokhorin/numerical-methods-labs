#include "io.hpp"

#include <algorithm>
#include <charconv>
#include <cmath>
#include <iomanip>
#include <istream>
#include <ostream>
#include <sstream>
#include <stdexcept>
#include <system_error>
#include <vector>

namespace {

constexpr int PRECISION = 4;
constexpr double ZERO_THRESHOLD = 5e-5;
constexpr std::size_t MAX_SIZE = 1000;
constexpr double MAX_ABS_VALUE = 1e100;

std::string readToken(std::istream& input) {
    std::string token;
    if (!(input >> token)) {
        throw std::invalid_argument("unexpected end of input");
    }
    return token;
}

template <typename Number>
Number parseToken(const std::string& token, const char* expected) {
    Number value{};
    const bool hasPlus = token.size() > 1 && token[0] == '+' && token[1] != '-';
    const char* begin = token.data() + (hasPlus ? 1 : 0);
    const char* end = token.data() + token.size();
    const auto [ptr, error] = std::from_chars(begin, end, value);
    if (error != std::errc() || ptr != end) {
        throw std::invalid_argument(std::string("expected ") + expected + ", got '" + token + "'");
    }
    return value;
}

}

std::size_t readSize(std::istream& input) {
    const auto size = parseToken<std::size_t>(readToken(input), "a matrix size");
    if (size == 0 || size > MAX_SIZE) {
        throw std::invalid_argument("matrix size must be between 1 and " +
                                    std::to_string(MAX_SIZE));
    }
    return size;
}

double readNumber(std::istream& input) {
    const auto value = parseToken<double>(readToken(input), "a number");
    if (!std::isfinite(value) || std::abs(value) > MAX_ABS_VALUE) {
        throw std::invalid_argument("numbers must lie in [-1e100, 1e100]");
    }
    return value;
}

double readTolerance(std::istream& input) {
    const double value = readNumber(input);
    if (value <= 0.0) {
        throw std::invalid_argument("precision must be positive");
    }
    return value;
}

Vector readVector(std::istream& input, std::size_t size) {
    Vector result(size);
    for (auto& value : result) {
        value = readNumber(input);
    }
    return result;
}

Matrix readMatrix(std::istream& input, std::size_t size) {
    Matrix result(size, size);
    for (std::size_t i = 0; i < size; ++i) {
        for (std::size_t j = 0; j < size; ++j) {
            result(i, j) = readNumber(input);
        }
    }
    return result;
}

void expectEnd(std::istream& input) {
    std::string token;
    if (input >> token) {
        throw std::invalid_argument("unexpected trailing input '" + token + "'");
    }
}

std::string formatNumber(double value) {
    std::ostringstream stream;
    stream << std::fixed << std::setprecision(PRECISION)
           << (std::abs(value) < ZERO_THRESHOLD ? 0.0 : value);
    return stream.str();
}

std::string formatScientific(double value) {
    std::ostringstream stream;
    stream << std::scientific << std::setprecision(PRECISION) << value;
    return stream.str();
}

std::string formatComplex(std::complex<double> value) {
    if (std::abs(value.imag()) < ZERO_THRESHOLD) {
        return formatNumber(value.real());
    }
    return formatNumber(value.real()) + (value.imag() < 0.0 ? " - " : " + ") +
           formatNumber(std::abs(value.imag())) + "i";
}

std::string formatVector(const Vector& vector) {
    std::string result = "(";
    for (std::size_t i = 0; i < vector.size(); ++i) {
        if (i > 0) {
            result += ", ";
        }
        result += formatNumber(vector[i]);
    }
    return result + ")";
}

void writeMatrix(std::ostream& output, const Matrix& matrix) {
    std::vector<std::string> cells;
    cells.reserve(matrix.rows() * matrix.cols());
    std::size_t width = 0;
    for (std::size_t i = 0; i < matrix.rows(); ++i) {
        for (std::size_t j = 0; j < matrix.cols(); ++j) {
            cells.push_back(formatNumber(matrix(i, j)));
            width = std::max(width, cells.back().size());
        }
    }
    const auto cellWidth = static_cast<int>(width);
    for (std::size_t i = 0; i < matrix.rows(); ++i) {
        for (std::size_t j = 0; j < matrix.cols(); ++j) {
            output << "  " << std::setw(cellWidth) << cells[i * matrix.cols() + j];
        }
        output << '\n';
    }
}
