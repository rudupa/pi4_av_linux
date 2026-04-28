cmake_minimum_required(VERSION 3.16)
project(pi4_control_sim_node LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(USE_ZENOH "Enable zenoh-c transport when available" ON)

if(USE_ZENOH)
	find_package(PkgConfig QUIET)
	if(PkgConfig_FOUND)
		pkg_check_modules(ZENOHC QUIET zenohc)
	endif()
endif()

add_executable(pi4_control_sim_node
	src/control_sim_node.cpp
	src/zenoh_adapter.cpp
)

if(USE_ZENOH AND ZENOHC_FOUND)
	target_compile_definitions(pi4_control_sim_node PRIVATE HAVE_ZENOHC)
	target_include_directories(pi4_control_sim_node PRIVATE ${ZENOHC_INCLUDE_DIRS})
	target_link_libraries(pi4_control_sim_node PRIVATE ${ZENOHC_LIBRARIES})
endif()
