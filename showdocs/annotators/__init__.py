from showdocs import errors

import sql

_all = [sql.SqlAnnotator]
_annotators = {}

for a in _all:
    for alias in a.alias:
        if alias in _annotators:
            raise ValueError('annotator %s alias %r collides with %s' %
                             (a.__name__, alias, _annotators[alias].__name__))
        _annotators[alias] = a

def get(lang):
    acls = _annotators.get(lang, None)
    if not acls:
        raise errors.NoAnnotatorFound("lang %r isn't supported" % lang)

    return acls()
