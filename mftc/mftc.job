#!/bin/bash

#SBATCH --job-name=mClassifier
#SBATCH --error=../logs/mClassifier_%A_%a.err
#SBATCH --output=../logs/mClassifier_%j.out
#SBATCH --array=3-3
#SBATCH --time=3:00:00
#SBATCH --ntasks=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --account=mdehghan_709

module purge
module restore selfharm
source ../../reddit/bin/activate

srun python moral_classifier.py ${SLURM_ARRAY_TASK_ID}

