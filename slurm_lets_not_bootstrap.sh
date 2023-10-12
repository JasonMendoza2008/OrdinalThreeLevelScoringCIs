#!/bin/bash

#SBATCH --job-name=bootstrap
#SBATCH --output=outs/%x.o%j.txt
#SBATCH --time=48:00:00
#SBATCH --partition=cpu_long
#SBATCH --array=0-999
#SBATCH --cpus-per-task=1
#SBATCH --mail-user=lhotteromain@gmail.com
#SBATCH --mail-type=ALL

# Load necessary modules
module purge
module load anaconda3/2021.05/gcc-9.2.0

# Activate anaconda environment
source activate bootstrap_env

# Run python script
for VARIABLE in 0 1000 2000 3000 4000 5000
do
  for n in 8 10 20 30 40 50 75 100 150 200 350 500 750 1000 2000
  do
    python main.py --seed=$((SLURM_ARRAY_TASK_ID + VARIABLE)) --test_set_size=$n --p0=0.1 --p1=0.7 --p2=0.2

    python main.py --seed=$((SLURM_ARRAY_TASK_ID + VARIABLE)) --test_set_size=$n --p0=0.1 --p1=0.2 --p2=0.7

    python main.py --seed=$((SLURM_ARRAY_TASK_ID + VARIABLE)) --test_set_size=$n --p0=0.05 --p1=0.05 --p2=0.9

    python main.py --seed=$((SLURM_ARRAY_TASK_ID + VARIABLE)) --test_set_size=$n --p0=0.005 --p1=0.005 --p2=0.99

    python main.py --seed=$((SLURM_ARRAY_TASK_ID + VARIABLE)) --test_set_size=$n --p0=0.2 --p1=0.6 --p2=0.2

    python main.py --seed=$((SLURM_ARRAY_TASK_ID + VARIABLE)) --test_set_size=$n --p0=0.3 --p1=0.5 --p2=0.2

    python main.py --seed=$((SLURM_ARRAY_TASK_ID + VARIABLE)) --test_set_size=$n --p0=0.05 --p1=0.04 --p2=0.91

    python main.py --seed=$((SLURM_ARRAY_TASK_ID + VARIABLE)) --test_set_size=$n --p0=0.05 --p1=0.06 --p2=0.89
  done
done
