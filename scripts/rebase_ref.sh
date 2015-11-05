#!/bin/bash

# Dagmc test suite
if false; then
  cd ../Dagmc

  for i in $(seq -f "%02g" 1 15); do
    echo Dagmc/$i
    if [ -a cases/$i/ref.dag.out ];   then cp results/$i/test$i.o cases/$i/ref.dag.out;   fi
    if [ -a cases/$i/ref.dag.mctal ]; then cp results/$i/test$i.m cases/$i/ref.dag.mctal; fi
  done
fi

# Meshtally test suite
if false; then
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
    echo Meshtally/$i
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
fi

# Regression test suite
if false; then
  cd ../Regression

  for i in $(seq -f "%02g" 1 99); do
    echo Regression/$i
    if [ -a Templates_c12/Linux/outp$i ]; then cp results/$i/inp"$i"o Templates_c12/Linux/outp$i; fi
    if [ -a Templates_c12/Linux/mctl$i ]; then cp results/$i/inp"$i"m Templates_c12/Linux/mctl$i; fi
    if [ -a Templates_c12/Linux/wout$i ]; then cp results/$i/inp"$i"e Templates_c12/Linux/wout$i; fi
  done
fi

# VALIDATION_CRITICALITY test suite
if false; then
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
    echo VALIDATION_CRITICALITY/$i
    if [ -a Templates/Linux/1e-4/outp$i ]; then cp results/$i/"$i"test.o Templates/Linux/1e-4/outp$i; fi
  done
fi

# VALIDATION_SHIELDING test suite
if false; then
  cd ../VALIDATION_SHIELDING

  cases_VS[ 1]=BE08
  cases_VS[ 2]=C29
  cases_VS[ 3]=CCR20
  cases_VS[ 4]=COAIR
  cases_VS[ 5]=COTEF
  cases_VS[ 6]=FE09
  cases_VS[ 7]=FS1ONN
  cases_VS[ 8]=FS3OFN
  cases_VS[ 9]=FS3ONP
  cases_VS[10]=FS7OFP
  cases_VS[11]=FS7ONN
  cases_VS[12]=H2O19
  cases_VS[13]=KERMIN
  cases_VS[14]=LI616
  cases_VS[15]=N31
  cases_VS[16]=PB14
  cases_VS[17]=SKYINP
  cases_VS[18]=SMAIR
  cases_VS[19]=SMTEF

  for i in "${cases_VS[@]}"; do
    echo VALIDATION_SHIELDING/$i
    if [ -a Templates/Linux/1e-4/outp_$i ]; then cp results/$i/"$i"test.o Templates/Linux/1e-4/outp_$i; fi
    if [ -a Templates/Linux/1e-4/mctl_$i ]; then cp results/$i/"$i"test.m Templates/Linux/1e-4/mctl_$i; fi
  done
fi

# VERIFICATION_KEFF test suite
if false; then
  cd ../VERIFICATION_KEFF
fi

# Done
cd ../scripts
