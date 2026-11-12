# Upstream sources

The Python binding, packaging, tests, and CI configuration are licensed under Apache-2.0; see the root LICENSE and NOTICE. Third-party files retain the licenses below.

ArUco2: https://github.com/rmsalinas/aruco2
Commit: c26b030cee4292649be566092812308fa179e871
License: Apache-2.0, retained in vendor/aruco2/LICENSE.

The binding compiles aruco2_dictionary.cpp (the source referenced by current aruco2.cpp), rather than the older aruco_dictionary.cpp listed by upstream CMakeLists.txt. Local patch: the public DictionaryType enum is missing DICT_RARUCO_16h4, which is referenced by aruco2_dictionary.cpp. We append this enum value without renumbering existing values. Upstream sources are otherwise unmodified.

OpenCV: https://github.com/opencv/opencv, tag 4.12.0, Apache-2.0.
Its license is included in the installed package when building the private copy.
pybind11: https://github.com/pybind/pybind11, BSD-style license, build dependency.
Local patch: disabled the OpenCV-internal ../precomp.hpp include in aruco2_dictionary.cpp for standalone compilation.
Local patch: removed the unused highgui include from aruco2.cpp so a headless OpenCV SDK suffices.
