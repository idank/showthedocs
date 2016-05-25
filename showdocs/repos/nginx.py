import subprocess, os, logging

import showdocs.filters.nginx
from showdocs import filters, errors, config
from showdocs.repos import common

logger = logging.getLogger(__name__)

@common.register
class NginxRepository(common.Repository):
    name = 'nginx'

    def __init__(self, stagingdir):
        devdocs = os.path.join(config.STAGING_DIR, 'devdocs')
        super(NginxRepository, self).__init__(devdocs)

        try:
            output = self.subprocess('thor docs:list')
            if len(output.split()) < 5:
                raise errors.RepoBuildError(
                    "thor docs:list returned unexpected output: %r" % output)
        except (OSError, subprocess.CalledProcessError), e:
            raise errors.RepoBuildError(
                "%s doesn't look like a clone of devdocs (looked for thor)" %
                self.stagingdir)

    @classmethod
    def filters(cls):
        mine = [filters.nginx.DirectiveFilter]
        return super(NginxRepository, cls).filters() + mine

    def build(self):
        outputs = []
        outputs.append(self.subprocess('thor docs:page nginx /ngx_core_module.html'))
        outputs.append(self.subprocess(
            'thor docs:page nginx /http/ngx_http_core_module.html'))

        for output in outputs:
            if 'failed' in output.lower():
                raise RuntimeError

    def match(self):
        yield 'public/docs/nginx/*.html'

    def outputpath(self, path):
        return path[len('public/docs/nginx/'):]
