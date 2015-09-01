#!/bin/bash

RUN_DIR=`pwd`
MCNP_BIN=`which mcnp5.mpi`

#SBATCH --partition=pre
#SBATCH --time=1-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem-per-cpu=4000
#SBATCH --error=screen_err
#SBATCH --output=screen_out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ljjacobson@wisc.edu

./waf configure -e $MCNP_BIN
./waf -e $MCNP_BIN -j 16
