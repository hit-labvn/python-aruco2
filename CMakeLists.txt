cmake_minimum_required(VERSION 3.24)
project(python_aruco2 LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

option(ARUCO2_BUILD_OPENCV "Build a private static OpenCV instead of using an installed SDK" ON)
if(ARUCO2_BUILD_OPENCV)
  include(FetchContent)
  set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
  set(BUILD_LIST core,imgproc,flann,calib3d CACHE STRING "" FORCE)
  foreach(opt BUILD_TESTS BUILD_PERF_TESTS BUILD_EXAMPLES BUILD_opencv_apps BUILD_JAVA
      BUILD_opencv_python2 BUILD_opencv_python3 WITH_IPP WITH_ITT WITH_FFMPEG WITH_MSMF
      WITH_VTK WITH_QT WITH_GTK WITH_OPENCL OPENCV_ENABLE_NONFREE)
    set(${opt} OFF CACHE BOOL "" FORCE)
  endforeach()
  set(OPENCV_FORCE_3RDPARTY_BUILD ON CACHE BOOL "" FORCE)
  set(OPENCV_SKIP_PYTHON_LOADER ON CACHE BOOL "" FORCE)
  FetchContent_Declare(opencv URL https://github.com/opencv/opencv/archive/refs/tags/4.12.0.tar.gz
      URL_HASH SHA256=44c106d5bb47efec04e531fd93008b3fcd1d27138985c5baf4eafac0e1ec9e9d
      DOWNLOAD_EXTRACT_TIMESTAMP TRUE)
  FetchContent_MakeAvailable(opencv)
  set(OpenCV_LIBS opencv_core opencv_imgproc opencv_flann opencv_calib3d)
  set(OpenCV_INCLUDE_DIRS "${opencv_BINARY_DIR}" "${opencv_SOURCE_DIR}/include")
  foreach(mod core imgproc flann calib3d features2d highgui imgcodecs videoio)
    list(APPEND OpenCV_INCLUDE_DIRS "${opencv_SOURCE_DIR}/modules/${mod}/include")
  endforeach()
else()
  find_package(OpenCV 4 REQUIRED COMPONENTS core imgproc flann calib3d)
endif()

set(ARUCO2_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vendor/aruco2")
add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/opencl_kernels_aruco2.hpp"
    "${CMAKE_CURRENT_BINARY_DIR}/opencl_kernels_aruco2.cpp"
  COMMAND ${CMAKE_COMMAND}
    "-DCL_PATH=${ARUCO2_SOURCE_DIR}/opencl/aruco2detect.cl"
    "-DHPP_PATH=${CMAKE_CURRENT_BINARY_DIR}/opencl_kernels_aruco2.hpp"
    "-DCPP_PATH=${CMAKE_CURRENT_BINARY_DIR}/opencl_kernels_aruco2.cpp"
    -P "${ARUCO2_SOURCE_DIR}/utils/cl2cpp.cmake"
  DEPENDS "${ARUCO2_SOURCE_DIR}/opencl/aruco2detect.cl" "${ARUCO2_SOURCE_DIR}/utils/cl2cpp.cmake")
pybind11_add_module(_native MODULE cpp/bindings.cpp
    "${ARUCO2_SOURCE_DIR}/src/aruco2.cpp"
    "${ARUCO2_SOURCE_DIR}/src/aruco2_dictionary.cpp"
    "${ARUCO2_SOURCE_DIR}/src/aruco2_fractal.cpp"
    "${CMAKE_CURRENT_BINARY_DIR}/opencl_kernels_aruco2.cpp")
target_include_directories(_native PRIVATE ${OpenCV_INCLUDE_DIRS}
    "${ARUCO2_SOURCE_DIR}" "${ARUCO2_SOURCE_DIR}/src" "${CMAKE_CURRENT_BINARY_DIR}")
target_link_libraries(_native PRIVATE ${OpenCV_LIBS})
option(ARUCO2_STATIC_CRT "Match an external OpenCV SDK built with the static MSVC runtime" OFF)
if(MSVC AND ((ARUCO2_BUILD_OPENCV AND BUILD_WITH_STATIC_CRT) OR ARUCO2_STATIC_CRT))
  set_property(TARGET _native PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()
if(MSVC)
  target_compile_options(_native PRIVATE /bigobj /utf-8)
endif()
install(TARGETS _native RUNTIME DESTINATION aruco2 COMPONENT python-aruco2
    LIBRARY DESTINATION aruco2 COMPONENT python-aruco2)

install(FILES "${ARUCO2_SOURCE_DIR}/LICENSE" DESTINATION aruco2/licenses RENAME aruco2-LICENSE COMPONENT python-aruco2)
if(ARUCO2_BUILD_OPENCV)
  install(FILES "${opencv_SOURCE_DIR}/LICENSE" DESTINATION aruco2/licenses RENAME opencv-LICENSE COMPONENT python-aruco2)
endif()
