import numpy as np
import argparse
import pathlib

from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, T5Config, Seq2SeqTrainingArguments, Seq2SeqTrainer

import utils
import model_utils


# TODO: implement this as the definitive version
def preprocess_buggy_to_fixed(tokenizer, bug):
    source = model_utils.source_str(bug.get_diff())
    target = model_utils.target_str(bug.get_diff())
    print("source: " + source)
    print("target: " + target)

    # TODO: parametrize this
    max_input_length = 128
    return tokenizer(source, max_length=max_input_length, truncation=True, return_tensors='pt'), target


# TODO: implement this as the definitive version
def preprocess_fixed_to_buggy(tokenizer, bug):
    pass


# TODO: implement this
def evaluate_fix(bug, tentative_fix):
    print("generated: " + tentative_fix)
    return True


# TODO: implement this
def evaluate_bug(bug, tentative_bug):
    print("generated " + tentative_bug)
    return True


def evaluate(args):
    dataset = utils.load_dataset(args)

    tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained)
    
    results = {}
    for bug in dataset.get_bugs():
        # TODO: Choose according to parameter
        source, target = preprocess_buggy_to_fixed(tokenizer, bug)
        
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
        results[bug.get_identifier()] = evaluate_fix(bug, generated_str)

    print(results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to evaluate a pretrained model on a given dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_eval_args(parser)
    args = parser.parse_args()

    evaluate(args)
