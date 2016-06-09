import os

from showdocs import filters, repos

import showdocs.repos.common

import showdocs.filters.gitconfig


@repos.common.register
class GitConfigRepository(repos.common.ScrapedRepository):
    name = 'gitconfig'

    @classmethod
    def filters(cls):
        mine = [filters.gitconfig.CleanHtmlFilter, filters.common.AbsoluteUrls,
                filters.gitconfig.AnnotatingFilter]
        return super(GitConfigRepository, cls).filters() + mine

    def build(self):
        url = 'https://git-scm.com/docs/git-config'

        path = os.path.join(self.stagingdir, 'git-config.html')
        with open(path, 'wb') as f:
            f.write(self.httpget(url))

        self.context.path_to_url[path] = url
