import numpy as np
import pandas as pd
import argparse
import pathlib
import subprocess
import functools
import tempfile
import os
import uuid
import torch

from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, T5Config, Seq2SeqTrainingArguments, Seq2SeqTrainer

import utils
import serialization_utils
import model_utils
from models.bug import Bug
from models.defects4j.defects4jbug import Defects4JBug
from models.bugsdotjar.bugsdotjar import BugsDotJarBug
from models.bears.bearsbug import BearsBug
from models.quixbugs.quixbugsbug import QuixBugsBug


def create_bug(args, original_bug, diff) -> Bug:
    uid = str(uuid.uuid4())
    if args.defects4j != None:
        return Defects4JBug(original_bug.get_identifier() + "-generated_bug-" + uid, original_bug.get_path(), diff)
    elif args.bugsdotjar != None:
        return BugsDotJarBug(original_bug.get_identifier() + "-generated_bug-" + uid, original_bug.get_path(), diff)
    elif args.bears != None:
        return BearsBug(original_bug.get_identifier() + "-generated_bug-" + uid, original_bug.get_path(), diff)
    elif args.quixbugs != None:
        return QuixBugsBug(original_bug.get_identifier() + "-generated_bug-" + uid, original_bug.get_path(), diff)
    else:
        return NotImplementedError("%s" % args)


def create_bugs(args, bug, original_file, df):
    bugs = []
    for index, row in df.iterrows():
        with open(original_file, "r") as f:
            lines = f.readlines()
            lines = lines[:row["start_line"]-1] + \
                    [row["generated_str"]] + \
                    lines[row["end_line"]:]

        buggy_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False, suffix=".java")
        buggy_file.writelines(lines)
        buggy_file.flush()
        buggy_file.close()

        # Compute diff
        diff = utils.get_diff(original_file, buggy_file.name)
        os.remove(str(pathlib.Path(buggy_file.name).absolute()))

        # Create the bug
        bugs += [create_bug(args, bug, diff)]

    return bugs


def generate(args):
    dataset = serialization_utils.load_dataset(args)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    tokenizer = AutoTokenizer.from_pretrained(args.from_pretrained)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.from_pretrained).to(device)

    new_dataset = serialization_utils.create_empty_dataset(args)

    for bug in dataset.get_bugs():
        for file in pathlib.Path(bug.get_path()).glob("**/*.java"):
            # Ignore tests
            if "test" in file.name or "Test" in file.name:
                continue

            cmd = "java -jar src/getlines/target/getlines-1.0-SNAPSHOT-jar-with-dependencies.jar %s" % file.absolute()
            run = subprocess.run(cmd, shell=True, capture_output=True)
            if run.returncode != 0:
                continue

            try:
                lns = run.stdout.decode("utf-8").split()
            except UnicodeDecodeError as e:
                continue
            if len(lns) == 0:
                continue
            print(len(lns))
            df = pd.DataFrame(
                    list(
                        map(lambda x: (int(x[0]), int(x[1])), 
                            map(lambda x: x.split("-"), lns))
                        )
                    ,
                    columns=["start_line", "end_line"])

            with open(file) as f:
                try:
                    lines = f.readlines()
                except UnicodeDecodeError as e:
                    continue
                df["source"] = df.apply(
                        lambda x: functools.reduce(
                            lambda y, z:
                            y.strip() + " " + z.strip(),
                            lines[max(0, x["start_line"]-6):x["start_line"]-1] + \
                                    ["[START_BUGGY]"] + \
                                    lines[x["start_line"]-1:x["end_line"]] + \
                                    ["[END_BUGGY]"] + \
                                    lines[x["end_line"]:min(len(lines), x["end_line"]+5)]
                                    ),
                        axis=1
                        )

            max_input_length = 732
            unchunked_sources = list(df["source"])
            chunk_size = 100
            chunked_sources = [unchunked_sources[i:i + chunk_size] for i in range(0, len(unchunked_sources), chunk_size)]

            df.loc[:, "generated_str"] = np.empty(len(unchunked_sources))
            for i, chunk in enumerate(chunked_sources):
                source = tokenizer(chunk, max_length=max_input_length, padding=True, truncation=True, return_tensors='pt').to(device)
                target_ids = model.generate(
                        input_ids=source.input_ids,
                        attention_mask=source.attention_mask,
                        num_beams=args.beam_width,
                        max_length=128,
                        early_stopping=False,
                        num_return_sequences=1,
                        )

                # Generate the tentative solution
                generated = tokenizer.batch_decode(target_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                df.loc[i*chunk_size:i*chunk_size+len(generated)-1, "generated_str"] = generated

            bugs_to_add = create_bugs(args, bug, file, df)
            print("Generated %d bugs for %s" % (len(bugs_to_add), file))
            for new_bug in bugs_to_add:
                new_dataset.add_bug(new_bug)

            # DEBUG ONLY
            #break

    serialization_utils.save_dataset(args, new_dataset)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to generate a dataset with a pretrained model from a given dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_generate_bugs_from_breaker_args(parser)
    args = parser.parse_args()

    generate(args)
