#!/bin/bash

cd Dagmc
sbatch w_dagmc.aci.sh
cd Meshtally
sbatch w_meshtal.aci.sh
cd Regression
sbatch w_reg.aci.sh
cd VALIDATION_CRITICALITY
sbatch w_vcrit.aci.sh
cd VALIDATION_SHIELDING
sbatch w_vshield.aci.sh
cd VERIFICATION_KEFF
sbatch w_vkeff.aci.sh
cd ..
