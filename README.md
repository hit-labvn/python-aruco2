# python-aruco2

[![PyPI](https://img.shields.io/pypi/v/python-aruco2.svg)](https://pypi.org/project/python-aruco2/)
[![Python](https://img.shields.io/pypi/pyversions/python-aruco2.svg)](https://pypi.org/project/python-aruco2/)
[![Wheels](https://github.com/hit-labvn/python-aruco2/actions/workflows/wheels.yml/badge.svg?branch=main)](https://github.com/hit-labvn/python-aruco2/actions/workflows/wheels.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Python bindings for [ArUco2](https://github.com/rmsalinas/aruco2), a fast fiducial marker detector.

## Features

- Marker detection for all ArUco, AprilTag, ALVAR and RArUco dictionaries
- Grid boards, diamonds and fractal markers
- Marker and board image generation, and drawing helpers
- Object/image point extraction for `cv2.solvePnP`
- Releases the GIL during detection

## Installation

```bash
pip install python-aruco2
```

Prebuilt wheels are available for CPython 3.10–3.14 on Windows x64, Linux x86_64 and macOS arm64.

## Quick start

```python
import cv2
import aruco2.compat as aruco  # instead of: import cv2.aruco as aruco

image = cv2.imread("markers.png", cv2.IMREAD_GRAYSCALE)

detector = aruco.ArucoDetector(aruco.getPredefinedDictionary(aruco.DICT_6X6_250), aruco.DetectorParameters())
corners, ids, rejected = detector.detectMarkers(image)
print(ids, corners[0])  # ids: int32 (N,); corners: float32 (1, 4, 2) per marker, sub-pixel
```

`aruco2.compat` mirrors OpenCV's detection API and returns OpenCV 5 shapes, so code written for `cv2.aruco` only changes its import.

The native API, `aruco2.detectFiducialMarkers(image, aruco2.DICT_6X6_250)`, returns markers with `id` and `corners`. For pose estimation, pass `aruco2.getSolvePnpPoints(marker, markerSize=0.05)` to `cv2.solvePnP`.

## Notes

- Input images must be `uint8` grayscale `(H, W)` / `(H, W, 1)` or BGR `(H, W, 3)`. Convert 16-bit images first.
- Do not modify an input array while detection is running on it.
- Detection parameters default to upstream values, except the corner refinement window: 5% of the marker side (2–9 px) instead of upstream's ~9%, so dark shapes printed near a marker do not pull its corners. Set `cornerRefinementWinScale = 3/34` and `cornerRefinementMinWinSize = 3` for upstream behaviour. `DetectorParameters` is an alias of `DetectionParameters`.
- OpenCL/UMat inputs and `drawAxis` are not exposed.

## Building from source

Requires CMake 3.24+ and a C++17 compiler (Visual Studio 2022 on Windows). The first build downloads and compiles OpenCV 4.12.0.

```bash
pip install .
```

To link against an existing OpenCV C++ SDK instead (the `opencv-python` wheel is not one):

```bash
pip install . \
  --config-settings cmake.define.ARUCO2_BUILD_OPENCV=OFF \
  --config-settings cmake.define.OpenCV_DIR=/path/to/opencv/build
```

On Windows, add `--config-settings cmake.define.ARUCO2_STATIC_CRT=ON` if the SDK was built with `/MT`.

## Development

```bash
pip install ".[test]"
pytest
```

CI builds and tests wheels on every push and pull request. Pushing a `v*` tag publishes to PyPI.

## License

Licensed under the [Apache License 2.0](LICENSE), the same license as the vendored ArUco2 and OpenCV sources. pybind11 is BSD-3-Clause. See [NOTICE](NOTICE) for attributions and [UPSTREAM.md](UPSTREAM.md) for upstream versions and local patches. This is an independent project, not an official ArUco2 release.
