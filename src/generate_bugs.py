import argparse
import sys
import pathlib
import subprocess
import os
import tempfile
import shutil
import uuid
import time

import utils
import serialization_utils
from models.bug import Bug
from models.defects4j.defects4jbug import Defects4JBug
from models.bugsdotjar.bugsdotjar import BugsDotJarBug
from models.bears.bearsbug import BearsBug
from models.quixbugs.quixbugsbug import QuixBugsBug


def apply_bug(original_file, infos):
    perturbed_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False, suffix=".java")

    action = infos[0]
    corrupt_code =  infos[1]  
    lineNo1 =  infos[2]
    lineNo2 =  infos[3]
    lineNo3 =  infos[4]
    lineNo4 =  infos[5]
    lineNo5 =  infos[6]

    # read and perturb code 
    perturbed_content = ""
    if "ADD" in action or "REPLACE" in action.upper() or "BUGLAB" in action.upper():
        with open(original_file, "r") as f:
            lines = f.readlines()
            for i in range(0,len(lines)):
                if i+1< int(lineNo1) or i+1> int(lineNo1)+4:
                    perturbed_content+=lines[i]
                elif i+1==int(lineNo1):
                    perturbed_content+=corrupt_code+"\n"
                elif i+1==int(lineNo1)+1: 
                    if lineNo2=='':
                        perturbed_content+=lines[i]
                    else:
                        perturbed_content+=" \n"
                elif i+1==int(lineNo1)+2:
                    if lineNo3=='':
                        perturbed_content+=lines[i]
                    else:
                        perturbed_content+=" \n"
                elif i+1==int(lineNo1)+3:  
                    if lineNo4=='':
                        perturbed_content+=lines[i]
                    else:
                        perturbed_content+=" \n"
                elif i+1==int(lineNo1)+4:
                    if lineNo5=='':
                        perturbed_content+=lines[i]
                    else:
                        perturbed_content+=" \n"
    elif "REMOVE" in action.upper():
        with open(original_file, "r") as f:
            lines = f.readlines()
            for i in range(0,len(lines)):
                if i+1< int(lineNo1) or i+1> int(lineNo1)+4:
                    perturbed_content+=lines[i]
                elif i+1==int(lineNo1):
                    perturbed_content+= lines[i]+" \n" +corrupt_code
                elif i+1==int(lineNo1)+1: 
                    if lineNo2=='':
                        perturbed_content+=lines[i]
                    else:
                        perturbed_content+=" \n"
                elif i+1==int(lineNo1)+2:
                    if lineNo3=='':
                        perturbed_content+=lines[i]
                    else:
                        perturbed_content+=" \n"
                elif i+1==int(lineNo1)+3:  
                    if lineNo4=='':
                        perturbed_content+=lines[i]
                    else:
                        perturbed_content+=" \n"
                elif i+1==int(lineNo1)+4:
                    if lineNo5=='':
                        perturbed_content+=lines[i]
                    else:
                        perturbed_content+=" \n"

    # Write the perturbed code back to the tmp file
    perturbed_file.write(perturbed_content)
    perturbed_file.flush()
    perturbed_file.close()
    
    diff = utils.get_diff(str(original_file), str(perturbed_file.name))
    # TODO: there is some bug which is makes the diff return an empty diff most of the times
    if diff == "" and corrupt_code != "":
        print("A %s following perturbation didn't generate any diff." % (infos[0]))
    os.remove(str(pathlib.Path(perturbed_file.name).absolute()))
    return diff


def create_bug(args, original_bug, diff) -> Bug:
    uid = str(uuid.uuid4())
    if args.defects4j != None:
        return Defects4JBug(original_bug.get_identifier() + "-" + uid, original_bug.get_path(), diff)
    elif args.bugsdotjar != None:
        return BugsDotJarBug(original_bug.get_identifier() + "-" + uid, original_bug.get_path(), diff)
    elif args.bears != None:
        return BearsBug(original_bug.get_identifier() + "-" + uid, original_bug.get_path(), diff)
    elif args.quixbugs != None:
        return QuixBugsBug(original_bug.get_identifier() + "-" + uid, original_bug.get_path(), diff)
    else:
        return NotImplementedError("%s" % args)


def construct_bug(args, original_bug, original_file, perturbations_file):
    bugs = []
    if pathlib.Path(perturbations_file).exists():
        with open(perturbations_file, "r") as pf:
            for line in pf.readlines():
                try:
                    if not '^' in line: continue
                    infos = line.split('^')
                    if len(infos) != 11: continue

                    # Create bug
                    diff = apply_bug(original_file, infos)
                    if diff != "":
                        bug = create_bug(args, original_bug, diff)
                        bugs.append(bug)

                except Exception as e:
                    print(e)
                    continue
            
                # TODO: Debug purposes only
                #break
    
        os.remove(perturbations_file)

    return bugs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to generate bugs for all projects of a dataset")
    parser = utils.add_core_args(parser)
    parser = utils.add_generation_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = serialization_utils.load_dataset(args)

    generation_strategy = None
    if args.selfapr:
        generation_strategy = "SelfAPR"
    elif args.buglab:
        generation_strategy = "BugLab"
    else:
        print("You must set either SelfAPR ou BugLab as the bug generation strategy.")
        sys.exit(1)


    for bug in dataset.get_bugs():
        counter = 0
        new_dataset = serialization_utils.create_empty_dataset(args)
        for file in pathlib.Path(bug.get_path()).glob("**/*.java"):
            # We don't want to generate bugs on the tests
            relative_path = str(file.relative_to(pathlib.Path(bug.get_path())))

            if "test" not in relative_path and "Test" not in relative_path:
                perturbations_file = "./perturbations-%s-%s" % (relative_path.replace("/", "."), str(uuid.uuid4()))
                cmd = "timeout 600 java -jar %s %s %s %s" % (args.perturbation_model, file, generation_strategy, perturbations_file)
                run = subprocess.run(cmd, shell=True, capture_output=True)

                generated_bugs = construct_bug(args, bug, file, perturbations_file)
                if generated_bugs != None:
                    counter += len(generated_bugs)
                    new_dataset.get_bugs().update(generated_bugs)
                    print("Generated %d bugs for %s..." % (len(generated_bugs), file.name))

            # TODO: debug purposes only
            #if counter > 0:
            #    break
            #break
        print("Generated %d bugs for project %s\n\n\n" % (counter, bug.get_identifier()))
       
        # Save the dataset
        path = pathlib.Path(args.storage, args.model_output.split(".json")[0] + "_" + bug.get_identifier().lower() + ".json")
        serialization_utils.save_dataset_to_file(args, new_dataset, path)
