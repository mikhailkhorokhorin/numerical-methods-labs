lab_library(lab1_core
    SOURCES
        src/matrix.cpp
        src/io.cpp
        src/lu.cpp
        src/tridiagonal.cpp
        src/iterative.cpp
        src/rotation.cpp
        src/qr.cpp
        src/cli.cpp
)

foreach(app IN ITEMS lu tridiagonal iterative rotation qr)
    lab_executable(lab1_${app}
        SOURCES app/${app}.cpp
        LINK lab1_core
    )
endforeach()

lab_tests(lab1_tests
    SOURCES
        tests/matrix.cpp
        tests/io.cpp
        tests/lu.cpp
        tests/tridiagonal.cpp
        tests/iterative.cpp
        tests/rotation.cpp
        tests/qr.cpp
        tests/cli.cpp
        tests/e2e.cpp
    LINK lab1_core
    BINARIES lab1_lu lab1_tridiagonal lab1_iterative lab1_rotation lab1_qr
)
