#!/bin/bash

if [ $# != 3 ]; then
    echo "Usage: ./run_filter_generated_bugs.sh <storage_path> <dataset_name> <perturbation_strategy>"
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

python src/filter_single_hunk.py --storage $1 --$2 ${datasets[$2]} --model_input $2_generated_bugs_$3.json --model_output $2_generated_bugs_$3_hunk.json > $1/$2_generated_bugs_$3_hunk.out 2>&1
python src/filter_compile.py --storage $1 --$2 ${datasets[$2]} --model_input $2_generated_bugs_$3_hunk.json --model_output $2_generated_bugs_$3_hunk_compile.json > $1/$2_generated_bugs_$3_compile.out 2>&1
python src/filter_test.py --storage $1 --$2 ${datasets[$2]} --model_input $2_generated_bugs_$3_hunk_compile.json --model_output $2_generated_bugs_$3_hunk_compile_test.json > $1/$2_generated_bugs_$3_test.out 2>&1
