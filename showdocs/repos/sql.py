from showdocs import filters, repos

import showdocs.repos.common
import showdocs.repos.devdocs

import showdocs.filters.postgres

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
