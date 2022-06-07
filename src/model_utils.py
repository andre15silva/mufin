from unidiff import PatchSet


def source_str(example):
    diff = PatchSet(example)
    source = ""
    start_buggy = -1
    end_buggy = -1
    for i, line in enumerate(diff[0][0].target_lines()):
        if line.is_added:
            if start_buggy == -1:
                start_buggy = i
            if end_buggy < i:
                end_buggy = i
    
    for i, line in enumerate(diff[0][0].target_lines()):
        if i == start_buggy:
            source += " [START_BUGGY] "
        source += " " + line.value.strip() + " "
        if i == end_buggy:
            source += " [END_BUGGY] "

    return source


def target_str(example):
    diff = PatchSet(example)
    start_fix = -1
    end_fix = -1
    for i, line in enumerate(diff[0][0].source_lines()):
        if line.is_removed:
            if start_fix == -1:
                start_fix = i
            if end_fix < i:
                end_fix = i

    target = ""
    for i, line in enumerate(diff[0][0].source_lines()):
        if i >= start_fix and i <= end_fix:
            target += " " + line.value.strip() + " "
    return target
