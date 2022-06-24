#!/bin/bash

if [ $# != 4 ]; then
    echo "Usage: ./run_generate_bugs_model.sh <storage_path> <dataset_name> <model_storage_path> <model_name>"
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

python src/generate_model.py --storage $1 --$2 ${datasets[$2]} --from_pretrained $3/$4 --results_file X --beam_width 1 --beam_groups 1 --repetition_penalty 1.0 --model_input $2_hunk_compile_test.json --model_output $2_generated_bugs_$4.json > $1/$2_generated_bugs_$4.out 2>&1
python src/filter_single_hunk.py --storage $1 --$2 ${datasets[$2]} --model_input $2_generated_bugs_$4.json --model_output $2_generated_bugs_$4_hunk.json > $1/$2_generated_bugs_$4_hunk.out 2>&1
python src/filter_compile.py --storage $1 --$2 ${datasets[$2]} --model_input $2_generated_bugs_$4_hunk.json --model_output $2_generated_bugs_$4_hunk_compile.json > $1/$2_generated_bugs_$4_hunk_compile.out 2>&1
python src/filter_test.py --storage $1 --$2 ${datasets[$2]} --model_input $2_generated_bugs_$4_hunk_compile.json --model_output $2_generated_bugs_$4_hunk_compile_test.json > $1/$2_generated_bugs_$4_hunk_compile_test.out 2>&1
