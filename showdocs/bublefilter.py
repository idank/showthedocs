from webassets.filter import register_filter, ExternalTool

class Buble(ExternalTool):
    name = 'buble'
    max_debug_level = None

    options = {
        'binary': 'BUBLE_BIN',
        'extra_args': 'BABEL_EXTRA_ARGS',
        'run_in_debug': 'BABEL_RUN_IN_DEBUG',
    }

    def setup(self):
        super(Buble, self).setup()
        if self.run_in_debug is False:
            # Disable running in debug mode for this instance.
            self.max_debug_level = False

    def input(self, _in, out, **kw):
        args = [self.binary or 'buble']
        if self.extra_args:
            args.extend(self.extra_args)
        return self.subprocess(args, out, _in)

register_filter(Buble)
