#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "opencv2/objdetect/aruco2.hpp"
#include <cstring>
#include <limits>
#include <cmath>
namespace py = pybind11;
namespace a = cv::aruco2;
using Image = py::array_t<uint8_t, py::array::c_style>;

Image image_array(const py::array &input) {
    if (!input.dtype().is(py::dtype::of<uint8_t>()))
        throw py::type_error("image must have dtype uint8; convert 16-bit images explicitly");
    if (input.ndim() != 2 && !(input.ndim() == 3 && (input.shape(2) == 1 || input.shape(2) == 3)))
        throw py::value_error("image must have shape (H, W), (H, W, 1), or (H, W, 3) in BGR order");
    for (int i = 0; i < 2; ++i)
        if (input.shape(i) <= 0 || input.shape(i) > std::numeric_limits<int>::max())
            throw py::value_error("image dimensions must be positive and fit an OpenCV int");
    return Image::ensure(input);
}
cv::Mat view(const Image &input) {
    int channels = input.ndim() == 2 ? 1 : int(input.shape(2));
    return cv::Mat(int(input.shape(0)), int(input.shape(1)), CV_MAKETYPE(CV_8U, channels), const_cast<uint8_t*>(input.data()));
}
py::array output(const cv::Mat &mat) {
    std::vector<py::ssize_t> shape{mat.rows, mat.cols};
    if (mat.channels() > 1) shape.push_back(mat.channels());
    py::dtype dtype = mat.depth() == CV_32F ? py::dtype::of<float>() : py::dtype::of<uint8_t>();
    py::array out(dtype, shape);
    auto continuous = mat.isContinuous() ? mat : mat.clone();
    if (mat.total()) std::memcpy(out.mutable_data(), continuous.data, mat.total() * mat.elemSize());
    return out;
}
py::array_t<float> corners(const std::vector<cv::Point2f> &points) {
    py::array_t<float> out({py::ssize_t(points.size()), py::ssize_t(2)});
    auto v = out.mutable_unchecked<2>();
    for (size_t i=0; i<points.size(); ++i) { v(i,0)=points[i].x; v(i,1)=points[i].y; }
    return out;
}
template <typename T> void bind_pose(py::module_ &m) {
    m.def("getSolvePnpPoints", [](const T &target, float size) {
        if (!(size > 0) || !std::isfinite(size)) throw py::value_error("markerSize must be finite and positive");
        cv::Mat obj, img;
        a::getSolvePnpPoints(target, obj, img, size);
        return py::make_tuple(output(obj), output(img));
    }, py::arg("target"), py::arg("markerSize")=1.f);
}
template <typename T, typename F> py::array draw(const py::array &input, const std::vector<T> &targets, const std::array<double,3> &color, F fn) {
    auto array = image_array(input);
    cv::Mat result = view(array).clone();
    fn(result, targets, cv::Scalar(color[0],color[1],color[2]));
    return output(result);
}
PYBIND11_MODULE(_native, m) {
    m.doc() = "Standalone NumPy bindings for ArUco2; detection releases the Python GIL";
    m.attr("__version__") = "1.1.0";
    m.attr("upstream_commit") = "c26b030cee4292649be566092812308fa179e871";
    m.attr("opencv_version") = CV_VERSION;
    auto dict = py::enum_<a::DictionaryType>(m, "DictionaryType");
#define DICT(name) dict.value(#name, a::name)
    DICT(DICT_4X4_50); DICT(DICT_4X4_100); DICT(DICT_4X4_250); DICT(DICT_4X4_1000);
    DICT(DICT_5X5_50); DICT(DICT_5X5_100); DICT(DICT_5X5_250); DICT(DICT_5X5_1000);
    DICT(DICT_6X6_50); DICT(DICT_6X6_100); DICT(DICT_6X6_250); DICT(DICT_6X6_1000);
    DICT(DICT_7X7_50); DICT(DICT_7X7_100); DICT(DICT_7X7_250); DICT(DICT_7X7_1000);
    DICT(DICT_ARUCO_ORIGINAL); DICT(DICT_APRILTAG_16h5); DICT(DICT_APRILTAG_25h9);
    DICT(DICT_APRILTAG_36h10); DICT(DICT_APRILTAG_36h11); DICT(DICT_ARUCO_MIP_36h12);
    DICT(DICT_ALVAR_5X5_256); DICT(DICT_ALVAR_7X7_1000); DICT(DICT_RARUCO_16h4);
#undef DICT
    dict.export_values();
    py::enum_<a::FractalType>(m, "FractalType")
        .value("FRACTAL_2L_6", a::FRACTAL_2L_6).value("FRACTAL_3L_6", a::FRACTAL_3L_6)
        .value("FRACTAL_4L_6", a::FRACTAL_4L_6).value("FRACTAL_5L_6", a::FRACTAL_5L_6).export_values();
    auto params = py::class_<a::DetectionParameters>(m,"DetectionParameters").def(py::init<>());
#define PARAM(name) params.def_readwrite(#name, &a::DetectionParameters::name)
    PARAM(boxFilterSize); PARAM(thres); PARAM(minSize); PARAM(maxAttemptsPerCandidate);
    PARAM(maxTimesRevisited); PARAM(errorCorrectionRate); PARAM(maxErroneousBitsInBorderRate);
    PARAM(detectColorMode); PARAM(gridBitSampling); PARAM(harrisThresh);
    PARAM(cornerRefinementWinScale); PARAM(cornerRefinementMinWinSize); PARAM(cornerRefinementMaxWinSize);
#undef PARAM
    m.attr("DetectorParameters") = m.attr("DetectionParameters");
    py::class_<a::FiducialMarker>(m,"FiducialMarker")
        .def_readonly("id", &a::FiducialMarker::id)
        .def_readonly("dictionary", &a::FiducialMarker::dictionary)
        .def_property_readonly("corners", [](const a::FiducialMarker &v){return corners(v.corners);});
    py::class_<a::GridBoard>(m,"GridBoard")
        .def_readonly("markers", &a::GridBoard::markers).def_readonly("dictionary", &a::GridBoard::dictionary)
        .def_property_readonly("gridSize", [](const a::GridBoard &b){return py::make_tuple(b.gridSize.width,b.gridSize.height);});
    py::class_<a::Diamond>(m,"Diamond")
        .def_readonly("markers", &a::Diamond::markers).def_readonly("dictionary", &a::Diamond::dictionary)
        .def_property_readonly("id", [](const a::Diamond &d){return std::array<int,4>{d.id[0],d.id[1],d.id[2],d.id[3]};});
    py::class_<a::FractalMarker>(m,"FractalMarker")
        .def_readonly("id", &a::FractalMarker::id).def_readonly("type", &a::FractalMarker::type)
        .def_property_readonly("corners", [](const a::FractalMarker &v){return corners(v.corners);});
    m.def("detectFiducialMarkers", [](const py::array &input, a::DictionaryType d, const a::DetectionParameters &p){
        auto arr=image_array(input); auto mat=view(arr); py::gil_scoped_release release;
        return a::detectFiducialMarkers(mat,d,p);
    }, py::arg("image"),py::arg("dictionary")=a::DICT_ARUCO_MIP_36h12,py::arg("parameters")=a::DetectionParameters());
    m.def("detectFiducialMarkers", [](const py::array &input, const std::vector<a::DictionaryType> &d, const a::DetectionParameters &p){
        if (d.empty()) throw py::value_error("dictionaries must not be empty");
        auto arr=image_array(input); auto mat=view(arr); py::gil_scoped_release release;
        return a::detectFiducialMarkers(mat,d,p);
    }, py::arg("image"),py::arg("dictionaries"),py::arg("parameters")=a::DetectionParameters());
    m.def("detectRArucoMarkers", [](const py::array &input,a::DictionaryType d,const a::DetectionParameters &p){
        auto arr=image_array(input); auto mat=view(arr); py::gil_scoped_release release;
        return a::detectRArucoMarkers(mat,d,p);
    },py::arg("image"),py::arg("dictionary")=a::DICT_APRILTAG_16h5,py::arg("parameters")=a::DetectionParameters());
    m.def("detectGridBoard", [](const py::array &input,std::array<int,2> size,a::DictionaryType d,const std::vector<int> &ids){
        if (size[0]<=0 || size[1]<=0) throw py::value_error("gridSize must be positive");
        auto arr=image_array(input); a::GridBoard board{}; bool found;
        {py::gil_scoped_release release; found=a::detectGridBoard(view(arr),cv::Size(size[0],size[1]),d,board,ids);}
        return py::make_tuple(found,board);
    },py::arg("image"),py::arg("gridSize"),py::arg("dictionary"),py::arg("ids")=std::vector<int>{});
    m.def("detectDiamonds", [](const py::array &input,a::DictionaryType d){
        auto arr=image_array(input); py::gil_scoped_release release; return a::detectDiamonds(view(arr),d);
    },py::arg("image"),py::arg("dictionary"));
    m.def("detectFractals", [](const py::array &input,a::FractalType t){
        auto arr=image_array(input); py::gil_scoped_release release; return a::detectFractals(view(arr),t);
    },py::arg("image"),py::arg("type"));
    m.def("getFiducialMarkerImage", [](a::DictionaryType d,int id,int bit,bool border){
        if(bit<=0) throw py::value_error("bitSize must be positive");
        cv::Mat img; a::getFiducialMarkerImage(img,d,id,bit,border); return output(img);
    },py::arg("dictionary"),py::arg("id"),py::arg("bitSize")=20,py::arg("externalBorder")=true);
    m.def("getGridBoardImage", [](std::array<int,2> size,a::DictionaryType d,int bit,const std::vector<int> &ids){
        if(size[0]<=0 || size[1]<=0 || bit<=0) throw py::value_error("boardSize and bitSize must be positive");
        cv::Mat img; a::getGridBoardImage(img,cv::Size(size[0],size[1]),d,bit,ids); return output(img);
    },py::arg("boardSize"),py::arg("dictionary"),py::arg("bitSize")=25,py::arg("ids")=std::vector<int>{});
    m.def("getDiamondImage", [](a::DictionaryType d,std::array<int,4> ids,int bit){
        if(bit<=0) throw py::value_error("bitSize must be positive");
        cv::Mat img; a::getDiamondImage(img,d,cv::Vec4i(ids[0],ids[1],ids[2],ids[3]),bit); return output(img);
    },py::arg("dictionary"),py::arg("ids"),py::arg("bitSize")=25);
    m.def("getFractalMarkerImage", [](a::FractalType t,int id,int bit){
        if(bit<=0) throw py::value_error("bitSize must be positive");
        cv::Mat img; a::getFractalMarkerImage(img,t,id,bit); return output(img);
    },py::arg("type"),py::arg("id")=0,py::arg("bitSize")=20);
    m.def("getRArucoMarkerImage", [](a::DictionaryType d,int id,int depth,int bit,int inner,bool border){
        if(bit<=0 || depth<0 || depth>8 || inner<0) throw py::value_error("invalid bitSize, depth (0..8), or innerBorders");
        cv::Mat img; a::getRArucoMarkerImage(img,d,id,depth,bit,inner,border); return output(img);
    },py::arg("dictionary")=a::DICT_APRILTAG_16h5,py::arg("id")=0,py::arg("depth")=2,
       py::arg("bitSize")=5,py::arg("innerBorders")=2,py::arg("externalBorder")=true);
    const auto green=std::array<double,3>{0,255,0};
    m.def("drawFiducialMarkers",[](const py::array &img,const std::vector<a::FiducialMarker> &v,std::array<double,3> color){
        return draw(img,v,color,[](auto &out,const auto &items,auto c){a::drawFiducialMarkers(out,items,c);});
    },py::arg("image"),py::arg("markers"),py::arg("color")=green);
    m.def("drawDiamonds",[](const py::array &img,const std::vector<a::Diamond> &v,std::array<double,3> color){
        return draw(img,v,color,[](auto &out,const auto &items,auto c){a::drawDiamonds(out,items,c);});
    },py::arg("image"),py::arg("diamonds"),py::arg("color")=green);
    m.def("drawFractals",[](const py::array &img,const std::vector<a::FractalMarker> &v,std::array<double,3> color,bool all){
        return draw(img,v,color,[all](auto &out,const auto &items,auto c){a::drawFractals(out,items,c,all);});
    },py::arg("image"),py::arg("fractals"),py::arg("color")=green,py::arg("drawAllImagePoints")=true);
    m.def("drawGridBoard",[](const py::array &img,const a::GridBoard &board,std::array<double,3> color,bool ids){
        auto arr=image_array(img); auto out=view(arr).clone();
        a::drawGridBoard(out,board,cv::Scalar(color[0],color[1],color[2]),ids); return output(out);
    },py::arg("image"),py::arg("board"),py::arg("color")=green,py::arg("drawMarkerIds")=false);
    bind_pose<a::FiducialMarker>(m); bind_pose<a::GridBoard>(m); bind_pose<a::Diamond>(m); bind_pose<a::FractalMarker>(m);
}
