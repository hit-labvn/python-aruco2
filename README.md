# python-aruco2

[![Wheels](https://github.com/hit-labvn/python-aruco2/actions/workflows/wheels.yml/badge.svg?branch=main)](https://github.com/hit-labvn/python-aruco2/actions/workflows/wheels.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Standalone Python/NumPy bindings for rmsalinas/aruco2. Distribution: `python-aruco2`; import: `aruco2`.

## Build on Windows

Requires Python 3.10+, CMake 3.24+ and Visual Studio 2022 with Desktop development with C++.

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe ".[test]"
.venv/Scripts/python.exe -m pytest
```

The first build downloads OpenCV 4.12.0 and compiles private static CPU libraries. No cv2 installation or OpenCV DLL search path is needed. Internet is needed for build dependencies and OpenCV on the first build. The runtime depends only on NumPy and the normal Microsoft Visual C++ runtime. The same CMake project is used for Linux and macOS wheel builds in CI.

To use an existing OpenCV C++ SDK instead:

```powershell
uv pip install . --config-settings "cmake.define.ARUCO2_BUILD_OPENCV=OFF" --config-settings "cmake.define.OpenCV_DIR=C:/opencv/build"
```

For an external Windows SDK compiled with /MT, also pass `--config-settings "cmake.define.ARUCO2_STATIC_CRT=ON"`. With an external shared SDK, distributing its runtime libraries is your responsibility. The opencv-python wheel does not provide a C++ SDK.

## Usage

```python
import aruco2
import numpy as np

image = aruco2.getFiducialMarkerImage(aruco2.DICT_6X6_250, 42)
markers = aruco2.detectFiducialMarkers(image, aruco2.DICT_6X6_250)
for marker in markers:
    print(marker.id, marker.corners)  # float32 (4, 2), clockwise
    object_points, image_points = aruco2.getSolvePnpPoints(marker, markerSize=0.05)
    # Pass these arrays to cv2.solvePnP if pose estimation is needed.
annotated = aruco2.drawFiducialMarkers(np.repeat(image[..., None], 3, axis=2), markers)
```

Inputs must be uint8 grayscale (H,W), (H,W,1), or BGR (H,W,3). Noncontiguous inputs are copied; 16-bit images must be explicitly converted by the caller. Detection releases the GIL; callers must not mutate input arrays concurrently. Output arrays own their memory. Drawing returns a new image and does not mutate its input. Parameters use upstream defaults, including strict error correction. `DetectionParameters` is the actual upstream name; `DetectorParameters` is also accepted as an alias.

Exposes single/multiple dictionary detection, grid boards (including custom IDs), diamonds, fractals, RArUco, generators, drawing, all dictionary/fractal constants, and solvePnP point extraction. This initial binding uses CPU Mat inputs; OpenCL/UMat and drawAxis are not exposed.

## Continuous integration

GitHub Actions builds and tests CPython 3.10 through 3.14 wheels for Windows x64, Linux x86_64 (manylinux), and macOS Apple Silicon on pushes, pull requests, and manual runs. Download wheels from the artifacts of a successful [Wheels workflow run](https://github.com/hit-labvn/python-aruco2/actions/workflows/wheels.yml). A separate job builds the source archive. Version tags (`v*`) publish all distributions to PyPI after every build and test succeeds, using the `pypi` GitHub environment and PyPI Trusted Publishing. CI tests the installed wheel rather than importing the source tree.

## Source and licensing

The binding code is licensed under **MIT**. Vendored ArUco2 and OpenCV retain their Apache-2.0 licenses; pybind11 retains its BSD license. MIT does not replace third-party licenses.

Upstream is vendored at commit `c26b030cee4292649be566092812308fa179e871`. See `UPSTREAM.md`, `LICENSE` and `vendor/aruco2/LICENSE`. This is an independent binding project, not an official upstream Python release.
