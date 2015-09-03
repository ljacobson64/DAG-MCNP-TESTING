#!/bin/bash

# Dagmc test suite
cd ../Dagmc

for i in $(seq -f "%02g" 1 15); do
  if [ -a cases/$i/ref.dag.out ];   then cp results/$i/test$i.o cases/$i/ref.dag.out;   fi
  if [ -a cases/$i/ref.dag.mctal ]; then cp results/$i/test$i.m cases/$i/ref.dag.mctal; fi
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
  if [ -a cases/$i/ref/outp ];          then cp results/$i/test_o             cases/$i/ref/outp;          fi
  if [ -a cases/$i/ref/left_outp ];     then cp results/$i/test_o             cases/$i/ref/left_outp;     fi
  if [ -a cases/$i/ref/right_outp ];    then cp results/$i/test_o             cases/$i/ref/right_outp;    fi
  if [ -a cases/$i/ref/meshtal ];       then cp results/$i/meshtal            cases/$i/ref/meshtal;       fi
  if [ -a cases/$i/ref/left_meshtal ];  then cp results/$i/meshtal            cases/$i/ref/left_meshtal;  fi
  if [ -a cases/$i/ref/right_meshtal ]; then cp results/$i/meshtal            cases/$i/ref/right_meshtal; fi
  if [ -a cases/$i/ref/meshtal4.vtk ];  then cp results/$i/test_meshtal4.vtk  cases/$i/ref/meshtal4.vtk;  fi
  if [ -a cases/$i/ref/meshtal14.vtk ]; then cp results/$i/test_meshtal14.vtk cases/$i/ref/meshtal14.vtk; fi
  if [ -a cases/$i/ref/meshtal24.vtk ]; then cp results/$i/test_meshtal24.vtk cases/$i/ref/meshtal24.vtk; fi
  if [ -a cases/$i/ref/meshtal34.vtk ]; then cp results/$i/test_meshtal34.vtk cases/$i/ref/meshtal34.vtk; fi
  if [ -a cases/$i/ref/meshtal44.vtk ]; then cp results/$i/test_meshtal44.vtk cases/$i/ref/meshtal44.vtk; fi
  if [ -a cases/$i/ref/meshtal54.vtk ]; then cp results/$i/test_meshtal54.vtk cases/$i/ref/meshtal54.vtk; fi
  if [ -a cases/$i/ref/meshtal64.vtk ]; then cp results/$i/test_meshtal64.vtk cases/$i/ref/meshtal64.vtk; fi
done

# Regression test suite
cd ../Regression

# VALIDATION_CRITICALITY test suite
cd ../VALIDATION_CRITICALITY

cases_VC[ 1]=BAWXI2
cases_VC[ 2]=BIGTEN
cases_VC[ 3]=FLAT23
cases_VC[ 4]=FLAT25
cases_VC[ 5]=FLATPU
cases_VC[ 6]=FLSTF1
cases_VC[ 7]=GODIVA
cases_VC[ 8]=GODIVR
cases_VC[ 9]=HISHPG
cases_VC[10]=ICT2C3
cases_VC[11]=IMF03
cases_VC[12]=IMF04
cases_VC[13]=JEZ233
cases_VC[14]=JEZ240
cases_VC[15]=JEZPU
cases_VC[16]=LST2C2
cases_VC[17]=ORNL10
cases_VC[18]=ORNL11
cases_VC[19]=PNL2
cases_VC[20]=PNL33
cases_VC[21]=PUBTNS
cases_VC[22]=PUSH2O
cases_VC[23]=SB25
cases_VC[24]=SB5RN3
cases_VC[25]=STACY36
cases_VC[26]=THOR
cases_VC[27]=TT2C11
cases_VC[28]=UH3C6
cases_VC[29]=UMF5C2
cases_VC[30]=ZEBR8H
cases_VC[31]=ZEUS2

for i in "${cases_VC[@]}"; do
  if [ -a Templates/Linux/1e-4/outp$i ]; then cp results/$i/"$i"test.o Templates/Linux/1e-4/outp$i; fi
done

# VALIDATION_SHIELDING test suite
cd ../VALIDATION_SHIELDING

# VERIFICATION_KEFF test suite
cd ../VERIFICATION_KEFF

# Done
cd ../scripts
