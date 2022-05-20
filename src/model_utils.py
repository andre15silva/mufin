from unidiff import PatchSet

# TODO: Change this to generate the definitive complex training sample
# It should iterate both target and source lines and add the buggy bounds
def source_str(example):
    diff = PatchSet(example)
    source = ""
    for line in diff[0][0].target_lines():
        if line.is_added:
            source += " [START_BUGGY] " + line.value.strip() + " [END_BUGGY] "
        else:
            source += line.value.strip()
    return source


# TODO: Change this to generate the definitive complex training sample
def target_str(example):
    diff = PatchSet(example)
    for line in diff[0][0].source_lines():
        if line.is_removed:
            return line.value.strip()
    return ""
