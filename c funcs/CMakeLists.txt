cmake_minimum_required(VERSION 3.31)
project( ThermalCamera )
set(SOURCE_FILES 
    main.cpp
    CameraController.cpp)
find_package( OpenCV REQUIRED )
include_directories( ${OpenCV_INCLUDE_DIRS} )
include_directories( ~/raylib )
include_directories( ~/raylib-cpp/include/ )
add_executable( ${PROJECT_NAME} ${SOURCE_FILES} )
target_link_libraries( ${PROJECT_NAME} ${OpenCV_LIBS})
target_link_libraries( ${PROJECT_NAME} raylib raylib_cpp)