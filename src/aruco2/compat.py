"""OpenCV ``cv2.aruco``-compatible marker detection backed by aruco2.

Code written for OpenCV's ``ArucoDetector`` can switch detectors by changing one import::

    import aruco2.compat as aruco   # instead of: import cv2.aruco as aruco

    detector = aruco.ArucoDetector(aruco.getPredefinedDictionary(aruco.DICT_6X6_250), aruco.DetectorParameters())
    corners, ids, rejected = detector.detectMarkers(gray)

Return values follow OpenCV 5: ``corners`` is a tuple of float32 ``(1, 4, 2)`` arrays, ``ids`` is an int32 ``(N,)``
array or ``None``, and ``rejected`` is always an empty tuple. Corners keep their sub-pixel precision.

Only detection is provided. ``DetectorParameters`` is :class:`aruco2.DetectionParameters`, so OpenCV-only fields such
as ``cornerRefinementMethod`` do not exist; aruco2 always refines corners.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from . import _native as _a

__all__ = ["ArucoDetector", "DetectorParameters", "Dictionary", "detectMarkers", "getPredefinedDictionary"]

DetectorParameters = _a.DetectionParameters

for _name in dir(_a):
    if _name.startswith("DICT_"):
        globals()[_name] = getattr(_a, _name)
        __all__.append(_name)
del _name

_DetectResult = tuple[tuple[NDArray[np.float32], ...], "NDArray[np.int32] | None", tuple[()]]


class Dictionary:
    """A predefined marker dictionary, as returned by :func:`getPredefinedDictionary`."""

    def __init__(self, dictionary: _a.DictionaryType) -> None:
        self.type = dictionary

    def __repr__(self) -> str:
        return f"Dictionary({self.type.name})"


def getPredefinedDictionary(dictionary: Any) -> Dictionary:
    """Return the predefined dictionary for a ``DICT_*`` constant or its integer value."""
    if isinstance(dictionary, Dictionary):
        return dictionary
    return Dictionary(dictionary if isinstance(dictionary, _a.DictionaryType) else _a.DictionaryType(int(dictionary)))


def _detect(image: NDArray[np.uint8], dictionary: Dictionary, parameters: Any) -> _DetectResult:
    markers = _a.detectFiducialMarkers(image, dictionary.type, parameters)
    if not markers:
        return (), None, ()
    corners = tuple(np.asarray(m.corners, dtype=np.float32).reshape(1, 4, 2) for m in markers)
    ids = np.array([m.id for m in markers], dtype=np.int32)
    return corners, ids, ()


class ArucoDetector:
    """Drop-in for ``cv2.aruco.ArucoDetector`` (detection only)."""

    def __init__(self, dictionary: Any = None, detectorParams: Any = None, refineParams: Any = None) -> None:
        self._dictionary = getPredefinedDictionary(_a.DICT_4X4_50 if dictionary is None else dictionary)
        self._params = DetectorParameters() if detectorParams is None else detectorParams

    def detectMarkers(self, image: NDArray[np.uint8], corners: Any = None, ids: Any = None,
                      rejectedImgPoints: Any = None) -> _DetectResult:
        """Detect markers in a uint8 grayscale or BGR image."""
        return _detect(image, self._dictionary, self._params)

    def getDictionary(self) -> Dictionary:
        return self._dictionary

    def setDictionary(self, dictionary: Any) -> None:
        self._dictionary = getPredefinedDictionary(dictionary)

    def getDetectorParameters(self) -> Any:
        return self._params

    def setDetectorParameters(self, detectorParameters: Any) -> None:
        self._params = detectorParameters


def detectMarkers(image: NDArray[np.uint8], dictionary: Any, corners: Any = None, ids: Any = None,
                  parameters: Any = None, rejectedImgPoints: Any = None) -> _DetectResult:
    """Legacy ``cv2.aruco.detectMarkers`` function form."""
    return _detect(image, getPredefinedDictionary(dictionary), DetectorParameters() if parameters is None else parameters)
