#!/bin/bash
#PBS -N oaat_postp_num
#PBS -q casper
#PBS -l walltime=1:00:00
#PBS -A P93300641
#PBS -j oe
#PBS -k eod
#PBS -l select=1:ncpus=1

source ~/.bashrc
conda activate ppe-py

python oaat_postp.py num





