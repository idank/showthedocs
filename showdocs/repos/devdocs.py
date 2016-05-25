import subprocess, os, logging

from showdocs import filters, errors, config, repos

import showdocs.filters.nginx
import showdocs.repos.common

logger = logging.getLogger(__name__)

class DevDocsRepository(repos.common.Repository):
    def __init__(self, stagingdir):
        devdocs = os.path.join(config.STAGING_DIR, 'devdocs')
        super(DevDocsRepository, self).__init__(devdocs)

        try:
            output = self.subprocess('thor docs:list')
            if len(output.split()) < 5:
                raise errors.RepoBuildError(
                    "thor docs:list returned unexpected output: %r" % output)
        except (OSError, subprocess.CalledProcessError), e:
            raise errors.RepoBuildError(
                "%s doesn't look like a clone of devdocs (looked for thor)" %
                self.stagingdir)

    def _page(self, page, name=None):
        if name is None:
            name = self.name
        output = self.subprocess('thor docs:page %s %s' % (name, page))
        if 'failed' in output.lower():
            raise RuntimeError('failed fetching %r: %s' % (page, output))
