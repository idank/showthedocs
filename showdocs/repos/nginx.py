from showdocs import filters, repos

import showdocs.filters.nginx

import showdocs.repos.common
import showdocs.repos.devdocs

@repos.common.register
class NginxRepository(repos.devdocs.DevDocsRepository):
    name = 'nginx'

    @classmethod
    def filters(cls):
        mine = [filters.nginx.DirectiveFilter]
        return super(NginxRepository, cls).filters() + mine

    def build(self):
        self._page('/ngx_core_module.html')
        self._page('/http/ngx_http_core_module.html')

    def match(self):
        yield 'public/docs/nginx/*.html'

    def outputpath(self, path):
        return path[len('public/docs/nginx/'):]
