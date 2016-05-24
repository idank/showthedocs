  $ . $TESTDIR/setup.t.bash

  $ for f in $(cd $TESTDIR/../external && find . -name '*.html' | cut -c 3-); do
  >     python $TESTDIR/validatedoc.py "$f"
  > done
  validating 'nginx/ngx_core_module.html'
  validating 'sql/mysql/select.html'
  tag '<em data-showdocs="s', group 'select-expr' has no showdocs-decorate-* class, found 'replaceable'
  tag '<code class="literal', group 'foo' has no showdocs-decorate-* class, found 'literal'
  tag '<code class="literal', group 'foo2' has no showdocs-decorate-* class, found 'literal'
  validating 'sql/pg/foo.html'
  validating 'sql/pg/select.html'
  validating 'test/select.html'
  tag '<em data-showdocs="s', group 'select-expr' has no showdocs-decorate-* class, found 'replaceable'
  tag '<code class="literal', group 'foo' has no showdocs-decorate-* class, found 'literal'
  tag '<code class="literal', group 'foo2' has no showdocs-decorate-* class, found 'literal'
