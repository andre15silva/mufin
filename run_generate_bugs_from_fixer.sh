#!/bin/bash

if [ $# != 5 ]; then
    echo "Usage: ./run_generate_bugs_from_fixer.sh <storage_path> <dataset_name> <from_pretrained> <round> <beam_width>"
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

if [[ "$4" == *"nocritic"* ]]; then
    python src/generate_bugs_from_fixer.py --storage $1 --$2 ${datasets[$2]} --from_pretrained $3 --beam_width $5 --model_input $2_hunk_compile_test.json --model_output $2_fixer_generated_bugs_$4.json --nocritic > $1/$2_fixer_generated_bugs_$4.out 2>&1
fi

if [[ "$4" == *"compiler"* ]]; then
    python src/generate_bugs_from_fixer.py --storage $1 --$2 ${datasets[$2]} --from_pretrained $3 --beam_width $5 --model_input $2_hunk_compile_test.json --model_output $2_fixer_generated_bugs_$4.json --compiler > $1/$2_fixer_generated_bugs_$4.out 2>&1
fi

if [[ "$4" == *"tests"* ]]; then
    python src/generate_bugs_from_fixer.py --storage $1 --$2 ${datasets[$2]} --from_pretrained $3 --beam_width $5 --model_input $2_hunk_compile_test.json --model_output $2_fixer_generated_bugs_$4.json --tests > $1/$2_fixer_generated_bugs_$4.out 2>&1
fi

if [[ "$4" == *"round0"* ]]; then
    python src/generate_bugs_from_fixer.py --storage $1 --$2 ${datasets[$2]} --from_pretrained $3 --beam_width $5 --model_input $2_hunk_compile_test.json --model_output $2_fixer_generated_bugs_$4.json --nocritic --compiler --tests > $1/$2_fixer_generated_bugs_$4.out 2>&1
fi
