cmake_minimum_required(VERSION 3.5)

project(RayTracing)

set(CMAKE_GENERATOR "MinGW Makefiles")
 
set(SOURCE_FILES
    # src/main.c
    src/raytracing.c
    src/geometry/geometry.c
)

set(HEADER_FILES
    src/raytracing.h
    src/geometry/geometry.h
)

include_directories(
    ${PROJECT_SOURCE_DIR}/src
    ${PROJECT_SOURCE_DIR}/src/geometry
)

# add_executable(RayTracing ${SOURCE_FILES} ${HEADER_FILES})
add_library(RayTracing SHARED ${SOURCE_FILES} ${HEADER_FILES})
