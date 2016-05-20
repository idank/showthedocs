# contributing

There are two main areas where showthedocs could improve: supporting a new
language and improving an existing parser/annotator. The UI itself doesn't work
very well on small/touch screens, so if someone cares about that, feel free to
send suggestions or pull requests.

## supporting a new language

Adding a language requires the following:

1. writing a parser (or using an existing one)
1. using that parser to annotate queries
1. importing the documentation (usually a small subset of it) and annotating it
   as well

[This commit](http://todo) that added the nginx parser, annotator and
documentation could be used as a reference for the various sections of the code
that need to be modified.

### writing a parser

The parsing that showthedocs needs is generally a lot more shallow than the one
used by the target language tooling. Python has a vast array of existing
parsers, so check what's out there before starting one from scratch. If you do
write one, prefer to write a lenient parser, since the purpose of showthedocs
isn't to validate.

The parser should produce some form of an AST that can be easily traversed by
the annotator (more on that next). In essence this is similar to what most
syntax highlighters do, but for the results to be more meaningful than "this is
a keyword", or "that is a string", parsing needs to go deeper and provide
things like "this is a SELECT statement, these are the table names", etc.

SQL is parsed using an external library (sqlparse), and nginx is a modified
version of nginxparser that produces an AST (that is richer than the original
output of the parser).

### annotating code

This is the definiton of an annotation:

    class Annotation(object):
        '''An annotation selects a range in the input, assigns it a group and
        a list of arbitrary class names. Annotations translate to HTML by
        wrapping the range in a <span> tag. The group appears as the value of
        a data-showdocs attribute, likewise for the class names.

        A group is an arbitrary string that identifies the selected range. A group
        is visualized in a special manner in the user interface, depending on the
        decoration applied to it. A group exists to connect a piece of the input to
        its documentation, which will somewhere have a tag with the same
        data-showdocs attribute.

        The list of class names is currently only used to apply decorations.
        A decoration controls the display of the annotation in the UI. The most
        common one is a back decoration, which changes the background color and
        supports things like connecting links when hovering the annotation.'''
        def __init__(self, start, end, group, classes):
            if end <= start:
                raise ValueError('end smaller than start')
            if not isinstance(classes, list):
                raise ValueError('classes needs to be a list')

            self.start = start
            self.end = end
            self.group = group
            self.classes = classes

The annotation process consists of creating annotations for the input by
traversing the AST produced by the parser. It is the responsibility of the
annotator to assign groups to certain parts of the input and apply
decorations. Lastly, the annotator needs to request a piece of
documentation to appear in the result of the query.

For example, if we consider the query:

    SELECT * FROM foo;

we might see these annotations:

- `SELECT`, group=select, decorate=back
- `*`, group=column, decorate=back
- `FROM`, group=from, decorate=back
- `foo`, group=table, decorate=back

### documentation

The final piece is bringing the documentation of the target language into
showthedocs. All we care about is HTML that has a bunch of tags with
`data-showdocs` and some decorations applied to those. Getting that without
manually editing potentially hundres of pages can be very
easy to extremely hard.

Usually documentation is written in a different format that is then used to
generate HTML. A common one is DocBook. Ideally you can edit those sources in
strategic places (such as a page that describes the SELECT statement for
postgresql) to include
`data-showdocs` with an appropriate group, and a decoration. Here's an [example
of such
a change](https://bitbucket.org/idank/nginx.org/commits/1f955652d11905b119de261e57a5798d533da52f#chg-xsls/directive.xsls)
in nginx's documentation. Sometimes the documentation is using arcane tools
from the early 90's (hello postgres) and trying to make them do as you please
can be frustrating. In those cases, we resort to building the docs as is and
annotating them by hand and with Javascript.

Once we've edited the doc sources, we add a script to build them and copy them
to a directory under `external/`.  An annotator can then request to include a file from this directory by calling
`self.add`, e.g. a file at `external/foo/bar.html` will show up in the result
of a query if its annotator calls `self.add('foo/bar.html')`.
