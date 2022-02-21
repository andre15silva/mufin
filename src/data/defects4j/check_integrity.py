import argparse
import subprocess
import os
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to checkout all bugs (buggy and fixed versions) from Defects4J")
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    parser.add_argument("--defects4j", help="Path to the defects4j directory", required=True, metavar="<path_to_defects4j>")
    args = parser.parse_args()

    # Get all project ids
    defects4j_bin = os.path.join(args.defects4j, "framework/bin/defects4j")
    run = subprocess.run([defects4j_bin, "pids"], capture_output=True)
    run.check_returncode()
    pids = {pid.decode("utf-8") for pid in run.stdout.split()}

    # Get all bug ids for all projects
    # bugs -> mapping (pid -> set of bids)
    bugs = {}
    for pid in pids:
        run = subprocess.run([defects4j_bin, "bids", "-p", pid], capture_output=True)
        run.check_returncode()
        bugs[pid] = {bid.decode("utf-8") for bid in run.stdout.split()}
        print("Found %3d bugs for project %s" % (len(bugs[pid]), pid))

    count = 0
    missing = set()
    # Checkout all buggy and fixed versions
    for pid in pids:
        for bid in bugs[pid]:
            count += 1

            buggy_path = os.path.join(args.storage, pid, bid, "buggy", "defects4j.build.properties")
            fixed_path = os.path.join(args.storage, pid, bid, "fixed", "defects4j.build.properties")
            if not os.path.exists(buggy_path) or not os.path.exists(fixed_path):
                missing.add(pid + "-" + bid)

    if len(missing) > 0:
        print("There is/are " + str(len(missing)) + " bug(s) missing or with compromised integrity.")
        for bug in missing:
            print(bug)
        sys.exit(1)
    else:
        print("There are no bugs missing or with compromised integrity.")
        sys.exit(0)
