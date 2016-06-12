from showdocs import errors, decorate, annotators, html, structs, docs

class formatoptions(object):
    known = ['reindent', 'keywordcase']
    def __init__(self):
        self.opts = {}
        for k in self.known:
            self.opts[k] = False

            def makesetter(k):
                def setter():
                    self.opts[k] = True
                    return self
                return setter
            setattr(self, k, makesetter(k))

    def asobject(self):
        class container(object):
            def __init__(self, d):
                for k, v in d.iteritems():
                    setattr(self, k, v)
        return container(self.opts)

    def asdict(self):
        return dict(self.opts)


def annotate(query, lang, formatquery):
    if lang == 'guess':
        pass

    ann = annotators.get(lang)

    if formatquery:
        # TODO: fix me?
        query = ann.format(query, formatoptions().reindent().keywordcase())

    annotations = ann.annotate(query)
    # TODO: verify annotations start/end are inside query

    if not ann.docs:
        raise errors.NoDocsError()

    return html.wrap(query, annotations), ann.docs
