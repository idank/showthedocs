import os

from showdocs import filters, repos

import showdocs.repos.common
import showdocs.repos.devdocs

import showdocs.filters.postgres
import showdocs.filters.mysql

@repos.common.register
class PostgresRepository(repos.devdocs.DevDocsRepository):
    name = 'postgres'

    @classmethod
    def filters(cls):
        mine = [filters.postgres.AnnotatingFilter]
        return super(PostgresRepository, cls).filters() + mine

    def build(self):
        self._page('/sql-select.html', name='postgres@9.5')

    def match(self):
        yield 'public/docs/postgresql~9.5/*.html'

    def outputpath(self, path):
        return path[len('public/docs/postgresql~9.5/'):]

@repos.common.register
class MySqlRepository(repos.common.ScrapedRepository):
    name = 'mysql'

    @classmethod
    def filters(cls):
        mine = [filters.mysql.CleanHtmlFilter, filters.common.AbsoluteUrls,
                filters.mysql.AnnotatingFilter]
        return super(MySqlRepository, cls).filters() + mine

    def build(self):
        base_url = 'http://dev.mysql.com/doc/refman/5.7/en/'
        urls = []
        urls.append('http://dev.mysql.com/doc/refman/5.7/en/select.html')

        for url in urls:
            path = os.path.join(self.stagingdir, url[len(base_url):])
            with open(path, 'wb') as f:
                f.write(self.httpget(url))
            self.context.path_to_url[path] = url
