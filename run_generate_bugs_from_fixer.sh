#!/bin/bash

if [ $# != 6 ]; then
    echo "Usage: ./run_generate_bugs_from_fixer.sh <storage_path> <dataset_name> <from_pretrained> <critic> <round> <beam_width>"
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

python src/generate_bugs_from_fixer.py --storage $1 --$2 ${datasets[$2]} --from_pretrained $3 --beam_width $6 --model_input $2_hunk_compile_test.json --model_output $2_fixer_generated_bugs_$6_$5.json > $1/$2_fixer_generated_bugs_$6_$5.out 2>&1
