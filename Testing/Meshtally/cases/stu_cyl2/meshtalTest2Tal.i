meshtalTest.i 
c DAGMC input file: use with meshtalTest.sat 
c
c Data Card
mode n
m1 1001 2 8016  1       $water
sdef erg=2 x=0.0 y=0.0 z=d1
si1  -60.96     60.96
sp1 0     1
f14:n 1 2 3 4 5 t
c I would like tally 24 to be the mesh tally
c
fmesh4:n geom=dag
fc4 dagmc inp=tallyTetMesh.h5m  tag=abaqus_set_name 
           tagval= heatTest-1-1 tagval=heatTest-2-1 
           tagval= heatTest-3-1 tagval=heatTest-4-1
           out=test_meshtal4.vtk
fm4 -1 0 -4 -1
c
fmesh64:n geom=dag
fc64 dagmc inp=tallyTetMesh.h5m tag=abaqus_set_name tagval=heatTest-5-1
           out=test_meshtal64.vtk
fm64 -1 0 -4 -1
c
print 110 126
nps 1e5
prdmp 2j -1
c end program
