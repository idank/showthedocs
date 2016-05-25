import os, shutil, logging

from showdocs import errors, repos
from showdocs.repos import *

import showdocs.repos.common

logger = logging.getLogger(__name__)

def listrepos():
    return repos.common.registered.keys()

def get(name):
    if name not in repos.common.registered:
        raise ValueError('unknown lang %r, known languages: %s' %
                         (name, ', '.join(repos.common.registered.keys())))
    return repos.common.registered[name]

class RepositoryManager(object):
    '''Builds the given repositories, creating and cleaning directories for
    each repo.'''
    def __init__(self, reposcls, stagingdir, outdir):
        self.reposcls = reposcls
        self.stagingdir = stagingdir
        self.outdir = outdir

    def generate(self):
        '''generates all repos. Each repository's output files end up under
        self.outdir/repo.name. Overwrites existing files.'''
        for repocls in self.reposcls:
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
