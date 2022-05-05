import numpy as np
import argparse
import pathlib

from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, T5Config, Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import load_dataset, load_metric

import utils
import model_utils


def train(args):
    # Load the pretrained model if the argument is set, otherwise build one from the base
    if args.from_pretrained != None:
        tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
        model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained)
    else:
        tokenizer = AutoTokenizer.from_pretrained("uclanlp/plbart-base")
        model = AutoModelForSeq2SeqLM.from_config(
                T5Config(
                    vocab_size=tokenizer.vocab_size,
                    bos_token_id=tokenizer.bos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.pad_token_id,
                    decoder_start_token_id=tokenizer.pad_token_id,
                    )
                )

    # Parametrize
    max_input_length = 128
    max_target_length = 128

    # TODO: Change this to generate the definitive complex training sample
    def preprocess_buggy_to_fixed(examples):
        inputs = [model_utils.source_str(ex) for ex in examples["diff"]]
        targets = [model_utils.target_str(ex) for ex in examples["diff"]]
        model_inputs = tokenizer(inputs, max_length=max_input_length, truncation=True, return_tensors='pt')

        # Set up the tokenizer for targets
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(targets, max_length=max_target_length, truncation=True, return_tensors='pt')

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs


    # TODO: Change this to generate the definitive complex training sample
    def preprocess_fixed_to_buggy(examples):
        inputs = [model_utils.target_str(ex) for ex in examples["diff"]]
        targets = [model_utils.source_str(ex) for ex in examples["diff"]]
        model_inputs = tokenizer(inputs, max_length=max_input_length, truncation=True)

        # Set up the tokenizer for targets
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(targets, max_length=max_target_length, truncation=True)

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    # Build Data Collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # Load the dataset
    dataset = load_dataset("json", data_files=str(utils.get_json_input_file(args).absolute()), field="bugs")

    # Split dataset into training and validation
    split_datasets = dataset["train"].train_test_split(train_size=0.9, seed=15)
    split_datasets["validation"] = split_datasets.pop("test")

    # Tokenize the datasets
    # TODO: Change this to an if condition
    preprocess_function = preprocess_buggy_to_fixed
    tokenized_datasets = split_datasets.map(
            preprocess_function,
            batched=True,
            remove_columns=split_datasets["train"].column_names,
            )

    # Setup training args
    # TODO: Parametrize
    training_args = Seq2SeqTrainingArguments(
            pathlib.Path(args.model_storage).absolute(),
            evaluation_strategy="no",
            save_strategy="no",
            learning_rate=2e-5,
            optim="adamw_torch",
            per_device_train_batch_size=8,
            per_device_eval_batch_size=16,
            weight_decay=0.01,
            save_total_limit=3,
            num_train_epochs=3,
            predict_with_generate=True,
            fp16=True,
            push_to_hub=False,
            )

    # Setup trainer
    trainer = Seq2SeqTrainer(
            model,
            training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"],
            data_collator=data_collator,
            tokenizer=tokenizer,
            )

    # Train the model
    trainer.train()

    # Store the trained model
    tokenizer.save_pretrained(args.model_storage)
    model.save_pretrained(args.model_storage)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to train a model based on a given dataset.")
    parser = utils.add_core_args(parser)
    parser = utils.add_train_args(parser)
    args = parser.parse_args()

    train(args)
