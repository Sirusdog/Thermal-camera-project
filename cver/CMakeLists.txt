cmake_minimum_required(VERSION 3.31)
project( ThermalCamera )
set(SOURCE_FILES 
    src/main.cpp
    src/CameraController.cpp)

#Taken from https://github.com/RobLoach/raylib-cpp/blob/master/projects/CMake/CMakeLists.txt
set(PLATFORM DRM)
find_package(raylib)
if (NOT raylib_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        raylib
        GIT_REPOSITORY https://github.com/raysan5/raylib.git
        GIT_TAG 6.0
        GIT_SHALLOW 1
    )
    FetchContent_MakeAvailable(raylib)
endif()


# raylib-cpp
find_package(raylib_cpp)
if (NOT raylib_cpp_FOUND)
    if (NOT DEFINED RAYLIB_CPP_VERSION)
        set(RAYLIB_CPP_VERSION v6.0.0)
    endif()
    include(FetchContent)
    FetchContent_Declare(
        raylib_cpp
        GIT_REPOSITORY https://github.com/RobLoach/raylib-cpp.git
        GIT_TAG ${RAYLIB_CPP_VERSION}
    )
    FetchContent_MakeAvailable(raylib_cpp)
endif()
unset(PLATFORM)

# opencv


# For the life of me I couldn't get opencv to compile using Cmake
set( opencv_DIR /usr/local/include/opencv5/opencv2 )
find_package(
    opencv
)
if (NOT opencv_FOUND)
    message(STATUS "OpenCV not found.")
    include(FetchContent)
    FetchContent_Declare(  
        opencv  
        GIT_REPOSITORY https://github.com/opencv/opencv.git
        GIT_TAG 4.14.0
        CMAKE_ARGS
            -DBUILD_DOCS=FALSE
            -DBUILD_EXAMPLES=FALSE
            -DBUILD_TESTS=FALSE
            -DBUILD_opencv_apps=FALSE
            -DBUILD_SHARED_LIBS=TRUE
            -DWITH_CUDA=FALSE
            -DBUILD_JAVA=FALSE
            -DBUILD_opencv_python3=FALSE
            -DWITH_FFMPEG=FALSE
            -DBUILD_PERF_TESTS=FALSE
            -DOPENCV_ENABLE_NONFREE=TRUE
            -DBUILD_opencv_java=OFF
            -DCMAKE_INSTALL_PREFIX=${OpenCV_INSTALL_DIR}
    )
    # Taken from wissem chiha's answer at https://stackoverflow.com/a/79280683
    FetchContent_MakeAvailable(opencv)
    #find_package(opencv) 
endif()
message(STATUS "OpenCV found: ${OpenCV_DIR}")

add_executable( ${PROJECT_NAME} ${SOURCE_FILES} )

target_link_libraries( ${PROJECT_NAME} PUBLIC raylib raylib-cpp) 

target_include_directories(${PROJECT_NAME} PRIVATE
        ${OPENCV_CONFIG_FILE_INCLUDE_DIRS}
        ${OPENCV_MODULE_opencv_core_LOCATION}/include
        ${OPENCV_MODULE_opencv_highgui_LOCATION}/include
        )
target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})