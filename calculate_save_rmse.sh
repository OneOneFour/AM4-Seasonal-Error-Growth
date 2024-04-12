#!/bin/bash 
#SBATCH -p serc
#SBATCH --time 06:00:00
#SBATCH -c 64
#SBATCH --mem 96G
ml python/3.9.0
source ~/.bashrc
conda activate $GROUP_HOME/robcking/am4_error_prop
python save_rmse.py $1
