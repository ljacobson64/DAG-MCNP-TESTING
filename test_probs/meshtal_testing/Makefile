MOAB_BASE_DIR = /local.hd/cnergg/sjackson/MOAB/acis-debug

include ${MOAB_BASE_DIR}/lib/moab.make


CXXSOURCES = tally_test.cpp ../Source/dagmc/meshtal_funcs.cpp
CXXOBJS = tally_test.o meshtal_funcs.o
CXXFLAGS = -g -Wall -Wextra -I../Source/dagmc/ ${MOAB_INCLUDES} ${MOAB_CXXFLAGS}
LDFLAGS = -ldagmc ${MOAB_LIBS_LINK} -Wl,--rpath=${HOME}/.root/lib


tally_test: ${CXXOBJS} Makefile
	${CXX} ${CXXFLAGS} -o $@ ${CXXOBJS} ${LDFLAGS} 

tally_test.o: tally_test.cpp
	${CXX} ${CXXFLAGS} -c $< -o $@

meshtal_funcs.o: ../Source/dagmc/meshtal_funcs.cpp
	${CXX} ${CXXFLAGS} -c ../Source/dagmc/meshtal_funcs.cpp -o $@

clean: 
	rm -rf tally_test *.o

