#include "cli.hpp"

#include <cstddef>
#include <exception>
#include <iomanip>
#include <istream>
#include <ostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "io.hpp"
#include "iterative.hpp"
#include "lu.hpp"
#include "qr.hpp"
#include "rotation.hpp"
#include "tridiagonal.hpp"

namespace {

std::string formatIndices(const std::vector<std::size_t>& indices) {
    std::string result = "(";
    for (std::size_t i = 0; i < indices.size(); ++i) {
        if (i > 0) {
            result += ", ";
        }
        result += std::to_string(indices[i] + 1);
    }
    return result + ")";
}

void writeIterationResult(std::ostream& output, const char* name, const IterationResult& result) {
    if (!result.converged) {
        output << name << ": no convergence after " << result.iterations << " iterations\n";
        return;
    }
    output << name << ": " << result.iterations << " iterations\n"
           << "x = " << formatVector(result.solution) << '\n';
}

}

int runTask(Task task, std::istream& input, std::ostream& output, std::ostream& error) {
    try {
        task(input, output);
        return 0;
    } catch (const std::exception& exception) {
        error << "error: " << exception.what() << '\n';
        return 1;
    }
}

void runLu(std::istream& input, std::ostream& output) {
    const std::size_t n = readSize(input);
    const Matrix matrix = readMatrix(input, n);
    const Vector rhs = readVector(input, n);
    expectEnd(input);

    const LuDecomposition lu = decomposeLu(matrix);
    const Vector solution = solveLu(lu, rhs);
    const Matrix inverted = inverse(lu);

    output << "P = " << formatIndices(lu.permutation) << '\n';
    output << "L =\n";
    writeMatrix(output, lu.lower);
    output << "U =\n";
    writeMatrix(output, lu.upper);
    output << "x = " << formatVector(solution) << '\n';
    output << "det(A) = " << formatNumber(determinant(lu)) << '\n';
    output << "A^-1 =\n";
    writeMatrix(output, inverted);
}

void runTridiagonal(std::istream& input, std::ostream& output) {
    const std::size_t n = readSize(input);
    TridiagonalSystem system;
    system.lower = readVector(input, n - 1);
    system.diagonal = readVector(input, n);
    system.upper = readVector(input, n - 1);
    system.rhs = readVector(input, n);
    expectEnd(input);

    const Vector solution = solveTridiagonal(system);

    output << "x = " << formatVector(solution) << '\n';
    output << "Stability condition: " << (meetsStabilityCondition(system) ? "yes" : "no") << '\n';
}

void runIterative(std::istream& input, std::ostream& output) {
    const std::size_t n = readSize(input);
    const Matrix matrix = readMatrix(input, n);
    const Vector rhs = readVector(input, n);
    const double eps = readTolerance(input);
    expectEnd(input);

    const IterationForm form = toIterationForm(matrix, rhs);
    const IterationResult jacobi = simpleIteration(matrix, rhs, eps);
    const IterationResult gaussSeidel = seidel(matrix, rhs, eps);
    const auto estimate = aprioriIterations(matrix, rhs, eps);
    if (!jacobi.converged && !gaussSeidel.converged) {
        throw std::runtime_error("neither method converged");
    }

    output << "||alpha|| = " << formatNumber(normInf(form.alpha)) << '\n';
    output << "A priori estimate: "
           << (estimate ? std::to_string(*estimate) + " iterations" : std::string("none")) << '\n';
    writeIterationResult(output, "Simple iteration", jacobi);
    writeIterationResult(output, "Seidel", gaussSeidel);
}

void runRotation(std::istream& input, std::ostream& output) {
    const std::size_t n = readSize(input);
    const Matrix matrix = readMatrix(input, n);
    const double eps = readTolerance(input);
    expectEnd(input);

    const EigenSystem eigen = rotationMethod(matrix, eps);

    output << "Rotations: " << eigen.rotations << '\n';
    output << "  k  off(A)\n";
    for (std::size_t k = 0; k < eigen.errors.size(); ++k) {
        output << std::setw(3) << k << "  " << formatScientific(eigen.errors[k]) << '\n';
    }
    for (std::size_t i = 0; i < n; ++i) {
        output << "lambda_" << i + 1 << " = " << formatNumber(eigen.values[i]) << ", x_" << i + 1
               << " = " << formatVector(eigen.vectors.column(i)) << '\n';
    }
}

void runQr(std::istream& input, std::ostream& output) {
    const std::size_t n = readSize(input);
    const Matrix matrix = readMatrix(input, n);
    const double eps = readTolerance(input);
    expectEnd(input);

    const QrDecomposition qr = decomposeQr(matrix);
    const QrEigenvalues eigen = qrAlgorithm(matrix, eps);

    output << "Q =\n";
    writeMatrix(output, qr.q);
    output << "R =\n";
    writeMatrix(output, qr.r);
    output << "Iterations: " << eigen.iterations << '\n';
    for (std::size_t i = 0; i < n; ++i) {
        output << "lambda_" << i + 1 << " = " << formatComplex(eigen.values[i]) << '\n';
    }
}
