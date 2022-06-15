import numpy as np
import argparse
import pathlib
import subprocess

from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, T5Config, Seq2SeqTrainingArguments, Seq2SeqTrainer

import utils
import serialization_utils
import model_utils


# TODO: implement this according to the defined format
def create_bug(args, bug, generated_str):
    pass


def generate(args):
    dataset = serialization_utils.load_dataset(args)

    tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained)

    new_dataset = serialization_utils.create_empty_dataset(args)
    
    # TODO: iterate over source code files of the fixed programs
    for bug in dataset.get_bugs():
        for file in pathlib.Path(bug.get_path()).glob("**/*.java"):
            print(file)
            
            cmd = "java -jar src/getlines/target/getlines-1.0-SNAPSHOT-jar-with-dependencies.jar %s" % file.absolute()
            run = subprocess.run(cmd, shell=True, capture_output=True)
            if run.returncode != 0:
                continue

            lns = run.stdout.decode("utf-8").split()
            lns = list(map(lambda x: (int(x[0]), int(x[1])), map(lambda x: x.split("-"), lns)))

            with open(file) as f:
                lines = f.readlines()
                samples = list(map(
                    lambda x: lines[max(0, x[0]-6):x[0]-1] + \
                            ["[START_BUGGY]"] + lines[x[0]-1:x[1]] + ["[END_BUGGY]"] + \
                            lines[x[1]:min(len(lines), x[1]+5)],
                    lns
                    ))
                print(samples[0])
            break
    #    # TODO: Choose according to parameter
    #    source = tokenizer(source, max_length=max_input_length, truncation=True, return_tensors='pt')
    #    
    #    # TODO: parametrize this
    #    target_ids = model.generate(
    #            input_ids=source.input_ids,
    #            attention_mask=source.attention_mask,
    #            num_beams=args.beam_width,
    #            num_beam_groups=args.beam_groups,
    #            repetition_penalty=args.repetition_penalty,
    #            max_length=128,
    #            early_stopping=False,
    #            num_return_sequences=args.beam_width,
    #            )

    #    # Generate the tentative solution
    #    generated_str = tokenizer.decode(target_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)

    #    # TODO: Choose according to parameter
    #    new_dataset.add_bug(create_bug(args, bug, generated_str))

    #serialization_utils.save_dataset(args, new_dataset)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to generate a dataset with a pretrained model from a given dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_eval_args(parser)
    args = parser.parse_args()

    generate(args)
