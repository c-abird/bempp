set(build_dir "@CMAKE_CURRENT_BINARY_DIR@/ExampleProject/build")
if(EXISTS "${build_dir}")
    message(STATUS "Removing previous build directory")
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${build_dir}
        RESULT_VARIABLE result
    )
    if(NOT result STREQUAL 0)
        message(FATAL_ERROR "Could not remove directory")
    endif()
endif()
file(MAKE_DIRECTORY "${build_dir}")
execute_process(
    COMMAND ${CMAKE_COMMAND} .. -DPROJECT_INCLUSION_UNIT_TESTS=ON
    WORKING_DIRECTORY "${build_dir}"
    RESULT_VARIABLE result
)
if(NOT result STREQUAL 0)
    message(FATAL_ERROR "Could not configure test project in ${build_dir}")
endif()