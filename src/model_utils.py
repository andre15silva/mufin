from unidiff import PatchSet


def get_type(example):
    diff = PatchSet(example)
    additions = 0
    removals = 0
    for i, line in enumerate(diff[0][0].target_lines()):
        if line.is_added:
            additions += 1
    for i, line in enumerate(diff[0][0].source_lines()):
        if line.is_removed:
            removals += 1

    # Replacement (there are additions and removals)
    if additions != 0 and removals != 0:
        return "REPLACE"
    # Addition (there are only removals from the source (i.e. fixed version))
    elif removals != 0:
        return "ADD"
    # Removals (there are only additions to the target (i.e. buggy_version))
    elif additions != 0:
        return "REMOVE"
    else:
        return "ERROR"


def source_str_hunk_targets(hunk, targets):
    source = ""
    for i, line in enumerate(hunk):
        if i == targets[0]:
            source += " [START_BUGGY] "
        if not line.is_removed:
            source += " " + line.value.strip() + " "
        if i == targets[1]:
            source += " [END_BUGGY] "

    return " ".join(source.split())


def source_str_hunk(hunk):
    start_buggy = -1
    end_buggy = -1
    for i, line in enumerate(hunk):
        if line.is_added or line.is_removed:
            if start_buggy == -1:
                start_buggy = i
            if end_buggy < i:
                end_buggy = i
    
    source = ""
    for i, line in enumerate(hunk):
        if i == start_buggy:
            source += " [START_BUGGY] "
        if not line.is_removed:
            source += " " + line.value.strip() + " "
        if i == end_buggy:
            source += " [END_BUGGY] "

    return " ".join(source.split())


def source_str(example):
    diff = PatchSet(example)
    return source_str_hunk(diff[0][0])


def target_str_hunk_targets(hunk, targets):
    target = ""
    for i, line in enumerate(hunk):
        if not line.is_added and i >= targets[0] and i <= targets[1]:
            target += " " + line.value.strip() + " "

    return " ".join(target.split())


def target_str_hunk(hunk):
    start_buggy = -1
    end_buggy = -1
    for i, line in enumerate(hunk):
        if line.is_added or line.is_removed:
            if start_buggy == -1:
                start_buggy = i
            if end_buggy < i:
                end_buggy = i

    target = ""
    for i, line in enumerate(hunk):
        if not line.is_added and i >= start_buggy and i <= end_buggy:
            target += " " + line.value.strip() + " "

    return " ".join(target.split())


def target_str(example):
    diff = PatchSet(example)
    return target_str_hunk(diff[0][0])


def source_str_buggy(example):
    diff = PatchSet(example)

    start_buggy = -1
    end_buggy = -1
    for i, line in enumerate(diff[0][0]):
        if line.is_removed or line.is_added:
            if start_buggy == -1:
                start_buggy = i
            if end_buggy < i:
                end_buggy = i
        
    source = ""
    for i, line in enumerate(diff[0][0]):
        if i == start_buggy:
            source += " [START_BUGGY] "
        if not line.is_added:
            source += " " + line.value.strip() + " "
        if i == end_buggy:
            source += " [END_BUGGY] "

    return " ".join(source.split())


def target_str_buggy(example):
    diff = PatchSet(example)

    start_fix = -1
    end_fix = -1
    for i, line in enumerate(diff[0][0]):
        if line.is_added or line.is_removed:
            if start_fix == -1:
                start_fix = i
            if end_fix < i:
                end_fix = i

    target = ""
    for i, line in enumerate(diff[0][0]):
        if not line.is_removed and i >= start_fix and i <= end_fix:
            target += " " + line.value.strip() + " "

    return " ".join(target.split())
