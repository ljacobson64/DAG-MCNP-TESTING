#! /usr/bin/env python

from itaps import iBase,iMesh
import numpy
import numpy.linalg.linalg as la
import itertools
import sys
import optparse

def sum_meshes( options, filenames ):
    prime_mesh = iMesh.Mesh()
    prime_mesh.load( filenames[0] )
    
    prime_tag = prime_mesh.getTagHandle( options.tag )
    output_tag = prime_mesh.createTag( options.tag+"_SUM", 1, numpy.float64 )

    # Initialize all output tag values to 0
    for i in prime_mesh.iterate( iBase.Type.region, iMesh.Topology.tetrahedron ):
        output_tag[i] = 0

    for secondary_file in filenames[1:]:
        second_mesh = iMesh.Mesh()
        second_mesh.load( secondary_file )

        second_tag = second_mesh.getTagHandle( options.tag )
        for (i,j) in itertools.izip( prime_mesh.iterate( iBase.Type.region, iMesh.Topology.tetrahedron ),
                                     second_mesh.iterate( iBase.Type.region, iMesh.Topology.tetrahedron ) ):
            # Check to be sure this is the same tetrahedron in both files
            v1 = prime_mesh.getEntAdj(i,iBase.Type.vertex)
            p1 = prime_mesh.getVtxCoords(v1)

            v2 = second_mesh.getEntAdj(j, iBase.Type.vertex)
            p2 = second_mesh.getVtxCoords(v2)

            if( not numpy.equal( p1, p2 ).all() ):
                print 'ERROR: These meshes do no appear to correspond geometrically.'
                print '       Will proceed, but results may not be trustworthy.'

            prime_val = prime_tag[i]
            second_val = second_tag[j]
            new_val = prime_val+second_val
            output_tag[i] += new_val
    
    prime_mesh.save( options.output_file )

def main():
    default_tally_tag = 'TALLY_TAG'
    default_output_file = 'tallyadd_out.vtk'
    op = optparse.OptionParser(usage='usage: %prog [options] tallymesh tallymesh [tallymesh...]')
    op.add_option( '-t', '--tag', default=default_tally_tag, 
                   help='Tag to sum across each input mesh (default %default)' )
    op.add_option( '-o', '--output', dest='output_file', default=default_output_file,
                   help='Output file to create (default %default)' )

    (options, args) = op.parse_args()

    if len(args) < 2:
        op.error( 'Need at least two arguments' )

    sum_meshes( options, args )

if __name__=='__main__':
    main()
