import os, fnmatch, subprocess, logging
import requests  # for ScrapedRepository

from showdocs import filters, errors

import showdocs.filters.common

logger = logging.getLogger(__name__)

registered = {}
def register(cls):
    if not getattr(cls, 'name'):
        raise ValueError('%r missing name attribute' % cls)
    registered[cls.name] = cls
    return cls

class Context(object):
    '''The context is used to pass around information during the doc generation
    process. Parts of it are immutable during generation, others change
    depending on the current stage and/or file being processed.'''
    def __init__(self):
        # The url of the current file being processed. It is used when making
        # urls absolute after scraping a page.
        self.current_url = None

        # Whenever the scraper writes a file, it saves its original url in this
        # map to update self.current_url when that file is later processed.
        self.path_to_url = {}

class Repository(object):
    '''A repository builds documentation for a language. Most often, this
    involves executing an external tool that generates HTML. The repository
    defines the files that end up in output dir, and specifies a list of
    filters that postprocess the generated HTML, e.g. to remove/add elements,
    change link urls, etc.'''
    def __init__(self, stagingdir):
        self.context = Context()
        self.stagingdir = stagingdir

    def build(self):
        '''builds the documentation, putting any outputs in self.stagingdir.'''
        raise NotImplementedError
    def match(self):
        '''match is a generator that yields either a function that takes a path
        and returns True if that file should be included in the output, or
        a glob string that is matched against files. The paths are relative to
        self.stagingdir. It is possible to yield more than one of the above.'''
        yield lambda p: True
    def outputpath(self, path):
        '''outputpath maps paths (that are relative to self.stagingdir) to
        their location in the outputdir.'''
        return path

    def files(self):
        '''Generator for files under self.stagingdir that should be included in
        the output of the repository, according to match().'''
        m = list(self.match())
        for root, dirs, files in os.walk(self.stagingdir):
            for f in files:
                fullpath = os.path.join(root, f)
                relstaging = os.path.relpath(fullpath, self.stagingdir)
                for predicate in m:
                    if callable(predicate):
                        if predicate(relstaging):
                            yield fullpath
                    elif fnmatch.fnmatch(relstaging, predicate):
                        yield fullpath

    @classmethod
    def filters(cls):
        return []

    def filter(self):
        '''Filters the output files with the filters defined by
        self.filters.'''
        self.log('info', 'starting to filter with %r', self.filters())
        for f in self.files():
            absolute = os.path.join(self.stagingdir, f)
            with open(absolute) as ff:
                contents = ff.read()

            self._updatecontext(absolute)
            filteredcontents = filters.common.pipeline(
                self.context, self.filters(), contents)
            if contents != filteredcontents:
                self.log('info', 'file %r changed, overwriting', f)
                with open(absolute, 'wb') as ff:
                    ff.write(filteredcontents)
            else:
                self.log('info', 'file %r unchanged by filters', f)
        self.log('info', 'done filtering')

    def clean(self):
        pass

    def subprocess(self, *args, **kwargs):
        '''Call subprocess.check_output with the given arguments. Sets cwd to
        self.stagingdir and shell by default.'''
        kwargs.setdefault('cwd', self.stagingdir)
        kwargs.setdefault('shell', True)

        self.log('info', 'running command: args=%r, kwargs=%r', args, kwargs)
        return subprocess.check_output(args, **kwargs)

    @classmethod
    def log(cls, level, message, *args):
        getattr(logger, level)('repo %s: ' + message, cls.name, *args)

    def _updatecontext(self, path):
        '''Updates parts of the context as we're handling file path.'''
        self.context.current_url = None
        if path in self.context.path_to_url:
            self.context.current_url = self.context.path_to_url[path]


class ScrapedRepository(Repository):
    '''A base class for repositories that scrape online docs.'''
    def httpget(self, url):
        '''Calls requests.get on the given URL and returns the response bytes.'''
        headers = {'user-agent': 'showthedocs'}

        self.log('info', 'http get: url=%s', url)
        # Let requests find the encoding and return a Unicode string, then
        # encode it as utf8.
        return requests.get(url, headers=headers).text.encode('utf8')
