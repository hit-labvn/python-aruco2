"""Public API. Images are uint8 NumPy arrays; coordinates are float32."""
from enum import Enum
from typing import Sequence
import numpy as np
from numpy.typing import NDArray

class DictionaryType(Enum):
    DICT_4X4_50 = 0
    DICT_4X4_100 = 1
    DICT_4X4_250 = 2
    DICT_4X4_1000 = 3
    DICT_5X5_50 = 4
    DICT_5X5_100 = 5
    DICT_5X5_250 = 6
    DICT_5X5_1000 = 7
    DICT_6X6_50 = 8
    DICT_6X6_100 = 9
    DICT_6X6_250 = 10
    DICT_6X6_1000 = 11
    DICT_7X7_50 = 12
    DICT_7X7_100 = 13
    DICT_7X7_250 = 14
    DICT_7X7_1000 = 15
    DICT_ARUCO_ORIGINAL = 16
    DICT_APRILTAG_16h5 = 17
    DICT_APRILTAG_25h9 = 18
    DICT_APRILTAG_36h10 = 19
    DICT_APRILTAG_36h11 = 20
    DICT_ARUCO_MIP_36h12 = 21
    DICT_ALVAR_5X5_256 = 22
    DICT_ALVAR_7X7_1000 = 23
    DICT_RARUCO_16h4 = 24

class FractalType(Enum):
    FRACTAL_2L_6 = 0
    FRACTAL_3L_6 = 1
    FRACTAL_4L_6 = 2
    FRACTAL_5L_6 = 3

class DetectionParameters:
    boxFilterSize: int
    thres: int
    minSize: int
    maxAttemptsPerCandidate: int
    maxTimesRevisited: float
    errorCorrectionRate: float
    maxErroneousBitsInBorderRate: float
    detectColorMode: int
    gridBitSampling: bool
    harrisThresh: float
    def __init__(self) -> None: ...
DetectorParameters = DetectionParameters

class FiducialMarker:
    @property
    def id(self) -> int: ...
    @property
    def dictionary(self) -> DictionaryType: ...
    @property
    def corners(self) -> NDArray[np.float32]: ...
class GridBoard:
    @property
    def gridSize(self) -> tuple[int, int]: ...
    @property
    def dictionary(self) -> DictionaryType: ...
    @property
    def markers(self) -> list[FiducialMarker]: ...
class Diamond:
    @property
    def id(self) -> list[int]: ...
    @property
    def dictionary(self) -> DictionaryType: ...
    @property
    def markers(self) -> list[FiducialMarker]: ...
class FractalMarker:
    @property
    def id(self) -> int: ...
    @property
    def type(self) -> FractalType: ...
    @property
    def corners(self) -> NDArray[np.float32]: ...

def detectFiducialMarkers(image: NDArray[np.uint8], dictionary: DictionaryType | Sequence[DictionaryType] = ..., parameters: DetectionParameters = ...) -> list[FiducialMarker]: ...
def detectRArucoMarkers(image: NDArray[np.uint8], dictionary: DictionaryType = ..., parameters: DetectionParameters = ...) -> list[FiducialMarker]: ...
def detectGridBoard(image: NDArray[np.uint8], gridSize: Sequence[int], dictionary: DictionaryType, ids: Sequence[int] = ...) -> tuple[bool, GridBoard]: ...
def detectDiamonds(image: NDArray[np.uint8], dictionary: DictionaryType) -> list[Diamond]: ...
def detectFractals(image: NDArray[np.uint8], type: FractalType) -> list[FractalMarker]: ...
def getFiducialMarkerImage(dictionary: DictionaryType, id: int, bitSize: int = ..., externalBorder: bool = ...) -> NDArray[np.uint8]: ...
def getGridBoardImage(boardSize: Sequence[int], dictionary: DictionaryType, bitSize: int = ..., ids: Sequence[int] = ...) -> NDArray[np.uint8]: ...
def getDiamondImage(dictionary: DictionaryType, ids: Sequence[int], bitSize: int = ...) -> NDArray[np.uint8]: ...
def getFractalMarkerImage(type: FractalType, id: int = ..., bitSize: int = ...) -> NDArray[np.uint8]: ...
def getRArucoMarkerImage(dictionary: DictionaryType = ..., id: int = ..., depth: int = ..., bitSize: int = ..., innerBorders: int = ..., externalBorder: bool = ...) -> NDArray[np.uint8]: ...
def getSolvePnpPoints(target: FiducialMarker | GridBoard | Diamond | FractalMarker, markerSize: float = ...) -> tuple[NDArray[np.float32], NDArray[np.float32]]: ...
def drawFiducialMarkers(image: NDArray[np.uint8], markers: Sequence[FiducialMarker], color: Sequence[float] = ...) -> NDArray[np.uint8]: ...
def drawGridBoard(image: NDArray[np.uint8], board: GridBoard, color: Sequence[float] = ..., drawMarkerIds: bool = ...) -> NDArray[np.uint8]: ...
def drawDiamonds(image: NDArray[np.uint8], diamonds: Sequence[Diamond], color: Sequence[float] = ...) -> NDArray[np.uint8]: ...
def drawFractals(image: NDArray[np.uint8], fractals: Sequence[FractalMarker], color: Sequence[float] = ..., drawAllImagePoints: bool = ...) -> NDArray[np.uint8]: ...
__version__: str
upstream_commit: str
opencv_version: str
DICT_4X4_50: DictionaryType
DICT_4X4_100: DictionaryType
DICT_4X4_250: DictionaryType
DICT_4X4_1000: DictionaryType
DICT_5X5_50: DictionaryType
DICT_5X5_100: DictionaryType
DICT_5X5_250: DictionaryType
DICT_5X5_1000: DictionaryType
DICT_6X6_50: DictionaryType
DICT_6X6_100: DictionaryType
DICT_6X6_250: DictionaryType
DICT_6X6_1000: DictionaryType
DICT_7X7_50: DictionaryType
DICT_7X7_100: DictionaryType
DICT_7X7_250: DictionaryType
DICT_7X7_1000: DictionaryType
DICT_ARUCO_ORIGINAL: DictionaryType
DICT_APRILTAG_16h5: DictionaryType
DICT_APRILTAG_25h9: DictionaryType
DICT_APRILTAG_36h10: DictionaryType
DICT_APRILTAG_36h11: DictionaryType
DICT_ARUCO_MIP_36h12: DictionaryType
DICT_ALVAR_5X5_256: DictionaryType
DICT_ALVAR_7X7_1000: DictionaryType
DICT_RARUCO_16h4: DictionaryType
FRACTAL_2L_6: FractalType
FRACTAL_3L_6: FractalType
FRACTAL_4L_6: FractalType
FRACTAL_5L_6: FractalType
