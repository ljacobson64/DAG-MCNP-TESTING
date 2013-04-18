#! /usr/bin/env python

from itaps import iBase,iMesh
import numpy
#import numpy.linalg.linalg as la
import itertools
import sys, re
from contextlib import closing

from matplotlib import pyplot as plt

# Pull tally information from an MCNP5 outp file
# This makes some assumptions: 
# * There is only one type-4 tally in the problem
# * There is only one energy bin in the tally
# Output is a dictionary mapping cell IDs to (value,error) tuples
# This function is deprecated and its use should be avoided except in 
# cases where an mctal file is absolutely impossible to get.
# Prefer get_mcnp_mctal_tallies function below.
def get_mcnp_tallies( filename ):

    ret = dict()
    with closing( open( filename, 'r' ) ) as outp:
        cell = 0
        for line in outp:
            if cell == 0:
                match = re.match( '^\s+cell\s+(\d+)', line )
                if match:
                    cell = match.group(1)
            else:
                ret[int(cell)] = tuple( [float(i) for i in line.split()] )
                cell = 0
    return ret

# Pull tally information from an MCTAL file
# There are several features unsupported, such as energy bins,
# but this is capable of reading in one or more basic F4 tallies.
# Output is a dictionary mapping tally numbers to tally dictionaries.
# Each tally dictionary maps fbin IDs (cell ids for F4 tallies) to (value, error) tuples.
def get_mcnp_mctal_tallies( filename ):

    tallies = dict()

    with open(filename, 'r') as mctal:

        # line 1: kod ver probid knod nps rnr
        # i.e. codename, version number, datetime/machine, dump number, # histories, # random nums
        # kod, ver, and probid may be absent if prdmp cards's MCT flag is negative
        mctal.readline() # ignore

        # line 2: first line of INP file (problem name)
        mctal.readline() # ignore

        # line 3: NTAL n [NPERT m] (number of tallies and perterbations)
        line = mctal.readline()
        ntal = int( line.split()[1] )

        # list of tally numbers
        while len(tallies) < ntal: 
            line = mctal.readline()
            for i in line.split():
                tallies[int(i)] = dict()

        if( len(tallies) != ntal ):
            raise RuntimeError( 'Problem parsing mctal: wrong number of tallies' )
        
        # for each tally
        for _ in range(0,ntal):
            # tally data line 1: TALLY m i j 
            # m is the tally number
            # i is the particle type (1=n,2=p,3=n+p,4=e,5=n+e,6=p+e,7=n+p+e)
            # j is the 'tally type': 0 = nondetector 
            line = mctal.readline()
            m = int( line.split()[1] )

            # FC comment lines, each beginning with five spaces
            line = mctal.readline()
            while( len(line) > 5 and line[0:5] == '     ' ):
                line = mctal.readline()

            # tally data 2: F n
            # n is the number of cell, surface, or detector bins
            num_fbins = int( line.split()[1] )
            fbins = []

            # list of the nbins for cells or surfaces.  zeros indicate a bin 
            # made of several cells or surfaces.
            while len(fbins) < num_fbins:
                line = mctal.readline()
                print len(fbins), line
                fbins.extend( [int(i) for i in line.split() ] )

            if( len(fbins) != num_fbins ):
                raise RuntimeError( 'Problem parsing mctal: wrong number of fbins' )

            
            # tally data 3: D n
            # n is the number of total vs. direct or flagged vs. unflagged bins
            # ignore for now
            line = mctal.readline()
            
            # tally data 4 (user bins): U n or UT n or UC n
            # ignore for now
            line = mctal.readline()

            # tally data 5 (segment bins): S n or ST n or SC n
            # ignore for now
            line = mctal.readline()

            # tally data 6 (multiplier bins): M n or MT n or MC n 
            # ignore for now
            line = mctal.readline()

            # tally data 7 (cosine bins): C n f or CT n f or CC n f
            # ignore for now
            line = mctal.readline()

            # tally data 8 (energy bins): E n f or ET n f or EC n f
            # ignore for now
            line = mctal.readline()

            # tally data 9 (time bins): T n f or TT n f or TC n f
            # ignore for now
            line = mctal.readline()

            # tally values: a line with the word VALS
            line = mctal.readline()
            assert( line[0:4].lower() == "vals" )
            
            vals = []
            num_vals = 2 * num_fbins
            while len(vals) < num_vals:
                line = mctal.readline()
                vals.extend( [float(i) for i in line.split()] )

            # tally fluctuation data: TFC n jtf
            # n is the number of sets of fluctuation data, jtf is a list of 8 numbers
            # indicating bin boundaries for tally fluctation chart
            # ignore this for now
            line = mctal.readline()
            num_tfc_lines = int( line.split()[1] )
            for _ in range(0, num_tfc_lines):
                line = mctal.readline()

            # assign data to the tally to be returned 
            # Output is a dictionary mapping fbin boundaries (cell IDs for type 4) to (val, err) tuples
            for idx, key in enumerate(fbins):
                #ignore 0-valued keys for now
                if key != 0:
                    tallies[m][key] = tuple( vals[2*idx:2*idx+2] )

            
        # There may be a KCODE blcok here, but we'll ignore it for now
    return tallies

