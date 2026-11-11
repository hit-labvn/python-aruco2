import numpy as np
import pytest
import aruco2 as a

D = a.DICT_6X6_250

def test_marker_roundtrip_and_owned_corners():
    image = a.getFiducialMarkerImage(D, 42)
    markers = a.detectFiducialMarkers(image, D)
    assert [m.id for m in markers] == [42]
    c = markers[0].corners
    assert c.shape == (4, 2) and c.dtype == np.float32
    assert c.flags.owndata
    obj, img = a.getSolvePnpPoints(markers[0], markerSize=0.05)
    assert obj.shape == (4, 1, 3) and img.shape == (4, 1, 2)
    assert np.isclose(np.ptp(obj[..., 0]), 0.05)

@pytest.mark.parametrize('mode', ['gray', 'bgr', 'strided', 'readonly'])
def test_input_layout(mode):
    image = a.getFiducialMarkerImage(D, 7)
    if mode == 'bgr':
        image = np.repeat(image[..., None], 3, axis=2)
    elif mode == 'strided':
        wide = np.empty((image.shape[0], image.shape[1]*2), np.uint8)
        wide[:, ::2] = image
        image = wide[:, ::2]
    elif mode == 'readonly':
        image.flags.writeable = False
    assert [m.id for m in a.detectFiducialMarkers(image, D)] == [7]

def test_multi_dictionary_and_no_detection():
    image = a.getFiducialMarkerImage(D, 21)
    assert [m.id for m in a.detectFiducialMarkers(image, [D, a.DICT_4X4_50])] == [21]
    assert a.detectFiducialMarkers(np.full((100,100), 255, np.uint8), D) == []

@pytest.mark.parametrize('image,exc', [(np.zeros((10,10),np.uint16),TypeError),
    (np.zeros((10,10,4),np.uint8),ValueError), (np.zeros((0,10),np.uint8),ValueError)])
def test_invalid_input(image, exc):
    with pytest.raises(exc):
        a.detectFiducialMarkers(image, D)

def test_drawing_returns_copy():
    image = a.getFiducialMarkerImage(D, 9)
    image = np.repeat(image[...,None], 3, axis=2)
    before = image.copy()
    drawn = a.drawFiducialMarkers(image, a.detectFiducialMarkers(image,D))
    assert np.array_equal(image,before)
    assert not np.shares_memory(drawn,image)
    assert np.any(drawn != image)

def test_grid_roundtrip():
    image = a.getGridBoardImage((3,2),D)
    image = np.pad(image,30,constant_values=255)
    found, board = a.detectGridBoard(image,(3,2),D)
    assert found and len(board.markers) == 6
    obj,img = a.getSolvePnpPoints(board)
    assert obj.size > 0 and img.size > 0

def test_parameters_and_secondary_generators():
    p = a.DetectionParameters()
    p.errorCorrectionRate = 0.5
    assert p.errorCorrectionRate == 0.5
    assert a.DetectorParameters is a.DetectionParameters
    assert a.getDiamondImage(D,[1,2,3,4]).dtype == np.uint8
    assert a.getFractalMarkerImage(a.FRACTAL_2L_6).dtype == np.uint8
    assert a.getRArucoMarkerImage().dtype == np.uint8

def test_secondary_detection_and_pose():
    cases = [
        (a.getDiamondImage(D,[1,2,3,4]), lambda im:a.detectDiamonds(im,D), a.drawDiamonds),
        (a.getFractalMarkerImage(a.FRACTAL_2L_6), lambda im:a.detectFractals(im,a.FRACTAL_2L_6), a.drawFractals),
        (a.getRArucoMarkerImage(), a.detectRArucoMarkers, a.drawFiducialMarkers),
    ]
    for image,detect,draw in cases:
        image=np.pad(image,40,constant_values=255)
        results=detect(image)
        assert results
        obj,img=a.getSolvePnpPoints(results[0])
        assert obj.shape[0] == img.shape[0] and obj.shape[-1] == 3
        assert draw(image,results).shape == image.shape

def test_custom_board_and_drawing():
    ids=[10,11,12,13,14,15]
    image=np.pad(a.getGridBoardImage((3,2),D,ids=ids),30,constant_values=255)
    found,board=a.detectGridBoard(image,(3,2),D,ids=ids)
    assert found and sorted(m.id for m in board.markers)==ids
    assert a.drawGridBoard(image,board).shape==image.shape

def test_threaded_detection():
    from concurrent.futures import ThreadPoolExecutor
    image=a.getFiducialMarkerImage(D,42)
    def scan(_):
        return [m.id for m in a.detectFiducialMarkers(image,D)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(scan,range(16)))==[[42]]*16
