import numpy as np
import argparse
import pathlib
import math

from datasets import load_dataset, concatenate_datasets

import utils
import serialization_utils
import model_utils


def group_data_for_fixer(args):
    # Load the dataset
    round0_dataset = load_dataset("json", data_files=str(pathlib.Path(args.round0_dataset).absolute()))
    fixer_dataset = load_dataset("json", data_files=str(pathlib.Path(args.fixer_generated_dataset).absolute()), field="bugs")
    breaker_dataset = load_dataset("json", data_files=str(pathlib.Path(args.breaker_generated_dataset).absolute()), field="bugs")

    # Compute repeat numbers
    round0_size = len(round0_dataset["train"])
    fixer_size = len(fixer_dataset["train"])
    breaker_size = len(breaker_dataset["train"])
    quarter = max(round0_size, fixer_size // 2, breaker_size)
    round0_repeats = quarter // round0_size if quarter > round0_size else 1
    fixer_repeats = (2 * quarter) // fixer_size if quarter > 2 * fixer_size else 1
    breaker_repeats = quarter // breaker_size if quarter > breaker_size else 1

    # Oversample the fixer dataset
    augmented_round0_dataset = load_dataset("json", data_files=[str(pathlib.Path(args.round0_dataset).absolute())]*round0_repeats)
    augmented_fixer_dataset = load_dataset("json", data_files=[str(pathlib.Path(args.fixer_generated_dataset).absolute())]*fixer_repeats, field="bugs")
    augmented_breaker_dataset = load_dataset("json", data_files=[str(pathlib.Path(args.breaker_generated_dataset).absolute())]*breaker_repeats, field="bugs")

    # Shuffle the dataset
    dataset = concatenate_datasets([augmented_round0_dataset["train"], augmented_fixer_dataset["train"], augmented_breaker_dataset["train"]])
    dataset = dataset.shuffle(seed=42)

    print(dataset)

    # Save the datasets
    dataset.to_json(str(pathlib.Path(args.training_dataset).absolute()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to shuffle and store the processed dataset.")
    parser = utils.add_group_data_for_fixer_args(parser)
    args = parser.parse_args()

    group_data_for_fixer(args)