# Pull tally information from a track-length tally mesh file using PyTAPS
# The file is assumed to have the tags TALLY_TAG and ERROR_TAG assigned to its tetrahedra,
# so energy bins are excluded
# Output is a dictionary mappign cell IDs to (value,error) tuples
def get_moab_tallies( moab_mesh ):
    mesh = iMesh.Mesh()
    mesh.load( moab_mesh )

    tally_tag = mesh.getTagHandle("TALLY_TAG")
    error_tag = mesh.getTagHandle("ERROR_TAG")

    ret = dict()

    for i, e in enumerate( mesh.iterate( iBase.Type.region, iMesh.Topology.tetrahedron ), start=1 ):

        moab_val = tally_tag[e]
        moab_err = error_tag[e]

        ret[i] = (moab_val, moab_err)

    return ret

# Compare a MOAB and an MCNP dictionary created with the get_*_tallies functions above.
# (Since the dictionary formats are identical, ordering is actually arbitrary except for labels
def compare_tallies( moab_dict, mcnp_dict ):
    
    vtot = 0
    etot = 0

    moab_vals, moab_errs = zip( *[ moab_dict[i] for i in range(1,len(moab_dict)) ] )
    mcnp_vals, mcnp_errs = zip( *[ mcnp_dict[i] for i in range(1,len(moab_dict)) ] )

    moab_vals = numpy.array(moab_vals)
    moab_errs = numpy.array(moab_errs)
    mcnp_vals = numpy.array(mcnp_vals)
    mcnp_errs = numpy.array(mcnp_errs)

    vdiff = moab_vals - mcnp_vals
    ediff = moab_errs - mcnp_errs

    vdiff_percent = vdiff / ((moab_vals+mcnp_vals) / 2.0 ) * 100
    ediff_percent = ediff / ((moab_errs+mcnp_errs) / 2.0 ) * 100

    plt.subplot(3,1,1)
    plt.plot(vdiff_percent)
    #plt.plot(ediff_percent)
    plt.legend(['vdiff%','ediff%'])
    plt.subplot(3,1,2)
    plt.plot(moab_vals)
    plt.plot(mcnp_vals)
    plt.legend(['moab','mcnp'])
    plt.title('Values')
    plt.subplot(3,1,3)
    plt.plot(moab_errs)
    plt.plot(mcnp_errs)
    plt.legend(['moab','mcnp'])
    plt.title('Errors')
    plt.show()

    return

if __name__ == '__main__':
    moab = get_moab_tallies( sys.argv[1] )
    mctal = get_mcnp_mctal_tallies( sys.argv[2] )
    #compare_tallies( moab, mcnp )
    compare_tallies( moab, mctal[4] )
