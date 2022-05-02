from unidiff import PatchSet

# TODO: Change this to generate the definitive complex training sample
def source_str(example):
    diff = PatchSet(example)
    for line in diff[0][0].source_lines():
        if line.is_removed:
            return line.value.strip()


# TODO: Change this to generate the definitive complex training sample
def target_str(example):
    diff = PatchSet(example)
    for line in diff[0][0].target_lines():
        if line.is_added:
            return line.value.strip() 
