import pandas as pd
import json
import argparse

import utils


buglab_rules = {
        "1" : "BugLab-Rule1: variable misuse",
        "2" : "BugLab-Rule2: argument swapping",
        "3" : "BugLab-Rule3: wrong operator",
        "4" : "BugLab-Rule4: wrong literal",
        "None" : "None"
        }

selfapr_rules = {
        "1" : "SelfAPR-Rule1: modify declaring type",
        "2" : "SelfAPR-Rule2: modify operator",
        "3" : "SelfAPR-Rule3: modify literal",
        "4" : "SelfAPR-Rule4: modify constructor",
        "5" : "SelfAPR-Rule5: modify/swap arguments",
        "6" : "SelfAPR-Rule6: reduce/expand boolean expression",
        "7" : "SelfAPR-Rule7: modify/replace invocation",
        "8" : "SelfAPR-Rule8: compoud of rules 1 to 7",
        "9" : "SelfAPR-Rule9: replace target statement with similar donor",
        "10" : "SelfAPR-Rule10: move later statement before target",
        "11" : "SelfAPR-Rule11: transplant donor statement",
        "12" : "SelfAPR-Rule12: wrap target statement with existing conditional block",
        "13" : "SelfAPR-Rule13: insert existing block",
        "14" : "SelfAPR-Rule14: delete target statement",
        "15" : "SelfAPR-Rule15: unwrap block",
        "16" : "SelfAPR-Rule16: remove block",
        "None" : "None"
        }



def request_validation(args, result, patch):
    if patch["identical"]:
        print("Patch is identical. Validation is automatic!")
        return True

    print("-" * 50)
    print("PATCH:")
    print(patch["patch"])
    print("GROUND TRUTH:")
    print(result["ground_truth"])
    
    i = input("VALIDATE? (Y/N) :")

    return "y" in i.lower()


def request_rule(args, result, patch):
    rules = buglab_rules if args.buglab else selfapr_rules

    print("-" * 50)
    for rule in rules:
        print("%s\t%s" % (rule, rules[rule]))
    print("-" * 50)
    print("PATCH:")
    print(patch["patch"])

    rule = input("Choose rule: ")
    while rule not in rules:
        rule = input("Choose rule: ")

    return rules[rule]


def analysis(args):
    # Load the results file
    with open(args.results) as f:
        results = json.load(f)


    # Iterate over bugs
    new_results = {}
    for bug in results:
        print("-" * 100)
        print("Analyzing %s..." % bug)
        result = results[bug]
        validated_patches = []

        # Validate patches
        for patch in result["patches"]:
            if (patch["test_exec"] and patch["test_pass"]) or patch["identical"]:
                patch["validation"] = request_validation(args, result, patch)
                if patch["validation"]:
                    validated_patches.append(patch)

        # Get rules
        for patch in validated_patches:
            patch["rule"] = request_rule(args, result, patch)

        # Store the results
        result["patches"] = validated_patches
        new_results[bug] = result

    # Store the result
    with open(args.output, "w") as f:
        json.dump(new_results, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to train a model based on a given dataset.")
    parser = utils.add_manual_analysis_args(parser)
    args = parser.parse_args()

    analysis(args)
