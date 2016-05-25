import os, fnmatch, shutil, subprocess, logging

from showdocs import filters, errors

import showdocs.filters.common

logger = logging.getLogger(__name__)

class Repository(object):
    '''A repository builds documentation for a language. Most often, this
    involves executing an external tool that generates HTML. The repository
    defines the files that end up in output dir, and specifies a list of
    filters that postprocess the generated HTML, e.g. to remove/add elements,
    change link urls, etc.'''
    def __init__(self, stagingdir):
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
            filteredcontents = filters.common.pipeline(self.filters(), contents)
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

registered = {}
def register(cls):
    if not getattr(cls, 'name'):
        raise ValueError('%r missing name attribute' % cls)
    registered[cls.name] = cls
    return cls

def listrepos():
    return registered.keys()

def get(name):
    if name not in registered:
        raise ValueError('unknown lang %r, known languages: %s' %
                         (name, ', '.join(registered.keys())))
    return registered[name]

class RepositoryManager(object):
    '''Builds the given repositories, creating and cleaning directories for
    each repo.'''
    def __init__(self, repos, stagingdir, outdir):
        self.repos = repos
        self.stagingdir = stagingdir
        self.outdir = outdir

    def generate(self):
        '''generates all repos. Each repository's output files end up under
        self.outdir/repo.name. Overwrites existing files.'''
        for repocls in self.repos:
            repostagingdir = os.path.join(self.stagingdir, repocls.name)

            if not os.path.exists(repostagingdir):
                os.mkdir(repostagingdir)

            repo = repocls(repostagingdir)
            repo.build()
            files = list(repo.files())
            if not len(files):
                raise errors.RepoBuildError('repo %r build returned no files' %
                                            repocls.name)
            repo.filter()
            repo.clean()

            repooutdir = os.path.join(self.outdir, repocls.name)
            if not os.path.exists(repooutdir):
                os.mkdir(repooutdir)

            for f in files:
                relpath = os.path.relpath(f, repo.stagingdir)
                outpath = repo.outputpath(relpath)
                destpath = os.path.join(self.outdir, repo.name, outpath)
                logger.info('copying staging file %r -> %r', f, destpath)
                dirname = os.path.dirname(destpath)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                shutil.copyfile(f, destpath)
