import numpy as np
import argparse
import pathlib

from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, T5Config, Seq2SeqTrainingArguments, Seq2SeqTrainer

import utils
import serialization_utils
import model_utils


def create_empty_dataset(args):
    if args.defects4j != None:
        defects4j = Defects4J(pathlib.Path(args.defects4j).absolute())
        return defects4j
    elif args.bugsdotjar != None:
        bugsdotjar = BugsDotJar(pathlib.Path(args.bugsdotjar).absolute())
        return bugsdotjar
    elif args.bears != None:
        bears = Bears(pathlib.Path(args.bears).absolute())
        return bears
    elif args.quixbugs != None:
        quixbugs = QuixBugs(pathlib.Path(args.quixbugs).absolute())
        return quixbugs
    else:
        return NotImplementedError("%s" % args)


# TODO: implement this as the definitive version
def preprocess_buggy_to_fixed(tokenizer, bug):
    source = model_utils.source_str(bug.get_diff())

    # TODO: parametrize this
    max_input_length = 128
    return tokenizer(source, max_length=max_input_length, truncation=True, return_tensors='pt')


# TODO: implement this as the definitive version
def preprocess_fixed_to_buggy(tokenizer, bug):
    pass


# TODO: implement this according to the defined format
def create_bug(args, bug, generated_str):
    pass


def generate(args):
    dataset = serialization_utils.load_dataset(args)

    tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained)

    new_dataset = create_empty_dataset(args)
    
    for bug in dataset.get_bugs():
        # TODO: Choose according to parameter
        source = preprocess_buggy_to_fixed(tokenizer, bug)
        
        # TODO: parametrize this
        target_ids = model.generate(
                input_ids=source.input_ids,
                attention_mask=source.attention_mask,
                num_beams=50,
                max_length=128,
                early_stopping=True,
                )

        # Generate the tentative solution
        generated_str = tokenizer.decode(target_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)

        # TODO: Choose according to parameter
        new_dataset.add_bug(create_bug(args, bug, generated_str))

    serialization_utils.save_dataset(args, new_dataset)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to generate a dataset with a pretrained model from a given dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_eval_args(parser)
    args = parser.parse_args()

    generate(args)
