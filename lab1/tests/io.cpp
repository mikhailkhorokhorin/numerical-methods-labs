#include "io.hpp"

#include <gtest/gtest.h>

#include <complex>
#include <sstream>
#include <stdexcept>
#include <string>

#include "support.hpp"

namespace {

TEST(IoTest, ReadsSizesNumbersAndMatrices) {
    std::istringstream input("2  1 -2.5\n3e-1 4\n  0.001");
    const std::size_t n = readSize(input);
    EXPECT_EQ(n, 2U);
    support::expectNear(readMatrix(input, n), Matrix{{1.0, -2.5}, {0.3, 4.0}}, 0.0);
    EXPECT_DOUBLE_EQ(readTolerance(input), 0.001);
    EXPECT_NO_THROW(expectEnd(input));
}

TEST(IoTest, ReadsVectors) {
    std::istringstream input("1 2 3");
    support::expectNear(readVector(input, 3), Vector{1.0, 2.0, 3.0}, 0.0);
}

TEST(IoTest, AcceptsExplicitPlusAndLargeNumbers) {
    std::istringstream input("+2 +1.5 -1e100 1e100");
    EXPECT_EQ(readSize(input), 2U);
    support::expectNear(readVector(input, 3), Vector{1.5, -1e100, 1e100}, 0.0);
}

TEST(IoTest, RejectsInvalidSizes) {
    for (const std::string text : {"0", "-1", "2.5", "abc", "1001", ""}) {
        std::istringstream input(text);
        EXPECT_THROW(readSize(input), std::invalid_argument) << text;
    }
}

TEST(IoTest, RejectsInvalidNumbers) {
    for (const std::string text : {"1x", "nan", "inf", "-", "+", "+-1", "1e101", "-1e400", ""}) {
        std::istringstream input(text);
        EXPECT_THROW(readNumber(input), std::invalid_argument) << text;
    }
}

TEST(IoTest, RejectsNonPositiveTolerance) {
    for (const std::string text : {"0", "-0.1"}) {
        std::istringstream input(text);
        EXPECT_THROW(readTolerance(input), std::invalid_argument) << text;
    }
}

TEST(IoTest, RejectsTrailingInput) {
    std::istringstream input("1 2");
    readNumber(input);
    EXPECT_THROW(expectEnd(input), std::invalid_argument);
}

TEST(IoTest, ReportsTheOffendingToken) {
    std::istringstream input("oops");
    try {
        readNumber(input);
        FAIL();
    } catch (const std::invalid_argument& error) {
        EXPECT_STREQ(error.what(), "expected a number, got 'oops'");
    }
}

TEST(IoTest, FormatsNumbers) {
    EXPECT_EQ(formatNumber(1.23456), "1.2346");
    EXPECT_EQ(formatNumber(-2.0), "-2.0000");
    EXPECT_EQ(formatNumber(-0.00001), "0.0000");
    EXPECT_EQ(formatScientific(0.000123), "1.2300e-04");
    EXPECT_EQ(formatVector(Vector{1.0, -0.5}), "(1.0000, -0.5000)");
    EXPECT_EQ(formatVector(Vector{}), "()");
}

TEST(IoTest, FormatsComplexNumbers) {
    EXPECT_EQ(formatComplex({1.5, 0.0}), "1.5000");
    EXPECT_EQ(formatComplex({1.5, 1e-9}), "1.5000");
    EXPECT_EQ(formatComplex({1.0, 2.0}), "1.0000 + 2.0000i");
    EXPECT_EQ(formatComplex({-1.0, -2.0}), "-1.0000 - 2.0000i");
}

TEST(IoTest, WritesAlignedMatrices) {
    std::ostringstream output;
    writeMatrix(output, Matrix{{1.0, -10.0}, {100.0, 0.0}});
    EXPECT_EQ(output.str(),
              "    1.0000  -10.0000\n"
              "  100.0000    0.0000\n");
}

}
