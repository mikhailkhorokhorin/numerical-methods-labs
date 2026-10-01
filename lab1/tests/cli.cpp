#include "cli.hpp"

#include <gtest/gtest.h>

#include <cstddef>
#include <filesystem>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "test_support/process.hpp"

namespace {

struct Result {
    int exitCode = 0;
    std::string out;
    std::string err;
};

Result run(Task task, const std::string& input) {
    std::istringstream in(input);
    std::ostringstream out;
    std::ostringstream err;
    const int exitCode = runTask(task, in, out, err);
    return Result{.exitCode = exitCode, .out = out.str(), .err = err.str()};
}

TEST(CliTest, MatchesGoldenOutputs) {
    const std::vector<std::pair<std::string, Task>> tasks{{"lu", runLu},
                                                          {"tridiagonal", runTridiagonal},
                                                          {"iterative", runIterative},
                                                          {"rotation", runRotation},
                                                          {"qr", runQr}};
    for (const auto& [name, task] : tasks) {
        const auto inputs = test_support::inputFiles(std::filesystem::path(TEST_DATA_DIR) / name);
        ASSERT_FALSE(inputs.empty()) << name;
        for (const auto& inputPath : inputs) {
            SCOPED_TRACE(name + "/" + inputPath.filename().string());
            auto expectedPath = inputPath;
            expectedPath.replace_extension(".out");
            const Result result = run(task, test_support::readFile(inputPath));
            EXPECT_EQ(result.exitCode, 0);
            EXPECT_EQ(result.err, "");
            EXPECT_EQ(result.out, test_support::readFile(expectedPath));
        }
    }
}

TEST(CliTest, ReportsErrorsWithoutPartialOutput) {
    const std::vector<std::pair<Task, std::string>> cases{
        {runLu, "2\n1 2\n2 4\n1 1\n"},
        {runLu, "1\n2\n4\n5\n"},
        {runTridiagonal, "2\n1\n0 1\n1\n1 1\n"},
        {runIterative, "2\n1 2\n3 1\n1 1\n0.001\n"},
        {runIterative, "2\n1 2\n3 1\n1 1\n0\n"},
        {runRotation, "2\n1 2\n3 4\n0.001\n"},
        {runQr, "2\n1 2\n3 4\n"},
    };
    const std::vector<std::string> messages{
        "error: matrix is singular\n",
        "error: unexpected trailing input '5'\n",
        "error: zero denominator in the Thomas algorithm\n",
        "error: neither method converged\n",
        "error: precision must be positive\n",
        "error: rotation method needs a symmetric matrix\n",
        "error: unexpected end of input\n",
    };
    for (std::size_t i = 0; i < cases.size(); ++i) {
        SCOPED_TRACE(cases[i].second);
        const Result result = run(cases[i].first, cases[i].second);
        EXPECT_EQ(result.exitCode, 1);
        EXPECT_EQ(result.out, "");
        EXPECT_EQ(result.err, messages[i]);
    }
}

}
