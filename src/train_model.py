import numpy as np
import argparse
import pathlib

from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, T5Config, Seq2SeqTrainingArguments, Seq2SeqTrainer, EarlyStoppingCallback
from datasets import load_dataset, load_metric

import utils
import serialization_utils
import model_utils


def train(args):
    # Load the pretrained model if the argument is set, otherwise build one from the base
    if args.from_pretrained != None:
        tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
        model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained)
    else:
        tokenizer = AutoTokenizer.from_pretrained("uclanlp/plbart-base")
        tokenizer.add_tokens(["[START_BUGGY]", "[END_BUGGY]", "[CONTEXT]", "[CLASS]", "[METHOD]", "[PARAMETERS]", "[RETURN_TYPE]", "[VARIABLES]", "[PATCH]"])
        model = AutoModelForSeq2SeqLM.from_config(
                T5Config(
                    vocab_size=len(tokenizer),
                    bos_token_id=tokenizer.bos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.pad_token_id,
                    decoder_start_token_id=tokenizer.pad_token_id,
                    )
                )

    max_input_length = 768
    max_target_length = 128

    def preprocess_buggy_to_fixed(examples):
        inputs = [model_utils.source_str(diff, context) for diff, context in zip(examples["diff"], examples["context"])]
        targets = [model_utils.target_str(diff) for diff in examples["diff"]]
        model_inputs = tokenizer(inputs, max_length=max_input_length, padding=True, truncation=True)

        # Set up the tokenizer for targets
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(targets, max_length=max_target_length, padding=True, truncation=True)

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs


    def preprocess_fixed_to_buggy(examples):
        inputs = [model_utils.source_str_buggy(ex) for ex in examples["diff"]]
        targets = [model_utils.target_str_buggy(ex) for ex in examples["diff"]]
        model_inputs = tokenizer(inputs, max_length=max_input_length, padding=True, truncation=True)

        # Set up the tokenizer for targets
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(targets, max_length=max_target_length, padding=True, truncation=True)

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    # Build Data Collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # Load the dataset
    data_files = {
            "train" : str(pathlib.Path(args.training_dataset).absolute()),
            "validation" : str(pathlib.Path(args.validation_dataset).absolute())
            }
    split_datasets = load_dataset("json", data_files=data_files)
    
    # Tokenize the datasets
    if args.buggy_to_fixed:
        preprocess_function = preprocess_buggy_to_fixed
    elif args.fixed_to_buggy:
        preprocess_function = preprocess_fixed_to_buggy

    tokenized_datasets = split_datasets.map(
            preprocess_function,
            batched=True,
            remove_columns=split_datasets["train"].column_names,
            )

    # Compute the number of max epochs
    max_epochs = (args.max_epochs * args.samples_per_epoch) // len(split_datasets["train"]) + 1

    # Setup training args
    training_args = Seq2SeqTrainingArguments(
            pathlib.Path(args.model_storage).absolute(),
            evaluation_strategy="steps",
            eval_steps=10000,
            save_strategy="steps",
            save_steps=10000,
            learning_rate=1e-4,
            optim="adamw_torch",
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            weight_decay=0.01,
            save_total_limit=4,
            num_train_epochs=max_epochs,
            predict_with_generate=True,
            fp16=True,
            push_to_hub=False,
            metric_for_best_model="eval_loss",
            load_best_model_at_end=True,
            )


    # Setup trainer
    trainer = Seq2SeqTrainer(
            model,
            training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"],
            data_collator=data_collator,
            tokenizer=tokenizer,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
            )

    # Train the model
    trainer.train()

    # Store the trained model
    tokenizer.save_pretrained(args.model_storage)
    model.save_pretrained(args.model_storage)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to train a model based on a given dataset.")
    parser = utils.add_train_args(parser)
    args = parser.parse_args()

    train(args)
