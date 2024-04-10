#!/bin/bash 
#SBATCH -p serc
#SBATCH --time 04:00:00
#SBATCH -c 64
#SBATCH --mem 96G

conda activate $GROUP_HOME/robcking/am4_error_prop
python save_rmse.py $1