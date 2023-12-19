#!/bin/bash
#PBS -N enscat
#PBS -q casper
#PBS -l walltime=1:00:00
#PBS -A P93300641
#PBS -j oe
#PBS -k eod
#PBS -l select=1:ncpus=1


module load nco
ncecat -u param /glade/scratch/djk2120/postp/oaat/oaat* postp.nc
source ~/.bashrc
conda activate ppe-py
python label.py
rm postp.nc
