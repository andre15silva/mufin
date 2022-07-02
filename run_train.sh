#!/bin/bash

if [ $# != 4 ]; then
    echo "Usage: ./run_train.sh <model_storage> <direction> <training_dataset> <validation_dataset>"
    exit 1
fi

python src/train_model.py --model_storage $1 --$2 --training_dataset $3 --validation_dataset $4 --max_epochs 2 --samples_per_epoch 30000000 > $1/training_logs.out 2>&1
