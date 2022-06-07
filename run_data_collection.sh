#!/bin/bash

if [ $# != 2 ]; then
    echo "Usage: ./run_data_collection.sh <storage_path> <dataset_name>"
    exit 1
fi

declare -A datasets=( ["defects4j"]="data/defects4j" 
                        ["bears"]="data/bears-benchmark" 
                        ["bugsdotjar"]="data/bugs-dot-jar" 
                        ["quixbugs"]="data/QuixBugs")

if [[ ! " ${!datasets[*]} " =~ " $2 " ]]; then
    echo "Dataset not found. Please use one of the following: ${!datasets[@]}"
    exit 1
fi

python src/checkout.py --storage $1 --$2 ${datasets[$2]} > $1/$2_checkout.out 2>&1
python src/filter_single_hunk.py --storage $1 --$2 ${datasets[$2]} --model_output $2_hunk.json > $1/$2_hunk.out 2>&1
python src/filter_compile.py --storage $1 --$2 ${datasets[$2]} --model_input $2_hunk.json --model_output $2_hunk_compile.json > $1/$2_compile.out 2>&1
python src/filter_test.py --storage $1 --$2 ${datasets[$2]} --model_input $2_hunk_compile.json --model_output $2_hunk_compile_test.json > $1/$2_test.out 2>&1
