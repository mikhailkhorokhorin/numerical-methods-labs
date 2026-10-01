#include <gtest/gtest.h>

#include <filesystem>
#include <ostream>
#include <string>

#include "test_support/process.hpp"

namespace {

struct App {
    std::string name;
    std::string path;
};

void PrintTo(const App& app, std::ostream* output) {
    *output << app.name;
}

class E2eTest : public ::testing::TestWithParam<App> {};

TEST_P(E2eTest, MatchesExpectedOutputs) {
    const auto inputs =
        test_support::inputFiles(std::filesystem::path(TEST_DATA_DIR) / GetParam().name);
    ASSERT_FALSE(inputs.empty());
    for (const auto& inputPath : inputs) {
        SCOPED_TRACE(inputPath.filename().string());
        auto expectedPath = inputPath;
        expectedPath.replace_extension(".out");
        const auto result =
            test_support::runProcess(GetParam().path, {}, test_support::readFile(inputPath));
        EXPECT_EQ(result.exitCode, 0);
        EXPECT_EQ(result.err, "");
        EXPECT_EQ(result.out, test_support::readFile(expectedPath));
    }
}

TEST_P(E2eTest, FailsOnEmptyInput) {
    const auto result = test_support::runProcess(GetParam().path);
    EXPECT_EQ(result.exitCode, 1);
    EXPECT_EQ(result.out, "");
    EXPECT_EQ(result.err, "error: unexpected end of input\n");
}

TEST_P(E2eTest, FailsOnMalformedInput) {
    const auto result = test_support::runProcess(GetParam().path, {}, "2\n1 x\n");
    EXPECT_EQ(result.exitCode, 1);
    EXPECT_EQ(result.out, "");
    EXPECT_EQ(result.err, "error: expected a number, got 'x'\n");
}

INSTANTIATE_TEST_SUITE_P(
    Apps, E2eTest,
    ::testing::Values(App{"lu", LAB1_LU_PATH}, App{"tridiagonal", LAB1_TRIDIAGONAL_PATH},
                      App{"iterative", LAB1_ITERATIVE_PATH}, App{"rotation", LAB1_ROTATION_PATH},
                      App{"qr", LAB1_QR_PATH}),
    [](const ::testing::TestParamInfo<App>& paramInfo) { return paramInfo.param.name; });

}
