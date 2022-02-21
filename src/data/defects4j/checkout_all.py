import argparse
import subprocess
import os

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

    # Checkout all buggy and fixed versions
    for pid in pids:
        for bid in bugs[pid]:
            buggy_path = os.path.join(args.storage, pid, bid, "buggy")
            if not os.path.exists(buggy_path):
                os.makedirs(buggy_path)
            else:
                continue
            print("Checking out buggy %s-%s..." % (pid, bid))
            run = subprocess.run([defects4j_bin, "checkout", "-p", pid, "-v", bid + "b", "-w", buggy_path], capture_output=True)
            try:
                run.check_returncode()
            except subprocess.CalledProcessError:
                print(run)
                os.rmdir(buggy_path)
                continue
            print("Checked-out out buggy %s-%s" % (pid, bid))

            fixed_path = os.path.join(args.storage, pid, bid, "fixed")
            if not os.path.exists(buggy_path):
                os.makedirs(fixed_path)
            print("Checking out fixed %s-%s..." % (pid, bid))
            run = subprocess.run([defects4j_bin, "checkout", "-p", pid, "-v", bid + "f", "-w", fixed_path], capture_output=True)
            try:
                run.check_returncode()
            except subprocess.CalledProcessError:
                os.rmdir(buggy_path)
                os.rmdir(fixed_path)
                break
            print("Checked-out out fixed %s-%s" % (pid, bid))
