#!/bin/bash

# Dagmc test suite
cd ../Dagmc

for i in $(seq -f "%02g" 1 15); do
  cp results/$i/test$i.o cases/$i/ref.dag.out
  cp results/$i/test$i.m cases/$i/ref.dag.mctal
done

# Meshtally test suite
cd ../Meshtally

cases_Meshtally[ 1]=conformal_cyl1
cases_Meshtally[ 2]=conformal_cyl2
cases_Meshtally[ 3]=energy_groups
cases_Meshtally[ 4]=gradient_flux
cases_Meshtally[ 5]=material_discontinuity
cases_Meshtally[ 6]=metroid
cases_Meshtally[ 7]=mode_np
cases_Meshtally[ 8]=reflecting_boundaries
cases_Meshtally[ 9]=squares
cases_Meshtally[10]=stu_cyl
cases_Meshtally[11]=stu_cyl2
cases_Meshtally[12]=tally_multipliers
cases_Meshtally[13]=uniform_flux
cases_Meshtally[14]=uniform_vol_source

for i in "${cases_Meshtally[@]}"; do
  if [ -a cases/$i/ref/outp ];          then cp results/$i/test_o        cases/$i/ref/outp;          fi
  if [ -a cases/$i/ref/left_outp ];     then cp results/$i/test_o        cases/$i/ref/left_outp;     fi
  if [ -a cases/$i/ref/right_outp ];    then cp results/$i/test_o        cases/$i/ref/right_outp;    fi
  if [ -a cases/$i/ref/meshtal ];       then cp results/$i/meshtal       cases/$i/ref/meshtal;       fi
  if [ -a cases/$i/ref/left_meshtal ];  then cp results/$i/meshtal       cases/$i/ref/left_meshtal;  fi
  if [ -a cases/$i/ref/right_meshtal ]; then cp results/$i/meshtal       cases/$i/ref/right_meshtal; fi
  if [ -a cases/$i/ref/meshtal4.vtk ];  then cp results/$i/meshtal4.vtk  cases/$i/ref/meshtal4.vtk;  fi
  if [ -a cases/$i/ref/meshtal14.vtk ]; then cp results/$i/meshtal14.vtk cases/$i/ref/meshtal14.vtk; fi
  if [ -a cases/$i/ref/meshtal24.vtk ]; then cp results/$i/meshtal24.vtk cases/$i/ref/meshtal24.vtk; fi
  if [ -a cases/$i/ref/meshtal34.vtk ]; then cp results/$i/meshtal34.vtk cases/$i/ref/meshtal34.vtk; fi
  if [ -a cases/$i/ref/meshtal44.vtk ]; then cp results/$i/meshtal44.vtk cases/$i/ref/meshtal44.vtk; fi
  if [ -a cases/$i/ref/meshtal54.vtk ]; then cp results/$i/meshtal54.vtk cases/$i/ref/meshtal54.vtk; fi
  if [ -a cases/$i/ref/meshtal64.vtk ]; then cp results/$i/meshtal64.vtk cases/$i/ref/meshtal64.vtk; fi
done

# Regression test suite

# VALIDATION_CRITICALITY test suite

# VALIDATION_SHIELDING test suite

# VERIFICATION_KEFF test suite

cd ../scripts
