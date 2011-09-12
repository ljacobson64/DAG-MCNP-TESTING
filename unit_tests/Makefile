#---------------------------------------------------------------------
# This is the makefile for the KDE Track Test code 
# --------------------------------------------------------------------
KDE_SRC_DIR = ../../Source/dagmc/
MOAB_LIB_DIR = /filespace/groups/cnerg/opt/MOAB/lib
include ${MOAB_LIB_DIR}/moab.make

# --------------------------------------------------------------------
# Specifies the C++ compiler and its flag options
# --------------------------------------------------------------------
CXX = g++
CXXFLAGS = -Wall -g -O3 ${MOAB_INCLUDES}
LDFLAGS = ${MOAB_LIBS_LINK}

# --------------------------------------------------------------------
# Lists the *.o files needed to create the $(NAME) executable.
# --------------------------------------------------------------------
NAME = kde_track_test
CXXOBJS = KDETrackTest.o KDEKernel.o KDETrack.o

# --------------------------------------------------------------------
# Compiles $(NAME) executable using $(CXXOBJS)
# --------------------------------------------------------------------
$(NAME) : $(CXXOBJS)
	$(CXX) $(CXXOBJS) $(LDFLAGS) $(CXXFLAGS) -o $@ 

KDETrackTest.o : KDETrackTest.cpp
	$(CXX) $(CXXFLAGS) -c $<

KDEKernel.o : $(KDE_SRC_DIR)KDEKernel.cpp $(KDE_SRC_DIR)KDEKernel.hpp
	$(CXX) $(CXXFLAGS) -c $<

KDETrack.o : $(KDE_SRC_DIR)KDETrack.cpp $(KDE_SRC_DIR)KDETrack.hpp
	$(CXX) $(CXXFLAGS) -c $<

# --------------------------------------------------------------------
# Removes all of the *.o files
# --------------------------------------------------------------------
clean :
	rm *.o

# --------------------------------------------------------------------
# Removes all of the *.o files and the executable
# --------------------------------------------------------------------
xclean :
	rm *.o $(NAME) 
