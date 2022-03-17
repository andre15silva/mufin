import subprocess
import pathlib

def get_diff(source: pathlib.Path, target: pathlib.Path) -> str:
    cmd = "find {} {} -type f ! -name '*.java' -printf '%f\n' | diff -N -u -r {} {} -X -".format(source, target, source, target)
    run = subprocess.run(cmd, shell=True, capture_output=True)
    return run.stdout.decode("utf-8")
