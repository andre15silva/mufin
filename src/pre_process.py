import numpy as np
import argparse
import pathlib

from datasets import load_dataset

import utils
import serialization_utils
import model_utils


def split_train_val(args):
    # Load the dataset
    dataset = load_dataset("json", data_files=str(pathlib.Path(args.dataset).absolute()) + "/*.json", field="bugs")

    # Shuffle the dataset
    dataset["train"] = dataset["train"].shuffle(seed=42)

    print(dataset)

    # Save the datasets
    dataset["train"].to_json(str(pathlib.Path(args.training_dataset).absolute()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to shuffle and store the processed dataset.")
    parser = utils.add_pre_process_args(parser)
    args = parser.parse_args()

    split_train_val(args)
