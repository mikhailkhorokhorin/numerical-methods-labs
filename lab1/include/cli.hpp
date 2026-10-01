#pragma once

#include <iosfwd>

using Task = void (*)(std::istream& input, std::ostream& output);

int runTask(Task task, std::istream& input, std::ostream& output, std::ostream& error);

void runLu(std::istream& input, std::ostream& output);
void runTridiagonal(std::istream& input, std::ostream& output);
void runIterative(std::istream& input, std::ostream& output);
void runRotation(std::istream& input, std::ostream& output);
void runQr(std::istream& input, std::ostream& output);
