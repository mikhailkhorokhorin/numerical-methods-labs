#include "iterative.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <utility>

namespace {

constexpr std::size_t MAX_ITERATIONS = 100000;

double upperNormInf(const Matrix& matrix) {
    double result = 0.0;
    for (std::size_t i = 0; i < matrix.rows(); ++i) {
        double rowSum = 0.0;
        for (std::size_t j = i + 1; j < matrix.cols(); ++j) {
            rowSum += std::abs(matrix(i, j));
        }
        result = std::max(result, rowSum);
    }
    return result;
}

bool isFinite(const Vector& vector) {
    for (const double value : vector) {
        if (!std::isfinite(value)) {
            return false;
        }
    }
    return true;
}

template <typename Step>
IterationResult iterate(const IterationForm& form, double eps, double factor, Step step) {
    IterationResult result{.solution = form.beta, .iterations = 0, .converged = false};
    while (result.iterations < MAX_ITERATIONS) {
        Vector next = step(result.solution);
        ++result.iterations;
        if (!isFinite(next)) {
            return result;
        }
        const double error = factor * distanceInf(next, result.solution);
        result.solution = std::move(next);
        if (error <= eps) {
            result.converged = true;
            return result;
        }
    }
    return result;
}

}

IterationForm toIterationForm(const Matrix& matrix, const Vector& rhs) {
    if (!matrix.isSquare() || matrix.rows() == 0 || rhs.size() != matrix.rows()) {
        throw std::invalid_argument("iterative methods need a square matrix and a matching rhs");
    }
    const std::size_t n = matrix.rows();
    IterationForm form{.alpha = Matrix(n, n), .beta = Vector(n)};
    for (std::size_t i = 0; i < n; ++i) {
        const double diagonal = matrix(i, i);
        if (diagonal == 0.0) {
            throw std::domain_error("zero on the main diagonal");
        }
        form.beta[i] = rhs[i] / diagonal;
        for (std::size_t j = 0; j < n; ++j) {
            form.alpha(i, j) = i == j ? 0.0 : -matrix(i, j) / diagonal;
        }
    }
    return form;
}

IterationResult simpleIteration(const Matrix& matrix, const Vector& rhs, double eps) {
    const IterationForm form = toIterationForm(matrix, rhs);
    const double alphaNorm = normInf(form.alpha);
    const double factor = alphaNorm < 1.0 ? alphaNorm / (1.0 - alphaNorm) : 1.0;
    return iterate(form, eps, factor, [&form](const Vector& current) {
        Vector next = form.alpha * current;
        for (std::size_t i = 0; i < next.size(); ++i) {
            next[i] += form.beta[i];
        }
        return next;
    });
}

IterationResult seidel(const Matrix& matrix, const Vector& rhs, double eps) {
    const IterationForm form = toIterationForm(matrix, rhs);
    const double alphaNorm = normInf(form.alpha);
    const double factor = alphaNorm < 1.0 ? upperNormInf(form.alpha) / (1.0 - alphaNorm) : 1.0;
    return iterate(form, eps, factor, [&form](const Vector& current) {
        Vector next = current;
        for (std::size_t i = 0; i < next.size(); ++i) {
            double value = form.beta[i];
            for (std::size_t j = 0; j < next.size(); ++j) {
                value += form.alpha(i, j) * next[j];
            }
            next[i] = value;
        }
        return next;
    });
}

std::optional<std::size_t> aprioriIterations(const Matrix& matrix, const Vector& rhs, double eps) {
    const IterationForm form = toIterationForm(matrix, rhs);
    const double alphaNorm = normInf(form.alpha);
    const double betaNorm = normInf(form.beta);
    if (alphaNorm >= 1.0) {
        return std::nullopt;
    }
    if (alphaNorm == 0.0 || betaNorm == 0.0) {
        return 0;
    }
    const double bound =
        (std::log(eps) - std::log(betaNorm) + std::log(1.0 - alphaNorm)) / std::log(alphaNorm);
    if (!std::isfinite(bound) ||
        bound >= static_cast<double>(std::numeric_limits<std::size_t>::max())) {
        return std::nullopt;
    }
    return bound <= 1.0 ? 0 : static_cast<std::size_t>(std::ceil(bound - 1.0));
}
