from showdocs import structs

import collections


def _splitnewline(s, a):
    lineno = 0
    indices = []
    start = end = a.start
    while end < a.end:
        if s[end] in '\r\n':
            indices.append((start, end, lineno))
            start = end = end+1
            lineno += 1
        else:
            end += 1

    if start < a.end:
        indices.append((start, end, lineno))
    assert a.end == indices[-1][1]

    stripped = []
    for x, y, lineno in indices:
        sub = s[x:y]
        if not sub.strip():
            continue
        left = sub.lstrip()
        right = sub.rstrip()
        x += len(sub)-len(left)
        y -= len(sub)-len(right)
        stripped.append((x, y, lineno))

    return [structs.Annotation(x, y, a.group, list(a.classes), lineno)
            for x, y, lineno in stripped]

def wrap(s, annotations):
    nonewlines = []
    for a in annotations:
        if a.decoration() == structs.decorate.UNDER:
            nonewlines.extend(_splitnewline(s, a))
        else:
            nonewlines.append(a)

    nooverlaps = []

    # TODO: only do this for UNDER
    fromend = sorted(nonewlines, key=lambda a: a.end, reverse=True)
    while fromend:
        a = fromend.pop(0)
        for aa in fromend:
            # aa |------|      => |------|    aa
            # a    |-------|        |----|    a
            #                            |--| a
            if aa.start < a.start < aa.end and a.end > aa.end:
                fromend.append(structs.Annotation(a.start, aa.end, a.group, a.classes))
                fromend.append(structs.Annotation(aa.end, a.end, a.group,
                                                  a.classes))
                break
        else:
            nooverlaps.append(a)

    add = []
    for a in nooverlaps:
        add.append((a.start, a.format()))
        add.append((a.end, '</span>'))

    def c(x, y):
        if x[0] != y[0]:
            return cmp(x[0], y[0])
        # If open/close tags are at the same index, put the closing after.
        if x[1] == '</span>':
            return -1
        # Maintain initial order otherwise.
        return 0
    sortedstart = sorted(add, cmp=c)

    shifted = 0
    l = list(s)
    for index, contents in sortedstart:
        shiftedindex = index + shifted
        for i, c in enumerate(contents):
            l.insert(shiftedindex + i, c)

        shifted += len(contents)

    return ''.join(l)
