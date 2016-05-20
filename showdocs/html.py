import collections
import markupsafe

from showdocs import structs


def _splitnewline(s, a):
    '''Split the given annotation, a, if it crosses a new line.

    Some decorations don't work well when they span more than one line. It's
    somewhat easier to handle that here than in the UI.'''
    lineno = 0

    # A list of (startpos, endpos, line number).
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

    # For each item in indices, strip it from both ends so it doesn't start on
    # a whitespace.
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
    '''wrap takes an input string and a list of annotations for that string,
    and produces HTML where each selection of an annotation is wrapped in
    a <span> with the specificed attributes for that annotation.

    It handles annotations crossing newlines and intersecting with one
    another.'''
    nonewlines = []
    for a in annotations:
        if a.decoration() == structs.decorate.UNDER:
            nonewlines.extend(_splitnewline(s, a))
        else:
            nonewlines.append(a)

    nooverlaps = []

    # If two annotations intersect such that one isn't fully contained in the
    # other, we need to split it so the closing tag of the first won't close
    # the opening tag of the second.
    fromend = sorted(nonewlines, key=lambda a: a.end, reverse=True)
    while fromend:
        a = fromend.pop(0)
        for aa in fromend:
            # aa |------|      => |------|    aa
            # a    |-------|        |----|    a
            #                            |--| a
            if aa.start < a.start < aa.end and a.end > aa.end:
                fromend.append(structs.Annotation(a.start, aa.end, a.group,
                                                  a.classes))
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

def formaterror(query, error):
    '''Formats the given query and ParsingError, decorating the query at the
    position the error happened.'''
    pos = error.position
    wrappedquery = wrap(query, [structs.Annotation(pos, pos + 1, 'error',
                                                   [structs.decorate.BACK])])

    wrappederrorstring = 'at position %d' % error.position
    epos = (len('at position '), len(wrappederrorstring))
    wrappederrorstring += ': %s.' % markupsafe.escape(error.message)
    wrappederrorstring = wrap(wrappederrorstring, [structs.Annotation(
        epos[0], epos[1], 'error', [structs.decorate.BACK])])

    return wrappedquery, wrappederrorstring
