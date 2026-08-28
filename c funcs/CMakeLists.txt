cmake_minimum_required(VERSION 3.31)
project( ThermalCamera )
set(SOURCE_FILES 
    main.cpp
    CameraController.cpp)

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

find_package(opencvD) 
# For the life of me I couldn't get opencv to compile using Cmake

if (NOT opencv_FOUND)
    include(FetchContent)
    FetchContent_Declare(  
        opencv  
        GIT_REPOSITORY https://github.com/opencv/opencv.git
        GIT_TAG 4.14.0
    )
    FetchContent_MakeAvailable(opencv)
endif()
message(STATUS "OpenCV found: ${OpenCV_DIR}")
include_directories( ${OpenCV_INCLUDE_DIRS} )


add_executable( ${PROJECT_NAME} ${SOURCE_FILES} )

target_link_libraries( ${PROJECT_NAME} PUBLIC raylib raylib-cpp) 
target_link_libraries( ${PROJECT_NAME} ${OpenCV_LIBS} )
target_include_directories(${PROJECT_NAME} PRIVATE ${OpenCV_INCLUDE_DIRS})