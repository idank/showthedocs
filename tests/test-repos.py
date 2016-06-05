import os, tempfile, shutil
import unittest

from showdocs import repos, filters
from showdocs.repos import *

import showdocs.filters.common
import showdocs.repos.manager

class testfilter(filters.common.Filter):
    def process(self):
        # Change text of node in file.html.
        links = self.root.cssselect('a')
        if len(links) != 0:
            links[0].text = 'c'

class testrepo(repos.common.Repository):
    name = 'test'
    def build(self):
        self.subprocess('echo')
        with open(os.path.join(self.stagingdir, 'file.html'), 'w') as f:
            f.write('<a>b</a>')
        subdir = os.path.join(self.stagingdir, 'foo')
        if not os.path.exists(subdir):
            os.mkdir(subdir)

        open(os.path.join(subdir, 'bar.html'), 'w').write('hi')
        # This file shouldn't appear in the output dir.
        open(os.path.join(subdir, 'baz.html'), 'w').write('hi')

        # Test lxml preserves unicode correctly.
        with open(os.path.join(self.stagingdir, 'unicode.html'), 'w') as f:
            f.write(u'<b>\u05d0</b>'.encode('utf8'))

    def match(self):
        yield lambda p: False
        yield 'file.html'
        yield 'unicode.html'
        yield 'foo/bar.html'

    def filters(self):
        return [testfilter]

class TestRepos(unittest.TestCase):
    def tearDown(self):
        if hasattr(self, 'tempdir') and os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_list(self):
        names = ['nginx', 'postgres', 'mysql']
        self.assertEquals(repos.manager.listrepos(), names)

    def test_generate(self):
        tempdir = tempfile.mkdtemp(prefix='showdocs')
        stagingdir = os.path.join(tempdir, 'stagingdir')
        outdir = os.path.join(tempdir, 'outdir')
        os.mkdir(stagingdir)
        os.mkdir(outdir)

        manager = repos.manager.RepositoryManager([testrepo], stagingdir, outdir)
        manager.generate()

        for p in ('file.html', 'unicode.html', 'foo/bar.html'):
            path = os.path.join(outdir, 'test', p)
            self.assertTrue(os.path.exists(path))
        self.assertFalse(os.path.exists(os.path.join(outdir, 'test', 'foo',
                                                     'baz.html')))

        self.assertEquals(open(os.path.join(outdir, 'test', 'file.html')).read(), '<a>c</a>')
        self.assertEquals(
            open(os.path.join(outdir, 'test', 'unicode.html')).read(),
            u'<b>\u05d0</b>'.encode('utf-8'))

        old = testrepo.filters
        testrepo.filters = lambda self: []

        manager.generate()
        self.assertEquals(
            open(os.path.join(outdir, 'test', 'file.html')).read(), '<a>b</a>')

        testrepo.filters = old
