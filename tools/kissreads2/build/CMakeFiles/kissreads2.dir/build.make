# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /opt/local/bin/cmake

# The command to remove a file.
RM = /opt/local/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The program to use to edit the cache.
CMAKE_EDIT_COMMAND = /opt/local/bin/ccmake

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2/build

# Include any dependencies generated for this target.
include CMakeFiles/kissreads2.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/kissreads2.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/kissreads2.dir/flags.make

CMakeFiles/kissreads2.dir/src/Test.o: CMakeFiles/kissreads2.dir/flags.make
CMakeFiles/kissreads2.dir/src/Test.o: ../src/Test.cpp
	$(CMAKE_COMMAND) -E cmake_progress_report /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2/build/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object CMakeFiles/kissreads2.dir/src/Test.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/kissreads2.dir/src/Test.o -c /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2/src/Test.cpp

CMakeFiles/kissreads2.dir/src/Test.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/kissreads2.dir/src/Test.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2/src/Test.cpp > CMakeFiles/kissreads2.dir/src/Test.i

CMakeFiles/kissreads2.dir/src/Test.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/kissreads2.dir/src/Test.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2/src/Test.cpp -o CMakeFiles/kissreads2.dir/src/Test.s

CMakeFiles/kissreads2.dir/src/Test.o.requires:
.PHONY : CMakeFiles/kissreads2.dir/src/Test.o.requires

CMakeFiles/kissreads2.dir/src/Test.o.provides: CMakeFiles/kissreads2.dir/src/Test.o.requires
	$(MAKE) -f CMakeFiles/kissreads2.dir/build.make CMakeFiles/kissreads2.dir/src/Test.o.provides.build
.PHONY : CMakeFiles/kissreads2.dir/src/Test.o.provides

CMakeFiles/kissreads2.dir/src/Test.o.provides.build: CMakeFiles/kissreads2.dir/src/Test.o

# Object files for target kissreads2
kissreads2_OBJECTS = \
"CMakeFiles/kissreads2.dir/src/Test.o"

# External object files for target kissreads2
kissreads2_EXTERNAL_OBJECTS =

kissreads2: CMakeFiles/kissreads2.dir/src/Test.o
kissreads2: CMakeFiles/kissreads2.dir/build.make
kissreads2: CMakeFiles/kissreads2.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking CXX executable kissreads2"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/kissreads2.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/kissreads2.dir/build: kissreads2
.PHONY : CMakeFiles/kissreads2.dir/build

CMakeFiles/kissreads2.dir/requires: CMakeFiles/kissreads2.dir/src/Test.o.requires
.PHONY : CMakeFiles/kissreads2.dir/requires

CMakeFiles/kissreads2.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/kissreads2.dir/cmake_clean.cmake
.PHONY : CMakeFiles/kissreads2.dir/clean

CMakeFiles/kissreads2.dir/depend:
	cd /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2 /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2 /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2/build /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2/build /Users/ppeterlo/workspace/gatb-tools/gatb-tools/tools/DiscoSNP/tools/kissreads2/build/CMakeFiles/kissreads2.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/kissreads2.dir/depend

